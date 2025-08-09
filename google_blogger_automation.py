import os
import json
import re
from datetime import datetime
from typing import Dict, List, Optional
import openai
import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
from dotenv import load_dotenv

class GoogleBloggerAutomation:
    def __init__(self, openai_api_key: str):
        """구글 블로그 자동화 클래스"""
        self.openai_api_key = openai_api_key
        openai.api_key = openai_api_key
        
        # 구글 블로그 API 설정
        self.SCOPES = ['https://www.googleapis.com/auth/blogger']
        self.creds = None
        self.blogger_service = None
        
        # 인증 및 서비스 초기화
        self._authenticate_google()
    
    def _authenticate_google(self):
        """구글 API 인증"""
        # 토큰 파일이 있으면 로드
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        
        # 유효한 인증 정보가 없으면 새로 생성
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                # client_secrets.json 파일이 필요합니다
                if not os.path.exists('client_secrets.json'):
                    print("❌ client_secrets.json 파일이 필요합니다.")
                    print("구글 클라우드 콘솔에서 Blogger API를 활성화하고 OAuth 2.0 클라이언트 ID를 다운로드하세요.")
                    return
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    'client_secrets.json', self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # 토큰 저장
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)
        
        # Blogger 서비스 생성
        self.blogger_service = build('blogger', 'v3', credentials=self.creds)
    
    def get_blog_info(self, blog_id: str = None) -> Dict:
        """블로그 정보 가져오기"""
        try:
            if blog_id:
                blog = self.blogger_service.blogs().get(blogId=blog_id).execute()
            else:
                # 사용자의 블로그 목록 가져오기
                blogs = self.blogger_service.blogs().listByUser(userId='self').execute()
                if blogs.get('items'):
                    blog = blogs['items'][0]  # 첫 번째 블로그 사용
                else:
                    return {"error": "블로그를 찾을 수 없습니다."}
            
            return {
                "blog_id": blog['id'],
                "name": blog['name'],
                "url": blog['url'],
                "description": blog.get('description', ''),
                "published": blog['published']
            }
        except Exception as e:
            return {"error": f"블로그 정보 가져오기 실패: {str(e)}"}
    
    def analyze_youtube_script(self, script_text: str) -> Dict:
        """유튜브 스크립트 분석하여 블로그 포스팅 구조 생성"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 구글 블로그 포스트 작성 전문가입니다. 유튜브 스크립트를 분석하여 SEO 최적화된 블로그 포스트를 작성해주세요."
                    },
                    {
                        "role": "user",
                        "content": f"""
                        다음 유튜브 스크립트를 분석하여 구글 블로그용 포스트를 작성해주세요:
                        
                        {script_text}
                        
                        다음 형식으로 JSON 응답해주세요:
                        {{
                            "title": "SEO 최적화된 제목",
                            "content": "HTML 형식의 블로그 포스트 내용",
                            "labels": ["태그1", "태그2", "태그3"],
                            "seo_description": "메타 설명",
                            "keywords": ["키워드1", "키워드2"],
                            "category": "카테고리",
                            "reading_time": "예상 읽기 시간"
                        }}
                        
                        HTML 내용은 다음을 포함해야 합니다:
                        - H1, H2, H3 태그
                        - 이미지 플레이스홀더
                        - 관련 링크
                        - 결론
                        """
                    }
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            print(f"스크립트 분석 중 오류: {e}")
            return self._get_default_blog_post(script_text)
    
    def create_blog_post(self, blog_id: str, post_data: Dict) -> Dict:
        """블로그 포스트 생성"""
        try:
            post_body = {
                'kind': 'blogger#post',
                'title': post_data['title'],
                'content': post_data['content'],
                'labels': post_data.get('labels', []),
                'blog': {
                    'id': blog_id
                }
            }
            
            # 포스트 생성
            post = self.blogger_service.posts().insert(
                blogId=blog_id,
                body=post_body,
                isDraft=False  # 바로 발행
            ).execute()
            
            return {
                "success": True,
                "post_id": post['id'],
                "url": post['url'],
                "title": post['title'],
                "published": post['published']
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"포스트 생성 실패: {str(e)}"
            }
    
    def create_draft_post(self, blog_id: str, post_data: Dict) -> Dict:
        """초안으로 블로그 포스트 생성"""
        try:
            post_body = {
                'kind': 'blogger#post',
                'title': post_data['title'],
                'content': post_data['content'],
                'labels': post_data.get('labels', []),
                'blog': {
                    'id': blog_id
                }
            }
            
            # 초안으로 포스트 생성
            post = self.blogger_service.posts().insert(
                blogId=blog_id,
                body=post_body,
                isDraft=True  # 초안으로 저장
            ).execute()
            
            return {
                "success": True,
                "post_id": post['id'],
                "draft_url": f"https://www.blogger.com/blogger.g?blogID={blog_id}#editor/target=post;postID={post['id']}",
                "title": post['title']
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"초안 생성 실패: {str(e)}"
            }
    
    def generate_images_for_post(self, post_data: Dict) -> List[str]:
        """포스트용 이미지 생성 (DALL-E)"""
        images = []
        
        try:
            # 메인 이미지 생성
            main_prompt = f"블로그 포스트 메인 이미지: {post_data.get('title', '')}"
            
            response = openai.Image.create(
                prompt=main_prompt,
                n=1,
                size="1024x1024"
            )
            
            images.append(response['data'][0]['url'])
            
            # 섹션별 이미지 생성
            content = post_data.get('content', '')
            sections = re.findall(r'<h[23][^>]*>(.*?)</h[23]>', content)
            
            for i, section in enumerate(sections[:3]):  # 최대 3개 섹션
                section_prompt = f"블로그 포스트 섹션 이미지: {section}"
                
                response = openai.Image.create(
                    prompt=section_prompt,
                    n=1,
                    size="512x512"
                )
                
                images.append(response['data'][0]['url'])
                
        except Exception as e:
            print(f"이미지 생성 중 오류: {e}")
            # 기본 이미지 URL
            images = [
                "https://via.placeholder.com/1024x1024/007bff/ffffff?text=Blog+Image",
                "https://via.placeholder.com/512x512/28a745/ffffff?text=Section+1",
                "https://via.placeholder.com/512x512/dc3545/ffffff?text=Section+2"
            ]
        
        return images
    
    def update_post_with_images(self, blog_id: str, post_id: str, images: List[str]) -> Dict:
        """포스트에 이미지 추가"""
        try:
            # 이미지 URL을 HTML에 삽입
            image_html = ""
            for i, img_url in enumerate(images):
                image_html += f'<img src="{img_url}" alt="Blog Image {i+1}" style="max-width: 100%; height: auto; margin: 20px 0;">'
            
            # 포스트 업데이트
            post_body = {
                'content': f'{image_html}<br><br>'
            }
            
            updated_post = self.blogger_service.posts().update(
                blogId=blog_id,
                postId=post_id,
                body=post_body
            ).execute()
            
            return {
                "success": True,
                "message": "이미지가 추가되었습니다."
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"이미지 추가 실패: {str(e)}"
            }
    
    def generate_full_blog_post(self, youtube_url: str, script_text: str, blog_id: str = None, publish_mode: str = "draft") -> Dict:
        """전체 블로그 포스트 생성 프로세스"""
        print("🔍 유튜브 스크립트 분석 중...")
        
        # 스크립트 분석
        post_data = self.analyze_youtube_script(script_text)
        
        print("📝 블로그 포스트 생성 중...")
        
        # 블로그 정보 가져오기
        blog_info = self.get_blog_info(blog_id)
        if "error" in blog_info:
            return {"error": blog_info["error"]}
        
        # 포스트 생성
        if publish_mode == "draft":
            result = self.create_draft_post(blog_info["blog_id"], post_data)
        else:
            result = self.create_blog_post(blog_info["blog_id"], post_data)
        
        if not result["success"]:
            return result
        
        print("🎨 이미지 생성 중...")
        
        # 이미지 생성
        images = self.generate_images_for_post(post_data)
        
        # 이미지 추가
        if images:
            self.update_post_with_images(blog_info["blog_id"], result["post_id"], images)
        
        return {
            "success": True,
            "blog_info": blog_info,
            "post_data": post_data,
            "result": result,
            "images": images,
            "generated_at": datetime.now().isoformat()
        }
    
    def _get_default_blog_post(self, script_text: str) -> Dict:
        """기본 블로그 포스트 데이터"""
        return {
            "title": "유튜브 스크립트 기반 블로그 포스트",
            "content": f"""
            <h1>유튜브 스크립트 기반 블로그 포스트</h1>
            <p>이 포스트는 유튜브 스크립트를 분석하여 생성되었습니다.</p>
            
            <h2>주요 내용</h2>
            <p>{script_text[:500]}...</p>
            
            <h2>결론</h2>
            <p>더 자세한 내용은 원본 유튜브 영상을 확인해보세요.</p>
            """,
            "labels": ["유튜브", "스크립트", "블로그"],
            "seo_description": "유튜브 스크립트를 분석하여 생성된 블로그 포스트입니다.",
            "keywords": ["유튜브", "스크립트", "블로그"],
            "category": "일반",
            "reading_time": "3분"
        }

# 사용 예시
def main():
    # OpenAI API 키 설정
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your-openai-api-key-here')
    
    # 자동화 인스턴스 생성
    automation = GoogleBloggerAutomation(OPENAI_API_KEY)
    
    print("🎥 유튜브 스크립트를 구글 블로그 포스트로 변환하는 프로그램")
    print("=" * 60)
    
    # 사용자 입력
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
    
    # 발행 모드 선택
    publish_mode = input("\n발행 모드를 선택하세요 (draft/publish): ").lower()
    if publish_mode not in ["draft", "publish"]:
        publish_mode = "draft"
    
    # 블로그 포스트 생성
    print(f"\n🚀 {publish_mode} 모드로 블로그 포스트 생성 중...")
    result = automation.generate_full_blog_post(youtube_url, script_text, publish_mode=publish_mode)
    
    if result.get("success"):
        print("\n🎉 성공!")
        print(f"블로그: {result['blog_info']['name']}")
        print(f"제목: {result['post_data']['title']}")
        
        if publish_mode == "draft":
            print(f"초안 URL: {result['result']['draft_url']}")
        else:
            print(f"포스트 URL: {result['result']['url']}")
        
        print(f"생성된 이미지: {len(result['images'])}개")
    else:
        print(f"❌ 오류: {result.get('error', '알 수 없는 오류')}")

if __name__ == "__main__":
    main()

