import time
from typing import Callable, Dict, Any, Optional
from datetime import date
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from .strategies.kream_scrap_1_strategy import KreamScrap1Strategy
from .strategies.kream_scrap_2_strategy import KreamScrap2Strategy
from utils.file_handler import save_to_csv


class WorkflowScraper:
    """워크플로우의 각 단계를 순차적으로 실행하는 범용 스크랩퍼 엔진."""
    
    # 상수 정의
    DEFAULT_WAIT_TIMEOUT = 3
    NAVIGATE_WAIT_TIME = 2
    
    def __init__(self, log_handler: Callable, progress_handler: Callable, step_start_handler: Callable):
        self.log_handler = log_handler
        self.progress_handler = progress_handler
        self.step_start_handler = step_start_handler
        self._is_running = True
        self.collected_data = []
        self.current_step_details: Dict[str, Any] = {}
        self.date_range: Dict[str, Optional[date]] = {}
        self.site_name = "default"
        
        self.driver = self._initialize_driver()
        self.wait = WebDriverWait(self.driver, self.DEFAULT_WAIT_TIMEOUT)
        
        self.strategy_map = {
            "kream_scrap_1": KreamScrap1Strategy,
            "kream_scrap_2": KreamScrap2Strategy
        }

    def _initialize_driver(self) -> webdriver.Chrome:
        """WebDriver를 초기화합니다."""
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        self.log_handler("브라우저가 실행되었습니다.", "blue")
        return driver

    def stop(self) -> None:
        """외부에서 스크랩핑 작업을 중단하도록 요청합니다."""
        if self._is_running:
            self.log_handler("작업 중단 신호를 받았습니다.", "orange")
            self._is_running = False

    def run_workflow(self, workflow_data: Dict[str, Any], **kwargs) -> None:
        """워크플로우의 모든 단계를 순서대로 실행합니다."""
        self.date_range = kwargs
        self.site_name = workflow_data.get('site_name', 'default')
        steps = workflow_data.get('steps', [])
        
        try:
            for i, step in enumerate(steps):
                if not self._is_running:
                    break
                
                self.current_step_details = step
                step_name = step.get('step_name', 'Unnamed Step')
                self.log_handler(f"\n작업 {i+1}: {step_name} 시작", "green")
                
                if not self._execute_step(step, step_name):
                    break

                self.log_handler(f"작업 {i+1}: {step_name} 완료", "green")
        finally:
            self.close()

    def _execute_step(self, step: Dict[str, Any], step_name: str) -> bool:
        """개별 스텝을 실행합니다.
        
        Returns:
            계속 진행 가능 여부 (False면 워크플로우 중단)
        """
        try:
            action_type = step.get('action_type')
            
            if action_type == 'navigate':
                self._execute_navigate(step)
            elif action_type == 'manual_login':
                if not self._execute_manual_login(step):
                    self.log_handler("로그인 실패. 작업을 중단합니다.", "red")
                    return False
            elif action_type in self.strategy_map:
                self._execute_scraping_strategy(step, step_name, action_type)
            else:
                self.log_handler(f"'{action_type}' 경고: 알 수 없는 action_type", "orange")
            
            return True
            
        except Exception as e:
            if self._is_running:
                self.log_handler(f"'{step_name}' 작업 중 오류: {e}", "red")
            
            # 예외 발생 시에도 수집된 데이터가 있으면 저장 시도
            if self.collected_data:
                self._safe_save_data()
            
            return True  # 다음 스텝 계속 진행

    def _execute_scraping_strategy(self, step: Dict[str, Any], step_name: str, action_type: str) -> None:
        """스크래핑 전략을 실행합니다."""
        self._execute_navigate(step)
        self.step_start_handler(step_name)
        
        strategy_class = self.strategy_map[action_type]
        strategy_instance = strategy_class(self, step, self.date_range)
        
        try:
            self.collected_data = strategy_instance.execute()
        except Exception as strategy_error:
            self.log_handler(f"수집 중 오류 발생: {strategy_error}", "red")
            # 오류가 발생해도 수집된 데이터가 있으면 가져옴
            self.collected_data = strategy_instance.collected_data
        
        # 데이터 저장
        if self.collected_data:
            self.save_collected_data()
        else:
            self.log_handler("수집된 데이터가 없습니다.", "orange")

    def _safe_save_data(self) -> None:
        """안전하게 데이터를 저장합니다 (예외 처리 포함)."""
        try:
            self.save_collected_data()
        except Exception as save_error:
            self.log_handler(f"데이터 저장 중 오류: {save_error}", "red")

    def save_collected_data(self) -> None:
        """수집된 데이터를 CSV 파일로 저장하는 헬퍼 메소드."""
        if not self.collected_data:
            return
            
        base_filename = self.current_step_details.get('output_filename')
        if not base_filename:
            self.log_handler("경고: output_filename이 설정되지 않았습니다.", "orange")
            return
        
        # 규칙 가져오기 (두 가지 키 지원)
        rules = (self.current_step_details.get('detail_page_rules') or 
                self.current_step_details.get('detail_rules', {}))
        
        start_date = self.date_range.get('start_date')
        end_date = self.date_range.get('end_date')
        
        # 파일명 생성
        filename = self._generate_filename(base_filename, start_date, end_date)
        
        # 컬럼 매핑 및 데이터 정리
        column_mappings = {key: rule.get('column_name', key) for key, rule in rules.items()}
        data_to_save = [{k: v for k, v in item.items() if k != '_date'} for item in self.collected_data]
        
        # CSV 저장
        save_to_csv(data_to_save, filename, self.site_name, column_mappings, self.log_handler)
        self.collected_data = []

    def _generate_filename(self, base_filename: str, start_date: Optional[date], end_date: Optional[date]) -> str:
        """파일명을 생성합니다."""
        first_item_date = self.collected_data[0].get('_date')
        last_item_date = self.collected_data[-1].get('_date')

        start_str = start_date.strftime("%Y%m%d") if start_date else last_item_date.strftime("%Y%m%d")
        end_str = end_date.strftime("%Y%m%d") if end_date else first_item_date.strftime("%Y%m%d")
        
        return f"{base_filename}_{start_str}_{end_str}.csv"

    def _execute_manual_login(self, step_details: Dict[str, Any]) -> bool:
        """사용자가 직접 로그인할 때까지 대기하고, 성공 여부를 감지합니다."""
        if not self._is_running:
            return False
        
        target_url = step_details.get('target_url')
        condition = step_details.get('success_condition', {})
        
        if not all([target_url, condition]):
            self.log_handler("에러: manual_login에 필요한 정보가 부족합니다.", "red")
            return False
        
        self.driver.get(target_url)
        
        timeout = condition.get('timeout', 120)
        selector = condition.get('selector')
        text_to_find = condition.get('text_contains')
        
        self.log_handler(f"\n브라우저에서 직접 로그인을 진행해주세요. (최대 {timeout}초 대기)", "orange")
        
        try:
            xpath_selector = self._build_xpath_selector(selector, text_to_find)
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.visibility_of_element_located((By.XPATH, xpath_selector)))

            if not self._is_running:
                return False
                
            return True
            
        except TimeoutException:
            if not self._is_running:
                return False
            self.log_handler(f"시간 초과: 로그인에 실패했습니다.", "orange")
            return False
            
        except Exception as e:
            if not self._is_running:
                return False
            self.log_handler(f"로그인 중 오류 발생: {e}", "red")
            return False

    def _build_xpath_selector(self, selector: str, text_to_find: str) -> str:
        """CSS 셀렉터를 XPath로 변환합니다."""
        tag, class_name = selector.split('.')
        return f"//{tag}[contains(@class, '{class_name}') and contains(text(), '{text_to_find}')]"

    def _execute_navigate(self, step_details: Dict[str, Any]) -> None:
        """단순 페이지 이동을 처리합니다."""
        if not self._is_running:
            return
        
        target_url = step_details.get('target_url')
        if not target_url:
            self.log_handler("에러: target_url이 지정되지 않았습니다.", "red")
            return
            
        self.log_handler(f"페이지로 이동 중: {target_url}", "black")
        self.driver.get(target_url)
        time.sleep(self.NAVIGATE_WAIT_TIME)
        self.log_handler("이동 완료.", "black")
    
    def close(self) -> None:
        """WebDriver를 안전하게 종료합니다."""
        if self.driver:
            try:
                self.driver.quit()
                self.log_handler("\n브라우저가 종료되었습니다.", "blue")
            except Exception:
                pass
            self.driver = None