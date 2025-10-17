# API 클라이언트 사용 가이드

## 개요

이 프로젝트는 서버와의 통신을 위한 깔끔하고 확장 가능한 API 클라이언트 구조를 제공합니다.

## 구조

```
api_client/
├── __init__.py          # 패키지 초기화 및 공개 인터페이스
├── config.py            # API 설정 관리
├── client.py            # 기본 HTTP 클라이언트
├── auth.py              # 인증 관련 API
└── exceptions.py        # 커스텀 예외 클래스들
```

## 주요 컴포넌트

### 1. APIClient (client.py)
기본 HTTP 통신을 처리하는 클라이언트 클래스입니다.

**기능:**
- GET, POST, PUT, DELETE 메서드 지원
- 자동 재시도 (지수 백오프)
- 토큰 기반 인증 자동 처리
- 상태 코드별 에러 핸들링
- 타임아웃 관리

### 2. AuthAPI (auth.py)
인증 관련 API를 처리하는 클래스입니다.

**제공 메서드:**
- `register()` - 회원가입
- `login()` - 로그인
- `logout()` - 로그아웃
- `refresh_token()` - 토큰 갱신
- `verify_token()` - 토큰 검증
- `get_user_info()` - 사용자 정보 조회
- `update_password()` - 비밀번호 변경
- `request_password_reset()` - 비밀번호 재설정 요청
- `reset_password()` - 비밀번호 재설정

### 3. APIConfig (config.py)
API 설정을 관리하는 클래스입니다.

**주요 설정:**
- `base_url` - API 서버 주소
- `timeout` - 요청 타임아웃
- `max_retries` - 최대 재시도 횟수
- `access_token` - 액세스 토큰
- `refresh_token` - 리프레시 토큰

### 4. 예외 클래스 (exceptions.py)
API 에러를 명확하게 구분하는 예외 클래스들입니다.

- `APIException` - 기본 API 예외
- `AuthenticationError` - 인증 실패 (401, 403)
- `ValidationError` - 입력 검증 실패 (400)
- `NetworkError` - 네트워크 연결 실패
- `ServerError` - 서버 에러 (500번대)
- `NotFoundError` - 리소스 없음 (404)

## 사용 예시

### 기본 설정

```python
from api_client import config

# API 서버 주소 설정
config.base_url = "https://api.example.com/v1"

# 타임아웃 설정 (초)
config.timeout = 30

# 최대 재시도 횟수 설정
config.max_retries = 3
```

### 환경 변수로 설정

`.env` 파일 또는 시스템 환경 변수로 설정 가능:

```bash
API_BASE_URL=https://api.example.com/v1
API_TIMEOUT=30
API_MAX_RETRIES=3
```

### 회원가입

```python
from api_client import AuthAPI, ValidationError, APIException

auth_api = AuthAPI()

try:
    response = auth_api.register(
        email="user@example.com",
        password="secure_password123"
    )
    print(f"회원가입 성공: {response}")
    
except ValidationError as e:
    print(f"입력 오류: {e.message}")
    
except APIException as e:
    print(f"회원가입 실패: {e.message}")
```

### 로그인

```python
from api_client import AuthAPI, AuthenticationError

auth_api = AuthAPI()

try:
    response = auth_api.login(
        email="user@example.com",
        password="secure_password123"
    )
    
    # 토큰은 자동으로 config에 저장됩니다
    print(f"로그인 성공: {response}")
    
except AuthenticationError as e:
    print(f"로그인 실패: {e.message}")
```

### 인증이 필요한 API 호출

로그인 후에는 자동으로 Authorization 헤더가 추가됩니다:

```python
from api_client import AuthAPI

auth_api = AuthAPI()

# 로그인 후
auth_api.login(email="user@example.com", password="password")

# 사용자 정보 조회 (자동으로 토큰 포함)
user_info = auth_api.get_user_info()
print(f"사용자 정보: {user_info}")
```

### 커스텀 API 엔드포인트 호출

```python
from api_client import APIClient

client = APIClient()

# GET 요청
data = client.get('/users', params={'page': 1, 'limit': 10})

# POST 요청
response = client.post('/items', data={'name': 'New Item', 'price': 100})

# PUT 요청
response = client.put('/items/1', data={'price': 150})

# DELETE 요청
response = client.delete('/items/1')
```

