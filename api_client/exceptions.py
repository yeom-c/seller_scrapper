"""API 예외 클래스들."""


class APIException(Exception):
    """API 관련 기본 예외 클래스."""
    
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
        super().__init__(self.message)


class AuthenticationError(APIException):
    """인증 관련 예외 (401, 403)."""
    pass


class ValidationError(APIException):
    """유효성 검사 실패 예외 (400)."""
    pass


class NetworkError(APIException):
    """네트워크 연결 실패 예외."""
    pass


class ServerError(APIException):
    """서버 에러 예외 (500번대)."""
    pass


class NotFoundError(APIException):
    """리소스를 찾을 수 없음 (404)."""
    pass
