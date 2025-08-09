import requests
import json
import re
from datetime import datetime
import os
from typing import Dict, List, Optional
import openai
from PIL import Image, ImageDraw, ImageFont
import io
import base64

class YouTubeToSEOContent:
    def __init__(self, openai_api_key: str):
        """유튜브 스크립트를 SEO 최적화된 콘텐츠로 변환하는 클래스"""
        self.openai_api_key = openai_api_key
        openai.api_key = openai_api_key
        
    def extract_youtube_id(self, url: str) -> str:
        """유튜브 URL에서 비디오 ID 추출"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/v\/([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        raise ValueError("유효한 유튜브 URL이 아닙니다.")
    
    def get_video_info(self, video_id: str) -> Dict:
        """유튜브 비디오 정보 가져오기 (YouTube Data API 사용)"""
        # 실제 구현에서는 YouTube Data API 키가 필요합니다
        # 여기서는 예시 데이터를 반환합니다
        return {
            "title": "샘플 비디오 제목",
            "description": "샘플 비디오 설명",
            "duration": "10:30",
            "view_count": "10000",
            "like_count": "500"
        }
    
    def analyze_script(self, script_text: str) -> Dict:
        """스크립트 분석하여 키워드, 주제, 구조 추출"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 SEO 전문가입니다. 유튜브 스크립트를 분석하여 다음 정보를 추출해주세요:"
                    },
                    {
                        "role": "user",
                        "content": f"""
                        다음 스크립트를 분석하여 SEO 최적화된 블로그 포스트를 위한 정보를 추출해주세요:
                        
                        {script_text}
                        
                        다음 형식으로 JSON 응답해주세요:
                        {{
                            "main_keywords": ["키워드1", "키워드2", "키워드3"],
                            "long_tail_keywords": ["롱테일 키워드1", "롱테일 키워드2"],
                            "main_topic": "주요 주제",
                            "sub_topics": ["서브 주제1", "서브 주제2"],
                            "target_audience": "타겟 독자",
                            "content_structure": ["섹션1", "섹션2", "섹션3"],
                            "seo_title": "SEO 최적화된 제목",
                            "meta_description": "메타 설명"
                        }}
                        """
                    }
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            print(f"스크립트 분석 중 오류: {e}")
            return self._get_default_analysis()
    
    def generate_seo_content(self, analysis: Dict, script_text: str) -> Dict:
        """SEO 최적화된 블로그 포스트 생성"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 SEO 최적화된 블로그 포스트 작성 전문가입니다."
                    },
                    {
                        "role": "user",
                        "content": f"""
                        다음 분석 결과를 바탕으로 SEO 최적화된 블로그 포스트를 작성해주세요:
                        
                        분석 결과: {json.dumps(analysis, ensure_ascii=False)}
                        원본 스크립트: {script_text[:1000]}...
                        
                        다음 형식으로 작성해주세요:
                        1. SEO 최적화된 제목
                        2. 메타 설명
                        3. 도입부 (독자의 관심을 끌 수 있는)
                        4. 주요 내용 (H2, H3 태그 포함)
                        5. 결론
                        6. 관련 키워드
                        7. 내부/외부 링크 제안
                        
                        HTML 형식으로 작성해주세요.
                        """
                    }
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            return {
                "html_content": response.choices[0].message.content,
                "analysis": analysis
            }
            
        except Exception as e:
            print(f"콘텐츠 생성 중 오류: {e}")
            return self._get_default_content(analysis)
    
    def generate_images(self, analysis: Dict, content: str) -> List[str]:
        """콘텐츠에 맞는 이미지 생성 (DALL-E 사용)"""
        images = []
        
        try:
            # 메인 이미지 생성
            main_prompt = f"SEO 최적화된 블로그 포스트용 이미지: {analysis.get('main_topic', '')}"
            
            response = openai.Image.create(
                prompt=main_prompt,
                n=1,
                size="1024x1024"
            )
            
            images.append(response['data'][0]['url'])
            
            # 추가 이미지들 생성
            for i, sub_topic in enumerate(analysis.get('sub_topics', [])[:3]):
                sub_prompt = f"블로그 포스트 섹션 이미지: {sub_topic}"
                
                response = openai.Image.create(
                    prompt=sub_prompt,
                    n=1,
                    size="512x512"
                )
                
                images.append(response['data'][0]['url'])
                
        except Exception as e:
            print(f"이미지 생성 중 오류: {e}")
            # 기본 이미지 생성
            images = self._generate_default_images(analysis)
        
        return images
    
    def create_social_media_content(self, analysis: Dict, content: str) -> Dict:
        """소셜미디어용 콘텐츠 생성"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "소셜미디어 마케팅 전문가입니다."
                    },
                    {
                        "role": "user",
                        "content": f"""
                        다음 콘텐츠를 바탕으로 소셜미디어용 포스트를 생성해주세요:
                        
                        주제: {analysis.get('main_topic', '')}
                        키워드: {analysis.get('main_keywords', [])}
                        
                        다음 플랫폼별로 작성해주세요:
                        1. Instagram (해시태그 포함)
                        2. Twitter (280자 이내)
                        3. LinkedIn (전문적 톤)
                        4. Facebook
                        
                        JSON 형식으로 응답해주세요.
                        """
                    }
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            print(f"소셜미디어 콘텐츠 생성 중 오류: {e}")
            return self._get_default_social_content(analysis)
    
    def generate_full_package(self, youtube_url: str, script_text: str) -> Dict:
        """전체 SEO 패키지 생성"""
        print("🔍 유튜브 URL 분석 중...")
        video_id = self.extract_youtube_id(youtube_url)
        video_info = self.get_video_info(video_id)
        
        print("📝 스크립트 분석 중...")
        analysis = self.analyze_script(script_text)
        
        print("✍️ SEO 콘텐츠 생성 중...")
        content = self.generate_seo_content(analysis, script_text)
        
        print("🎨 이미지 생성 중...")
        images = self.generate_images(analysis, content['html_content'])
        
        print("📱 소셜미디어 콘텐츠 생성 중...")
        social_content = self.create_social_media_content(analysis, content['html_content'])
        
        return {
            "video_info": video_info,
            "analysis": analysis,
            "seo_content": content,
            "images": images,
            "social_media": social_content,
            "generated_at": datetime.now().isoformat()
        }
    
    def save_to_files(self, package: Dict, output_dir: str = "seo_output"):
        """결과를 파일로 저장"""
        os.makedirs(output_dir, exist_ok=True)
        
        # HTML 파일 저장
        with open(f"{output_dir}/blog_post.html", "w", encoding="utf-8") as f:
            f.write(package['seo_content']['html_content'])
        
        # 분석 결과 JSON 저장
        with open(f"{output_dir}/analysis.json", "w", encoding="utf-8") as f:
            json.dump(package['analysis'], f, ensure_ascii=False, indent=2)
        
        # 소셜미디어 콘텐츠 저장
        with open(f"{output_dir}/social_media.json", "w", encoding="utf-8") as f:
            json.dump(package['social_media'], f, ensure_ascii=False, indent=2)
        
        # 이미지 URL 저장
        with open(f"{output_dir}/images.txt", "w", encoding="utf-8") as f:
            for i, img_url in enumerate(package['images']):
                f.write(f"Image {i+1}: {img_url}\n")
        
        print(f"✅ 모든 파일이 {output_dir} 폴더에 저장되었습니다!")
    
    def _get_default_analysis(self) -> Dict:
        """기본 분석 결과"""
        return {
            "main_keywords": ["키워드1", "키워드2"],
            "long_tail_keywords": ["롱테일 키워드"],
            "main_topic": "주요 주제",
            "sub_topics": ["서브 주제1", "서브 주제2"],
            "target_audience": "일반 독자",
            "content_structure": ["도입", "본문", "결론"],
            "seo_title": "SEO 최적화된 제목",
            "meta_description": "메타 설명"
        }
    
    def _get_default_content(self, analysis: Dict) -> Dict:
        """기본 콘텐츠"""
        return {
            "html_content": f"""
            <h1>{analysis.get('seo_title', '제목')}</h1>
            <p>{analysis.get('meta_description', '설명')}</p>
            <h2>도입</h2>
            <p>도입 내용...</p>
            <h2>본문</h2>
            <p>본문 내용...</p>
            <h2>결론</h2>
            <p>결론 내용...</p>
            """,
            "analysis": analysis
        }
    
    def _get_default_social_content(self, analysis: Dict) -> Dict:
        """기본 소셜미디어 콘텐츠"""
        return {
            "instagram": f"📱 {analysis.get('main_topic', '주제')} #키워드1 #키워드2",
            "twitter": f"🔍 {analysis.get('main_topic', '주제')}에 대해 알아보세요!",
            "linkedin": f"💼 {analysis.get('main_topic', '주제')}에 대한 전문적인 분석",
            "facebook": f"📖 {analysis.get('main_topic', '주제')}에 대한 자세한 내용"
        }
    
    def _generate_default_images(self, analysis: Dict) -> List[str]:
        """기본 이미지 URL (실제로는 더 나은 방법 필요)"""
        return [
            "https://via.placeholder.com/1024x1024/007bff/ffffff?text=Main+Image",
            "https://via.placeholder.com/512x512/28a745/ffffff?text=Section+1",
            "https://via.placeholder.com/512x512/dc3545/ffffff?text=Section+2"
        ]

