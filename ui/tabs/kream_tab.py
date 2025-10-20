from PySide6.QtCore import QDate, Signal, Qt, QTimer
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QDateEdit, QProgressBar
)

from api_client.token_manager import Permission


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
                background-color: #4A90E2;
                color: white;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
            QPushButton:pressed {
                background-color: #2868A8;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
        """)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #EF5350;
                color: white;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E53935;
            }
            QPushButton:pressed {
                background-color: #C62828;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
        """)
        self.folder_button.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #616161;
            }
            QPushButton:pressed {
                background-color: #424242;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
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
        self.progress_bar.setTextVisible(True)

        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)

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
            
            remaining_seconds = self.permission.expires_in()
            is_expired = self.permission.is_expired()

            # 색상 테마 정의
            themes = {
                "safe": {"bg": "#E6F4EA", "name": "#1E8E3E", "time": "#000000"},
                "warning": {"bg": "#FFF8E1", "name": "#E67C00", "time": "#000000"},
                "danger": {"bg": "#FCE8E6", "name": "#D93025", "time": "#000000"},
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
                QWidget {{
                    background-color: {theme['bg']};
                    border-radius: 8px;
                }}
            """)
            self.permission_name_label.setStyleSheet(
                f"font-size: 13px; font-weight: bold; color: {theme['name']};"
            )
            self.permission_time_label.setStyleSheet(
                f"font-size: 12px; color: {theme['time']};"
            )
        else:
            # 이용권 정보가 없는 경우
            theme = themes["danger"]
            self.permission_badge.setStyleSheet(f"background-color: {theme['bg']}; border-radius: 8px;")
            self.permission_name_label.setText("이용권 정보 없음")
            self.permission_name_label.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {theme['name']};")
            self.permission_time_label.setText("기능을 사용할 수 없습니다.")
            self.permission_time_label.setStyleSheet(f"font-size: 11px; color: {theme['time']};")
            self.start_button.setEnabled(False)

    def _emit_start_signal(self):
        """시작 버튼 클릭 시 날짜 정보를 포함하여 start_scraping_signal을 발생시킵니다."""
        start_date = self.start_date_edit.date().toPython()
        end_date = self.end_date_edit.date().toPython()
        date_range = {'start_date': start_date, 'end_date': end_date}
        
        self.start_scraping_signal.emit(self.workflow_data, date_range)
