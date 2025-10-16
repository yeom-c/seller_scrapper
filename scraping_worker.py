from PySide6.QtCore import QObject, Signal
from core.scraper import WorkflowScraper

class ScraperWorker(QObject):
    """
    백그라운드 스레드에서 스크랩핑 작업을 실행하는 워커 클래스.
    """
    log_message = Signal(str, str)
    finished = Signal()
    error = Signal(str)
    progress_updated = Signal(int, int)
    step_started = Signal(str)

    def __init__(self, workflow_data, date_range):
        super().__init__()
        self.workflow_data = workflow_data
        self.date_range = date_range
        self.scraper = None

    def run(self):
        """스크랩핑 작업을 시작합니다."""
        try:
            self.scraper = WorkflowScraper(
                log_handler=self.log_message.emit,
                progress_handler=self.progress_updated.emit,
                step_start_handler=self.step_started.emit
            )
            self.scraper.run_workflow(self.workflow_data, **self.date_range)
        except Exception as e:
            self.error.emit(f"작업 중 오류 발생: {e}")
        finally:
            if self.scraper:
                self.scraper.close()
            self.finished.emit()

    def stop(self):
        """스크랩퍼에 작업 중단을 요청합니다."""
        if self.scraper:
            self.scraper.stop()