# 사용 예시
def main():
    # OpenAI API 키 설정 (실제 사용시 필요)
    OPENAI_API_KEY = "your-openai-api-key-here"
    
    # 프로그램 초기화
    converter = YouTubeToSEOContent(OPENAI_API_KEY)
    
    # 사용자 입력
    print("🎥 유튜브 스크립트를 SEO 콘텐츠로 변환하는 프로그램")
    print("=" * 50)
    
    youtube_url = input("유튜브 URL을 입력하세요: ")
    print("\n스크립트를 입력하세요 (입력 완료 후 Ctrl+D 또는 Ctrl+Z):")
    
    script_lines = []
    try:
        while True:
            line = input()
            script_lines.append(line)
    except (EOFError, KeyboardInterrupt):
        pass
    
    script_text = "\n".join(script_lines)
    
    if not script_text.strip():
        print("❌ 스크립트가 입력되지 않았습니다.")
        return
    
    # SEO 패키지 생성
    print("\n🚀 SEO 패키지 생성 중...")
    package = converter.generate_full_package(youtube_url, script_text)
    
    # 파일로 저장
    converter.save_to_files(package)
    
    print("\n🎉 완료! 생성된 파일들을 확인해보세요:")
    print("- blog_post.html: SEO 최적화된 블로그 포스트")
    print("- analysis.json: 키워드 및 분석 결과")
    print("- social_media.json: 소셜미디어용 콘텐츠")
    print("- images.txt: 생성된 이미지 URL들")

if __name__ == "__main__":
    main()
