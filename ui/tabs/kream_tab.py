from PySide6.QtCore import QDate, Signal, Qt, QTimer
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QDateEdit, QProgressBar
)

from api_client.token_manager import Permission
from api_client import token_manager

class KreamTab(QWidget):
    """KREAM 탭의 UI와 시그널을 관리하는 독립적인 위젯 클래스."""
    start_scraping_signal = Signal(dict, dict)

    def __init__(self, workflow_data: dict, permission: Permission):
        super().__init__()
        self.workflow_data = workflow_data
        self.permission = permission
        self._setup_ui()
        self._setup_timer()

    def _setup_ui(self):
        """탭의 UI 요소들을 생성하고 배치합니다."""
        main_layout = QVBoxLayout(self)

        # --- 권한 정보 뱃지 레이아웃 ---
        permission_layout = QHBoxLayout()
        permission_layout.addStretch()
        
        self.permission_badge = QWidget()
        badge_layout = QVBoxLayout(self.permission_badge)
        badge_layout.setContentsMargins(12, 6, 12, 6)
        badge_layout.setSpacing(2)

        self.permission_name_label = QLabel()
        self.permission_name_label.setAlignment(Qt.AlignRight)
        self.permission_time_label = QLabel()
        self.permission_time_label.setAlignment(Qt.AlignRight)

        badge_layout.addWidget(self.permission_name_label)
        badge_layout.addWidget(self.permission_time_label)
        
        permission_layout.addWidget(self.permission_badge)
        
        date_layout = QHBoxLayout()
        self.start_date_edit = QDateEdit(QDate.currentDate().addMonths(-1))
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.end_date_edit = QDateEdit(QDate.currentDate())
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDisplayFormat("yyyy-MM-dd")
        date_layout.addWidget(QLabel("시작일:"))
        date_layout.addWidget(self.start_date_edit)
        date_layout.addWidget(QLabel("종료일:"))
        date_layout.addWidget(self.end_date_edit)
        date_layout.addStretch()

        button_layout = QHBoxLayout()
        self.start_button = QPushButton("수집 시작")
        self.start_button.setFixedHeight(40)
        self.stop_button = QPushButton("수집 중단")
        self.stop_button.setFixedHeight(40)
        self.stop_button.setEnabled(False)
        
        self.folder_button = QPushButton("폴더")
        self.folder_button.setFixedHeight(40)
        self.folder_button.setFixedWidth(100)

        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #3A86FF;
                color: #FFFFFF;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #5093FF;
            }
            QPushButton:pressed {
                background-color: #3174DE;
            }
            QPushButton:disabled {
                background-color: #EBF0F5;
                color: #8A94A6;
            }
        """)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #DC3545;
                font-weight: bold;
                border: 1px solid #DC3545;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #FFF5F5;
                color: #DC3545;
                border: 1px solid #DC3545;
            }
            QPushButton:pressed {
                background-color: #FEE5E5;
                color: #DC3545;
                border: 1px solid #DC3545;
            }
            QPushButton:disabled {
                background-color: transparent;
                color: #8A94A6;
                border: 1px solid #EBF0F5;
            }
        """)
        self.folder_button.setStyleSheet("""
            QPushButton {
                background-color: #8A94A6;
                color: #FFFFFF;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #757F93;
                color: #FFFFFF;
            }
            QPushButton:pressed {
                background-color: #606A7A;
                color: #FFFFFF;
            }
            QPushButton:disabled {
                background-color: #EBF0F5;
                color: #8A94A6;
            }
        """)

        self.start_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.stop_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.folder_button.setCursor(QCursor(Qt.PointingHandCursor))

        button_layout.addWidget(self.start_button, 1)
        button_layout.addWidget(self.stop_button, 1)
        button_layout.addWidget(self.folder_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)

        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setStyleSheet("""
            QTextEdit {
                border: 1px solid #e2e8f0;
                border-radius: 5px;
                padding: 8px;
                background-color: white;
            }
        """)

        main_layout.addLayout(permission_layout)
        main_layout.addLayout(date_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.log_edit)

        self.start_button.clicked.connect(self._emit_start_signal)

    def _setup_timer(self):
        """남은 시간 표시를 위한 타이머를 설정합니다."""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_permission_display)
        self.timer.start(1000)  # 1초마다 업데이트
        self._update_permission_display()  # 남은 시간 표기

    def _update_permission_display(self):
        """권한 만료까지 남은 시간을 뱃지에 업데이트합니다."""
        if self.permission:
            self.permission_name_label.setText(self.permission.name)
            
            remaining_seconds = token_manager.permission_expires_in(self.permission)
            is_expired = token_manager.is_permission_expired(self.permission)

            # 색상 테마 정의
            themes = {
                "safe": {
                    "bg": "#F0FDFA",
                    "border": "#0D9488",
                    "name": "#0D9488",
                    "time": "#0D254C"
                },
                "warning": {
                    "bg": "#FEFDE8",
                    "border": "#CA8A04",
                    "name": "#CA8A04",
                    "time": "#0D254C"
                },
                "danger": {
                    "bg": "#FEF2F2", 
                    "border": "#DC2626",
                    "name": "#DC2626",
                    "time": "#0D254C"
                },
            }

            if is_expired:
                theme = themes["danger"]
                self.permission_time_label.setText("만료되었습니다.")
                self.start_button.setEnabled(False)
                self.timer.stop()

            else:
                if remaining_seconds >= 3600:  # 1시간 이상
                    theme = themes["safe"]
                elif remaining_seconds >= 600:  # 10분 이상
                    theme = themes["warning"]
                else:  # 10분 미만
                    theme = themes["danger"]

                if remaining_seconds >= 86400:
                    days = remaining_seconds // 86400
                    time_str = f"{days}일 이상"
                elif remaining_seconds >= 3600:
                    hours = remaining_seconds // 3600
                    time_str = f"{hours}시간 이상"
                else:
                    minutes, seconds = divmod(remaining_seconds, 60)
                    time_str = f"{minutes}분 {seconds}초"
                
                self.permission_time_label.setText(f"{time_str} 남음")

            # 스타일시트 적용
            self.permission_badge.setStyleSheet(f"""
                background-color: {theme['bg']};
                border: 1px solid {theme['border']};
                border-radius: 5px;
            """)
            self.permission_name_label.setStyleSheet(
                f"font-size: 13px; font-weight: bold; color: {theme['name']}; border: none; background: transparent;"
            )
            self.permission_time_label.setStyleSheet(
                f"font-size: 12px; color: {theme['time']}; border: none; background: transparent;"
            )
        else:
            # 이용권 정보가 없는 경우
            theme = themes["danger"]
            self.permission_badge.setStyleSheet(f"""
                background-color: {theme['bg']};
                border: 1px solid {theme['border']};
                border-radius: 5px;
            """)
            self.permission_name_label.setText("이용권 정보 없음")
            self.permission_name_label.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {theme['name']}; border: none; background: transparent;")
            self.permission_time_label.setText("기능을 사용할 수 없습니다.")
            self.permission_time_label.setStyleSheet(f"font-size: 11px; color: {theme['time']}; border: none; background: transparent;")
            self.start_button.setEnabled(False)

    def _emit_start_signal(self):
        """시작 버튼 클릭 시 날짜 정보를 포함하여 start_scraping_signal을 발생시킵니다."""
        start_date = self.start_date_edit.date().toPython()
        end_date = self.end_date_edit.date().toPython()
        date_range = {'start_date': start_date, 'end_date': end_date}
        
        self.start_scraping_signal.emit(self.workflow_data, date_range)
