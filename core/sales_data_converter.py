"""수집된 데이터를 판매 데이터 형식으로 변환하는 변환기"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta


class SalesDataConverter:
    """사이트별 수집 데이터를 범용 판매 데이터 형식으로 변환"""
    
    @staticmethod
    def convert_with_mapping(collected_data: List[Dict[str, Any]], mapping: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        매핑 룰을 사용하여 수집된 데이터를 판매 데이터 형식으로 변환합니다.
        
        Args:
            collected_data: 수집된 원본 데이터
            mapping: 데이터베이스 필드 매핑 룰
                {
                    "platform_name": {"type": "fixed", "value": "KREAM"},
                    "order_number": {"type": "field", "value": "order_number"},
                    "sale_date": {"type": "field", "value": "_date"},
                    "product_name": {"type": "field", "value": "product_name_kor"},
                    "product_code": {"type": "field", "value": "product_model"},
                    "product_size": {"type": "field", "value": "size"},
                    "product_color": {"type": "fixed", "value": null},
                    "sale_price": {"type": "field", "value": "instant_sell_price"},
                    "quantity": {"type": "fixed", "value": 1}
                }
            
        Returns:
            변환된 판매 데이터 리스트
        """
        sales_data = []
        
        for item in collected_data:
            try:
                sales_item = {}
                skip_item = False
                
                for db_field, rule in mapping.items():
                    mapping_type = rule.get('type')
                    mapping_value = rule.get('value')
                    
                    # fixed 타입: 고정값 사용
                    if mapping_type == 'fixed':
                        sales_item[db_field] = mapping_value
                    
                    # field 타입: 수집 데이터에서 필드 값 가져오기
                    elif mapping_type == 'field':
                        value = item.get(mapping_value)
                        
                        # 날짜 필드는 datetime으로 변환
                        if db_field == 'sale_date':
                            value = SalesDataConverter._parse_date(value)
                            if not value:
                                skip_item = True
                                break
                        
                        # 가격 필드는 숫자로 변환
                        elif db_field == 'sale_price':
                            value = SalesDataConverter._parse_price(value)
                            if value is None or value <= 0:
                                skip_item = True
                                break
                        
                        # 문자열 필드는 strip 처리
                        elif isinstance(value, str):
                            value = value.strip() or None
                        
                        sales_item[db_field] = value
                    
                    else:
                        # 알 수 없는 타입은 None
                        sales_item[db_field] = None
                
                # 스킵 플래그가 설정되었으면 이 항목은 제외
                if skip_item:
                    continue
                
                # 필수 필드 검증
                required_fields = ['platform_name', 'order_number', 'sale_date', 
                                 'product_name', 'sale_price', 'quantity']
                if all(sales_item.get(field) for field in required_fields):
                    sales_data.append(sales_item)
                    
            except Exception as e:
                # 개별 항목 변환 실패는 로그만 남기고 계속 진행
                print(f"데이터 변환 중 오류 (항목 스킵): {e}")
                continue
        
        return sales_data
    
    @staticmethod
    def convert(site_name: str, collected_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        사이트별로 수집된 데이터를 판매 데이터 형식으로 변환합니다.
        
        Args:
            site_name: 사이트 이름 (예: "KREAM", "크림")
            collected_data: 수집된 원본 데이터
            
        Returns:
            변환된 판매 데이터 리스트
        """
        print(collected_data)
        # 사이트 이름 정규화
        normalized_site = site_name.upper().strip()
        
        if normalized_site in ["KREAM", "크림"]:
            return SalesDataConverter._convert_kream_data(collected_data)
        else:
            # 알 수 없는 사이트는 빈 리스트 반환
            return []
    
    @staticmethod
    def _convert_kream_data(collected_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        KREAM 사이트의 수집 데이터를 변환합니다.
        
        수집 데이터 예시:
        {
            'order_number': '주문번호 A-AC118664302',
            'instant_sell_price': '189,000원',
            'product_name_kor': '슈프림 x 노스페이스 페이퍼 프린트 700 필 다운 스카프',
            'product_model': 'NF0A3FM28YJ',
            'size': 'ONE SIZE',
            '_date': datetime.date(2025, 10, 20)
        }
        """
        sales_data = []
        
        for item in collected_data:
            try:
                # 날짜 변환 (_date 필드 사용)
                sale_date = SalesDataConverter._parse_date(item.get('_date'))
                if not sale_date:
                    continue  # 날짜가 없으면 스킵
                
                # 주문번호 추출 ("주문번호 A-AC118664302" -> "A-AC118664302")
                order_number = str(item.get('order_number', '')).strip()
                if order_number.startswith('주문번호 '):
                    order_number = order_number.replace('주문번호 ', '')
                
                # 가격 변환 (instant_sell_price 사용: "189,000원" -> 189000)
                price_str = str(item.get('instant_sell_price', '0')).replace(',', '').replace('원', '').strip()
                try:
                    sale_price = float(price_str) if price_str else 0
                except ValueError:
                    sale_price = 0
                
                # 상품명 (한글명 우선, 없으면 영문명)
                product_name = (item.get('product_name_kor') or 
                              item.get('product_name_eng') or '').strip()
                
                # 판매 데이터 생성
                sales_item = {
                    'platform_name': 'KREAM',
                    'order_number': order_number,
                    'sale_date': sale_date,
                    'product_name': product_name,
                    'product_code': SalesDataConverter._get_optional_field(item, 'product_model'),
                    'product_size': SalesDataConverter._get_optional_field(item, 'size'),
                    'product_color': None,  # KREAM 데이터에는 색상 정보 없음
                    'sale_price': sale_price,
                    'quantity': 1  # KREAM은 항상 1개씩 판매
                }
                
                # 필수 필드 검증
                if sales_item['order_number'] and sales_item['product_name'] and sales_item['sale_price'] > 0:
                    sales_data.append(sales_item)
                    
            except Exception as e:
                # 개별 항목 변환 실패는 로그만 남기고 계속 진행
                print(f"데이터 변환 중 오류 (항목 스킵): {e}")
                continue
        
        return sales_data
    
    @staticmethod
    def _parse_price(price_value: Any) -> Optional[float]:
        """가격 문자열을 숫자로 변환 (쉼표, 원 제거)"""
        if isinstance(price_value, (int, float)):
            return float(price_value)
        
        if isinstance(price_value, str):
            # "189,000원", "-13,490원" 등 처리
            price_str = price_value.replace(',', '').replace('원', '').strip()
            try:
                return float(price_str)
            except ValueError:
                pass
        
        return None
    
    @staticmethod
    def _parse_date(date_value: Any) -> Optional[datetime]:
        """다양한 날짜 형식을 datetime으로 변환 (KST → UTC)"""
        # KST는 UTC+9
        KST = timezone(timedelta(hours=9))
        
        if isinstance(date_value, datetime):
            # 이미 datetime이면 KST로 간주하고 UTC로 변환
            if date_value.tzinfo is None:
                date_value = date_value.replace(tzinfo=KST)
            return date_value.astimezone(timezone.utc)
        
        # date 객체를 datetime으로 변환 (00:00:00 KST)
        if hasattr(date_value, 'year') and hasattr(date_value, 'month') and hasattr(date_value, 'day'):
            try:
                dt = datetime(date_value.year, date_value.month, date_value.day, tzinfo=KST)
                return dt.astimezone(timezone.utc)
            except Exception:
                pass
        
        if isinstance(date_value, str):
            dt = None
            
            # "25/10/11 01:32" 형식 (YY/MM/DD HH:MM)
            if '/' in date_value and ' ' in date_value:
                try:
                    dt = datetime.strptime(date_value, '%y/%m/%d %H:%M')
                except ValueError:
                    pass
            
            # "2025.01.21" 형식
            elif '.' in date_value:
                try:
                    dt = datetime.strptime(date_value, '%Y.%m.%d')
                except ValueError:
                    pass
            
            # "2025-01-21" 형식
            elif '-' in date_value:
                try:
                    dt = datetime.strptime(date_value, '%Y-%m-%d')
                except ValueError:
                    pass
            
            # "25/10/20" 형식 (YY/MM/DD)
            elif '/' in date_value and len(date_value.split('/')) == 3:
                try:
                    dt = datetime.strptime(date_value, '%y/%m/%d')
                except ValueError:
                    pass
            
            # 파싱된 datetime을 KST로 간주하고 UTC로 변환
            if dt:
                dt = dt.replace(tzinfo=KST)
                return dt.astimezone(timezone.utc)
        
        return None
    
    @staticmethod
    def _get_optional_field(item: Dict[str, Any], field: str) -> Optional[str]:
        """선택적 필드를 가져오고, 빈 문자열이면 None 반환"""
        value = item.get(field)
        if value is None:
            return None
        
        value_str = str(value).strip()
        return value_str if value_str else None
