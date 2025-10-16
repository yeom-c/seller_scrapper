from PySide6.QtCore import QObject, Signal
from core.scraper import WorkflowScraper

class ScraperWorker(QObject):
    """
    백그라운드 스레드에서 스크레이핑 작업을 실행하는 워커 클래스.
    """
    log_message = Signal(str, str)
    finished = Signal()
    error = Signal(str)
    progress_updated = Signal(int, int) # (현재 값, 최대 값)
    step_started = Signal(str) # (스텝 이름 전달)

    def __init__(self, workflow_data, date_range):
        super().__init__()
        self.workflow_data = workflow_data
        self.date_range = date_range
        self.scraper = None

    def run(self):
        """스크레이핑 작업을 시작합니다."""
        try:
            # Scraper에 로그 핸들러와 진행률 핸들러를 함께 전달
            self.scraper = WorkflowScraper(
                log_handler=self.log_message.emit,
                progress_handler=self.progress_updated.emit,
                step_start_handler=self.step_started.emit
            )
            self.scraper.run_workflow(self.workflow_data, **self.date_range)
        except Exception as e:
            self.error.emit(f"작업 중 오류 발생: {e}")
        finally:
            # stop()에 의해 scraper가 먼저 닫혔을 수 있으므로 확인
            if self.scraper:
                self.scraper.close()
            self.finished.emit()

    def stop(self):
        """스크레이퍼에 작업 중단을 요청합니다."""
        if self.scraper:
            self.scraper.stop()