#!/usr/bin/env python3
"""
Build script to create standalone EXE file for AI Blogging Studio
"""
import os
import sys
import subprocess
from pathlib import Path
import shutil

def install_pyinstaller():
    """Install PyInstaller if not available"""
    try:
        import PyInstaller
        print("✅ PyInstaller already installed")
        return True
    except ImportError:
        print("📦 Installing PyInstaller...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
            print("✅ PyInstaller installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install PyInstaller")
            return False

def create_spec_file():
    """Create PyInstaller spec file"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['standalone_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('server', 'server'),
        ('assets', 'assets'),
    ],
    hiddenimports=[
        'flask',
        'flask_sqlalchemy',
        'sqlalchemy',
        'werkzeug',
        'requests',
        'google.generativeai',
        'youtube_transcript_api',
        'email_validator',
    ],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AI_Blogging_Studio',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    with open('AI_Blogging_Studio.spec', 'w') as f:
        f.write(spec_content)
    print("✅ Spec file created")

def build_exe():
    """Build the EXE file"""
    print("🔨 Building EXE file...")
    
    try:
        # Run PyInstaller
        subprocess.run([
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            "AI_Blogging_Studio.spec"
        ], check=True)
        
        print("✅ EXE build completed!")
        
        # Check if file was created
        exe_path = Path("dist/AI_Blogging_Studio.exe")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"📁 EXE file created: {exe_path}")
            print(f"📊 File size: {size_mb:.1f} MB")
            return True
        else:
            print("❌ EXE file not found after build")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False

def create_license():
    """Create license file"""
    license_text = '''AI 블로깅 스튜디오 라이선스

Copyright (c) 2024 AI Blogging Studio

본 소프트웨어는 구매자에게 다음 권리를 부여합니다:

✅ 허용사항:
- 개인적 용도로 무제한 사용
- 상업적 목적의 블로그 운영
- 여러 대의 컴퓨터에 설치 (구매자 본인만)

❌ 금지사항:
- 소프트웨어 재판매 또는 배포
- 리버스 엔지니어링
- 소스 코드 추출 시도
- 타인에게 라이선스 키 공유

⚠️ 책임 제한:
- 본 소프트웨어는 "있는 그대로" 제공됩니다
- 생성된 콘텐츠의 저작권은 사용자에게 있습니다
- AI 생성 콘텐츠의 정확성을 보장하지 않습니다
- 외부 API 서비스 중단에 대한 책임을 지지 않습니다

🔄 업데이트:
- 무료 업데이트 1년 제공
- 주요 기능 개선 및 버그 수정 포함

문의: 크몽 메시지를 통해 연락 가능

구매해주셔서 감사합니다!
'''
    
    with open('LICENSE.txt', 'w', encoding='utf-8') as f:
        f.write(license_text)
    print("✅ License file created")

def main():
    """Main build process"""
    print("🚀 AI 블로깅 스튜디오 EXE 빌드 시작")
    print("=" * 50)
    
    # Install PyInstaller
    if not install_pyinstaller():
        return False
    
    # Install required packages
    print("📦 Installing required packages...")
    packages = [
        "flask", "flask-sqlalchemy", "requests", 
        "google-generativeai", "youtube-transcript-api",
        "email-validator"
    ]
    
    for package in packages:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", package], 
                         check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print(f"⚠️ Failed to install {package}, continuing...")
    
    # Create spec file
    create_spec_file()
    
    # Create license
    create_license()
    
    # Build EXE
    if build_exe():
        print("\n🎉 빌드 완료!")
        print("📋 생성된 파일:")
        print("  • dist/AI_Blogging_Studio.exe (메인 실행 파일)")
        print("\n💡 사용 방법:")
        print("  1. AI_Blogging_Studio.exe를 실행하세요")
        print("  2. '서버 시작' 버튼을 클릭하세요")  
        print("  3. 자동으로 브라우저가 열립니다")
        return True
    else:
        print("❌ 빌드 실패")
        return False

if __name__ == "__main__":
    main()