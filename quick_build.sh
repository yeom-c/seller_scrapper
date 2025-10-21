#!/bin/bash
# 빠른 빌드 테스트 (의존성 설치 스킵)

echo "======================================"
echo "빠른 빌드 테스트 (현재 환경 사용)"
echo "======================================"

# PyInstaller 확인
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller를 설치합니다..."
    pip install pyinstaller
fi

# 이전 빌드 정리
echo "이전 빌드 파일을 정리합니다..."
rm -rf build dist

# 빌드
echo "빌드를 시작합니다..."
pyinstaller build_config.spec --clean

# 결과
echo ""
echo "======================================"
if [ "$(uname)" == "Darwin" ]; then
    if [ -d "dist/SellerAutomation.app" ]; then
        echo "✅ 빌드 성공!"
        echo "실행: open dist/SellerAutomation.app"
    else
        echo "❌ 빌드 실패"
    fi
else
    if [ -f "dist/SellerAutomation/SellerAutomation" ]; then
        echo "✅ 빌드 성공!"
        echo "실행: cd dist/SellerAutomation && ./SellerAutomation"
    else
        echo "❌ 빌드 실패"
    fi
fi
echo "======================================"
