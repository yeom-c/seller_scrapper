@echo off
REM Windows 빌드 스크립트

echo ======================================
echo Seller Scrapper 빌드 시작
echo ======================================

REM 1. 가상환경 확인
if not exist "venv" (
    echo 가상환경을 생성합니다...
    python -m venv venv
)

REM 가상환경 활성화
echo 가상환경을 활성화합니다...
call venv\Scripts\activate.bat

REM 2. 의존성 설치
echo 의존성을 설치합니다...
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

REM 3. 이전 빌드 정리
echo 이전 빌드 파일을 정리합니다...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
REM build_config.spec을 제외한 다른 .spec 파일들 삭제
for %%f in (*.spec) do (
    if not "%%f"=="build_config.spec" del /q "%%f"
)

REM 4. PyInstaller로 빌드
echo PyInstaller로 빌드를 시작합니다...
pyinstaller build_config.spec

REM 5. 결과 확인
echo.
echo ======================================
echo 빌드 완료!
echo ======================================

if exist "dist\SellerAutomation\SellerAutomation.exe" (
    echo ✅ Windows 실행 파일 생성 완료: dist\SellerAutomation\
    echo.
    echo 실행 방법:
    echo   cd dist\SellerAutomation
    echo   SellerAutomation.exe
    echo.
    echo 또는 dist\SellerAutomation 폴더를 통째로 복사하여 사용할 수 있습니다.
) else (
    echo ❌ 빌드 실패! 에러 로그를 확인하세요.
)

echo.
echo Output 폴더는 실행 파일과 같은 디렉토리에 생성됩니다.
pause
