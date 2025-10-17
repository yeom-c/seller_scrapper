from typing import Dict, Any, Optional
from .client import APIClient
from .config import config
from .token_manager import token_manager


class AuthAPI:
    """인증 관련 API를 처리하는 클래스."""
    
    def __init__(self, client: Optional[APIClient] = None):
        """
        AuthAPI 초기화.
        
        Args:
            client: APIClient 인스턴스 (None인 경우 새로 생성)
        """
        self.client = client or APIClient()
    
    def register(self, email: str, password: str, **kwargs) -> Dict[str, Any]:
        """
        회원가입을 수행합니다.
        
        Args:
            email: 이메일 주소
            password: 비밀번호
            **kwargs: 추가 사용자 정보 (예: name, phone 등)
            
        Returns:
            회원가입 응답 데이터
            
        Raises:
            ValidationError: 입력 데이터 검증 실패
            APIException: API 에러 발생
        """
        data = {
            'email': email,
            'password': password,
            **kwargs
        }
        
        response = self.client.post('/auth/register', data=data)
        return response
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        로그인을 수행합니다.
        
        Args:
            email: 이메일 주소
            password: 비밀번호
            
        Returns:
            로그인 응답 데이터 (토큰 포함)
            
        Raises:
            AuthenticationError: 인증 실패
            ValidationError: 입력 데이터 검증 실패
            APIException: API 에러 발생
        """
        data = {
            'email': email,
            'password': password
        }
        
        response = self.client.post('/auth/login', data=data)
        
        # 토큰 저장 (config와 token_manager 모두 업데이트)
        if 'access_token' in response and 'refresh_token' in response:
            access_token = response['access_token']
            refresh_token = response['refresh_token']
            
            # config에 저장 (기존 방식 유지)
            config.access_token = access_token
            config.refresh_token = refresh_token
            
            # token_manager에 저장하여 권한 정보 파싱
            token_manager.set_tokens(access_token, refresh_token)
        
        return response
    
    def logout(self) -> Dict[str, Any]:
        """
        로그아웃을 수행합니다. API 호출 없이 로컬 토큰만 정리합니다.
        
        Returns:
            로그아웃 성공 메시지
        """
        # 로컬 토큰 제거
        config.clear_tokens()
        token_manager.clear()
        
        return {
            'success': True,
            'message': '로그아웃되었습니다.'
        }
    
    def refresh_token(self) -> Dict[str, Any]:
        """
        액세스 토큰을 갱신합니다.
        
        Returns:
            토큰 갱신 응답 데이터
            
        Raises:
            AuthenticationError: 리프레시 토큰이 유효하지 않음
            APIException: API 에러 발생
        """
        if not config.refresh_token:
            from .exceptions import AuthenticationError
            raise AuthenticationError('리프레시 토큰이 없습니다.')
        
        data = {
            'refresh_token': config.refresh_token
        }
        
        response = self.client.post('/auth/refresh', data=data)
        
        # 새 토큰 저장 (config와 token_manager 모두 업데이트)
        if 'access_token' in response and 'refresh_token' in response:
            access_token = response['access_token']
            refresh_token = response['refresh_token']
            
            # config에 저장
            config.access_token = access_token
            config.refresh_token = refresh_token
            
            # token_manager에 저장하여 권한 정보 파싱
            token_manager.set_tokens(access_token, refresh_token)
        
        return response
    
    def verify_token(self) -> Dict[str, Any]:
        """
        현재 액세스 토큰의 유효성을 확인합니다.
        
        Returns:
            토큰 검증 응답 데이터
            
        Raises:
            AuthenticationError: 토큰이 유효하지 않음
            APIException: API 에러 발생
        """
        return self.client.get('/auth/verify')
    
    def get_user_info(self) -> Dict[str, Any]:
        """
        현재 로그인한 사용자 정보를 가져옵니다.
        
        Returns:
            사용자 정보
            
        Raises:
            AuthenticationError: 인증 실패
            APIException: API 에러 발생
        """
        return self.client.get('/auth/me')
    
    def update_password(self, current_password: str, new_password: str) -> Dict[str, Any]:
        """
        비밀번호를 변경합니다.
        
        Args:
            current_password: 현재 비밀번호
            new_password: 새 비밀번호
            
        Returns:
            비밀번호 변경 응답 데이터
            
        Raises:
            AuthenticationError: 현재 비밀번호 불일치
            ValidationError: 새 비밀번호 검증 실패
            APIException: API 에러 발생
        """
        data = {
            'current_password': current_password,
            'new_password': new_password
        }
        
        return self.client.put('/auth/password', data=data)
    
    def request_password_reset(self, email: str) -> Dict[str, Any]:
        """
        비밀번호 재설정을 요청합니다.
        
        Args:
            email: 이메일 주소
            
        Returns:
            비밀번호 재설정 요청 응답 데이터
            
        Raises:
            ValidationError: 이메일 검증 실패
            APIException: API 에러 발생
        """
        data = {
            'email': email
        }
        
        return self.client.post('/auth/password-reset/request', data=data)
    
    def reset_password(self, token: str, new_password: str) -> Dict[str, Any]:
        """
        비밀번호를 재설정합니다.
        
        Args:
            token: 비밀번호 재설정 토큰
            new_password: 새 비밀번호
            
        Returns:
            비밀번호 재설정 응답 데이터
            
        Raises:
            AuthenticationError: 토큰이 유효하지 않음
            ValidationError: 새 비밀번호 검증 실패
            APIException: API 에러 발생
        """
        data = {
            'token': token,
            'new_password': new_password
        }
        
        return self.client.post('/auth/password-reset/confirm', data=data)
