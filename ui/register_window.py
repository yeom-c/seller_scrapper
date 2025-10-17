from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QMessageBox, QApplication
)


class RegisterWindow(QWidget):
    """회원가입 화면."""
    
    register_successful = Signal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("판매내역 수집기")
        self.setFixedSize(400, 500)
        self._setup_ui()
        self._center_on_screen()
    
    def _setup_ui(self):
        """UI 구성."""
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # 제목
        title_label = QLabel("회원가입")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 22px; font-weight: bold; margin-bottom: 15px;")
        layout.addWidget(title_label)
        
        # 이메일 입력
        email_label = QLabel("이메일")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("이메일을 입력하세요")
        self.email_input.setFixedHeight(40)
        self.email_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #4A90E2;
            }
        """)
        layout.addWidget(email_label)
        layout.addWidget(self.email_input)
        
        # 비밀번호 입력
        password_label = QLabel("비밀번호")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("비밀번호를 입력하세요")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(40)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #4A90E2;
            }
        """)
        layout.addWidget(password_label)
        layout.addWidget(self.password_input)
        
        # 비밀번호 확인 입력
        confirm_password_label = QLabel("비밀번호 확인")
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("비밀번호를 다시 입력하세요")
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setFixedHeight(40)
        self.confirm_password_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #4A90E2;
            }
        """)
        layout.addWidget(confirm_password_label)
        layout.addWidget(self.confirm_password_input)
        
        # 회원가입 버튼
        self.register_button = QPushButton("회원가입")
        self.register_button.setFixedHeight(40)
        self.register_button.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
            QPushButton:pressed {
                background-color: #2868A8;
            }
        """)
        self.register_button.clicked.connect(self._handle_register)
        layout.addWidget(self.register_button)
        
        # 로그인 화면으로 돌아가기
        back_layout = QHBoxLayout()
        back_layout.addStretch()
        back_label = QLabel("이미 계정이 있으신가요?")
        back_label.setStyleSheet("color: #666; font-size: 13px;")
        self.back_link = QPushButton("로그인")
        self.back_link.setStyleSheet("""
            QPushButton {
                color: #4A90E2;
                border: none;
                text-decoration: underline;
                font-size: 13px;
                padding: 0;
            }
            QPushButton:hover {
                color: #357ABD;
            }
        """)
        self.back_link.clicked.connect(self.close)
        back_layout.addWidget(back_label)
        back_layout.addWidget(self.back_link)
        back_layout.addStretch()
        layout.addLayout(back_layout)
        
        self.setLayout(layout)
        
        # Enter 키 이벤트 연결
        self.email_input.returnPressed.connect(self.password_input.setFocus)
        self.password_input.returnPressed.connect(self.confirm_password_input.setFocus)
        self.confirm_password_input.returnPressed.connect(self._handle_register)
    
    def _center_on_screen(self):
        """창을 화면 중앙에 배치합니다."""
        screen = QApplication.primaryScreen().geometry()
        window_geometry = self.frameGeometry()
        center_point = screen.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())
    
    def _handle_register(self):
        """회원가입 처리."""
        email = self.email_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        
        # 유효성 검사
        if not email:
            QMessageBox.warning(self, "입력 오류", "이메일을 입력해주세요.")
            self.email_input.setFocus()
            return
        
        if '@' not in email or '.' not in email:
            QMessageBox.warning(self, "입력 오류", "올바른 이메일 형식이 아닙니다.")
            self.email_input.setFocus()
            return
        
        if not password:
            QMessageBox.warning(self, "입력 오류", "비밀번호를 입력해주세요.")
            self.password_input.setFocus()
            return
        
        if len(password) < 6:
            QMessageBox.warning(self, "입력 오류", "비밀번호는 최소 6자 이상이어야 합니다.")
            self.password_input.setFocus()
            return
        
        if password != confirm_password:
            QMessageBox.warning(self, "입력 오류", "비밀번호가 일치하지 않습니다.")
            self.confirm_password_input.setFocus()
            return
        
        # TODO: 실제 회원가입 로직 구현
        QMessageBox.information(
            self, 
            "회원가입 완료", 
            f"회원가입이 완료되었습니다!\n이메일: {email}\n\n로그인 화면으로 돌아갑니다."
        )
        
        self.register_successful.emit()
        self.close()
