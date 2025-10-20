import time
from typing import List, Dict, Any
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from .scraping_strategy import ScrapingStrategy

class KreamScrap2Strategy(ScrapingStrategy):
    """'보관 판매 내역' 스크랩핑 전략을 담당하는 클래스."""

    STALE_ELEMENT_REFRESH_WAIT_TIME = 2

    def execute(self) -> List[Dict[str, Any]]:
        """보관 판매 내역을 스크래핑합니다."""
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
        
        self.log_handler(f"총 {len(filtered_items)}개의 아이템을 찾았습니다.", "black")

        # 3. 상세 정보 수집
        self._collect_detail_data(filtered_items)
        
        return self.collected_data

    def _filter_items_by_date(self, start_date, end_date) -> List[Dict[str, Any]]:
        """날짜 범위에 맞는 아이템만 필터링합니다.
        
        Raises:
            Exception: 요소 검색 또는 날짜 파싱 중 오류
        """
        all_list_items = self.driver.find_elements(By.CSS_SELECTOR, self.step_details['list_item_selector'])
        filtered_items = []
        max_items = self._get_max_items()  # TRIAL이면 15, 아니면 None
        
        for item in all_list_items:
            date_element = item.find_element(By.CSS_SELECTOR, self.step_details['list_date_selector'])
            item_date = self._parse_date_from_text(date_element.text)
            
            if item_date and self._is_date_in_range(item_date, start_date, end_date):
                filtered_items.append({"element": item, "date": item_date})
                
                # TRIAL 권한의 경우 최대 개수 제한
                if max_items and len(filtered_items) >= max_items:
                    self.log_handler(f"체험판은 최대 {max_items}개까지만 수집 가능합니다.", "red")
                    break
        
        return filtered_items

    def _collect_detail_data(self, filtered_items: List[Dict[str, Any]]) -> None:
        """각 아이템의 상세 정보를 수집합니다.
        
        Raises:
            StaleElementReferenceException: 요소 참조 오류
            WebDriverException: WebDriver 실행 중 오류
            Exception: 기타 예외
        """
        total_items = len(filtered_items)
        self.progress_handler(0, total_items)
        rules = self.step_details.get('detail_rules', {})

        for i, item_info in enumerate(filtered_items):
            if not self.scraper._is_running:
                break

            self.progress_handler(i + 1, total_items)
            self.log_handler(f"  - 아이템 {i+1}/{total_items} 상세 정보 수집 중...", "black")
            
            self._scrape_item_detail(item_info, rules)

        self._log_completion_status()

    def _scrape_item_detail(self, item_info: Dict[str, Any], rules: Dict[str, Any]) -> None:
        """개별 아이템의 상세 정보를 스크래핑합니다.
        
        Raises:
            TimeoutException: Drawer 로딩 대기 시간 초과
            Exception: 요소 검색 또는 데이터 파싱 중 오류
        """
        # Drawer 열기
        detail_button = item_info['element'].find_element(
            By.CSS_SELECTOR, 
            self.step_details['detail_button_selector']
        )
        self.driver.execute_script("arguments[0].click();", detail_button)
        
        # 정산금액 요소 대기 (Drawer 로딩 확인)
        payout_amount_xpath = "//span[@class='key' and contains(., '정산금액')]/following-sibling::p[@class='value']"
        self.wait.until(EC.visibility_of_element_located((By.XPATH, payout_amount_xpath)))
        
        # 데이터 파싱
        drawer = self.driver.find_element(By.CSS_SELECTOR, self.step_details['drawer_selector'])
        soup = BeautifulSoup(drawer.get_attribute('innerHTML'), 'html.parser')
        
        item_data = self._parse_item_data(soup, rules)
        item_data['_date'] = item_info['date']
        self.collected_data.append(item_data)
        
        # Drawer 닫기
        self._close_drawer()

    def _close_drawer(self) -> None:
        """Drawer를 닫고 완전히 사라질 때까지 대기합니다.
        
        Raises:
            TimeoutException: Drawer 닫기 대기 시간 초과
            Exception: 요소 검색 중 오류
        """
        close_button = self.driver.find_element(
            By.CSS_SELECTOR, 
            self.step_details['drawer_close_button_selector']
        )
        self.driver.execute_script("arguments[0].click();", close_button)
        self.wait.until(EC.invisibility_of_element_located(
            (By.CSS_SELECTOR, self.step_details['drawer_selector'])
        ))

    def _log_completion_status(self) -> None:
        """작업 완료 상태를 로깅합니다."""
        if self.scraper._is_running:
            self.log_handler("모든 아이템 상세 정보 수집 완료.", "blue")
        else:
            self.log_handler(f"작업이 중단되었습니다. 총 {len(self.collected_data)}개 데이터가 수집되었습니다.", "orange")