from typing import Dict, Any
from .supabase_client import supabase
from .token_manager import token_manager


def register(email: str, password: str) -> Dict[str, Any]:
    """
    회원가입을 수행합니다.
    
    Args:
        email: 이메일 주소
        password: 비밀번호 (최소 8자)
        
    Returns:
        {"success": True, "message": "회원가입이 완료되었습니다."}
        또는 {"success": False, "message": "오류 메시지"}
    """
    try:
        # Supabase Auth 회원가입
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        
        if response.user:
            return {
                "success": True,
                "message": "회원가입이 완료되었습니다.",
                "user_id": response.user.id
            }
        else:
            return {
                "success": False,
                "message": "회원가입에 실패했습니다."
            }
            
    except Exception as e:
        error_msg = str(e)
        if "already registered" in error_msg.lower():
            return {"success": False, "message": "이미 가입된 이메일입니다."}
        return {"success": False, "message": "회원가입 중 오류가 발생했습니다."}


def login(email: str, password: str) -> Dict[str, Any]:
    """
    로그인을 수행합니다.
    
    Args:
        email: 이메일 주소
        password: 비밀번호
        
    Returns:
        {"success": True} 또는 {"success": False, "message": "오류 메시지"}
    """
    try:
        # Supabase Auth 로그인
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response.session:
            # 토큰 저장
            token_manager.set_tokens(
                access_token=response.session.access_token,
                refresh_token=response.session.refresh_token
            )
            
            return {"success": True}
        else:
            return {"success": False, "message": "로그인에 실패했습니다."}
            
    except Exception as e:
        error_msg = str(e)
        if "invalid" in error_msg.lower():
            return {"success": False, "message": "이메일 또는 비밀번호가 올바르지 않습니다."}
        return {"success": False, "message": "로그인 중 오류가 발생했습니다."}


def logout() -> Dict[str, Any]:
    """
    로그아웃을 수행합니다.
    
    Returns:
        {"success": True, "message": "로그아웃되었습니다."}
    """
    try:
        # Supabase 로그아웃
        supabase.auth.sign_out()
        
        # 로컬 토큰 제거
        token_manager.clear()
        
        return {"success": True, "message": "로그아웃되었습니다."}
        
    except Exception as e:
        # 로그아웃 실패해도 로컬 토큰은 제거
        token_manager.clear()
        return {"success": True, "message": "로그아웃되었습니다."}


def refresh_token() -> Dict[str, Any]:
    """
    액세스 토큰을 갱신합니다.
    
    Returns:
        {"success": True} 또는 {"success": False, "message": "오류 메시지"}
    """
    try:
        # 현재 세션 갱신
        response = supabase.auth.refresh_session()
        
        if response.session:
            # 새 토큰 저장
            token_manager.set_tokens(
                access_token=response.session.access_token,
                refresh_token=response.session.refresh_token
            )
            
            return {"success": True}
        else:
            return {"success": False, "message": "토큰 갱신에 실패했습니다."}
            
    except Exception as e:
        return {"success": False, "message": "토큰 갱신 중 오류가 발생했습니다."}

