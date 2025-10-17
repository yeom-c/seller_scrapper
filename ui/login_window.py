from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QMessageBox, QApplication, QStackedWidget
)


class LoginWindow(QWidget):
    """로그인 화면."""
    
    login_successful = Signal(dict)

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
        # 입력 필드 초기화
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
        
        # TODO: 실제 회원가입 로직 구현
        QMessageBox.information(
            self, 
            "회원가입 완료", 
            f"회원가입이 완료되었습니다!\n이메일: {email}\n\n로그인 화면으로 돌아갑니다."
        )
        
        self._show_login_page()
    
    def _handle_login(self):
        """로그인 처리."""
        email = self.email_input.text().strip()
        password = self.password_input.text()
        
        # 유효성 검사
        if not email or not password:
            QMessageBox.warning(self, "입력 오류", "이메일과 비밀번호를 입력해주세요.")
            return
        
        # TODO: 실제 로그인 로직 구현
        # 임시로 모든 로그인을 성공 처리하고 워크플로우 권한을 부여
        workflows_by_permission = {
            "kream": """
            {
                "site_name": "KREAM",
                "steps": [
                    {
                        "step_name": "사용자 로그인",
                        "action_type": "manual_login",
                        "target_url": "https://kream.co.kr/login",
                        "success_condition": {
                            "type": "element_visible",
                            "selector": "a.top_link",
                            "text_contains": "로그아웃",
                            "timeout": 120
                        }
                    },
                    {
                        "step_name": "일반 판매 정산 내역 수집",
                        "action_type": "kream_scrap_1",
                        "target_url": "https://kream.co.kr/my/selling?tab=finished&status=payout_completed",
                        "output_filename": "크림_일반판매",
                        "list_item_selector": "a.product_list_info_action",
                        "list_date_selector": ".caption_item p",
                        "detail_page_rules": {
                            "order_number": {
                                "column_name": "주문번호",
                                "selector": ".text-header-checkout p",
                                "type": "text"
                            },
                            "product_name_eng": {
                                "column_name": "상품명(영문)",
                                "selector": "p.product_title",
                                "type": "text"
                            },
                            "product_name_kor": {
                                "column_name": "상품명(한글)",
                                "selector": "p.product_subtitle",
                                "type": "text"
                            },
                            "product_model": {
                                "column_name": "상품 모델",
                                "selector": "p.product_description",
                                "type": "text"
                            },
                            "size": {
                                "column_name": "사이즈",
                                "selector": "span.product_option--name",
                                "type": "text"
                            },
                            "transaction_date": {
                                "column_name": "거래 일시",
                                "label": "거래 일시",
                                "type": "find_by_label"
                            },
                            "payout_date": {
                                "column_name": "정산일",
                                "label": "정산일",
                                "type": "find_by_label"
                            },
                            "instant_sell_price": {
                                "column_name": "즉시 판매가",
                                "label": "즉시 판매가",
                                "type": "find_by_label"
                            },
                            "commission_fee": {
                                "column_name": "수수료",
                                "label": "수수료",
                                "type": "find_by_label"
                            },
                            "payout_amount": {
                                "column_name": "정산금액",
                                "label": "정산금액",
                                "type": "find_by_label"
                            }
                        }
                    },
                    {
                        "step_name": "보관 판매 정산 내역 수집",
                        "action_type": "kream_scrap_2",
                        "target_url": "https://kream.co.kr/my/inventory?tab=finished&status=payout_completed",
                        "output_filename": "크림_보관판매",
                        "list_item_selector": ".inventory_item",
                        "list_date_selector": ".tab_item.date .value",
                        "detail_button_selector": ".btn.detail",
                        "drawer_selector": ".drawer__content",
                        "drawer_close_button_selector": ".btn_layer_close",
                        "detail_rules": {
                            "order_number": {
                                "column_name": "주문번호",
                                "selector": ".inventory_product .inventory_number",
                                "type": "text"
                            },
                            "product_name_eng": {
                                "column_name": "상품명(영문)",
                                "selector": ".inventory_product .name",
                                "type": "text"
                            },
                            "product_model": {
                                "column_name": "상품 모델",
                                "selector": "p.code span.code_text",
                                "type": "text"
                            },
                            "size": {
                                "column_name": "사이즈",
                                "selector": ".inventory_product .size_text",
                                "type": "text"
                            },
                            "transaction_date": {
                                "column_name": "거래 일시",
                                "label": "거래일시",
                                "type": "find_by_label_v2"
                            },
                            "payout_date": {
                                "column_name": "정산일",
                                "selector": ".status_bar_info .info_desc",
                                "type": "text"
                            },
                            "instant_sell_price": {
                                "column_name": "즉시 판매가",
                                "label": "판매가",
                                "type": "find_by_label_v2"
                            },
                            "commission_fee": {
                                "column_name": "수수료",
                                "label": "수수료",
                                "type": "find_by_label_v2"
                            },
                            "payout_amount": {
                                "column_name": "정산금액",
                                "label": "정산금액",
                                "type": "find_by_label_v2"
                            }
                        }
                    }
                ]
            }
            """,
            "tab1": """
            {
                "site_name": "TAB 1",
                "steps": []
            }
            """,
            "tab2": """
            {
                "site_name": "TAB 2",
                "steps": []
            }
            """,
            "tab3": """
            {
                "site_name": "TAB 3",
                "steps": []
            }
            """
        }
        
        self.login_successful.emit(workflows_by_permission)
        self.close()
