"""판매 데이터 저장을 위한 클라이언트"""
from typing import List, Dict, Any
from datetime import datetime
from .supabase_client import supabase
import json


class SalesData:
    """판매 데이터를 Supabase Edge Function에 저장하는 클라이언트"""
    
    def save_sales_data(self, sales_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        판매 데이터를 저장합니다.
        
        Args:
            sales_data: 저장할 판매 데이터 리스트. 각 항목은 다음 필드를 포함해야 합니다:
                - platform_name (str): 플랫폼 이름 (예: "KREAM")
                - order_number (str): 주문 번호
                - sale_date (str or datetime): 판매 날짜 (ISO 8601 형식)
                - product_name (str): 상품명
                - product_code (str, optional): 상품 코드
                - product_size (str, optional): 상품 사이즈
                - product_color (str, optional): 상품 색상
                - sale_price (float): 판매 가격
                - quantity (int): 수량
        
        Returns:
            Dict[str, Any]: 응답 데이터
                - success (bool): 성공 여부
                - message (str): 메시지
                - inserted (int): 삽입된 데이터 개수
                - error (str, optional): 에러 메시지
        """
        if not sales_data:
            return {
                "success": True,
                "message": "No sales data to save",
                "inserted": 0
            }
        
        # 날짜 형식 변환
        formatted_sales_data = []
        for sale in sales_data:
            formatted_sale = sale.copy()
            
            # datetime 객체를 ISO 8601 문자열로 변환
            if isinstance(formatted_sale.get('sale_date'), datetime):
                formatted_sale['sale_date'] = formatted_sale['sale_date'].isoformat()
            
            # 필수 필드 검증
            required_fields = ['platform_name', 'order_number', 'sale_date', 'product_name', 'sale_price', 'quantity']
            missing_fields = [field for field in required_fields 
                            if field not in formatted_sale or formatted_sale[field] is None]
            
            if missing_fields:
                return {
                    "success": False,
                    "error": f"Missing required fields: {', '.join(missing_fields)}"
                }
            
            formatted_sales_data.append(formatted_sale)
        
        try:
            # Edge Function 호출
            response_data = supabase.functions.invoke(
                'save-sales-data',
                invoke_options={
                    'body': {'sales': formatted_sales_data}
                }
            )
            
            # response_data가 bytes일 경우 디코딩
            if isinstance(response_data, bytes):
                data = json.loads(response_data.decode('utf-8'))
            else:
                # 만약 이미 dict로 파싱되었다면 그대로 사용
                data = response_data
            
            # 에러 체크
            if isinstance(data, dict) and data.get('error'):
                return {
                    "success": False,
                    "error": data.get('error', 'Unknown error'),
                    "details": data.get('details')
                }
            
            return {
                "success": True,
                "message": data.get('message', 'Sales data saved successfully'),
                "inserted": data.get('inserted', 0)
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error calling Edge Function: {str(e)}"
            }


# 전역 인스턴스
sales_data = SalesData()
