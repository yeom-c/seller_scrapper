import json
import time
from typing import Any, Dict, Optional, Union
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from urllib.parse import urlencode

from .config import config
from .exceptions import (
    APIException,
    AuthenticationError,
    NetworkError,
    ValidationError,
    ServerError,
    NotFoundError
)


class APIClient:
    """API 통신을 위한 기본 클라이언트 클래스."""
    
    def __init__(self, base_url: Optional[str] = None):
        """
        APIClient 초기화.
        
        Args:
            base_url: API 베이스 URL (None인 경우 config에서 가져옴)
        """
        self.base_url = base_url or config.base_url
        self.timeout = config.timeout
        self.max_retries = config.max_retries
    
    def _build_url(self, endpoint: str) -> str:
        """
        전체 URL을 구성합니다.
        
        Args:
            endpoint: API 엔드포인트
            
        Returns:
            전체 URL
        """
        endpoint = endpoint.lstrip('/')
        return f"{self.base_url}/{endpoint}"
    
    def _get_headers(self, custom_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        요청 헤더를 구성합니다.
        
        Args:
            custom_headers: 추가 헤더
            
        Returns:
            헤더 딕셔너리
        """
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        
        # 액세스 토큰이 있으면 Authorization 헤더 추가
        if config.access_token:
            headers['Authorization'] = f'Bearer {config.access_token}'
        
        # 커스텀 헤더 병합
        if custom_headers:
            headers.update(custom_headers)
        
        return headers
    
    def _handle_response(self, response_data: bytes, status_code: int) -> Any:
        """
        응답을 처리합니다.
        
        Args:
            response_data: 응답 데이터
            status_code: HTTP 상태 코드
            
        Returns:
            파싱된 응답 데이터
            
        Raises:
            APIException: API 에러 발생 시
        """
        try:
            data = json.loads(response_data.decode('utf-8')) if response_data else {}
        except json.JSONDecodeError:
            data = {'raw_response': response_data.decode('utf-8', errors='ignore')}
        
        # 상태 코드별 에러 처리
        if 200 <= status_code < 300:
            return data
        elif status_code == 400:
            raise ValidationError(
                data.get('message', '잘못된 요청입니다.'),
                status_code=status_code,
                response_data=data
            )
        elif status_code == 401:
            raise AuthenticationError(
                data.get('message', '인증이 필요합니다.'),
                status_code=status_code,
                response_data=data
            )
        elif status_code == 403:
            raise AuthenticationError(
                data.get('message', '접근 권한이 없습니다.'),
                status_code=status_code,
                response_data=data
            )
        elif status_code == 404:
            raise NotFoundError(
                data.get('message', '요청한 리소스를 찾을 수 없습니다.'),
                status_code=status_code,
                response_data=data
            )
        elif 500 <= status_code < 600:
            raise ServerError(
                data.get('message', '서버 오류가 발생했습니다.'),
                status_code=status_code,
                response_data=data
            )
        else:
            raise APIException(
                data.get('message', f'알 수 없는 오류가 발생했습니다. (상태 코드: {status_code})'),
                status_code=status_code,
                response_data=data
            )
    
    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        retry_count: int = 0
    ) -> Any:
        """
        HTTP 요청을 수행합니다.
        
        Args:
            method: HTTP 메서드 (GET, POST, PUT, DELETE 등)
            endpoint: API 엔드포인트
            data: 요청 바디 데이터
            params: 쿼리 파라미터
            headers: 추가 헤더
            retry_count: 현재 재시도 횟수
            
        Returns:
            응답 데이터
            
        Raises:
            NetworkError: 네트워크 연결 실패
            APIException: API 에러 발생
        """
        url = self._build_url(endpoint)
        
        # 쿼리 파라미터 추가
        if params:
            url = f"{url}?{urlencode(params)}"
        
        # 요청 헤더 구성
        request_headers = self._get_headers(headers)
        
        # 요청 바디 인코딩
        request_data = None
        if data is not None:
            request_data = json.dumps(data).encode('utf-8')
        
        try:
            request = Request(
                url,
                data=request_data,
                headers=request_headers,
                method=method.upper()
            )
            
            with urlopen(request, timeout=self.timeout) as response:
                response_data = response.read()
                return self._handle_response(response_data, response.status)
                
        except HTTPError as e:
            # HTTP 에러 응답 처리
            response_data = e.read()
            return self._handle_response(response_data, e.code)
            
        except URLError as e:
            # 네트워크 에러 처리 - 재시도 로직
            if retry_count < self.max_retries:
                wait_time = min(2 ** retry_count, config.retry_max_delay)
                time.sleep(wait_time)
                return self._request(method, endpoint, data, params, headers, retry_count + 1)
            
            raise NetworkError(
                f'네트워크 연결에 실패했습니다: {str(e)}',
                response_data={'original_error': str(e)}
            )
        
        except Exception as e:
            raise APIException(
                f'요청 처리 중 오류가 발생했습니다: {str(e)}',
                response_data={'original_error': str(e)}
            )
    
    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Any:
        """
        GET 요청을 수행합니다.
        
        Args:
            endpoint: API 엔드포인트
            params: 쿼리 파라미터
            headers: 추가 헤더
            
        Returns:
            응답 데이터
        """
        return self._request('GET', endpoint, params=params, headers=headers)
    
    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Any:
        """
        POST 요청을 수행합니다.
        
        Args:
            endpoint: API 엔드포인트
            data: 요청 바디 데이터
            headers: 추가 헤더
            
        Returns:
            응답 데이터
        """
        return self._request('POST', endpoint, data=data, headers=headers)
    
    def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Any:
        """
        PUT 요청을 수행합니다.
        
        Args:
            endpoint: API 엔드포인트
            data: 요청 바디 데이터
            headers: 추가 헤더
            
        Returns:
            응답 데이터
        """
        return self._request('PUT', endpoint, data=data, headers=headers)
    
    def delete(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None
    ) -> Any:
        """
        DELETE 요청을 수행합니다.
        
        Args:
            endpoint: API 엔드포인트
            headers: 추가 헤더
            
        Returns:
            응답 데이터
        """
        return self._request('DELETE', endpoint, headers=headers)
