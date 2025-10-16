import sys
from PySide6.QtWidgets import QApplication
from ui.login_window import LoginWindow
from ui.main_window import MainWindow

class MainApplication:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.main_window = None

        self.login_window = LoginWindow()
        self.login_window.login_successful.connect(self.show_main_window)
        self.login_window.show()

    def show_main_window(self, workflows_by_permission):
        """로그인 성공 후 메인 윈도우를 표시하는 메소드."""
        self.main_window = MainWindow(workflows_by_permission)
        self.main_window.show()

    def run(self):
        """애플리케이션을 실행합니다."""
        sys.exit(self.app.exec())

if __name__ == "__main__":
    main_app = MainApplication()
    main_app.run()