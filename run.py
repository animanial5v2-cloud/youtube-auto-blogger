#!/usr/bin/env python3
"""
YouTube to SEO Content Generator
유튜브 스크립트를 SEO 최적화된 콘텐츠로 변환하는 프로그램
"""

import os
import sys
from dotenv import load_dotenv

def check_dependencies():
    """필요한 패키지들이 설치되어 있는지 확인"""
    try:
        import flask
        import openai
        import requests
        from PIL import Image
        print("✅ 모든 의존성 패키지가 설치되어 있습니다.")
        return True
    except ImportError as e:
        print(f"❌ 필요한 패키지가 설치되지 않았습니다: {e}")
        print("다음 명령어로 설치해주세요:")
        print("pip install -r requirements.txt")
        return False

def check_openai_key():
    """OpenAI API 키가 설정되어 있는지 확인"""
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key or api_key == 'your-openai-api-key-here':
        print("❌ OpenAI API 키가 설정되지 않았습니다.")
        print("다음 중 하나의 방법으로 설정해주세요:")
        print("1. 환경 변수 설정: export OPENAI_API_KEY='your-key'")
        print("2. .env 파일 생성: echo 'OPENAI_API_KEY=your-key' > .env")
        return False
    
    print("✅ OpenAI API 키가 설정되어 있습니다.")
    return True

def main():
    """메인 실행 함수"""
    print("🎥 YouTube to SEO Content Generator")
    print("=" * 50)
    
    # 의존성 확인
    if not check_dependencies():
        sys.exit(1)
    
    # API 키 확인
    if not check_openai_key():
        sys.exit(1)
    
    print("\n🚀 웹 애플리케이션을 시작합니다...")
    print("브라우저에서 http://localhost:5000 으로 접속하세요.")
    print("종료하려면 Ctrl+C를 누르세요.")
    print("-" * 50)
    
    # 웹 애플리케이션 실행
    try:
        from web_app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 프로그램을 종료합니다.")
    except Exception as e:
        print(f"❌ 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    main()
