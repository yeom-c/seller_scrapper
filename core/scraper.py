import time
import pandas as pd
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class WorkflowScraper:
    """워크플로우의 각 단계를 순차적으로 실행하는 웹 스크레이퍼 클래스"""
    
    def __init__(self):
        """WorkflowScraper 클래스 초기화 시 WebDriver를 자동으로 설정합니다."""
        service = ChromeService(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)

    def run_workflow(self, steps, **kwargs):
        """워크플로우의 모든 단계를 순서대로 실행합니다."""
        try:
            for i, step in enumerate(steps):
                print(f"\n--- Step {i+1}: {step.get('step_name', 'Unnamed Step')} 시작 ---")
                action_type = step.get('action_type')
                
                if action_type == 'navigate':
                    self._execute_navigate(step)
                elif action_type == 'manual_login':
                    if not self._execute_manual_login(step): break
                elif action_type == 'kream_scrap_1':
                    self._execute_kream_scrap_1(step, **kwargs)
                elif action_type == 'kream_scrap_2':
                    self._execute_kream_scrap_2(step, **kwargs)
                else:
                    print(f"경고: 알 수 없는 action_type '{action_type}'입니다.")
            
            print("\n✅ 모든 워크플로우 단계가 완료되었습니다.")
        finally:
            self.close()

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
        target_url = step_details.get('target_url')
        condition = step_details.get('success_condition', {})
        if not all([target_url, condition]):
            print("에러: manual_login에 필요한 정보가 부족합니다.")
            return False
        self.driver.get(target_url)
        timeout = condition.get('timeout', 120)
        selector = condition.get('selector')
        text_to_find = condition.get('text_contains')
        print(f"\n브라우저에서 직접 로그인을 진행해주세요. (최대 {timeout}초 대기)")
        try:
            # XPath를 사용해 특정 텍스트를 포함하는 요소를 직접 찾아 대기
            xpath_selector = f"//{selector.split('.')[0]}[contains(@class, '{selector.split('.')[1]}') and contains(text(), '{text_to_find}')]"
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.visibility_of_element_located((By.XPATH, xpath_selector)))
            print("\n🎉 로그인 성공! 다음 단계를 진행합니다.")
            return True
        except TimeoutException:
            print(f"\n⏰ 시간 초과! 로그인된 요소를 찾지 못했습니다.")
            return False
        except Exception as e:
            print(f"로그인 감지 중 오류 발생: {e}")
            return False

    def _execute_navigate(self, step_details):
        """단순 페이지 이동을 처리합니다."""
        target_url = step_details.get('target_url')
        if not target_url:
            print("에러: target_url이 지정되지 않았습니다.")
            return
        self.driver.get(target_url)
        time.sleep(2) # 페이지 로딩 및 안정화를 위한 최소 대기
        print(f"페이지 이동 완료: {target_url}")

    def _execute_kream_scrap_1(self, step_details, start_date=None, end_date=None):
        """판매 내역 목록을 스크롤하며 아이템별 상세 정보를 스크랩합니다."""
        self._execute_navigate(step_details)
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height: break
            if start_date:
                try:
                    # 스크롤 최적화: 시작일 이전 데이터가 보이면 스크롤 중단
                    last_item_date_str = self.driver.find_elements(By.CSS_SELECTOR, step_details['list_date_selector'])[-1].text
                    last_item_date = datetime.strptime(last_item_date_str, "%y/%m/%d")
                    if last_item_date < start_date:
                        break
                except (IndexError, ValueError): pass
            last_height = new_height

        all_items = self.driver.find_elements(By.CSS_SELECTOR, step_details['list_item_selector'])
        filtered_items = []
        for item in all_items:
            try:
                date_element = item.find_element(By.CSS_SELECTOR, step_details['list_date_selector'])
                item_date = datetime.strptime(date_element.text, "%y/%m/%d")
                if (start_date and item_date < start_date) or (end_date and item_date > end_date): continue
                filtered_items.append({"url": item.get_attribute('href'), "date": item_date})
            except (ValueError, Exception): continue
        if not filtered_items:
            print("지정한 기간 내에 수집할 아이템이 없습니다.")
            return
        print(f"총 {len(filtered_items)}개의 필터링된 아이템 URL을 수집했습니다.")

        all_items_data = []
        rules = step_details.get('detail_page_rules', {})
        wait = WebDriverWait(self.driver, 3)

        for i, item_info in enumerate(filtered_items):
            url = item_info['url']
            print(f"  - 아이템 {i+1}/{len(filtered_items)} 상세 정보 스크래핑 중...")
            self.driver.get(url)
            
            try:
                # 주문번호가 표시될 때까지 동적으로 대기하여 속도 향상
                wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, rules['order_number']['selector'])))
            except TimeoutException:
                print("    - 상세 페이지 로딩 시간 초과. 다음 아이템으로 넘어갑니다.")
                continue
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            item_data = self._parse_item_data(soup, rules)
            all_items_data.append(item_data)

        print("모든 상세 정보 스크래핑 완료.")
        
        base_filename = step_details.get('output_filename')
        if base_filename and all_items_data:
            start_str = start_date.strftime("%Y%m%d") if start_date else filtered_items[-1]['date'].strftime("%Y%m%d")
            end_str = end_date.strftime("%Y%m%d") if end_date else filtered_items[0]['date'].strftime("%Y%m%d")
            final_filename = f"{base_filename}_{start_str}_{end_str}.csv"
            column_mappings = {key: rule.get('column_name', key) for key, rule in rules.items()}
            save_to_csv(all_items_data, final_filename, column_mappings)

    def _execute_kream_scrap_2(self, step_details, start_date=None, end_date=None):
        """보관 판매 내역에서 버튼을 클릭하여 사이드 메뉴의 상세 정보를 스크랩합니다."""
        self._execute_navigate(step_details)
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height: break
            if start_date:
                try:
                    last_item_date_str = self.driver.find_elements(By.CSS_SELECTOR, step_details['list_date_selector'])[-1].text
                    last_item_date = datetime.strptime(last_item_date_str, "%y/%m/%d")
                    if last_item_date < start_date:
                        break
                except (IndexError, ValueError): pass
            last_height = new_height

        all_list_items = self.driver.find_elements(By.CSS_SELECTOR, step_details['list_item_selector'])
        filtered_items = []
        for item in all_list_items:
            try:
                date_element = item.find_element(By.CSS_SELECTOR, step_details['list_date_selector'])
                item_date = datetime.strptime(date_element.text, "%y/%m/%d")
                if (start_date and item_date < start_date) or (end_date and item_date > end_date): continue
                filtered_items.append({"element": item, "date": item_date})
            except Exception: continue
        
        if not filtered_items:
            print("지정한 기간 내에 수집할 아이템이 없습니다.")
            return
        print(f"총 {len(filtered_items)}개의 필터링된 아이템을 찾았습니다.")

        all_items_data = []
        rules = step_details.get('detail_rules', {})
        wait = WebDriverWait(self.driver, 3)

        for i, item_info in enumerate(filtered_items):
            print(f"  - 아이템 {i+1}/{len(filtered_items)} 상세 정보 스크래핑 중...")
            try:
                item_element = item_info['element']
                
                detail_button_selector = step_details['detail_button_selector']
                # 버튼이 클릭 가능해질 때까지 최대 3초 대기
                detail_button = wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, f".inventory_item:nth-child({i+1}) {detail_button_selector}")
                ))
                self.driver.execute_script("arguments[0].click();", detail_button)

                payout_amount_xpath = "//span[@class='key' and contains(., '정산금액')]/following-sibling::p[@class='value']"
                wait.until(EC.visibility_of_element_located((By.XPATH, payout_amount_xpath)))
                
                drawer = self.driver.find_element(By.CSS_SELECTOR, step_details['drawer_selector'])
                soup = BeautifulSoup(drawer.get_attribute('innerHTML'), 'html.parser')
                
                item_data = self._parse_item_data(soup, rules)
                all_items_data.append(item_data)
                
                close_button_selector = step_details['drawer_close_button_selector']
                # 닫기 버튼이 클릭 가능해질 때까지 최대 3초 대기
                close_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, close_button_selector)))
                self.driver.execute_script("arguments[0].click();", close_button)
                
                wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, step_details['drawer_selector'])))

            except StaleElementReferenceException:
                print(f"    - StaleElement 에러 발생. 다음 아이템으로 넘어갑니다.")
                self.driver.refresh()
            except Exception as e:
                print(f"    - 에러 발생: {e}. 다음 아이템으로 넘어갑니다.")

        print("모든 상세 정보 스크래핑 완료.")
        base_filename = step_details.get('output_filename')
        if base_filename and all_items_data:
            start_str = start_date.strftime("%Y%m%d") if start_date else filtered_items[-1]['date'].strftime("%Y%m%d")
            end_str = end_date.strftime("%Y%m%d") if end_date else filtered_items[0]['date'].strftime("%Y%m%d")
            final_filename = f"{base_filename}_{start_str}_{end_str}.csv"
            column_mappings = {key: rule.get('column_name', key) for key, rule in rules.items()}
            save_to_csv(all_items_data, final_filename, column_mappings)
    
    def close(self):
        """WebDriver를 안전하게 종료합니다."""
        if self.driver:
            self.driver.quit()


def save_to_csv(data, filename, column_mappings=None):
    """스크레이핑한 데이터를 ./output 폴더에 CSV 파일로 저장합니다."""
    if not data:
        print("저장할 데이터가 없습니다.")
        return
    output_dir = os.path.join(BASE_DIR, 'output')
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, filename)
    df = pd.DataFrame(data)
    if column_mappings:
        df.rename(columns=column_mappings, inplace=True)
    df.to_csv(file_path, index=False, encoding='utf-8-sig')
    print(f"'{file_path}' 파일으로 저장이 완료되었습니다.")