#!/usr/bin/env python3
"""
Desktop packaging script for AI Blogging Studio
Packages the application for distribution on 크몽
"""
import os
import shutil
import zipfile
from pathlib import Path
import subprocess

def create_package_directory():
    """Create the package directory structure"""
    package_dir = Path("AI_Blogging_Studio_Desktop_Package")
    if package_dir.exists():
        shutil.rmtree(package_dir)
    
    package_dir.mkdir()
    return package_dir

def copy_installer_files(package_dir):
    """Copy installer files to package directory"""
    dist_dir = Path("dist")
    
    if not dist_dir.exists():
        print("❌ Build files not found. Please run 'python build.py' first.")
        return False
    
    # Copy Windows installer
    exe_files = list(dist_dir.glob("*.exe"))
    if exe_files:
        shutil.copy2(exe_files[0], package_dir / "AI_Blogging_Studio_Setup.exe")
        print(f"✅ Copied: {exe_files[0].name}")
    
    # Copy Mac installer
    dmg_files = list(dist_dir.glob("*.dmg"))
    if dmg_files:
        shutil.copy2(dmg_files[0], package_dir / "AI_Blogging_Studio.dmg")
        print(f"✅ Copied: {dmg_files[0].name}")
    
    # Copy Linux installer
    appimage_files = list(dist_dir.glob("*.AppImage"))
    if appimage_files:
        shutil.copy2(appimage_files[0], package_dir / "AI_Blogging_Studio.AppImage")
        print(f"✅ Copied: {appimage_files[0].name}")
    
    return True

def create_documentation(package_dir):
    """Create Korean documentation for Kmong sales"""
    
    # 설치 가이드
    install_guide = """# AI 블로깅 스튜디오 설치 가이드

## 🚀 프로그램 소개
AI 블로깅 스튜디오는 YouTube 영상이나 주제를 입력하면 자동으로 블로그 포스트를 생성하고 여러 플랫폼에 발행하는 프로그램입니다.

## 📋 시스템 요구사항
- Windows 10 이상 (권장)
- 인터넷 연결 (AI 기능 사용 시)
- 4GB RAM 이상
- 500MB 하드디스크 여유공간

## 🔧 설치 방법

### Windows 설치
1. `AI_Blogging_Studio_Setup.exe` 파일을 더블클릭
2. 설치 마법사 안내에 따라 진행
3. 설치 완료 후 바탕화면 아이콘으로 실행

### 주의사항
- 처음 실행 시 Windows Defender 경고가 뜰 수 있습니다
- "추가 정보" → "실행" 버튼으로 실행하세요
- 백신 프로그램에서 예외 처리하시면 됩니다

## 🔑 초기 설정

### 1단계: Google API 키 발급
1. https://console.cloud.google.com 접속
2. 새 프로젝트 생성
3. "API 및 서비스" → "라이브러리"에서 다음 API 활성화:
   - Gemini API
   - YouTube Data API v3
   - Blogger API v3
4. "사용자 인증 정보"에서 API 키 생성

### 2단계: 프로그램에서 설정
1. 프로그램 실행 후 "설정" 메뉴
2. Google API 키 입력
3. 블로그 플랫폼 연동 설정

## 📝 사용법
1. YouTube URL 입력 또는 주제 작성
2. "블로그 포스트 생성" 버튼 클릭
3. 생성된 내용 확인 및 수정
4. 원하는 블로그 플랫폼에 발행

## 🛠️ 문제 해결
- 프로그램이 실행되지 않는 경우: 관리자 권한으로 실행
- AI 기능이 작동하지 않는 경우: 인터넷 연결 및 API 키 확인
- 블로그 발행이 안 되는 경우: 플랫폼 연동 설정 확인

구매해주셔서 감사합니다! 🎉
"""

    user_manual = """# AI 블로깅 스튜디오 사용자 매뉴얼

## 📖 목차
1. 프로그램 개요
2. 주요 기능
3. 단계별 사용법
4. 고급 설정
5. 문제 해결

## 1. 프로그램 개요

AI 블로깅 스튜디오는 콘텐츠 제작자를 위한 자동 블로깅 도구입니다.
- YouTube 영상을 블로그 포스트로 변환
- 주제만으로도 완전한 블로그 글 생성
- 여러 블로그 플랫폼 동시 발행
- SEO 최적화된 콘텐츠 생성

## 2. 주요 기능

### ✨ AI 콘텐츠 생성
- Google Gemini AI 모델 사용
- 자연스러운 한국어 블로그 포스트
- 이미지 자동 삽입
- 태그 및 카테고리 자동 생성

### 🔗 다중 플랫폼 연동
- Google Blogger 자동 발행
- WordPress.com 연동
- 네이버 블로그 API 지원
- Tistory 수동 복사 기능

### 📊 콘텐츠 관리
- 발행 이력 관리
- 임시저장 기능
- 콘텐츠 수정 및 재발행

## 3. 단계별 사용법

### 3-1. YouTube 영상에서 블로그 생성
1. 메인 화면에서 "YouTube URL" 입력란에 영상 링크 붙여넣기
2. "설정" 에서 원하는 톤앤매너 선택 (전문적, 친근한, 유머러스 등)
3. "블로그 포스트 생성" 버튼 클릭
4. AI가 영상 내용을 분석하여 블로그 포스트 생성
5. 생성된 내용 검토 및 필요시 수정
6. 원하는 플랫폼 선택하여 발행

### 3-2. 주제로 블로그 생성
1. "주제 입력" 탭 선택
2. 블로그 주제나 키워드 입력
3. 대상 독자층 설정 (일반인, 전문가, 학생 등)
4. "생성" 버튼으로 AI 블로그 작성
5. 결과 확인 및 발행

### 3-3. 이미지 자동 삽입
- Pexels API를 통한 저작권 무료 이미지 자동 검색
- 블로그 내용과 관련된 이미지 자동 선택
- 수동으로 이미지 교체 가능

## 4. 고급 설정

### 4-1. AI 모델 설정
- Gemini 1.5 Pro: 고품질, 느림
- Gemini 2.0 Flash: 빠름, 표준 품질
- 커스텀 프롬프트 설정 가능

### 4-2. SEO 최적화
- 자동 메타 태그 생성
- 키워드 밀도 조절
- 제목 최적화 옵션

### 4-3. 플랫폼별 설정
각 블로그 플랫폼의 고유 설정:
- 카테고리 매핑
- 태그 형식 설정
- 발행 시간 예약

## 5. 문제 해결

### 자주 묻는 질문

**Q: API 키는 어디서 발급받나요?**
A: Google Cloud Console (console.cloud.google.com)에서 무료로 발급 가능합니다.

**Q: 생성된 블로그 글이 이상해요.**
A: 설정에서 AI 모델을 변경하거나 프롬프트를 조정해보세요.

**Q: 블로그 발행이 실패해요.**
A: 각 플랫폼의 API 키와 권한 설정을 확인해주세요.

**Q: 프로그램이 느려요.**
A: 인터넷 연결 상태와 Google API 할당량을 확인해주세요.

### 오류 코드
- Error 401: API 키 인증 실패
- Error 403: API 사용량 초과
- Error 404: 블로그 주소 오류
- Error 500: 서버 오류

## 📞 지원

이 프로그램은 크몽에서 구매하신 상품입니다.
문의사항이 있으시면 크몽 메시지를 통해 연락주세요.

**즐거운 블로깅 되세요! 🎉**
"""

    license_text = """AI 블로깅 스튜디오 라이선스

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
"""
    
    # Write files
    (package_dir / "설치_가이드.txt").write_text(install_guide, encoding='utf-8')
    (package_dir / "사용자_매뉴얼.txt").write_text(user_manual, encoding='utf-8')
    (package_dir / "라이선스.txt").write_text(license_text, encoding='utf-8')
    
    print("✅ Documentation created")

