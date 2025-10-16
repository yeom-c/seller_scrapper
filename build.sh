#!/bin/bash
# macOS/Linux 빌드 스크립트

set -e  # 에러 발생 시 즉시 중단

echo "======================================"
echo "Seller Scrapper 빌드 시작"
echo "======================================"

# 1. 가상환경 확인
if [ ! -d "venv" ]; then
    echo "가상환경을 생성합니다..."
    python3 -m venv venv
fi

# 가상환경 활성화
echo "가상환경을 활성화합니다..."
source venv/bin/activate

# 2. 의존성 설치
echo "의존성을 설치합니다..."
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

# 3. 이전 빌드 정리
echo "이전 빌드 파일을 정리합니다..."
rm -rf build dist
# build_config.spec을 제외한 다른 .spec 파일들 삭제
find . -maxdepth 1 -name "*.spec" ! -name "build_config.spec" -type f -delete

# 4. PyInstaller로 빌드
echo "PyInstaller로 빌드를 시작합니다..."
pyinstaller build_config.spec

# 5. 결과 확인
echo ""
echo "======================================"
echo "빌드 완료!"
echo "======================================"

if [ "$(uname)" == "Darwin" ]; then
    # macOS
    if [ -d "dist/SellerScrapper.app" ]; then
        echo "✅ macOS 앱 번들 생성 완료: dist/SellerScrapper.app"
        echo ""
        echo "실행 방법:"
        echo "  open dist/SellerScrapper.app"
    fi
else
    # Linux
    if [ -f "dist/SellerScrapper/SellerScrapper" ]; then
        echo "✅ Linux 실행 파일 생성 완료: dist/SellerScrapper/"
        echo ""
        echo "실행 방법:"
        echo "  cd dist/SellerScrapper"
        echo "  ./SellerScrapper"
    fi
fi

echo ""
echo "Output 폴더는 실행 파일과 같은 디렉토리에 생성됩니다."
