from PySide6.QtCore import Signal, Qt, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QMessageBox, QApplication, QStackedWidget
)
from api_client import auth


class LoginWindow(QWidget):
    """로그인 화면."""
    
    login_successful = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("판매내역 수집기")
        self.setFixedSize(400, 500)
        self._setup_ui()
        self._center_on_screen()

    def _setup_ui(self):
        """UI 구성."""
        # 스택 위젯으로 로그인/회원가입 화면 관리
        self.stacked_widget = QStackedWidget()
        
        # 로그인 페이지
        self.login_page = self._create_login_page()
        self.stacked_widget.addWidget(self.login_page)
        
        # 회원가입 페이지
        self.register_page = self._create_register_page()
        self.stacked_widget.addWidget(self.register_page)
        
        # 메인 레이아웃
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)
    
    def _create_login_page(self):
        """로그인 페이지 생성."""
        page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(40, 60, 40, 40)
        
        # 제목
        title_label = QLabel("로그인")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 30px;")
        layout.addWidget(title_label)
        
        # 상단 여백
        layout.addSpacing(20)
        
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
        
        # 버튼 전 여백
        layout.addSpacing(10)
        
        # 로그인 버튼
        self.login_button = QPushButton("로그인")
        self.login_button.setFixedHeight(40)
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_button.setStyleSheet("""
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
        self.login_button.clicked.connect(self._handle_login)
        layout.addWidget(self.login_button)
        
        # 하단 여백
        layout.addSpacing(20)
        
        # 회원가입 링크
        register_layout = QHBoxLayout()
        register_layout.addStretch()
        register_label = QLabel("계정이 없으신가요?")
        register_label.setStyleSheet("color: #666; font-size: 13px;")
        self.register_link = QPushButton("회원가입")
        self.register_link.setCursor(Qt.CursorShape.PointingHandCursor)
        self.register_link.setStyleSheet("""
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
        self.register_link.clicked.connect(self._show_register_page)
        register_layout.addWidget(register_label)
        register_layout.addWidget(self.register_link)
        register_layout.addStretch()
        layout.addLayout(register_layout)
        
        # 하단 여백 추가
        layout.addStretch()
        
        page.setLayout(layout)
        
        # Enter 키 이벤트 연결
        self.email_input.returnPressed.connect(self.password_input.setFocus)
        self.password_input.returnPressed.connect(self._handle_login)
        
        return page
    
    def _create_register_page(self):
        """회원가입 페이지 생성."""
        page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(40, 50, 40, 40)
        
        # 제목
        title_label = QLabel("회원가입")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title_label)
        
        # 상단 여백
        layout.addSpacing(10)
        
        # 이메일 입력
        email_label = QLabel("이메일")
        self.register_email_input = QLineEdit()
        self.register_email_input.setPlaceholderText("이메일을 입력하세요")
        self.register_email_input.setFixedHeight(40)
        self.register_email_input.setStyleSheet("""
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
        layout.addWidget(self.register_email_input)
        
        # 비밀번호 입력
        password_label = QLabel("비밀번호")
        self.register_password_input = QLineEdit()
        self.register_password_input.setPlaceholderText("비밀번호를 입력하세요")
        self.register_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.register_password_input.setFixedHeight(40)
        self.register_password_input.setStyleSheet("""
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
        layout.addWidget(self.register_password_input)
        
        # 비밀번호 확인 입력
        confirm_password_label = QLabel("비밀번호 확인")
        self.register_confirm_password_input = QLineEdit()
        self.register_confirm_password_input.setPlaceholderText("비밀번호를 다시 입력하세요")
        self.register_confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.register_confirm_password_input.setFixedHeight(40)
        self.register_confirm_password_input.setStyleSheet("""
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
        layout.addWidget(self.register_confirm_password_input)
        
        # 버튼 전 여백
        layout.addSpacing(10)
        
        # 회원가입 버튼
        self.register_button = QPushButton("회원가입")
        self.register_button.setFixedHeight(40)
        self.register_button.setCursor(Qt.CursorShape.PointingHandCursor)
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
        
        # 하단 여백
        layout.addSpacing(15)
        
        # 로그인 화면으로 돌아가기
        back_layout = QHBoxLayout()
        back_layout.addStretch()
        back_label = QLabel("이미 계정이 있으신가요?")
        back_label.setStyleSheet("color: #666; font-size: 13px;")
        self.back_link = QPushButton("로그인")
        self.back_link.setCursor(Qt.CursorShape.PointingHandCursor)
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
        self.back_link.clicked.connect(self._show_login_page)
        back_layout.addWidget(back_label)
        back_layout.addWidget(self.back_link)
        back_layout.addStretch()
        layout.addLayout(back_layout)
        
        # 하단 여백 추가
        layout.addStretch()
        
        page.setLayout(layout)
        
        # Enter 키 이벤트 연결
        self.register_email_input.returnPressed.connect(self.register_password_input.setFocus)
        self.register_password_input.returnPressed.connect(self.register_confirm_password_input.setFocus)
        self.register_confirm_password_input.returnPressed.connect(self._handle_register)
        
        return page
    
    def _center_on_screen(self):
        """창을 화면 중앙에 배치합니다."""
        screen = QApplication.primaryScreen().geometry()
        window_geometry = self.frameGeometry()
        center_point = screen.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())
    
    def _show_register_page(self):
        """회원가입 페이지로 전환합니다."""
        self.setWindowTitle("회원가입")
        self.stacked_widget.setCurrentIndex(1)
        self.register_email_input.setFocus()
        # 로그인 입력 필드 초기화
        self.email_input.clear()
        self.password_input.clear()
        # 회원가입 입력 필드 초기화
        self.register_email_input.clear()
        self.register_password_input.clear()
        self.register_confirm_password_input.clear()
    
    def _show_login_page(self):
        """로그인 페이지로 전환합니다."""
        self.setWindowTitle("로그인")
        self.stacked_widget.setCurrentIndex(0)
        self.email_input.setFocus()
    
    def _handle_register(self):
        """회원가입 처리."""
        email = self.register_email_input.text().strip()
        password = self.register_password_input.text()
        confirm_password = self.register_confirm_password_input.text()
        
        # 유효성 검사
        if not email:
            QMessageBox.warning(self, "입력 오류", "이메일을 입력해주세요.")
            self.register_email_input.setFocus()
            return
        
        if '@' not in email or '.' not in email:
            QMessageBox.warning(self, "입력 오류", "올바른 이메일 형식이 아닙니다.")
            self.register_email_input.setFocus()
            return
        
        if not password:
            QMessageBox.warning(self, "입력 오류", "비밀번호를 입력해주세요.")
            self.register_password_input.setFocus()
            return
        
        if len(password) < 6:
            QMessageBox.warning(self, "입력 오류", "비밀번호는 최소 6자 이상이어야 합니다.")
            self.register_password_input.setFocus()
            return
        
        if password != confirm_password:
            QMessageBox.warning(self, "입력 오류", "비밀번호가 일치하지 않습니다.")
            self.register_confirm_password_input.setFocus()
            return
        
        # UI 업데이트 먼저 수행
        self.register_button.setEnabled(False)
        self.register_button.setText("처리 중...")
        self.register_button.repaint()  # 즉시 다시 그리기
        
        # 실제 API 호출을 다음 이벤트 루프로 지연
        QTimer.singleShot(10, lambda: self._do_register(email, password))
    
    def _do_register(self, email: str, password: str):
        """실제 회원가입 API 호출."""
        try:
            # API 호출하여 회원가입
            response = auth.register(email=email, password=password)
            
            if response.get('success'):
                QMessageBox.information(
                    self,
                    "회원가입 완료",
                    f"회원가입이 완료되었습니다!\n이메일: {email}\n"
                )
                self._show_login_page()
            else:
                error_message = response.get('message', '회원가입 중 오류가 발생했습니다.')
                QMessageBox.warning(
                    self,
                    "회원가입 실패",
                    error_message
                )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "회원가입 오류",
                "회원가입 중 오류가 발생했습니다."
            )
            
        finally:
            # 버튼 활성화
            self.register_button.setEnabled(True)
            self.register_button.setText("회원가입")
    
    def _handle_login(self):
        """로그인 처리."""
        email = self.email_input.text().strip()
        password = self.password_input.text()
        
        # 유효성 검사
        if not email or not password:
            QMessageBox.warning(self, "입력 오류", "이메일과 비밀번호를 입력해주세요.")
            return
        
        # UI 업데이트 먼저 수행
        self.login_button.setEnabled(False)
        self.login_button.setText("로그인 중...")
        self.login_button.repaint()  # 즉시 다시 그리기
        
        # 실제 API 호출을 다음 이벤트 루프로 지연
        QTimer.singleShot(10, lambda: self._do_login(email, password))
    
    def _do_login(self, email: str, password: str):
        """실제 로그인 API 호출."""
        try:
            # 로그인 API 호출하여 JWT 토큰 받기
            response = auth.login(email=email, password=password)
            
            if response.get('success'):
                # 로그인 성공 시그널 발생 (워크플로우는 MainWindow에서 로드)
                self.login_successful.emit()
                self.close()
            else:
                error_message = response.get('message', '로그인 중 오류가 발생했습니다.')
                QMessageBox.warning(
                    self,
                    "로그인 실패",
                    error_message
                )
                self.password_input.clear()
                self.password_input.setFocus()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "로그인 오류",
                f"로그인 중 오류가 발생했습니다:\n{str(e)}"
            )
            
        finally:
            # 버튼 활성화
            self.login_button.setEnabled(True)
            self.login_button.setText("로그인")