def create_sales_package():
    """Create the final sales package for Kmong"""
    
    # Create README for the package
    readme_content = """# AI 블로깅 스튜디오 - 데스크톱 버전

## 🎯 크몽 판매용 패키지

이 폴더에는 고객에게 전달할 모든 파일이 포함되어 있습니다.

### 📦 포함 파일:
1. **AI_Blogging_Studio_Setup.exe** - Windows 설치 파일
2. **설치_가이드.txt** - 설치 방법 안내
3. **사용자_매뉴얼.txt** - 상세 사용법
4. **라이선스.txt** - 이용 약관

### 💰 판매 전략:
- **가격대**: 30,000원 ~ 50,000원
- **타겟**: 블로거, 유튜버, 마케터
- **강점**: 완전 자동화, 다중 플랫폼 지원

### 📋 고객 안내사항:
1. Windows 10 이상 필요
2. Google API 키 별도 발급 필요 (무료)
3. 인터넷 연결 필요 (AI 기능 사용 시)
4. 1년 무료 업데이트 제공

### 🛡️ A/S 정책:
- 설치 문제: 원격 지원
- 사용법 문의: 크몽 메시지 대응
- 버그 신고: 1주일 내 수정
- 기능 요청: 검토 후 업데이트

크몽에서 성공적인 판매 되시길 바랍니다! 🚀
"""
    
    package_dir = Path("AI_Blogging_Studio_Desktop_Package")
    (package_dir / "README_판매자용.txt").write_text(readme_content, encoding='utf-8')
    
    # Create ZIP file for easy distribution
    zip_path = "AI_Blogging_Studio_크몽판매용.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in package_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(package_dir.parent)
                zipf.write(file_path, arcname)
    
    print(f"✅ Sales package created: {zip_path}")

def main():
    """Main packaging process"""
    print("🎁 AI 블로깅 스튜디오 크몽 판매 패키지 생성 중...")
    
    try:
        # Create package directory
        package_dir = create_package_directory()
        print(f"📁 Package directory created: {package_dir}")
        
        # Copy installer files
        if not copy_installer_files(package_dir):
            print("❌ Please build the application first using 'python build.py'")
            return
        
        # Create documentation
        create_documentation(package_dir)
        
        # Create sales package
        create_sales_package()
        
        print("\n🎉 크몽 판매 패키지 완성!")
        print("📋 다음 단계:")
        print("1. AI_Blogging_Studio_크몽판매용.zip 파일 확인")
        print("2. 크몽에 상품 등록")
        print("3. 상품 설명에 기능 및 설치법 안내")
        print("4. 고객 구매 시 ZIP 파일 전달")
        
    except Exception as e:
        print(f"❌ 패키징 실패: {e}")

if __name__ == "__main__":
    main()