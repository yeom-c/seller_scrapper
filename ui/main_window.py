import sys
import json
from PySide6.QtCore import QThread
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget, QLabel, QTextEdit
)
from scraping_worker import ScraperWorker
from .tabs.kream_tab import KreamTab
from utils.system_handler import open_output_folder

class MainWindow(QMainWindow):
    """애플리케이션의 메인 윈도우 (컨테이너 역할)."""
    
    def __init__(self, workflows_by_permission):
        super().__init__()
        self.setWindowTitle("판매내역 스크래퍼")
        self.setGeometry(300, 300, 800, 600)
        self.thread = None
        self.worker = None

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        self.authorized_workflows = self._parse_workflows(workflows_by_permission)
        self._create_tabs()

        if hasattr(self, '_parsing_errors') and self._parsing_errors:
            first_tab = self.tabs.widget(0)
            if first_tab and hasattr(first_tab, 'log_edit'):
                for error_msg in self._parsing_errors:
                    self.update_log_on_tab(first_tab, error_msg, "red")

    def _parse_workflows(self, workflows_by_permission):
        """워크플로우 데이터를 파싱하고, 에러는 별도로 저장합니다."""
        parsed_workflows = {}
        self._parsing_errors = []
        for permission, workflow_json_string in workflows_by_permission.items():
            try:
                workflow_data = json.loads(workflow_json_string)
                parsed_workflows[permission] = workflow_data
            except json.JSONDecodeError:
                error_msg = f"'{permission}' 권한의 워크플로우 JSON 형식이 잘못되었습니다."
                self._parsing_errors.append(error_msg)
        return parsed_workflows

    def _create_tabs(self):
        """워크플로우 객체를 기반으로 탭 위젯을 생성하고 추가합니다."""
        if not self.authorized_workflows:
            fallback_tab = QWidget()
            self.tabs.addTab(fallback_tab, "알림")
            layout = QVBoxLayout(fallback_tab)
            log_edit = QTextEdit("표시할 수 있는 작업이 없습니다.")
            log_edit.setReadOnly(True)
            layout.addWidget(log_edit)
            return

        for permission, workflow_data in self.authorized_workflows.items():
            tab_name = workflow_data.get("site_name", permission.upper())
            
            if permission == 'kream':
                # 1. KreamTab 인스턴스를 생성하여 tab_widget에 할당
                tab_widget = KreamTab(workflow_data)
                # 2. 생성된 tab_widget의 신호를 메인 윈도우의 메소드에 연결
                tab_widget.start_scraping_signal.connect(self.start_scraping)
                tab_widget.stop_button.clicked.connect(self.stop_scraping)
                tab_widget.folder_button.clicked.connect(self.open_current_tab_folder)
            else:
                # 다른 권한에 대한 탭 위젯 생성
                tab_widget = QWidget()
                layout = QVBoxLayout(tab_widget)
                layout.addWidget(QLabel(f"{tab_name} 탭입니다."))
            
            # 3. 완성된 tab_widget을 탭에 추가
            self.tabs.addTab(tab_widget, tab_name)

    def open_current_tab_folder(self):
        """현재 활성화된 탭에 해당하는 output 하위 폴더를 엽니다."""
        current_tab_name = self.tabs.tabText(self.tabs.currentIndex())
        open_output_folder(current_tab_name)

    def start_scraping(self, workflow_data, date_range):
        """탭으로부터 신호를 받아 스크레이핑 스레드를 시작합니다."""
        active_tab = self.tabs.currentWidget()
        if not (active_tab and hasattr(active_tab, 'start_button')): return

        active_tab.start_button.setEnabled(False)
        active_tab.stop_button.setEnabled(True)
        active_tab.log_edit.clear()
        active_tab.progress_bar.setValue(0)
        self.update_log_on_tab(active_tab, "작업을 준비 중입니다...", "black")
        
        self.thread = QThread()
        self.worker = ScraperWorker(workflow_data, date_range)
        self.worker.moveToThread(self.thread)

        self.worker.step_started.connect(self.on_step_started)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.log_message.connect(lambda msg, color: self.update_log_on_tab(self.tabs.currentWidget(), msg, color))
        self.worker.error.connect(lambda msg: self.update_log_on_tab(self.tabs.currentWidget(), msg, "red"))
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_scraping_finished)
        
        self.thread.start()

    def stop_scraping(self):
        """진행 중인 스크레이핑 작업을 중단하도록 요청합니다."""
        active_tab = self.tabs.currentWidget()
        if self.worker:
            self.update_log_on_tab(active_tab, "작업 중단을 요청합니다...", "orange")
            self.worker.stop()
            if hasattr(active_tab, 'stop_button'):
                active_tab.stop_button.setEnabled(False)

    def on_scraping_finished(self):
        """스크레이핑 작업이 완료/중단되었을 때 UI를 정리합니다."""
        active_tab = self.tabs.currentWidget()
        self.update_log_on_tab(active_tab, "작업 스레드가 종료되었습니다.", "blue")
        
        if hasattr(active_tab, 'start_button'):
            active_tab.start_button.setEnabled(True)
            active_tab.stop_button.setEnabled(False)
        
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()
        
        self.thread = None
        self.worker = None
    
    def update_log_on_tab(self, tab, message, color="black"):
        """지정된 탭의 로그 창에 메시지를 업데이트합니다."""
        if hasattr(tab, 'log_edit'):
            html_message = f'<font color="{color}">{message}</font>'
            tab.log_edit.append(html_message)
            
    def update_progress(self, current, total):
        """프로그레스 바의 값을 업데이트합니다."""
        active_tab = self.tabs.currentWidget()
        if hasattr(active_tab, 'progress_bar'):
            active_tab.progress_bar.setMaximum(total)
            active_tab.progress_bar.setValue(current)

    def on_step_started(self, step_name):
        """새로운 스크랩 단계가 시작될 때 프로그레스 바를 리셋합니다."""
        active_tab = self.tabs.currentWidget()
        if hasattr(active_tab, 'progress_bar'):
            active_tab.progress_bar.setValue(0)
            active_tab.progress_bar.setFormat(f"'{step_name}' 진행 중... %p%")