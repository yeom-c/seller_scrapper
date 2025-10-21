# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller 빌드 설정 파일
Windows와 macOS용 실행 파일 생성

사용법:
  pyinstaller build_config.spec
"""

import sys
from pathlib import Path

block_cipher = None

# 프로젝트 루트 디렉토리
root_dir = Path(SPECPATH)

# 아이콘 파일 경로 설정
icon_file = None
if sys.platform == 'win32':
    icon_file = str(root_dir / 'icon.ico')
elif sys.platform == 'darwin':
    icon_file = str(root_dir / 'icon.icns')

# 데이터 파일 및 폴더 수집
datas = []

# 숨겨진 imports (동적으로 로드되는 모듈)
hiddenimports = [
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'selenium',
    'selenium.webdriver',
    'selenium.webdriver.common.by',
    'selenium.webdriver.chrome.service',
    'selenium.webdriver.support.ui',
    'selenium.webdriver.support.expected_conditions',
    'selenium.common.exceptions',
    'bs4',
    'pandas',
    'webdriver_manager',
    'webdriver_manager.chrome',
]

a = Analysis(
    ['main.py'],
    pathex=[str(root_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SellerAutomation',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI 앱이므로 콘솔 숨김
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file,  # 플랫폼에 맞는 아이콘 자동 적용
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SellerAutomation',
)

# macOS 전용: .app 번들 생성
if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='SellerAutomation.app',
        icon=str(root_dir / 'icon.icns'),  # macOS용 아이콘
        bundle_identifier='com.SellerAutomation.app',
        info_plist={
            'NSHighResolutionCapable': 'True',
            'LSBackgroundOnly': 'False',
        },
    )
