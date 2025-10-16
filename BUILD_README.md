# Seller Scrapper 빌드 가이드

이 문서는 Windows와 macOS에서 실행 가능한 독립 실행 파일을 생성하는 방법을 설명합니다.

## 📋 준비 사항

### 공통
- Python 3.8 이상 설치
- 프로젝트 소스 코드

### Windows
- Python이 PATH에 등록되어 있어야 합니다
- Visual C++ Redistributable (보통 이미 설치되어 있음)

### macOS
- Xcode Command Line Tools 설치 권장
  ```bash
  xcode-select --install
  ```

## 🚀 빌드 방법

### macOS / Linux

1. 터미널에서 프로젝트 디렉토리로 이동
   ```bash
   cd /path/to/seller_scrapper
   ```

2. 빌드 스크립트 실행 권한 부여
   ```bash
   chmod +x build.sh
   ```

3. 빌드 실행
   ```bash
   ./build.sh
   ```

4. 빌드 완료 후 실행
   ```bash
   # macOS
   open dist/SellerScrapper.app
   
   # Linux
   cd dist/SellerScrapper
   ./SellerScrapper
   ```

### Windows

1. 명령 프롬프트(CMD) 또는 PowerShell에서 프로젝트 디렉토리로 이동
   ```cmd
   cd C:\path\to\seller_scrapper
   ```

2. 빌드 스크립트 실행
   ```cmd
   build.bat
   ```

3. 빌드 완료 후 실행
   ```cmd
   cd dist\SellerScrapper
   SellerScrapper.exe
   ```

## 📦 수동 빌드 (고급)

자동 스크립트를 사용하지 않고 수동으로 빌드하려면:

```bash
# 1. 가상환경 생성 및 활성화
python -m venv venv

# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate

# 2. 의존성 설치
pip install -r requirements.txt
pip install pyinstaller

# 3. 빌드
pyinstaller build_config.spec
```

## 📁 빌드 결과물

### macOS
```
dist/
└── SellerScrapper.app/          # 더블클릭으로 실행 가능한 앱 번들
```

### Windows / Linux
```
dist/
└── SellerScrapper/
    ├── SellerScrapper.exe       # Windows 실행 파일
    ├── SellerScrapper           # Linux 실행 파일
    ├── workflows/               # 워크플로우 설정 파일들
    └── [기타 의존성 파일들]
```

## 🎯 배포 방법

### macOS
1. `dist/SellerScrapper.app`을 압축
2. 사용자에게 전달
3. 사용자는 압축 해제 후 앱을 Applications 폴더로 이동

### Windows
1. `dist/SellerScrapper` 폴더 전체를 압축
2. 사용자에게 전달
3. 사용자는 원하는 위치에 압축 해제 후 `SellerScrapper.exe` 실행

### Linux
1. `dist/SellerScrapper` 폴더 전체를 압축
2. 사용자에게 전달
3. 사용자는 압축 해제 후 실행 권한 부여:
   ```bash
   chmod +x SellerScrapper
   ./SellerScrapper
   ```

## ⚙️ 빌드 설정 커스터마이징

`build_config.spec` 파일을 수정하여 빌드 옵션을 변경할 수 있습니다:

### 아이콘 추가
```python
# Windows용
icon='icon.ico'

# macOS용
icon='icon.icns'
```

아이콘 파일을 프로젝트 루트에 배치하고 spec 파일의 `icon=None` 부분을 수정하세요.

### 콘솔 창 표시 (디버그용)
```python
console=True  # False에서 True로 변경
```

### Single File 빌드 (모든 것을 하나의 실행 파일로)
```python
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,      # 추가
    a.zipfiles,      # 추가
    a.datas,         # 추가
    [],
    exclude_binaries=False,  # True에서 False로 변경
    name='SellerScrapper',
    # ... 나머지 옵션
)

# COLLECT 섹션 주석 처리
# coll = COLLECT(...)
```

## 🔧 문제 해결

### "No module named ..." 에러
- `build_config.spec`의 `hiddenimports` 리스트에 해당 모듈 추가

### Chrome WebDriver 관련 오류
- 실행 파일은 webdriver-manager가 자동으로 ChromeDriver를 다운로드합니다
- 인터넷 연결이 필요합니다 (첫 실행 시)

### macOS에서 "앱이 손상되었습니다" 메시지
```bash
# 보안 속성 제거
xattr -cr dist/SellerScrapper.app
```

### Windows Defender 경고
- PyInstaller로 생성된 실행 파일은 때때로 오탐지될 수 있습니다
- 예외 추가하거나 코드 서명 인증서 사용을 고려하세요

## 📝 참고사항

1. **파일 크기**: 빌드된 앱은 Python 인터프리터와 모든 의존성을 포함하므로 크기가 큽니다 (약 100-200MB)

2. **Output 폴더**: 프로그램 실행 시 생성되는 `output/` 폴더는 실행 파일과 같은 디렉토리에 생성됩니다

3. **업데이트**: 코드 변경 후 반드시 다시 빌드해야 합니다

4. **테스트**: 빌드 후 반드시 실제 환경에서 테스트하세요

## 🆘 추가 도움말

PyInstaller 공식 문서: https://pyinstaller.org/

문제가 계속되면 빌드 로그를 확인하세요:
- `build.log` (자동 생성됨)
- 콘솔 출력 메시지
