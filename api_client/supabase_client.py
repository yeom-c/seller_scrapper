from supabase import create_client, Client
from .config import config


class SupabaseClient:
    """Supabase 클라이언트 싱글톤"""
    _instance: Client = None
    
    @classmethod
    def get_client(cls) -> Client:
        """Supabase 클라이언트 인스턴스를 반환합니다."""
        if cls._instance is None:
            supabase_url = config.supabase_url
            supabase_key = config.supabase_anon_key
            
            if not supabase_url or not supabase_key:
                raise ValueError(
                    "SUPABASE_URL과 SUPABASE_ANON_KEY 환경 변수가 필요합니다."
                )
            
            cls._instance = create_client(supabase_url, supabase_key)
        
        return cls._instance

# 전역 클라이언트 인스턴스
supabase = SupabaseClient.get_client()
