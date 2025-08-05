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
    icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else None,
)
'''
    
    with open('AI_Blogging_Studio.spec', 'w') as f:
        f.write(spec_content)
    print("✅ Spec file created")

def convert_icon():
    """Convert SVG icon to ICO format"""
    try:
        from PIL import Image
        import cairosvg
        import io
        
        svg_path = Path('assets/icon.svg')
        ico_path = Path('assets/icon.ico')
        
        if svg_path.exists():
            # Convert SVG to PNG first
            png_data = cairosvg.svg2png(url=str(svg_path), output_width=256, output_height=256)
            
            # Convert PNG to ICO
            image = Image.open(io.BytesIO(png_data))
            image.save(ico_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
            print("✅ Icon converted to ICO format")
            return True
    except ImportError:
        print("⚠️ PIL/cairosvg not available, skipping icon conversion")
    except Exception as e:
        print(f"⚠️ Icon conversion failed: {e}")
    
    return False

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

def create_installer_script():
    """Create NSIS installer script"""
    nsis_script = '''!define APP_NAME "AI Blogging Studio"
!define APP_VERSION "1.0.0"
!define APP_PUBLISHER "AI Blogging Studio"
!define APP_URL "https://github.com/ai-blogging-studio"
!define APP_EXE "AI_Blogging_Studio.exe"

!include "MUI2.nsh"

Name "${APP_NAME}"
OutFile "AI_Blogging_Studio_Setup.exe"
InstallDir "$PROGRAMFILES\\${APP_NAME}"
InstallDirRegKey HKCU "Software\\${APP_NAME}" ""
RequestExecutionLevel admin

!define MUI_ABORTWARNING
!define MUI_ICON "assets\\icon.ico"
!define MUI_UNICON "assets\\icon.ico"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "Korean"

Section "MainSection" SEC01
  SetOutPath "$INSTDIR"
  File "dist\\${APP_EXE}"
  CreateDirectory "$SMPROGRAMS\\${APP_NAME}"
  CreateShortCut "$SMPROGRAMS\\${APP_NAME}\\${APP_NAME}.lnk" "$INSTDIR\\${APP_EXE}"
  CreateShortCut "$DESKTOP\\${APP_NAME}.lnk" "$INSTDIR\\${APP_EXE}"
  WriteRegStr HKCU "Software\\${APP_NAME}" "" $INSTDIR
  WriteUninstaller "$INSTDIR\\Uninstall.exe"
SectionEnd

Section "Uninstall"
  Delete "$INSTDIR\\${APP_EXE}"
  Delete "$INSTDIR\\Uninstall.exe"
  Delete "$SMPROGRAMS\\${APP_NAME}\\${APP_NAME}.lnk"
  Delete "$DESKTOP\\${APP_NAME}.lnk"
  RMDir "$SMPROGRAMS\\${APP_NAME}"
  RMDir "$INSTDIR"
  DeleteRegKey /ifempty HKCU "Software\\${APP_NAME}"
SectionEnd
'''
    
    with open('installer.nsi', 'w', encoding='utf-8') as f:
        f.write(nsis_script)
    print("✅ NSIS installer script created")

def create_license():
    """Create license file"""
    license_text = '''AI 블로깅 스튜디오 라이선스

이 소프트웨어를 사용함으로써 다음 조건에 동의하는 것으로 간주됩니다:

1. 개인적 용도로의 사용이 허가됩니다.
2. 상업적 목적의 블로그 운영에 사용할 수 있습니다.
3. 소프트웨어의 재배포는 금지됩니다.
4. 소스 코드의 리버스 엔지니어링은 금지됩니다.

이 소프트웨어는 "있는 그대로" 제공되며, 명시적이거나 묵시적인 
어떠한 보증도 제공하지 않습니다.

Copyright (c) 2024 AI Blogging Studio
'''
    
    with open('LICENSE.txt', 'w', encoding='utf-8') as f:
        f.write(license_text)
    print("✅ License file created")

def main():
    """Main build process"""
    print("🚀 AI 블로깅 스튜디오 EXE 빌드 시작")
    print("=" * 50)
    
    # Change to desktop-app directory
    os.chdir(Path(__file__).parent)
    
    # Install PyInstaller
    if not install_pyinstaller():
        return False
    
    # Install required packages
    print("📦 Installing required packages...")
    packages = [
        "flask", "flask-sqlalchemy", "requests", 
        "google-generativeai", "youtube-transcript-api",
        "email-validator", "pillow", "cairosvg"
    ]
    
    for package in packages:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", package], 
                         check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print(f"⚠️ Failed to install {package}, continuing...")
    
    # Convert icon
    convert_icon()
    
    # Create spec file
    create_spec_file()
    
    # Create license
    create_license()
    
    # Build EXE
    if build_exe():
        create_installer_script()
        print("\n🎉 빌드 완료!")
        print("📋 생성된 파일:")
        print("  • dist/AI_Blogging_Studio.exe (메인 실행 파일)")
        print("  • installer.nsi (설치 프로그램 스크립트)")
        print("\n💡 사용 방법:")
        print("  1. AI_Blogging_Studio.exe를 실행하세요")
        print("  2. '서버 시작' 버튼을 클릭하세요")  
        print("  3. 자동으로 브라우저가 열립니다")
        print("\n📦 NSIS로 설치 프로그램을 만들려면:")
        print("  makensis installer.nsi")
        return True
    else:
        print("❌ 빌드 실패")
        return False

if __name__ == "__main__":
    main()