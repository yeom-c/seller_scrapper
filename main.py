import sys
from PySide6.QtWidgets import QApplication
from ui.login_window import LoginWindow
from ui.main_window import MainWindow

class MainApplication:
    """애플리케이션의 시작과 창 관리를 담당하는 메인 클래스."""
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.main_window = None

        # 1. 로그인 창을 먼저 띄웁니다.
        self.login_window = LoginWindow()
        # 로그인 성공 신호가 오면 메인 윈도우를 띄우는 함수와 연결합니다.
        self.login_window.login_successful.connect(self.show_main_window)
        self.login_window.show()

    def show_main_window(self):
        """로그인 성공 후 메인 윈도우를 생성하고 표시합니다."""
        self.main_window = MainWindow()
        # 로그아웃 시그널 연결
        self.main_window.logout_requested.connect(self.show_login_window)
        self.main_window.show()
    
    def show_login_window(self):
        """로그아웃 후 로그인 창을 다시 표시합니다."""
        self.login_window = LoginWindow()
        self.login_window.login_successful.connect(self.show_main_window)
        self.login_window.show()

    def run(self):
        """애플리케이션의 이벤트 루프를 시작합니다."""
        sys.exit(self.app.exec())

if __name__ == "__main__":
    main_app = MainApplication()
    main_app.run()