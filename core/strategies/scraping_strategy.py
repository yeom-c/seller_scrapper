import time
from datetime import datetime, date
from selenium.webdriver.common.by import By
from typing import List, Dict, Any, Optional

class ScrapingStrategy:
    """모든 스크레이핑 전략의 기반이 되는 클래스."""

    # 상수 정의
    SCROLL_PAUSE_TIME = 2
    DATE_FORMAT = "%y/%m/%d"

    def __init__(self, scraper, step_details, date_range):
        """전략 클래스 초기화."""
        self.scraper = scraper
        self.driver = scraper.driver
        self.wait = scraper.wait
        self.log_handler = scraper.log_handler
        self.progress_handler = scraper.progress_handler
        self.step_details = step_details
        self.date_range = date_range
        self.collected_data: List[Dict[str, Any]] = []

    def execute(self):
        """이 메소드는 모든 하위 전략 클래스에서 반드시 구현해야 합니다."""
        raise NotImplementedError("execute 메소드는 하위 클래스에서 구현해야 합니다.")

    def _scroll_to_load_items(self, start_date: Optional[date] = None) -> bool:
        """페이지를 스크롤하여 아이템을 로드합니다.
        
        Args:
            start_date: 시작 날짜. 이 날짜에 도달하면 스크롤 중단
            
        Returns:
            스크롤 완료 여부 (중단되지 않고 완료되면 True)
        """
        self.log_handler("지정한 기간에 맞춰 페이지를 스크롤합니다...", "black")
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        while self.scraper._is_running:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(self.SCROLL_PAUSE_TIME)
            
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
                
            if start_date and self._check_reached_start_date(start_date):
                self.log_handler("시작일에 도달하여 스크롤을 중단합니다.", "blue")
                break
                
            last_height = new_height
        
        if not self.scraper._is_running:
            return False
            
        self.log_handler("페이지 스크롤 완료.", "black")
        return True

    def _check_reached_start_date(self, start_date: date) -> bool:
        """마지막 아이템의 날짜가 시작일보다 이전인지 확인합니다."""
        try:
            date_selector = self.step_details['list_date_selector']
            last_item_date_str = self.driver.find_elements(By.CSS_SELECTOR, date_selector)[-1].text
            last_item_date = datetime.strptime(last_item_date_str, self.DATE_FORMAT).date()
            return last_item_date < start_date
        except (IndexError, ValueError):
            return False

    def _parse_date_from_text(self, date_text: str) -> Optional[date]:
        """텍스트에서 날짜를 파싱합니다."""
        try:
            return datetime.strptime(date_text, self.DATE_FORMAT).date()
        except ValueError:
            return None

    def _is_date_in_range(self, item_date: date, start_date: Optional[date], end_date: Optional[date]) -> bool:
        """날짜가 지정된 범위 내에 있는지 확인합니다."""
        if start_date and item_date < start_date:
            return False
        if end_date and item_date > end_date:
            return False
        return True

    def _parse_item_data(self, soup, rules):
        """BeautifulSoup 객체와 추출 규칙을 받아 데이터를 파싱합니다."""
        item_data = {}
        for key, attr_info in rules.items():
            value = None
            rule_type = attr_info.get('type')

            if rule_type == 'text':
                element = soup.select_one(attr_info['selector'])
                if element: 
                    value = element.get_text(strip=True)
            
            elif rule_type == 'find_by_label':
                value = self._find_value_by_label(soup, attr_info['label'], 
                                                  'p', 'line_title', 
                                                  'div', 'display_line',
                                                  'p', 'line_description')
                                
            elif rule_type == 'find_by_label_v2':
                value = self._find_value_by_label(soup, attr_info['label'],
                                                  'span', 'key',
                                                  'div', 'text',
                                                  'p', 'value')
            
            item_data[key] = value
        return item_data

    def _find_value_by_label(self, soup, label_text: str, 
                            label_tag: str, label_class: str,
                            parent_tag: str, parent_class: str,
                            value_tag: str, value_class: str) -> Optional[str]:
        """라벨을 기준으로 값을 찾습니다."""
        labels = soup.find_all(label_tag, class_=label_class)
        for label_element in labels:
            if label_text in label_element.get_text(strip=True):
                parent_div = label_element.find_parent(parent_tag, class_=parent_class)
                if parent_div:
                    value_element = parent_div.find(value_tag, class_=value_class)
                    if value_element:
                        return value_element.get_text(strip=True)
        return None