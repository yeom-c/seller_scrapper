from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QApplication

class LoginWindow(QWidget):
    """로그인 성공 시 워크플로우 데이터를 전송하는 신호를 가진 로그인 창 클래스."""
    login_successful = Signal(dict)

    def __init__(self):
        """LoginWindow 클래스의 생성자입니다."""
        super().__init__()
        self.setWindowTitle("로그인")
        self.resize(300, 150)
        self._center_on_screen()

        layout = QVBoxLayout()
        self.label = QLabel("로그인 화면입니다.")
        self.login_button = QPushButton("로그인")
        
        layout.addWidget(self.label)
        layout.addWidget(self.login_button)
        self.setLayout(layout)

        self.login_button.clicked.connect(self._handle_login)

    def _center_on_screen(self):
        """창을 화면 중앙에 배치합니다."""
        screen = QApplication.primaryScreen().geometry()
        window_geometry = self.frameGeometry()
        center_point = screen.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())

    def _handle_login(self):
        """로그인 버튼 클릭 시 처리하는 함수 (데이터 구조 시뮬레이션)."""
        
        workflows_by_permission = {
            "kream": """
            {
                "site_name": "KREAM",
                "steps": [
                    {
                        "step_name": "KREAM 로그인",
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
                        "step_name": "일반 판매 정산 내역 스크랩핑",
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
                        "step_name": "보관 판매 정산 내역 스크랩핑",
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