### 에러 핸들링

```python
from api_client import (
    AuthAPI,
    AuthenticationError,
    ValidationError,
    NetworkError,
    ServerError,
    APIException
)

auth_api = AuthAPI()

try:
    response = auth_api.login(email="user@example.com", password="wrong")
    
except AuthenticationError as e:
    print(f"인증 실패: {e.message}")
    print(f"상태 코드: {e.status_code}")
    print(f"응답 데이터: {e.response_data}")
    
except ValidationError as e:
    print(f"입력 오류: {e.message}")
    
except NetworkError as e:
    print(f"네트워크 오류: {e.message}")
    
except ServerError as e:
    print(f"서버 오류: {e.message}")
    
except APIException as e:
    print(f"알 수 없는 오류: {e.message}")
```

### 토큰 관리

```python
from api_client import config, AuthAPI

# 토큰 확인
if config.has_valid_token():
    print("로그인 상태입니다")

# 토큰 갱신
auth_api = AuthAPI()
try:
    response = auth_api.refresh_token()
    print("토큰이 갱신되었습니다")
except AuthenticationError:
    print("토큰 갱신 실패, 다시 로그인해주세요")

# 로그아웃 (토큰 제거)
auth_api.logout()
```

## 새로운 API 엔드포인트 추가하기

### 1. 새 API 클래스 생성

`api_client/workflow.py` 예시:

```python
from typing import Dict, Any, Optional, List
from .client import APIClient


class WorkflowAPI:
    """워크플로우 관련 API를 처리하는 클래스."""
    
    def __init__(self, client: Optional[APIClient] = None):
        self.client = client or APIClient()
    
    def get_workflows(self) -> List[Dict[str, Any]]:
        """사용자의 워크플로우 목록을 가져옵니다."""
        return self.client.get('/workflows')
    
    def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """특정 워크플로우를 가져옵니다."""
        return self.client.get(f'/workflows/{workflow_id}')
    
    def create_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """새 워크플로우를 생성합니다."""
        return self.client.post('/workflows', data=workflow_data)
    
    def update_workflow(
        self,
        workflow_id: str,
        workflow_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """워크플로우를 수정합니다."""
        return self.client.put(f'/workflows/{workflow_id}', data=workflow_data)
    
    def delete_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """워크플로우를 삭제합니다."""
        return self.client.delete(f'/workflows/{workflow_id}')
```

### 2. __init__.py에 추가

```python
from .workflow import WorkflowAPI

__all__ = [
    # ... 기존 항목들
    'WorkflowAPI',
]
```

### 3. 사용

```python
from api_client import WorkflowAPI

workflow_api = WorkflowAPI()

# 워크플로우 목록 조회
workflows = workflow_api.get_workflows()

# 새 워크플로우 생성
new_workflow = workflow_api.create_workflow({
    'name': 'My Workflow',
    'steps': [...]
})
```

## 테스트

```python
# 간단한 연결 테스트
from api_client import APIClient, config

# 테스트 서버 설정
config.base_url = "http://localhost:8000/api"

client = APIClient()

try:
    # 헬스 체크 엔드포인트 호출 (서버에 있다고 가정)
    response = client.get('/health')
    print("서버 연결 성공:", response)
except Exception as e:
    print("서버 연결 실패:", e)
```

## 주의사항

1. **토큰 보안**: 토큰은 메모리에만 저장됩니다. 앱을 재시작하면 다시 로그인해야 합니다.
2. **HTTPS 사용**: 프로덕션 환경에서는 반드시 HTTPS를 사용하세요.
3. **에러 핸들링**: 모든 API 호출은 try-except로 감싸서 에러를 적절히 처리하세요.
4. **타임아웃**: 네트워크 상황에 따라 타임아웃 값을 조정하세요.

## 확장 가능성

이 구조는 다음과 같은 확장이 쉽습니다:

- 새로운 API 엔드포인트 추가
- 인증 방식 변경 (OAuth, API Key 등)
- 응답 캐싱
- 요청 로깅
- 멀티파트 파일 업로드
- WebSocket 지원

필요에 따라 각 클래스를 상속하거나 확장하여 기능을 추가할 수 있습니다.
