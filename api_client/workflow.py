from typing import Dict, Any, Optional
from .client import APIClient


class WorkflowAPI:
    """워크플로우 관련 API를 처리하는 클래스."""
    
    def __init__(self, client: Optional[APIClient] = None):
        """
        WorkflowAPI 초기화.
        
        Args:
            client: APIClient 인스턴스 (None인 경우 새로 생성)
        """
        self.client = client or APIClient()
    
    def get_workflows(self) -> Dict[str, str]:
        """
        사용자의 워크플로우 목록을 가져옵니다.
        
        Returns:
            권한별 워크플로우 JSON 문자열 딕셔너리
            예: {
                "kream": "{ workflow json string }",
                "tab1": "{ workflow json string }"
            }
            
        Raises:
            AuthenticationError: 인증 실패
            APIException: API 에러 발생
        """
        response = self.client.get('/workflows')
        return response.get('workflows', {})
    
    def get_workflow(self, permission: str) -> Dict[str, Any]:
        """
        특정 권한의 워크플로우를 가져옵니다.
        
        Args:
            permission: 권한 이름 (예: 'kream')
            
        Returns:
            워크플로우 데이터
            
        Raises:
            NotFoundError: 워크플로우를 찾을 수 없음
            APIException: API 에러 발생
        """
        response = self.client.get(f'/workflows/{permission}')
        return response
