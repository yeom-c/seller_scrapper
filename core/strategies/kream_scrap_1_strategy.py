import time
from typing import List, Dict, Any
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from .scraping_strategy import ScrapingStrategy

class KreamScrap1Strategy(ScrapingStrategy):
    """'일반 판매 내역' 스크랩핑 전략을 담당하는 클래스."""

    def execute(self) -> List[Dict[str, Any]]:
        """일반 판매 내역을 스크래핑합니다."""
        start_date = self.date_range.get('start_date')
        end_date = self.date_range.get('end_date')

        # 1. 페이지 스크롤
        if not self._scroll_to_load_items(start_date):
            return []

        # 2. 아이템 필터링
        filtered_items = self._filter_items_by_date(start_date, end_date)
        if not filtered_items:
            self.log_handler("지정한 기간 내에 수집할 아이템이 없습니다.", "orange")
            return []
        
        self.log_handler(f"총 {len(filtered_items)}개의 필터링된 아이템을 수집했습니다.", "black")

        # 3. 상세 정보 수집
        self._collect_detail_data(filtered_items)
        
        return self.collected_data

    def _filter_items_by_date(self, start_date, end_date) -> List[Dict[str, Any]]:
        """날짜 범위에 맞는 아이템만 필터링합니다."""
        all_items = self.driver.find_elements(By.CSS_SELECTOR, self.step_details['list_item_selector'])
        filtered_items = []
        
        for item in all_items:
            try:
                date_element = item.find_element(By.CSS_SELECTOR, self.step_details['list_date_selector'])
                item_date = self._parse_date_from_text(date_element.text)
                
                if item_date and self._is_date_in_range(item_date, start_date, end_date):
                    filtered_items.append({"url": item.get_attribute('href'), "date": item_date})
            except Exception:
                continue
        
        return filtered_items

    def _collect_detail_data(self, filtered_items: List[Dict[str, Any]]) -> None:
        """각 아이템의 상세 정보를 수집합니다."""
        total_items = len(filtered_items)
        self.progress_handler(0, total_items)
        rules = self.step_details.get('detail_page_rules', {})

        for i, item_info in enumerate(filtered_items):
            if not self.scraper._is_running:
                self.log_handler(f"작업 중단 요청됨. 현재까지 {len(self.collected_data)}개 데이터 수집 완료.", "orange")
                break
            
            self.progress_handler(i + 1, total_items)
            self.log_handler(f"  - 아이템 {i+1}/{total_items} 상세 정보 수집 중...", "black")
            
            try:
                self._scrape_item_detail(item_info, rules)
            except TimeoutException:
                self.log_handler("    - 상세 페이지 로딩 시간 초과. 다음 아이템으로 넘어갑니다.", "orange")
            except WebDriverException as e:
                if not self.scraper._is_running:
                    self.log_handler(f"작업 중단됨. 현재까지 {len(self.collected_data)}개 데이터 수집 완료.", "orange")
                    break
                self.log_handler(f"    - 오류 발생: {e}. 다음 아이템으로 넘어갑니다.", "orange")

        self._log_completion_status()

    def _scrape_item_detail(self, item_info: Dict[str, Any], rules: Dict[str, Any]) -> None:
        """개별 아이템의 상세 정보를 스크래핑합니다."""
        url = item_info['url']
        self.driver.get(url)
        
        # 페이지 로딩 대기
        self.wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, rules['order_number']['selector'])
        ))
        
        # 데이터 파싱
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        item_data = self._parse_item_data(soup, rules)
        item_data['_date'] = item_info['date']
        self.collected_data.append(item_data)

    def _log_completion_status(self) -> None:
        """작업 완료 상태를 로깅합니다."""
        if self.scraper._is_running:
            self.log_handler("모든 아이템 상세 정보 수집 완료.", "blue")
        else:
            self.log_handler(f"작업이 중단되었습니다. 총 {len(self.collected_data)}개 데이터가 수집되었습니다.", "orange")