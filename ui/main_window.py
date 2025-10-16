import sys
import json
from datetime import datetime
from PySide6.QtCore import QDate, QThread, Qt
from PySide6.QtGui import QCursor # QCursor import 추가
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget,
    QLabel, QPushButton, QTextEdit, QHBoxLayout, QDateEdit
)
from scraping_worker import ScraperWorker

class MainWindow(QMainWindow):
    """애플리케이션의 메인 윈도우 클래스."""
    
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
            for error_msg in self._parsing_errors:
                self.update_log(error_msg, "red")

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
        """워크플로우 객체를 기반으로 탭을 생성하고 UI를 구성합니다."""
        if not self.authorized_workflows:
            self.setup_fallback_ui()
            self.update_log("표시할 수 있는 작업이 없습니다.", "orange")
            return

        for permission, workflow_data in self.authorized_workflows.items():
            tab_name = workflow_data.get("site_name", permission.upper())
            tab_widget = QWidget()
            self.tabs.addTab(tab_widget, tab_name)
            
            if permission == 'kream':
                self.setup_kream_tab(tab_widget, workflow_data)
            else:
                layout = QVBoxLayout(tab_widget)
                layout.addWidget(QLabel(f"{tab_name} 탭입니다."))
    
    def setup_fallback_ui(self):
        """워크플로우가 하나도 없을 때 표시할 최소한의 UI를 설정합니다."""
        fallback_tab = QWidget()
        self.tabs.addTab(fallback_tab, "알림")
        layout = QVBoxLayout(fallback_tab)
        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        layout.addWidget(self.log_edit)

    def setup_kream_tab(self, tab, workflow_data):
        """KREAM 탭의 UI 레이아웃을 설정하고 버튼에 기능을 연결합니다."""
        main_layout = QVBoxLayout(tab)
        
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
        self.start_button = QPushButton("시작 ▶")
        self.start_button.setFixedHeight(40)
        self.stop_button = QPushButton("중단 ■")
        self.stop_button.setFixedHeight(40)
        self.stop_button.setEnabled(False)
        
        self.start_button.setStyleSheet("background-color: #4A90E2; color: white; border-radius: 5px; font-weight: bold;")
        self.stop_button.setStyleSheet("background-color: #EF5350; color: white; border-radius: 5px; font-weight: bold;")
        
        self.start_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.stop_button.setCursor(QCursor(Qt.PointingHandCursor))
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)

        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)

        main_layout.addLayout(date_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.log_edit)

        self.start_button.clicked.connect(lambda: self.start_scraping(workflow_data))
        self.stop_button.clicked.connect(self.stop_scraping)

    def update_log(self, message, color="black"):
        """지정된 색상으로 로그 메시지를 추가합니다."""
        if not hasattr(self, 'log_edit'): return
        html_message = f'<font color="{color}">{message}</font>'
        self.log_edit.append(html_message)

    def start_scraping(self, workflow_data):
        """스크레이핑 작업을 백그라운드 스레드에서 시작합니다."""
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.log_edit.clear()
        self.update_log("작업을 준비 중입니다...", "black")

        start_date = self.start_date_edit.date().toPython()
        end_date = self.end_date_edit.date().toPython()
        
        date_range = {'start_date': start_date, 'end_date': end_date}

        self.thread = QThread()
        self.worker = ScraperWorker(workflow_data, date_range)
        self.worker.moveToThread(self.thread)

        self.worker.log_message.connect(self.update_log)
        self.worker.error.connect(lambda msg: self.update_log(msg, "red"))
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_scraping_finished)
        
        self.thread.start()

    def stop_scraping(self):
        """진행 중인 스크레이핑 작업을 중단하도록 요청합니다."""
        if self.worker:
            self.update_log("작업 중단을 요청합니다...", "orange")
            self.worker.stop()
            self.stop_button.setEnabled(False)

    def on_scraping_finished(self):
        """스크레이핑 작업이 완료되거나 중단되었을 때 UI를 정리합니다."""
        self.update_log("작업 스레드가 종료되었습니다.", "blue")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()
        
        self.thread = None
        self.worker = None