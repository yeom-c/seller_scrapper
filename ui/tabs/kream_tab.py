from PySide6.QtCore import QDate, Signal, Qt
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QDateEdit, QProgressBar
)

class KreamTab(QWidget):
    """KREAM 탭의 UI와 시그널을 관리하는 독립적인 위젯 클래스."""
    start_scraping_signal = Signal(dict, dict)

    def __init__(self, workflow_data):
        super().__init__()
        self.workflow_data = workflow_data
        self._setup_ui()

    def _setup_ui(self):
        """탭의 UI 요소들을 생성하고 배치합니다."""
        main_layout = QVBoxLayout(self)
        
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

        main_layout.addLayout(date_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.log_edit)

        self.start_button.clicked.connect(self._emit_start_signal)

    def _emit_start_signal(self):
        """시작 버튼 클릭 시 날짜 정보를 포함하여 start_scraping_signal을 발생시킵니다."""
        start_date = self.start_date_edit.date().toPython()
        end_date = self.end_date_edit.date().toPython()
        date_range = {'start_date': start_date, 'end_date': end_date}
        
        self.start_scraping_signal.emit(self.workflow_data, date_range)