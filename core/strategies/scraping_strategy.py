class ScrapingStrategy:
    """모든 스크레이핑 전략의 기반이 되는 클래스."""

    def __init__(self, scraper, step_details, date_range):
        """전략 클래스 초기화."""
        self.scraper = scraper
        self.driver = scraper.driver
        self.wait = scraper.wait
        self.log_handler = scraper.log_handler
        self.progress_handler = scraper.progress_handler # 진행률 핸들러 상속
        self.step_details = step_details
        self.date_range = date_range
        self.collected_data = []

    def execute(self):
        """이 메소드는 모든 하위 전략 클래스에서 반드시 구현해야 합니다."""
        raise NotImplementedError("execute 메소드는 하위 클래스에서 구현해야 합니다.")

    def _parse_item_data(self, soup, rules):
        """BeautifulSoup 객체와 추출 규칙을 받아 데이터를 파싱합니다."""
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