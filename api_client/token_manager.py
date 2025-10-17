import jwt
import time
from typing import Dict, List, Optional, Any
from datetime import datetime


class Permission:
    """개별 권한 정보를 관리하는 클래스."""
    
    def __init__(self, name: str, exp: int):
        """
        Permission 초기화.
        
        Args:
            name: 권한 이름 (예: 'kream')
            exp: 만료 시간 (Unix timestamp)
        """
        self.name = name
        self.exp = exp
    
    def is_expired(self) -> bool:
        """권한이 만료되었는지 확인합니다."""
        return time.time() > self.exp
    
    def expires_in(self) -> int:
        """권한 만료까지 남은 시간(초)을 반환합니다."""
        return max(0, int(self.exp - time.time()))
    
    def __repr__(self) -> str:
        return f"Permission(name={self.name}, exp={self.exp}, expired={self.is_expired()})"


class TokenManager:
    """JWT 토큰을 관리하는 클래스."""
    
    def __init__(self):
        self._access_token: Optional[str] = None
        self._refresh_token: Optional[str] = None
        self._permissions: List[Permission] = []
        self._token_exp: Optional[int] = None
    
    def set_tokens(self, access_token: str, refresh_token: str) -> None:
        """
        토큰을 설정하고 권한 정보를 파싱합니다.
        
        Args:
            access_token: JWT 액세스 토큰
            refresh_token: 리프레시 토큰
        """
        self._access_token = access_token
        self._refresh_token = refresh_token
        self._parse_token()
    
    def _parse_token(self) -> None:
        """JWT 토큰을 파싱하여 권한 정보를 추출합니다."""
        if not self._access_token:
            return
        
        try:
            # JWT 토큰 디코딩 (서명 검증 없이 - 서버에서 이미 검증됨)
            payload = jwt.decode(
                self._access_token,
                options={"verify_signature": False}
            )
            
            # 토큰 만료 시간
            self._token_exp = payload.get('exp')
            
            # 권한 정보 파싱
            self._permissions = []
            permissions_data = payload.get('permissions', [])
            
            for perm_dict in permissions_data:
                for name, info in perm_dict.items():
                    exp = info.get('exp', 0)
                    self._permissions.append(Permission(name, exp))
        
        except Exception as e:
            print(f"토큰 파싱 오류: {e}")
            self._permissions = []
    
    @property
    def access_token(self) -> Optional[str]:
        """액세스 토큰을 반환합니다."""
        return self._access_token
    
    @property
    def refresh_token(self) -> Optional[str]:
        """리프레시 토큰을 반환합니다."""
        return self._refresh_token
    
    def get_permissions(self) -> List[Permission]:
        """권한 목록을 반환합니다."""
        return self._permissions.copy()
    
    def get_permission(self, name: str) -> Optional[Permission]:
        """특정 권한을 반환합니다."""
        for perm in self._permissions:
            if perm.name == name:
                return perm
        return None
    
    def has_permission(self, name: str) -> bool:
        """특정 권한이 있고 만료되지 않았는지 확인합니다."""
        perm = self.get_permission(name)
        return perm is not None and not perm.is_expired()
    
    def is_token_expired(self) -> bool:
        """토큰이 만료되었는지 확인합니다."""
        if not self._token_exp:
            return True
        return time.time() > self._token_exp
    
    def token_expires_in(self) -> int:
        """토큰 만료까지 남은 시간(초)을 반환합니다."""
        if not self._token_exp:
            return 0
        return max(0, int(self._token_exp - time.time()))
    
    def has_any_expired_permission(self) -> bool:
        """만료된 권한이 하나라도 있는지 확인합니다."""
        return any(perm.is_expired() for perm in self._permissions)
    
    def needs_refresh(self, buffer_seconds: int = 60) -> bool:
        """
        토큰 갱신이 필요한지 확인합니다.
        
        Args:
            buffer_seconds: 토큰 만료 전 미리 갱신할 버퍼 시간 (초)
                           권한 만료는 버퍼 없이 실제 만료 시간만 체크
        
        Returns:
            갱신이 필요하면 True
        """
        # 토큰 자체가 만료되었거나 곧 만료될 예정 (버퍼 적용)
        if self.token_expires_in() < buffer_seconds:
            return True
        
        # 권한 중 하나라도 실제로 만료됨 (버퍼 없음, 현재 시간 이후만 체크)
        for perm in self._permissions:
            if perm.is_expired():
                return True
        
        return False
    
    def clear(self) -> None:
        """모든 토큰과 권한 정보를 초기화합니다."""
        self._access_token = None
        self._refresh_token = None
        self._permissions = []
        self._token_exp = None
    
    def get_status(self) -> Dict[str, Any]:
        """현재 토큰 및 권한 상태를 반환합니다."""
        return {
            'has_token': self._access_token is not None,
            'token_expired': self.is_token_expired(),
            'token_expires_in': self.token_expires_in(),
            'permissions': [
                {
                    'name': perm.name,
                    'expired': perm.is_expired(),
                    'expires_in': perm.expires_in()
                }
                for perm in self._permissions
            ],
            'needs_refresh': self.needs_refresh()
        }


# 전역 토큰 매니저 인스턴스
token_manager = TokenManager()
