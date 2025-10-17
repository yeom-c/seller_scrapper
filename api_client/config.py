import os
from typing import Optional


class APIConfig:
    """API 설정을 관리하는 클래스."""
    
    # 기본 설정값
    DEFAULT_BASE_URL = "http://localhost:8000/api"
    DEFAULT_TIMEOUT = 10
    DEFAULT_MAX_RETRIES = 2
    DEFAULT_RETRY_MAX_DELAY = 3  # 재시도 최대 대기 시간 (초)
    
    def __init__(self):
        self._base_url: str = os.getenv("API_BASE_URL", self.DEFAULT_BASE_URL)
        self._timeout: int = int(os.getenv("API_TIMEOUT", str(self.DEFAULT_TIMEOUT)))
        self._max_retries: int = int(os.getenv("API_MAX_RETRIES", str(self.DEFAULT_MAX_RETRIES)))
        self._retry_max_delay: int = int(os.getenv("API_RETRY_MAX_DELAY", str(self.DEFAULT_RETRY_MAX_DELAY)))
        self._access_token: Optional[str] = None
        self._refresh_token: Optional[str] = None
    
    @property
    def base_url(self) -> str:
        """API 베이스 URL을 반환합니다."""
        return self._base_url
    
    @base_url.setter
    def base_url(self, value: str) -> None:
        """API 베이스 URL을 설정합니다."""
        self._base_url = value.rstrip('/')
    
    @property
    def timeout(self) -> int:
        """타임아웃 값을 반환합니다."""
        return self._timeout
    
    @timeout.setter
    def timeout(self, value: int) -> None:
        """타임아웃 값을 설정합니다."""
        self._timeout = value
    
    @property
    def max_retries(self) -> int:
        """최대 재시도 횟수를 반환합니다."""
        return self._max_retries
    
    @max_retries.setter
    def max_retries(self, value: int) -> None:
        """최대 재시도 횟수를 설정합니다."""
        self._max_retries = value
    
    @property
    def retry_max_delay(self) -> int:
        """재시도 최대 대기 시간을 반환합니다."""
        return self._retry_max_delay
    
    @retry_max_delay.setter
    def retry_max_delay(self, value: int) -> None:
        """재시도 최대 대기 시간을 설정합니다."""
        self._retry_max_delay = value
    
    @property
    def access_token(self) -> Optional[str]:
        """액세스 토큰을 반환합니다."""
        return self._access_token
    
    @access_token.setter
    def access_token(self, value: Optional[str]) -> None:
        """액세스 토큰을 설정합니다."""
        self._access_token = value
    
    @property
    def refresh_token(self) -> Optional[str]:
        """리프레시 토큰을 반환합니다."""
        return self._refresh_token
    
    @refresh_token.setter
    def refresh_token(self, value: Optional[str]) -> None:
        """리프레시 토큰을 설정합니다."""
        self._refresh_token = value
    
    def clear_tokens(self) -> None:
        """저장된 토큰들을 초기화합니다."""
        self._access_token = None
        self._refresh_token = None
    
    def has_valid_token(self) -> bool:
        """유효한 토큰이 있는지 확인합니다."""
        return self._access_token is not None


# 전역 설정 인스턴스
config = APIConfig()
