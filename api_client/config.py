import os
from typing import Optional


class APIConfig:
    """API 설정을 관리하는 클래스."""
    
    # Supabase 기본 설정
    DEFAULT_SUPABASE_URL = "https://poeslenmqbamnxzvyanz.supabase.co"
    DEFAULT_SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBvZXNsZW5tcWJhbW54enZ5YW56Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA4Nzk3OTMsImV4cCI6MjA3NjQ1NTc5M30.Dspj3qFIR46kgCkPSkbDFRflqKVz0CdsA6y3Cq2z7WA"
    
    def __init__(self):
        # Supabase 설정
        self._supabase_url: str = os.getenv("SUPABASE_URL", self.DEFAULT_SUPABASE_URL)
        self._supabase_anon_key: str = os.getenv("SUPABASE_ANON_KEY", self.DEFAULT_SUPABASE_ANON_KEY)
        
        # 토큰 관리
        self._access_token: Optional[str] = None
        self._refresh_token: Optional[str] = None
    
    @property
    def supabase_url(self) -> str:
        """Supabase URL을 반환합니다."""
        return self._supabase_url
    
    @supabase_url.setter
    def supabase_url(self, value: str) -> None:
        """Supabase URL을 설정합니다."""
        self._supabase_url = value.rstrip('/')
    
    @property
    def supabase_anon_key(self) -> str:
        """Supabase Anon Key를 반환합니다."""
        return self._supabase_anon_key
    
    @supabase_anon_key.setter
    def supabase_anon_key(self, value: str) -> None:
        """Supabase Anon Key를 설정합니다."""
        self._supabase_anon_key = value
    
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
