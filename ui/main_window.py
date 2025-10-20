import json
from collections import OrderedDict
from typing import Dict, Optional
from PySide6.QtCore import QThread, Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTabWidget,
    QLabel, QTextEdit, QMessageBox, QApplication
)
from scraping_worker import ScraperWorker
from .tabs.kream_tab import KreamTab
from utils.system_handler import open_output_folder
from api_client import auth, workflow, token_manager

class MainWindow(QMainWindow):
    """애플리케이션의 메인 윈도우 (컨테이너 역할)."""
    
    # 로그아웃 시그널 (MainApplication으로 알림)
    logout_requested = Signal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("판매내역 수집기")
        self.resize(800, 600)
        self.thread: Optional[QThread] = None
        self.worker: Optional[ScraperWorker] = None
        self._is_closing = False

        self._setup_ui()
        self._center_on_screen()
        
        # 토큰 갱신 타이머 시작 (30초마다 체크)
        self._start_token_refresh_timer()
        
        # 워크플로우 로드를 지연 실행 (창이 표시된 후)
        QTimer.singleShot(100, self._refresh_workflows)
    
    def _center_on_screen(self) -> None:
        """창을 화면 중앙에 배치합니다."""
        screen = QApplication.primaryScreen().geometry()
        window_geometry = self.frameGeometry()
        center_point = screen.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())

    def _setup_ui(self) -> None:
        """UI 구성요소를 설정합니다."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        self.tabs = QTabWidget()
        
        # 탭 바에 손가락 커서 적용
        self.tabs.tabBar().setCursor(Qt.CursorShape.PointingHandCursor)
        
        main_layout.addWidget(self.tabs)

    def _parse_workflows(self, workflows_by_permission: Dict[str, str]) -> Dict[str, Dict]:
        """워크플로우 데이터를 파싱하고, 에러는 별도로 저장합니다."""
        parsed_workflows = {}
        self._parsing_errors = []
        
        for permission, workflow_json_string in workflows_by_permission.items():
            try:
                # JSON 파싱 시 순서 보장을 위해 object_pairs_hook 사용
                workflow_data = json.loads(workflow_json_string, object_pairs_hook=OrderedDict)
                parsed_workflows[permission] = workflow_data
            except json.JSONDecodeError:
                error_msg = f"'{permission}' 권한의 워크플로우 JSON 형식이 잘못되었습니다."
                self._parsing_errors.append(error_msg)
        
        return parsed_workflows

    def _show_parsing_errors(self) -> None:
        """파싱 에러가 있으면 첫 번째 탭에 표시합니다."""
        if hasattr(self, '_parsing_errors') and self._parsing_errors:
            first_tab = self.tabs.widget(0)
            if first_tab and hasattr(first_tab, 'log_edit'):
                for error_msg in self._parsing_errors:
                    self.update_log_on_tab(first_tab, error_msg, "red")

    def _create_tabs(self) -> None:
        """워크플로우 객체를 기반으로 탭 위젯을 생성하고 추가합니다."""
        if not self.authorized_workflows:
            self._setup_fallback_ui()
            self.update_log_on_tab(self.tabs.widget(0), "표시할 수 있는 작업이 없습니다.", "orange")
            return

        for permission, workflow_data in self.authorized_workflows.items():
            tab_name = workflow_data.get("site_name", permission.upper())
            tab_widget = self._create_tab_widget(permission, workflow_data, tab_name)
            self.tabs.addTab(tab_widget, tab_name)

    def _create_tab_widget(self, permission: str, workflow_data: Dict, tab_name: str) -> QWidget:
        """개별 탭 위젯을 생성합니다."""
        if permission == 'kream':
            tab_widget = KreamTab(workflow_data)
            tab_widget.start_scraping_signal.connect(self.start_scraping)
            tab_widget.stop_button.clicked.connect(self.stop_scraping)
            tab_widget.folder_button.clicked.connect(self.open_current_tab_folder)
            tab_widget.permission = permission
            return tab_widget
        else:
            # 기타 권한용 기본 탭
            tab_widget = QWidget()
            layout = QVBoxLayout(tab_widget)
            layout.addWidget(QLabel("업데이트 예정입니다."))
            tab_widget.permission = permission
            return tab_widget

    def _setup_fallback_ui(self) -> None:
        """워크플로우가 하나도 없을 때 표시할 최소한의 UI를 설정합니다."""
        fallback_tab = QWidget()
        self.tabs.addTab(fallback_tab, "알림")
        layout = QVBoxLayout(fallback_tab)
        log_edit = QTextEdit()
        log_edit.setReadOnly(True)
        layout.addWidget(log_edit)
        fallback_tab.log_edit = log_edit

    def _show_no_workflow_message(self) -> None:
        """워크플로우가 없을 때 중앙에 안내 메시지를 표시합니다."""
        # 모든 탭 제거
        while self.tabs.count() > 0:
            self.tabs.removeTab(0)
        
        # 안내 메시지 탭 생성
        message_tab = QWidget()
        self.tabs.addTab(message_tab, "안내")
        
        layout = QVBoxLayout(message_tab)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 메시지 라벨
        message_label = QLabel(
            "사용 가능한 워크플로우가 없습니다.\n\n"
            "관리자에게 문의바랍니다."
        )
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: #666;
                padding: 40px;
                line-height: 1.6;
            }
        """)
        
        layout.addWidget(message_label)

    def open_current_tab_folder(self) -> None:
        """현재 활성화된 탭에 해당하는 output 하위 폴더를 엽니다."""
        current_tab_name = self.tabs.tabText(self.tabs.currentIndex())
        open_output_folder(current_tab_name)

    def start_scraping(self, workflow_data: Dict, date_range: Dict) -> None:
        """탭으로부터 신호를 받아 스크랩핑 스레드를 시작합니다."""
        active_tab = self.tabs.currentWidget()
        if not (active_tab and hasattr(active_tab, 'start_button')):
            return

        # 스크래핑 시작 전 토큰 체크 및 갱신 (권한 체크 포함)
        current_permission = getattr(active_tab, 'permission', None)
        if not self._check_and_refresh_token(current_permission):
            return

        self._prepare_ui_for_scraping(active_tab)
        self._create_and_start_worker(workflow_data, date_range, active_tab)

    def _prepare_ui_for_scraping(self, active_tab: QWidget) -> None:
        """스크래핑 시작을 위한 UI 준비"""
        active_tab.start_button.setEnabled(False)
        active_tab.stop_button.setEnabled(True)
        active_tab.log_edit.clear()
        active_tab.progress_bar.setValue(0)

    def _create_and_start_worker(self, workflow_data: Dict, date_range: Dict, active_tab: QWidget) -> None:
        """워커 스레드를 생성하고 시작합니다."""
        self.thread = QThread()
        self.worker = ScraperWorker(workflow_data, date_range)
        self.worker.moveToThread(self.thread)

        # 시그널 연결
        self.worker.step_started.connect(self.on_step_started)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.log_message.connect(
            lambda msg, color: self.update_log_on_tab(self.tabs.currentWidget(), msg, color)
        )
        self.worker.error.connect(
            lambda msg: self.update_log_on_tab(self.tabs.currentWidget(), msg, "red")
        )
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_scraping_finished)
        
        self.thread.start()

    def stop_scraping(self) -> None:
        """진행 중인 스크랩핑 작업을 중단하도록 요청합니다."""
        active_tab = self.tabs.currentWidget()
        if self.worker:
            self.update_log_on_tab(active_tab, "작업 중단을 요청합니다...", "orange")
            self.worker.stop()
            if hasattr(active_tab, 'stop_button'):
                active_tab.stop_button.setEnabled(False)

    def on_scraping_finished(self) -> None:
        """스크랩핑 작업이 완료/중단되었을 때 UI를 정리합니다."""
        active_tab = self.tabs.currentWidget()
        self.update_log_on_tab(active_tab, "작업 스레드가 종료되었습니다.", "blue")
        
        if hasattr(active_tab, 'start_button'):
            active_tab.start_button.setEnabled(True)
            active_tab.stop_button.setEnabled(False)
        
        self._cleanup_thread()

        if self._is_closing:
            self.close()
            return
        
        # 작업 완료 후 토큰이 만료되었는지 확인
        self._check_and_refresh_token()

    def _cleanup_thread(self) -> None:
        """스레드 정리"""
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()
        
        self.thread = None
        self.worker = None
    
    def update_log_on_tab(self, tab: QWidget, message: str, color: str = "black") -> None:
        """지정된 탭의 로그 창에 메시지를 업데이트합니다."""
        if hasattr(tab, 'log_edit'):
            html_message = f'<font color="{color}">{message}</font>'
            tab.log_edit.append(html_message)
            # 자동 스크롤 다운
            scrollbar = tab.log_edit.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
            
    def update_progress(self, current: int, total: int) -> None:
        """프로그레스 바의 값을 업데이트합니다."""
        active_tab = self.tabs.currentWidget()
        if hasattr(active_tab, 'progress_bar'):
            active_tab.progress_bar.setMaximum(total)
            active_tab.progress_bar.setValue(current)

    def on_step_started(self, step_name: str) -> None:
        """새로운 스크랩 단계가 시작될 때 프로그레스 바를 리셋합니다."""
        active_tab = self.tabs.currentWidget()
        if hasattr(active_tab, 'progress_bar'):
            active_tab.progress_bar.setValue(0)
            active_tab.progress_bar.setFormat(f"'{step_name}' 진행 중... %p%")

    def _start_token_refresh_timer(self) -> None:
        """토큰 갱신 타이머를 시작합니다. 30초마다 토큰 상태를 확인합니다."""
        self.token_refresh_timer = QTimer(self)
        self.token_refresh_timer.timeout.connect(self._check_and_refresh_token)
        self.token_refresh_timer.start(30000)  # 30초마다 체크

    def _check_and_refresh_token(self, check_permission: Optional[str] = None) -> bool:
        """
        토큰 갱신이 필요한지 확인하고, 필요하면 갱신합니다.
        
        Args:
            check_permission: 체크할 권한명. 제공되면 권한 유효성 확인 후 탭 유지/재생성 결정
                            None이면 무조건 탭 재생성
            
        Returns:
            토큰이 유효하거나 갱신 성공하면 True, 실패하면 False
        """
        try:
            # 토큰이 60초 이내에 만료되거나 권한이 만료되었는지 확인
            if token_manager.needs_refresh(buffer_seconds=60):
                # 작업 진행 중인지 확인
                is_scraping = self.thread is not None and self.thread.isRunning()
                
                # 토큰 갱신 시도
                result = auth.refresh_token()
                
                if result.get("success"):
                    # 특정 권한 체크가 요청된 경우 (스크래핑 시작 전)
                    if check_permission:
                        # token_manager를 통해 권한 유효성 확인
                        if not token_manager.has_permission(check_permission):
                            # 권한 없음 - 탭 재생성 필요
                            QMessageBox.critical(
                                self,
                                "권한 오류",
                                f"권한 만료({check_permission})\n화면을 새로고침합니다."
                            )
                            self._refresh_workflows()
                            return False
                        
                        # 권한 유효 - 작업 계속 진행 (탭 유지)
                        return True
                    else:
                        # 일반 갱신 (타이머, 작업 완료 후) - 탭 재생성
                        self._refresh_workflows()
                        return True
                else:
                    # 갱신 실패 처리
                    if is_scraping:
                        # 수집 작업 중이면 로그에만 경고 표시 (로그아웃하지 않음)
                        active_tab = self.tabs.currentWidget()
                        self.update_log_on_tab(
                            active_tab,
                            "인증 만료(갱신 실패). 작업 완료 후 다시 로그인해주세요.",
                            "orange"
                        )
                        return False
                    else:
                        # 작업 중이 아니면 팝업과 함께 로그아웃 처리
                        QMessageBox.critical(
                            self, 
                            "인증 오류",
                            "인증 만료(갱신 실패)\n다시 로그인해주세요."
                        )
                        self._logout()
                        return False
            
            return True  # 갱신 불필요
                    
        except Exception as e:
            # 예외 발생 시 처리
            is_scraping = self.thread is not None and self.thread.isRunning()
            
            if is_scraping:
                # 수집 작업 중이면 로그에만 경고 표시
                active_tab = self.tabs.currentWidget()
                self.update_log_on_tab(
                    active_tab,
                    "인증 만료(갱신 실패). 작업 완료 후 다시 로그인해주세요.",
                    "orange"
                )
                return False
            else:
                # 작업 중이 아니면 팝업과 함께 로그아웃 처리
                QMessageBox.critical(
                    self, 
                    "인증 오류", 
                    "인증 만료(갱신 실패)\n다시 로그인해주세요."
                )
                self._logout()
                return False

    def _refresh_workflows(self) -> None:
        """워크플로우를 서버에서 다시 가져와 탭을 업데이트합니다."""
        try:
            # 워크플로우 가져오기
            workflows = workflow.get_workflows()
            
            if not workflows:
                # 워크플로우가 없는 경우 중앙 안내 화면 표시
                self._show_no_workflow_message()
                return
            
            # 기존 탭 모두 제거
            while self.tabs.count() > 0:
                self.tabs.removeTab(0)
            
            # 워크플로우 파싱 및 탭 재생성
            self.authorized_workflows = self._parse_workflows(workflows)
            self._create_tabs()
            self._show_parsing_errors()
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "워크플로우 오류", 
                "워크플로우 로드 실패.\n다시 로그인해주세요."
            )
            self._logout()

    def _logout(self) -> None:
        """로그아웃 처리: 타이머 중지, 토큰 정리 후 로그아웃 시그널 발생."""
        # 토큰 갱신 타이머 중지
        if hasattr(self, 'token_refresh_timer') and self.token_refresh_timer.isActive():
            self.token_refresh_timer.stop()
        
        # 토큰 정리
        auth.logout()
        
        # 로그아웃 시그널 발생 (MainApplication이 처리)
        self.logout_requested.emit()
        
        # 창 닫기
        self.close()

    def closeEvent(self, event) -> None:
        """창이 닫힐 때 호출되는 이벤트 핸들러."""
        # 토큰 갱신 타이머 중지
        if hasattr(self, 'token_refresh_timer') and self.token_refresh_timer.isActive():
            self.token_refresh_timer.stop()
        
        if self.thread and self.thread.isRunning():
            reply = QMessageBox.question(
                self, 
                '종료 확인', 
                "수집 작업이 진행 중입니다.\n정말로 종료하시겠습니까?", 
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self._is_closing = True
                self.stop_scraping()
                event.ignore()
            else:
                event.ignore()
        else:
            event.accept()