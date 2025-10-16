import time
import pandas as pd
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from bs4 import BeautifulSoup
from .strategies.kream_scrap_1_strategy import KreamScrap1Strategy
from .strategies.kream_scrap_2_strategy import KreamScrap2Strategy
from utils.file_handler import save_to_csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class WorkflowScraper:
    """워크플로우의 각 단계를 순차적으로 실행하는 범용 스크레이퍼 엔진."""
    
    def __init__(self, log_handler, progress_handler, step_start_handler):
        self.log_handler = log_handler
        self.progress_handler = progress_handler
        self.step_start_handler = step_start_handler
        self._is_running = True
        self.collected_data = []
        self.current_step_details = {}
        self.date_range = {}
        self.site_name = "default"
        
        service = ChromeService(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        self.wait = WebDriverWait(self.driver, 3)
        self.log_handler("WebDriver가 시작되었습니다.", "blue")

        self.strategy_map = {
            "kream_scrap_1": KreamScrap1Strategy,
            "kream_scrap_2": KreamScrap2Strategy
        }

    def stop(self):
        """외부에서 스크레이핑 작업을 중단하도록 요청하고 브라우저를 즉시 종료합니다."""
        if self._is_running:
            self.log_handler("작업 중단 신호를 받았습니다. 즉시 종료합니다.", "orange")
            self._is_running = False
            
            if self.driver:
                try:
                    self.driver.quit()
                    self.log_handler("WebDriver가 강제 종료되었습니다.", "orange")
                except Exception:
                    pass
                self.driver = None

    def run_workflow(self, workflow_data, **kwargs):
        """워크플로우의 모든 단계를 순서대로 실행합니다."""
        self.date_range = kwargs
        self.site_name = workflow_data.get('site_name', 'default')
        steps = workflow_data.get('steps', [])
        try:
            for i, step in enumerate(steps):
                if not self._is_running: break
                
                self.current_step_details = step
                step_name = step.get('step_name', 'Unnamed Step')
                self.log_handler(f"\n--- Step {i+1}: {step_name} 시작 ---", "black")
                
                try:
                    action_type = step.get('action_type')
                    
                    if action_type == 'navigate':
                        self._execute_navigate(step)
                    elif action_type == 'manual_login':
                        if not self._execute_manual_login(step):
                            self.log_handler("로그인 실패. 워크플로우를 중단합니다.", "red")
                            break
                    elif action_type in self.strategy_map:
                        self._execute_navigate(step)
                        self.step_start_handler(step_name)
                        strategy_class = self.strategy_map[action_type]
                        strategy_instance = strategy_class(self, step, kwargs)
                        self.collected_data = strategy_instance.execute()

                        if self._is_running and self.collected_data:
                            self.save_collected_data()
                    else:
                        self.log_handler(f"경고: 알 수 없는 action_type '{action_type}'입니다.", "orange")
                
                except Exception as e:
                    if self._is_running:
                        self.log_handler(f"❌ '{step_name}' 작업 중 오류가 발생했습니다: {e}", "red")
            
        finally:
            self.close()

    def save_collected_data(self):
        """수집된 데이터를 CSV 파일로 저장하는 헬퍼 메소드."""
        base_filename = self.current_step_details.get('output_filename')
        rules = self.current_step_details.get('detail_page_rules', {})
        start_date = self.date_range.get('start_date')
        end_date = self.date_range.get('end_date')
        subfolder_name = self.site_name

        if base_filename and self.collected_data:
            first_item_date = self.collected_data[0].get('_date')
            last_item_date = self.collected_data[-1].get('_date')

            start_str = start_date.strftime("%Y%m%d") if start_date else last_item_date.strftime("%Y%m%d")
            end_str = end_date.strftime("%Y%m%d") if end_date else first_item_date.strftime("%Y%m%d")
            
            final_filename = f"{base_filename}_{start_str}_{end_str}.csv"
            column_mappings = {key: rule.get('column_name', key) for key, rule in rules.items()}
            
            data_to_save = [{k: v for k, v in item.items() if k != '_date'} for item in self.collected_data]
            
            save_to_csv(data_to_save, final_filename, subfolder_name, column_mappings, self.log_handler)
            self.collected_data = []

    def _execute_manual_login(self, step_details):
        """사용자가 직접 로그인할 때까지 대기하고, 성공 여부를 감지합니다."""
        if not self._is_running: return False
        
        target_url = step_details.get('target_url')
        condition = step_details.get('success_condition', {})
        if not all([target_url, condition]):
            self.log_handler("에러: manual_login에 필요한 정보가 부족합니다.", "red")
            return False
        self.driver.get(target_url)
        timeout = condition.get('timeout', 120)
        selector = condition.get('selector')
        text_to_find = condition.get('text_contains')
        self.log_handler(f"\n브라우저에서 직접 로그인을 진행해주세요. (최대 {timeout}초 대기)", "purple")
        try:
            xpath_selector = f"//{selector.split('.')[0]}[contains(@class, '{selector.split('.')[1]}') and contains(text(), '{text_to_find}')]"
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.visibility_of_element_located((By.XPATH, xpath_selector)))

            if not self._is_running: return False
            self.log_handler("🎉 로그인 성공! 다음 단계를 진행합니다.", "green")
            return True
        except TimeoutException:
            if not self._is_running: return False
            self.log_handler(f"⏰ 시간 초과! 로그인된 요소를 찾지 못했습니다.", "orange")
            return False
        except Exception as e:
            if not self._is_running: return False
            self.log_handler(f"로그인 감지 중 오류 발생: {e}", "red")
            return False

    def _execute_navigate(self, step_details):
        """단순 페이지 이동을 처리합니다."""
        if not self._is_running: return
        
        target_url = step_details.get('target_url')
        if not target_url:
            self.log_handler("에러: target_url이 지정되지 않았습니다.", "red")
            return
        self.log_handler(f"페이지로 이동 중: {target_url}", "black")
        self.driver.get(target_url)
        time.sleep(2)
        self.log_handler("이동 완료.", "black")
    
    def close(self):
        """WebDriver를 안전하게 종료하고, 남은 데이터가 있으면 저장합니다."""
        if not self._is_running and self.collected_data:
            self.log_handler(f"\n작업이 중단되었습니다. 지금까지 수집된 {len(self.collected_data)}개의 데이터를 저장합니다...", "orange")
            self.save_collected_data()

        if self.driver:
            try:
                self.driver.quit()
                self.log_handler("\nWebDriver가 종료되었습니다.", "blue")
            except Exception:
                pass
            self.driver = None