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

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class WorkflowScraper:
    """워크플로우의 각 단계를 순차적으로 실행하는 웹 스크레이퍼 클래스"""

    def __init__(self, log_handler):
        """WorkflowScraper 초기화 시 WebDriver를 설정하고, 로그 핸들러를 등록합니다."""
        self.log_handler = log_handler
        self._is_running = True
        self.collected_data = []
        self.current_step_details = {}
        self.date_range = {}
        
        service = ChromeService(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        self.log_handler("WebDriver가 시작되었습니다.", "blue")

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

    def run_workflow(self, steps, **kwargs):
        """워크플로우의 모든 단계를 순서대로 실행합니다."""
        self.date_range = kwargs
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
                    elif action_type == 'kream_scrap_1' or action_type == 'kream_scrap_2':
                        self.collected_data = []
                        if action_type == 'kream_scrap_1':
                            self._execute_kream_scrap_1(step, **kwargs)
                        else:
                            self._execute_kream_scrap_2(step, **kwargs)
                        
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

        if base_filename and self.collected_data:
            first_item_date = self.collected_data[0].get('_date')
            last_item_date = self.collected_data[-1].get('_date')

            start_str = start_date.strftime("%Y%m%d") if start_date else last_item_date.strftime("%Y%m%d")
            end_str = end_date.strftime("%Y%m%d") if end_date else first_item_date.strftime("%Y%m%d")
            
            final_filename = f"{base_filename}_{start_str}_{end_str}.csv"
            column_mappings = {key: rule.get('column_name', key) for key, rule in rules.items()}
            
            data_to_save = [{k: v for k, v in item.items() if k != '_date'} for item in self.collected_data]
            
            save_to_csv(data_to_save, final_filename, column_mappings, self.log_handler)
            self.collected_data = []

    def _parse_item_data(self, soup, rules):
        """BeautifulSoup 객체와 추출 규칙(rules)을 받아 데이터를 파싱하고 딕셔너리로 반환합니다."""
        item_data = {}
        for key, attr_info in rules.items():
            value = None
            rule_type = attr_info.get('type')

            if rule_type == 'text':
                element = soup.select_one(attr_info['selector'])
                if element: value = element.get_text(strip=True)
            
            elif rule_type == 'find_by_label':
                labels = soup.find_all('p', class_='line_title')
                for label_element in labels:
                    if label_element.get_text(strip=True) == attr_info['label']:
                        parent_div = label_element.find_parent('div', class_='display_line')
                        if parent_div:
                            value_element = parent_div.find('p', class_='line_description')
                            if value_element:
                                value = value_element.get_text(strip=True)
                                break
                                
            elif rule_type == 'find_by_label_v2':
                labels = soup.find_all('span', class_='key')
                for label_element in labels:
                    if attr_info['label'] in label_element.get_text(strip=True):
                        parent_div = label_element.find_parent('div', class_='text')
                        if parent_div:
                            value_element = parent_div.find('p', class_='value')
                            if value_element:
                                value = value_element.get_text(strip=True)
                                break
            
            item_data[key] = value
        return item_data

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

    def _execute_kream_scrap_1(self, step_details, start_date=None, end_date=None):
        """판매 내역 목록을 스크롤하며 아이템별 상세 정보를 스크랩합니다."""
        if not self._is_running: return
        self._execute_navigate(step_details)
        self.log_handler("지정한 기간에 맞춰 페이지를 스크롤합니다...", "black")
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while self._is_running:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height: break
            if start_date:
                try:
                    last_item_date_str = self.driver.find_elements(By.CSS_SELECTOR, step_details['list_date_selector'])[-1].text
                    last_item_date = datetime.strptime(last_item_date_str, "%y/%m/%d").date()
                    if last_item_date < start_date:
                        self.log_handler("시작일에 도달하여 스크롤을 중단합니다.", "blue")
                        break
                except (IndexError, ValueError): pass
            last_height = new_height
        if not self._is_running: return
        self.log_handler("페이지 스크롤 완료.", "black")

        all_items = self.driver.find_elements(By.CSS_SELECTOR, step_details['list_item_selector'])
        filtered_items = []
        for item in all_items:
            try:
                date_element = item.find_element(By.CSS_SELECTOR, step_details['list_date_selector'])
                item_date = datetime.strptime(date_element.text, "%y/%m/%d").date()
                if (start_date and item_date < start_date) or (end_date and item_date > end_date): continue
                filtered_items.append({"url": item.get_attribute('href'), "date": item_date})
            except (ValueError, Exception): continue
        if not filtered_items:
            self.log_handler("지정한 기간 내에 수집할 아이템이 없습니다.", "orange")
            return
        self.log_handler(f"총 {len(filtered_items)}개의 필터링된 아이템 URL을 수집했습니다.", "black")

        rules = step_details.get('detail_page_rules', {})
        wait = WebDriverWait(self.driver, 3)

        for i, item_info in enumerate(filtered_items):
            if not self._is_running: break
            url = item_info['url']
            self.log_handler(f"  - 아이템 {i+1}/{len(filtered_items)} 상세 정보 스크래핑 중...", "black")
            self.driver.get(url)
            
            try:
                wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, rules['order_number']['selector'])))
            except TimeoutException:
                self.log_handler("    - 상세 페이지 로딩 시간 초과. 다음 아이템으로 넘어갑니다.", "orange")
                continue
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            item_data = self._parse_item_data(soup, rules)
            item_data['_date'] = item_info['date']
            self.collected_data.append(item_data)

        if not self._is_running: return
        self.log_handler("모든 상세 정보 스크래핑 완료.", "green")

    def _execute_kream_scrap_2(self, step_details, start_date=None, end_date=None):
        """보관 판매 내역에서 버튼을 클릭하여 사이드 메뉴의 상세 정보를 스크랩합니다."""
        if not self._is_running: return
        self._execute_navigate(step_details)
        self.log_handler("지정한 기간에 맞춰 페이지를 스크롤합니다...", "black")
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while self._is_running:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height: break
            if start_date:
                try:
                    last_item_date_str = self.driver.find_elements(By.CSS_SELECTOR, step_details['list_date_selector'])[-1].text
                    last_item_date = datetime.strptime(last_item_date_str, "%y/%m/%d").date()
                    if last_item_date < start_date:
                        self.log_handler("시작일에 도달하여 스크롤을 중단합니다.", "blue")
                        break
                except (IndexError, ValueError): pass
            last_height = new_height
        if not self._is_running: return
        self.log_handler("페이지 스크롤 완료.", "black")

        all_list_items = self.driver.find_elements(By.CSS_SELECTOR, step_details['list_item_selector'])
        filtered_items = []
        for item in all_list_items:
            try:
                date_element = item.find_element(By.CSS_SELECTOR, step_details['list_date_selector'])
                item_date = datetime.strptime(date_element.text, "%y/%m/%d").date()
                if (start_date and item_date < start_date) or (end_date and item_date > end_date):
                    continue
                filtered_items.append({"element": item, "date": item_date})
            except Exception: continue
        
        if not filtered_items:
            self.log_handler("지정한 기간 내에 수집할 아이템이 없습니다.", "orange")
            return
        self.log_handler(f"총 {len(filtered_items)}개의 필터링된 아이템을 찾았습니다.", "black")

        rules = step_details.get('detail_rules', {})
        wait = WebDriverWait(self.driver, 3)

        for i, item_info in enumerate(filtered_items):
            if not self._is_running: break
            self.log_handler(f"  - 아이템 {i+1}/{len(filtered_items)} 상세 정보 스크래핑 중...", "black")
            try:
                detail_button = item_info['element'].find_element(By.CSS_SELECTOR, step_details['detail_button_selector'])
                self.driver.execute_script("arguments[0].click();", detail_button)
                
                payout_amount_xpath = "//span[@class='key' and contains(., '정산금액')]/following-sibling::p[@class='value']"
                wait.until(EC.visibility_of_element_located((By.XPATH, payout_amount_xpath)))
                
                drawer = self.driver.find_element(By.CSS_SELECTOR, step_details['drawer_selector'])
                soup = BeautifulSoup(drawer.get_attribute('innerHTML'), 'html.parser')
                
                item_data = self._parse_item_data(soup, rules)
                item_data['_date'] = item_info['date']
                self.collected_data.append(item_data)
                
                close_button = self.driver.find_element(By.CSS_SELECTOR, step_details['drawer_close_button_selector'])
                self.driver.execute_script("arguments[0].click();", close_button)
                wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, step_details['drawer_selector'])))
                time.sleep(1)

            except StaleElementReferenceException:
                self.log_handler(f"    - StaleElement 에러 발생. 다음 아이템으로 넘어갑니다.", "orange")
                self.driver.refresh()
                time.sleep(2)
            except Exception as e:
                self.log_handler(f"    - 에러 발생: {e}. 다음 아이템으로 넘어갑니다.", "red")

        if not self._is_running: return
        self.log_handler("모든 상세 정보 스크래핑 완료.", "green")
    
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


def save_to_csv(data, filename, column_mappings=None, log_handler=print):
    """스크레이핑한 데이터를 ./output 폴더에 CSV 파일로 저장합니다."""
    if not data:
        log_handler("저장할 데이터가 없습니다.", "orange")
        return
    output_dir = os.path.join(BASE_DIR, 'output')
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, filename)
    df = pd.DataFrame(data)
    if column_mappings:
        df.rename(columns=column_mappings, inplace=True)
    df.to_csv(file_path, index=False, encoding='utf-8-sig')
    log_handler(f"'{file_path}' 파일으로 저장이 완료되었습니다.", "green")