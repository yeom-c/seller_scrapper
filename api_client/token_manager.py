import jwt
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone


class Permission:
    """개별 권한 정보를 담는 데이터 클래스."""
    
    def __init__(self, name: str, exp: int, payment_type: str, type: str):
        self.name = name
        self.exp = exp
        self.payment_type = payment_type
        self.type = type
    
    def __repr__(self) -> str:
        return (f"Permission(name={self.name}, type={self.type}, "
                f"payment_type={self.payment_type}, exp={self.exp})")


class TokenManager:
    """
    JWT 토큰 및 권한을 관리하고, 서버 시간과 동기화된 시간 비교를 수행하는 클래스.
    """
    
    def __init__(self):
        self._access_token: Optional[str] = None
        self._refresh_token: Optional[str] = None
        self._permissions: List[Permission] = []
        self._token_exp: Optional[int] = None
        self._server_time_offset: float = 0.0
    
    def _get_current_timestamp(self) -> float:
        """서버 시간과 동기화된 현재 타임스탬프를 반환합니다."""
        return time.time() + self._server_time_offset

    def set_tokens(self, access_token: str, refresh_token: str) -> None:
        """
        토큰을 설정하고, 서버 시간과 동기화하며, 권한 정보를 파싱합니다.
        """
        self._access_token = access_token
        self._refresh_token = refresh_token
        self._parse_token()
    
    def _parse_token(self) -> None:
        """
        JWT 토큰을 파싱하여 만료 시간, 권한 정보, 서버 시간 오프셋을 추출합니다.
        """
        if not self._access_token:
            return
        
        try:
            payload = jwt.decode(self._access_token, options={"verify_signature": False})
            
            # 서버 시간과 로컬 시간의 오프셋 계산
            iat = payload.get('iat')
            if iat:
                self._server_time_offset = iat - time.time()
            
            self._token_exp = payload.get('exp')
            
            # 권한 정보 파싱
            self._permissions = []
            user_metadata = payload.get('user_metadata', {})
            permissions_data = user_metadata.get('permissions', [])
            
            for perm_data in permissions_data:
                name = perm_data.get('name')
                expires_at_str = perm_data.get('expires_at')
                payment_type = perm_data.get('payment_type')
                perm_type = perm_data.get('type')

                if name and expires_at_str and payment_type and perm_type:
                    dt_obj = datetime.fromisoformat(expires_at_str)
                    exp_timestamp = int(dt_obj.timestamp())
                    self._permissions.append(
                        Permission(name, exp_timestamp, payment_type, perm_type)
                    )
        
        except Exception as e:
            print(f"토큰 파싱 오류: {e}")
            self._permissions = []
            self._server_time_offset = 0.0
    
    @property
    def access_token(self) -> Optional[str]:
        return self._access_token
    
    @property
    def refresh_token(self) -> Optional[str]:
        return self._refresh_token
    
    def get_permissions(self) -> List[Permission]:
        return self._permissions.copy()
    
    def get_permission(self, perm_type: str) -> Optional[Permission]:
        """특정 타입의 권한을 반환합니다."""
        for perm in self._permissions:
            if perm.type.lower() == perm_type.lower():
                return perm
        return None

    def is_permission_expired(self, permission: Permission) -> bool:
        """특정 권한이 만료되었는지 확인합니다."""
        if not permission:
            return True
        return self._get_current_timestamp() > permission.exp

    def permission_expires_in(self, permission: Permission) -> int:
        """특정 권한의 만료까지 남은 시간(초)을 반환합니다."""
        if not permission:
            return 0
        return max(0, int(permission.exp - self._get_current_timestamp()))

    def has_permission(self, perm_type: str) -> bool:
        """특정 타입의 권한이 있고 만료되지 않았는지 확인합니다."""
        perm = self.get_permission(perm_type)
        return perm is not None and not self.is_permission_expired(perm)
    
    def is_token_expired(self) -> bool:
        """토큰이 만료되었는지 확인합니다."""
        if not self._token_exp:
            return True
        return self._get_current_timestamp() > self._token_exp
    
    def token_expires_in(self) -> int:
        """토큰 만료까지 남은 시간(초)을 반환합니다."""
        if not self._token_exp:
            return 0
        return max(0, int(self._token_exp - self._get_current_timestamp()))
    
    def has_any_expired_permission(self) -> bool:
        """만료된 권한이 하나라도 있는지 확인합니다."""
        return any(self.is_permission_expired(perm) for perm in self._permissions)
    
    def needs_refresh(self, buffer_seconds: int = 60) -> bool:
        """토큰 갱신이 필요한지 확인합니다."""
        if self.token_expires_in() < buffer_seconds:
            return True
        
        for perm in self._permissions:
            if self.is_permission_expired(perm):
                return True
        
        return False
    
    def clear(self) -> None:
        """모든 토큰과 권한 정보를 초기화합니다."""
        self._access_token = None
        self._refresh_token = None
        self._permissions = []
        self._token_exp = None
        self._server_time_offset = 0.0
    
    def get_status(self) -> Dict[str, Any]:
        """현재 토큰 및 권한 상태를 반환합니다."""
        return {
            'has_token': self._access_token is not None,
            'token_expired': self.is_token_expired(),
            'token_expires_in': self.token_expires_in(),
            'permissions': [
                {
                    'name': perm.name,
                    'type': perm.type,
                    'expired': self.is_permission_expired(perm),
                    'expires_in': self.permission_expires_in(perm)
                }
                for perm in self._permissions
            ],
            'needs_refresh': self.needs_refresh()
        }


# 전역 토큰 매니저 인스턴스
token_manager = TokenManager()
