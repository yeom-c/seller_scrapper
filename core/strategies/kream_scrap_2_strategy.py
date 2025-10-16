import time
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from .scraping_strategy import ScrapingStrategy

class KreamScrap2Strategy(ScrapingStrategy):
    """'보관 판매 내역' 스크레이핑 전략을 담당하는 클래스."""

    def execute(self):
        start_date = self.date_range.get('start_date')
        end_date = self.date_range.get('end_date')

        self.log_handler("지정한 기간에 맞춰 페이지를 스크롤합니다...", "black")
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while self.scraper._is_running:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height: break
            if start_date:
                try:
                    last_item_date_str = self.driver.find_elements(By.CSS_SELECTOR, self.step_details['list_date_selector'])[-1].text
                    last_item_date = datetime.strptime(last_item_date_str, "%y/%m/%d").date()
                    if last_item_date < start_date:
                        self.log_handler("시작일에 도달하여 스크롤을 중단합니다.", "blue")
                        break
                except (IndexError, ValueError): pass
            last_height = new_height
        
        if not self.scraper._is_running: return []
        self.log_handler("페이지 스크롤 완료.", "black")

        all_list_items = self.driver.find_elements(By.CSS_SELECTOR, self.step_details['list_item_selector'])
        filtered_items = []
        for item in all_list_items:
            try:
                date_element = item.find_element(By.CSS_SELECTOR, self.step_details['list_date_selector'])
                item_date = datetime.strptime(date_element.text, "%y/%m/%d").date()
                if (start_date and item_date < start_date) or (end_date and item_date > end_date): continue
                filtered_items.append({"element": item, "date": item_date})
            except Exception: continue
        
        if not filtered_items:
            self.log_handler("지정한 기간 내에 수집할 아이템이 없습니다.", "orange")
            return []
        self.log_handler(f"총 {len(filtered_items)}개의 필터링된 아이템을 찾았습니다.", "black")

        total_items = len(filtered_items)
        self.progress_handler(0, total_items)

        rules = self.step_details.get('detail_rules', {})
        for i, item_info in enumerate(filtered_items):
            if not self.scraper._is_running:
                self.log_handler(f"작업 중단 요청됨. 현재까지 {len(self.collected_data)}개 데이터 수집 완료.", "orange")
                break

            self.progress_handler(i + 1, total_items)
            self.log_handler(f"  - 아이템 {i+1}/{len(filtered_items)} 상세 정보 스크래핑 중...", "black")
            try:
                detail_button = item_info['element'].find_element(By.CSS_SELECTOR, self.step_details['detail_button_selector'])
                self.driver.execute_script("arguments[0].click();", detail_button)
                
                payout_amount_xpath = "//span[@class='key' and contains(., '정산금액')]/following-sibling::p[@class='value']"
                self.wait.until(EC.visibility_of_element_located((By.XPATH, payout_amount_xpath)))
                
                drawer = self.driver.find_element(By.CSS_SELECTOR, self.step_details['drawer_selector'])
                soup = BeautifulSoup(drawer.get_attribute('innerHTML'), 'html.parser')
                
                item_data = self._parse_item_data(soup, rules)
                item_data['_date'] = item_info['date']
                self.collected_data.append(item_data)
                
                close_button = self.driver.find_element(By.CSS_SELECTOR, self.step_details['drawer_close_button_selector'])
                self.driver.execute_script("arguments[0].click();", close_button)
                self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.step_details['drawer_selector'])))
                time.sleep(1)

            except StaleElementReferenceException:
                self.log_handler(f"    - StaleElement 에러 발생. 다음 아이템으로 넘어갑니다.", "orange")
                self.driver.refresh()
                time.sleep(2)
            except Exception as e:
                # 중단 신호로 인한 WebDriver 오류는 조용히 처리
                if not self.scraper._is_running:
                    self.log_handler(f"작업 중단됨. 현재까지 {len(self.collected_data)}개 데이터 수집 완료.", "orange")
                    break
                else:
                    self.log_handler(f"    - 에러 발생: {e}. 다음 아이템으로 넘어갑니다.", "red")
        
        if self.scraper._is_running:
            self.log_handler("모든 상세 정보 스크래핑 완료.", "green")
        else:
            self.log_handler(f"작업이 중단되었습니다. 총 {len(self.collected_data)}개 데이터가 수집되었습니다.", "orange")

        return self.collected_data