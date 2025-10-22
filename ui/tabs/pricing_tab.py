from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QApplication
)


class PricingTab(QWidget):
    """요금제 탭의 UI를 관리하는 독립적인 위젯 클래스."""
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
    
    def _setup_ui(self):
        """탭의 UI 요소들을 생성하고 배치합니다."""
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(20)
        
        # === 상단: 타이틀 ===
        title_label = QLabel("자동화로 지금부터 당신의 시간을 지키세요")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 26px;
                font-weight: 600;
                color: #000b17;
            }
        """)
        
        main_layout.addWidget(title_label)
        
        # === 서브 타이틀: 기능 요청 안내 ===
        subtitle_label = QLabel("언제든 필요한 기능을 요청해주세요\n성심껏 한줄 한줄 코딩하겠습니다!\n⌨️⌨️⌨️")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #666;
                margin-top: 5px;
            }
        """)
        main_layout.addWidget(subtitle_label)
        
        # === 이메일 주소 (클릭 시 복사) ===
        email_container = QWidget()
        email_container.setStyleSheet("background-color: transparent;")
        email_layout = QHBoxLayout(email_container)
        email_layout.setContentsMargins(0, 5, 0, 0)
        email_layout.addStretch()
        
        contact_label = QLabel("구매 및 기능 요청: ")
        contact_label.setStyleSheet("""
            QLabel {
                font-size: 15px;
                color: #000b17;
            }
        """)
        
        self.email_label = QLabel("yun0ga222@gmail.com")
        self.email_label.setStyleSheet("""
            QLabel {
                font-size: 15px;
                color: #4A90E2;
                text-decoration: underline;
            }
        """)
        self.email_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.email_label.mousePressEvent = self._copy_email
        
        email_layout.addWidget(contact_label)
        email_layout.addWidget(self.email_label)
        email_layout.addStretch()
        
        main_layout.addWidget(email_container)
        
        # === 하단: 가격 플랜 섹션 ===
        # 중앙 정렬을 위한 컨테이너
        plans_container = QWidget()
        plans_container.setStyleSheet("background-color: transparent;")
        plans_container_layout = QHBoxLayout(plans_container)
        plans_container_layout.setContentsMargins(0, 0, 0, 0)
        plans_container_layout.addStretch()
        
        plans_widget = QWidget()
        plans_widget.setStyleSheet("background-color: transparent;")
        plans_widget.setMaximumWidth(960)  # MainWindow 너비(1000) - 여백(40) = 960
        plans_layout = QHBoxLayout(plans_widget)
        plans_layout.setSpacing(15)  # 카드 간격 조정
        
        # 플랜 데이터
        plans = [
            {
                "name": "체험판",
                "price": "무료",
                "period": "1시간",
                "features": [
                    "KREAM 판매내역",
                    "최대 15개 수집"
                ]
            },
            {
                "name": "1일 이용권",
                "price": "₩1,000",
                "period": "1일",
                "features": [
                    "특정 기능 1개 이용",
                    "무제한 수집"
                ]
            },
            {
                "name": "30일 이용권",
                "price": "₩9,900",
                "period": "30일",
                "features": [
                    "모든 기능 이용",
                    "무제한 수집",
                    "추가 기능 업데이트"
                ]
            },
            {
                "name": "1년 이용권",
                "price": "₩19,900",
                "period": "1년",
                "features": [
                    "모든 기능 이용",
                    "무제한 수집",
                    "추가 기능 업데이트"
                ]
            }
        ]
        
        for plan in plans:
            plan_card = self._create_plan_card(plan)
            plans_layout.addWidget(plan_card)
        
        plans_container_layout.addWidget(plans_widget)
        plans_container_layout.addStretch()
        
        main_layout.addWidget(plans_container)
        main_layout.addStretch()
    
    def _copy_email(self, event):
        """이메일 주소를 클립보드에 복사합니다."""
        email = "yun0ga222@gmail.com"
        clipboard = QApplication.clipboard()
        clipboard.setText(email)
        
        # 임시로 복사 완료 표시
        original_text = self.email_label.text()
        self.email_label.setText("✓ 복사되었습니다!")
        self.email_label.setStyleSheet("""
            QLabel {
                font-size: 15px;
                color: #10b981;
                font-weight: bold;
            }
        """)
        
        # 1초 후 원래대로
        from PySide6.QtCore import QTimer
        QTimer.singleShot(1000, lambda: self._reset_email_label(original_text))
    
    def _reset_email_label(self, original_text):
        """이메일 라벨을 원래 상태로 복원합니다."""
        self.email_label.setText(original_text)
        self.email_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #4A90E2;
                text-decoration: underline;
            }
        """)
    
    def _create_plan_card(self, plan: dict) -> QWidget:
        """개별 플랜 카드를 생성합니다."""
        card = QWidget()
        card.setFixedWidth(220)  # 고정 너비 설정 (960 - 45 간격) / 4 = 220
        card.setFixedHeight(260)  # 고정 높이 설정
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(0)
        card_layout.setContentsMargins(0, 0, 0, 0)
        
        # 카드 컨테이너
        container = QWidget()
        container.setStyleSheet("background-color: transparent; border: none;")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(18, 18, 18, 18)
        container_layout.setSpacing(12)
        
        # 플랜 이름
        name_label = QLabel(plan["name"])
        name_label.setStyleSheet("""
            QLabel {
                font-size: 15px;
                font-weight: 600;
                color: #142438;
            }
        """)
        container_layout.addWidget(name_label)
        
        # 가격
        price_layout = QHBoxLayout()
        price_layout.setContentsMargins(0, 0, 0, 0)
        price_layout.setSpacing(4)
        
        price_label = QLabel(plan["price"])
        price_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: 700;
                color: #000b17;
            }
        """)
        
        period_label = QLabel(f"/ {plan['period']}")
        period_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #2a5c96;
                padding-top: 6px;
            }
        """)
        
        price_layout.addWidget(price_label)
        price_layout.addWidget(period_label)
        price_layout.addStretch()
        
        container_layout.addLayout(price_layout)
        container_layout.addSpacing(6)
        
        # 구분선
        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #cdd7e4;")
        container_layout.addWidget(separator)
        container_layout.addSpacing(6)
        
        # 기능 목록
        for feature in plan["features"]:
            feature_layout = QHBoxLayout()
            feature_layout.setContentsMargins(0, 0, 0, 0)
            feature_layout.setSpacing(6)
            
            # 체크마크
            check_label = QLabel("✓")
            check_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    color: #10b981;
                    font-weight: bold;
                }
            """)
            check_label.setFixedWidth(14)
            
            # 기능 텍스트
            feature_label = QLabel(feature)
            feature_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    color: #00162f;
                }
            """)
            feature_label.setWordWrap(True)
            
            feature_layout.addWidget(check_label)
            feature_layout.addWidget(feature_label, 1)
            
            container_layout.addLayout(feature_layout)
        
        container_layout.addStretch()
        
        card_layout.addWidget(container)
        
        # 모든 카드 동일한 스타일
        card.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #edf1f5;
                border-radius: 5px;
            }
            QWidget:hover {
                border: 1px solid #cdd7e4;
            }
        """)
        
        return card
