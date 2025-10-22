#!/bin/bash
# macOS/Linux 빌드 스크립트

set -e  # 에러 발생 시 즉시 중단

echo "======================================"
echo "Seller Scrapper 빌드 시작"
echo "======================================"

# Python 실행 파일 경로 확인
PYTHON_PATH="/Users/yeomc/.pyenv/versions/3.13.7/bin/python"

if [ ! -f "$PYTHON_PATH" ]; then
    echo "❌ Python을 찾을 수 없습니다: $PYTHON_PATH"
    echo "pyenv를 사용하여 Python 3.13.7을 설치해주세요."
    exit 1
fi

echo "✓ Python 경로: $PYTHON_PATH"

# 2. 의존성 확인
echo "의존성을 확인합니다..."
$PYTHON_PATH -m pip install --upgrade pip --quiet
$PYTHON_PATH -m pip install -r requirements.txt --quiet
$PYTHON_PATH -m pip install pyinstaller --quiet

# 3. 이전 빌드 정리
echo "이전 빌드 파일을 정리합니다..."
rm -rf build dist
# build_config.spec을 제외한 다른 .spec 파일들 삭제
find . -maxdepth 1 -name "*.spec" ! -name "build_config.spec" -type f -delete

# 4. PyInstaller로 빌드
echo "PyInstaller로 빌드를 시작합니다..."
$PYTHON_PATH -m PyInstaller build_config.spec

# 5. 결과 확인
echo ""
echo "======================================"
echo "빌드 완료!"
echo "======================================"

if [ "$(uname)" == "Darwin" ]; then
    # macOS
    if [ -d "dist/SellerAutomation.app" ]; then
        echo "✅ macOS 앱 번들 생성 완료: dist/SellerAutomation.app"
        echo ""
        echo "실행 방법:"
        echo "  open dist/SellerAutomation.app"
    fi
else
    # Linux
    if [ -f "dist/SellerAutomation/SellerAutomation" ]; then
        echo "✅ Linux 실행 파일 생성 완료: dist/SellerAutomation/"
        echo ""
        echo "실행 방법:"
        echo "  cd dist/SellerAutomation"
        echo "  ./SellerAutomation"
    fi
fi

echo ""
echo "Output 폴더는 실행 파일과 같은 디렉토리에 생성됩니다."
