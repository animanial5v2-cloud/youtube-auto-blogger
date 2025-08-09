import os
import json
import requests
from typing import Optional, Dict, List
from pytube import YouTube
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pickle
import base64
from PIL import Image
import io
import re
import html
import xml.etree.ElementTree as ET
import json as jsonlib

# Optional dependency: youtube-transcript-api for robust caption fetching
try:
    from youtube_transcript_api import (
        YouTubeTranscriptApi,
        TranscriptsDisabled,
        NoTranscriptFound,
        VideoUnavailable,
    )
except Exception:
    YouTubeTranscriptApi = None

class YouTubeAutoBlogger:
    def __init__(self, pexels_api_key: Optional[str] = None):
        self.pexels_base_url = "https://api.pexels.com/v1"
        self.pexels_api_key = pexels_api_key
        # OpenAI (GPT) 설정: 환경변수 사용 (필수)
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        
        # Google Blogger API 설정
        self.SCOPES = ['https://www.googleapis.com/auth/blogger']
        self.creds = None
        self.blogger_service = None
        self.log_callback = None
        
    def initialize_blogger_from_token(self) -> bool:
        """token.pickle이 있으면 이를 사용해 Blogger 서비스를 초기화."""
        try:
            if self.blogger_service:
                return True
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    self.creds = pickle.load(token)
                if self.creds:
                    self.blogger_service = build('blogger', 'v3', credentials=self.creds)
                    return True
        except Exception as _:
            return False
        return False
    def setup_google_auth(self, client_id: str = None, client_secret: str = None):
        """Google OAuth 2.0 인증 설정"""
        # 토큰이 이미 있으면 로드
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        
        # 유효한 인증 정보가 없으면 새로 생성
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                # credentials.json 파일이 없으면 자동 생성
                if not os.path.exists('credentials.json'):
                    if client_id and client_secret:
                        # 클라이언트 ID/Secret로 credentials.json 생성
                        self._create_credentials_file(client_id, client_secret)
                    else:
                        print("⚠️ credentials.json 파일이 없습니다.")
                        print("Google 인증 없이 콘텐츠 생성만 진행합니다.")
                        return False
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # 토큰 저장
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)
        
        # Blogger API 서비스 생성
        try:
            # 프록시가 TLS를 깨뜨리는 환경을 회피
            self._disable_system_proxies()
            self.blogger_service = build('blogger', 'v3', credentials=self.creds)
            return True
        except Exception as e:
            print(f"❌ Blogger API 서비스 생성 실패: {e}")
            return False
    
    def _create_credentials_file(self, client_id: str, client_secret: str):
        """클라이언트 ID/Secret로 credentials.json 파일 생성"""
        credentials_data = {
            "installed": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
            }
        }
        
        with open('credentials.json', 'w', encoding='utf-8') as f:
            json.dump(credentials_data, f, indent=2)
        
        print("✅ credentials.json 파일이 생성되었습니다.")

    def _disable_system_proxies(self) -> None:
        """일부 환경에서 SSL 프록시로 인해 TLS 핸드셰이크 오류가 발생하는 것을 방지."""
        proxy_vars = [
            'HTTP_PROXY', 'http_proxy',
            'HTTPS_PROXY', 'https_proxy',
            'ALL_PROXY', 'all_proxy',
            'REQUESTS_CA_BUNDLE', 'CURL_CA_BUNDLE'
        ]
        for var in proxy_vars:
            if os.environ.get(var):
                os.environ.pop(var, None)

    def _log(self, message: str) -> None:
        try:
            if self.log_callback:
                self.log_callback(message)
            else:
                print(message)
        except Exception:
            print(message)

    def _llm_generate_text(self, prompt: str) -> Optional[str]:
        """OpenAI(Chat Completions)으로 텍스트 생성. 키가 없으면 생성 불가."""
        if not self.openai_api_key:
            self._log("❌ OpenAI API 키가 설정되지 않았습니다. AI 생성을 진행할 수 없습니다.")
            return None
        try:
            # 시스템 프록시로 인해 TLS 문제가 발생하는 환경 방지
            self._disable_system_proxies()
            self._log(f"LLM: OpenAI ({self.openai_model})")
            headers = {"Authorization": f"Bearer {self.openai_api_key}", "Content-Type": "application/json"}
            payload = {
                "model": self.openai_model,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that writes fluent Korean when appropriate."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
            }
            session = requests.Session()
            session.trust_env = False  # OS 프록시 무시
            resp = session.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=120)
            if resp.status_code == 200:
                return resp.json().get("choices", [{}])[0].get("message", {}).get("content")
            else:
                try:
                    txt = resp.text[:500]
                except Exception:
                    txt = str(resp)
                self._log(f"❌ OpenAI 응답 오류: {resp.status_code} {txt}")
        except Exception as e:
            self._log(f"❌ OpenAI 호출 오류: {e}")
        return None
    
    def auto_setup_google_auth(self):
        """자동 Google 인증 설정 (기본값 사용)"""
        # 기본 클라이언트 ID/Secret (개발용)
        default_client_id = "your-default-client-id.apps.googleusercontent.com"
        default_client_secret = "your-default-client-secret"
        
        print("🔧 자동 Google 인증 설정을 시작합니다...")
        print("⚠️  기본 설정을 사용합니다. 실제 사용을 위해서는 Google Cloud Console에서 설정하세요.")
        
        # 사용자에게 기본값 사용 여부 확인
        try:
            response = input("기본 설정을 사용하시겠습니까? (y/n): ").lower()
            if response == 'y':
                return self.setup_google_auth(default_client_id, default_client_secret)
            else:
                print("Google Cloud Console에서 설정을 완료한 후 다시 시도하세요.")
                return False
        except KeyboardInterrupt:
            print("\n설정이 취소되었습니다.")
            return False
    
    def extract_youtube_script(self, youtube_url: str) -> Optional[str]:
        """YouTube URL에서 스크립트 추출"""
        try:
            print(f"🎥 YouTube 스크립트 추출 중: {youtube_url}")

            # 1) youtube-transcript-api로 자막 우선 시도 (ko -> en)
            def _extract_video_id(url: str) -> Optional[str]:
                patterns = [r"v=([\w-]{11})", r"youtu\.be/([\w-]{11})", r"/shorts/([\w-]{11})"]
                for p in patterns:
                    m = re.search(p, url)
                    if m:
                        return m.group(1)
                return None

            video_id = _extract_video_id(youtube_url)
            # 1) 공식 timedtext XML 우선 시도 (로그인/제한 영상 제외)
            if video_id:
                script = self._fetch_timedtext_script(video_id)
                if script:
                    print("✅ timedtext XML에서 스크립트 추출 완료")
                    return script
            # 1.5) youtube-transcript-api 보조 시도 (있으면)
            if YouTubeTranscriptApi and video_id:
                preferred_langs = ['ko', 'ko-KR', 'en', 'en-US', 'ja', 'zh-Hans', 'zh-Hant', 'zh']
                for attempt in range(2):
                    try:
                        for lang in preferred_langs:
                            try:
                                data = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
                                script = "\n".join(seg['text'] for seg in data if seg.get('text'))
                                if script.strip():
                                    print("✅ 자막 API에서 스크립트 추출 완료")
                                    return script
                            except Exception:
                                continue
                        break
                    except Exception:
                        break

            # 2) pytube로 메타 정보(제목/설명) 확보 (자막은 사용하지 않음)
            title, description = None, None
            try:
                yt = YouTube(youtube_url)
                title = yt.title
                description = yt.description
            except Exception:
                # oEmbed로 최소 제목 확보
                try:
                    oembed = requests.get(
                        "https://www.youtube.com/oembed",
                        params={"url": youtube_url, "format": "json"}, timeout=10,
                    )
                    if oembed.ok:
                        title = oembed.json().get('title')
                except Exception:
                    pass

            # 3) 자막이 없으면 AI로 스크립트 생성
            print("📝 AI로 스크립트 생성 중...")
            prompt = f"""
            다음 YouTube 동영상 정보를 바탕으로 상세한 스크립트를 생성해주세요.
            
            제목: {title or '제목 없음'}
            설명: {(description or '')[:500]}...
            
            실제 스크립트처럼 자연스럽고 상세하게 작성해주세요.
            """

            script = self._llm_generate_text(prompt)
            if script:
                print("✅ AI로 스크립트 생성 완료")
                return script
            else:
                print("❌ AI 스크립트 생성 실패")
                return None

        except Exception as e:
            print(f"❌ YouTube 스크립트 추출 실패: {e}")
            return None

    def _fetch_timedtext_script(self, video_id: str) -> Optional[str]:
        """YouTube timedtext XML 엔드포인트로 자막을 폴백 추출"""
        try:
            # 사용 가능한 언어 목록 조회
            list_url = "https://video.google.com/timedtext"
            r = requests.get(list_url, params={"type": "list", "v": video_id}, timeout=10)
            if r.status_code != 200 or not r.text.strip():
                return None
            root = ET.fromstring(r.text)
            tracks = root.findall('track')
            if not tracks:
                return None
            # 선호 언어 선택
            preferred = ['ko', 'ko-KR', 'en', 'en-US']
            lang = None
            for p in preferred:
                if any(t.get('lang_code') == p for t in tracks):
                    lang = p; break
            if not lang:
                lang = tracks[0].get('lang_code')

            # 자막 다운로드 (XML)
            r2 = requests.get(list_url, params={"lang": lang, "v": video_id}, timeout=15)
            if r2.status_code != 200 or not r2.text.strip():
                return None
            root2 = ET.fromstring(r2.text)
            lines = []
            for node in root2.findall('text'):
                t = node.text or ''
                t = html.unescape(t)
                t = t.replace('\n', ' ').strip()
                if t:
                    lines.append(t)
            text = "\n".join(lines)
            return text if text.strip() else None
        except Exception:
            return None
    
    def analyze_content(self, script_text: str, target_audience: str = "일반인", desired_min_len: int = 3000, desired_max_len: int = 4000) -> Dict:
        """AI로 콘텐츠 분석 및 SEO 최적화 (OpenAI 전용)"""
        # 안전 가드: 비정상 인자 교정
        try:
            desired_min_len = int(desired_min_len)
            desired_max_len = int(desired_max_len)
            if desired_min_len < 1000:
                desired_min_len = 1000
            if desired_max_len < desired_min_len + 500:
                desired_max_len = desired_min_len + 500
        except Exception:
            desired_min_len, desired_max_len = 3000, 4000

        prompt = f"""
        다음 유튜브 스크립트를 기반으로 {target_audience} 타겟의 고품질 한국어 블로그 포스트를 작성하세요.
        - 길이: 본문은 {desired_min_len}~{desired_max_len}자 사이 (가독성 유지, 불필요한 군더더기 금지)
        - 품질: 구체적 사례/데이터/실행 가능한 팁 포함, 중복·상투적 표현 지양, 광고성·과장 금지
        - 구조: H1 제목, H2 소제목 4~6개, 각 소제목 아래 자연스러운 H3 수준의 단락들로 구성
        - SEO: 한글 키워드 10개, 150자 내 메타 설명, 자연스러운 키워드 배치(키워드 나열 금지)
        - 금지 표현 예: "이 글에서는", "결론적으로", "요약하면" 등 템플릿 문구 남발 금지
        - 출력 형식: 반드시 '유효한 JSON'만 반환. 마크다운 코드펜스(```), 추가 설명, 주석 등 기타 텍스트 금지
        - JSON 키: title, subheadings, content, keywords, meta_description, target_audience

        스크립트 원문:
        {script_text}

        JSON만 반환:
        {{
            "title": "",
            "subheadings": ["", "", "", ""],
            "content": "",
            "keywords": ["", "", "", "", "", "", "", "", "", ""],
            "meta_description": "",
            "target_audience": "{target_audience}"
        }}
        """
        
        try:
            raw = (self._llm_generate_text(prompt) or '').strip()
            # 코드펜스 제거 및 JSON 부분만 추출
            if raw.startswith('```'):
                raw = raw.strip('`')
            def _parse_json(s: str) -> Dict:
                try:
                    return jsonlib.loads(s)
                except Exception:
                    try:
                        start = s.find('{')
                        end = s.rfind('}')
                        if start != -1 and end != -1:
                            return jsonlib.loads(s[start:end+1])
                    except Exception:
                        pass
                return {}

            data = _parse_json(raw) or {}
            if not data:
                # 최소 구조 반환
                data = {
                    "title": f"{target_audience}을 위한 블로그 포스트",
                    "subheadings": ["주요 내용", "상세 설명", "결론"],
                    "content": raw,
                    "keywords": ["키워드1", "키워드2", "키워드3", "키워드4", "키워드5",
                                   "키워드6", "키워드7", "키워드8", "키워드9", "키워드10"],
                    "meta_description": "유튜브 콘텐츠를 바탕으로 한 블로그 포스트입니다.",
                    "target_audience": target_audience
                }

            # 본문 길이 보정(목표 {desired_min_len}~{desired_max_len}자)
            try:
                body = (data.get('content') or '').strip()
                body_len = len(body)
                if body_len < desired_min_len:
                    expand_prompt = f"""
                    아래 본문을 {desired_min_len}~{desired_max_len}자 범위로 자연스럽게 확장하세요.
                    - 소제목(H2)별로 구체 사례/데이터/실행 팁 보강
                    - 중복 제거, 밀도 높게 서술, 상투적 문구 금지
                    - 반환은 '본문 텍스트'만. 다른 형식·주석·마크다운 금지

                    본문:
                    {body}
                    """
                    r_len_text = self._llm_generate_text(expand_prompt)
                    if r_len_text:
                        data['content'] = r_len_text.strip()
                elif body_len > desired_max_len:
                    shrink_prompt = f"""
                    아래 본문을 핵심은 유지하되 {desired_min_len}~{desired_max_len}자로 응축하세요.
                    - 정보 손실 최소화, 불필요한 수사/중복 제거
                    - 문장 간 결속 강화, 논리 흐름 유지
                    - 반환은 '본문 텍스트'만. 다른 형식·주석·마크다운 금지

                    본문:
                    {body}
                    """
                    r_len_text = self._llm_generate_text(shrink_prompt)
                    if r_len_text:
                        data['content'] = r_len_text.strip()
            except Exception:
                pass

            # 한글 강제: 본문이 영어 위주면 한국어로 변환
            try:
                text = data.get('content') or ''
                # 간단한 한글 문자 비율 체크
                hangul = sum(1 for ch in text if '\uac00' <= ch <= '\ud7a3')
                ratio = hangul / max(len(text), 1)
                if ratio < 0.2 and text.strip():
                    to_kr_prompt = f"""
                    다음 영어(또는 비한국어) 블로그 본문을 한국어로 매끄럽게 번역하되, 의미를 충실히 반영하세요.
                    - 존댓말, 자연스러운 한국어 문장
                    - 마크다운/코드펜스 금지, 본문 텍스트만 반환

                    본문:
                    {text}
                    """
                    r3_text = self._llm_generate_text(to_kr_prompt)
                    if r3_text:
                        data['content'] = r3_text
            except Exception:
                pass

            return data
                
        except Exception as e:
            print(f"❌ 콘텐츠 분석 실패: {e}")
            return {}
    
    def translate_keywords_to_english(self, keywords: List[str]) -> List[str]:
        """키워드를 영어로 번역"""
        prompt = f"""
        다음 한글 키워드들을 영어로 번역해주세요. 
        이미지 검색에 적합한 영어 단어로 변환해주세요.
        
        키워드: {', '.join(keywords[:5])}
        
        영어 키워드만 쉼표로 구분해서 응답해주세요.
        """
        
        try:
            text = self._llm_generate_text(prompt)
            if text:
                english_keywords = text.strip().split(',')
                return [kw.strip() for kw in english_keywords]
            return keywords[:5]
        except Exception as e:
            print(f"❌ 키워드 번역 실패: {e}")
            return keywords[:5]
    
    def search_pexels_image(self, keyword: str) -> Optional[str]:
        """Pexels에서 이미지 검색"""
        try:
            headers = {}
            if self.pexels_api_key:
                headers['Authorization'] = self.pexels_api_key
            
            url = f"{self.pexels_base_url}/search"
            params = {
                'query': keyword,
                'per_page': 1,
                'orientation': 'landscape'
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data['photos']:
                    photo = data['photos'][0]
                    return photo['src']['large']
            else:
                print(f"Pexels API 오류: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"이미지 검색 실패: {e}")
        
        return None
    
    def create_blog_post_content(self, analysis: Dict, image_url: Optional[str] = None) -> str:
        """블로그 포스트 HTML 생성"""
        title = analysis.get('title', '블로그 포스트')
        subheadings = analysis.get('subheadings', [])
        content = analysis.get('content', '')
        keywords = analysis.get('keywords', [])
        
        html_content = f"""
        <h1>{title}</h1>
        """

        # 이미지 추가 (원본 제목을 alt로 사용해 이미지 검색 최적화)
        if image_url:
            html_content += (
                f'<img src="{image_url}" alt="{title}" title="{title}" '
                f'style="max-width: 100%; height: auto; margin: 20px 0;" />'
            )

        # 전체 본문을 소제목 개수에 맞춰 균등 분할하여 모든 문단을 포함
        # - LLM 출력이 \n\n 단락 구분을 사용하지 않을 수 있어 보조 분할을 사용
        raw_parts = [p.strip() for p in content.split('\n\n') if p.strip()]
        if len(raw_parts) <= 1:
            raw_parts = [p.strip() for p in content.split('\n') if p.strip()]
        if not raw_parts:
            raw_parts = [content.strip()]

        if subheadings:
            num_sections = max(1, len(subheadings))
            # 구간 경계: 분할 손실 없이 모든 단락 포함
            total = len(raw_parts)
            for idx, sub in enumerate(subheadings):
                start = (idx * total) // num_sections
                end = ((idx + 1) * total) // num_sections
                chunk = raw_parts[start:end] if start < end else []
                html_content += f"""
                <h2>{sub}</h2>
                {''.join(f'<p>{para}</p>' for para in chunk) if chunk else ''}
                """
            # 남는 단락이 있다면 마지막 섹션 뒤에 안전하게 추가
            if len(raw_parts) > (((len(subheadings)) * total) // num_sections):
                leftover = raw_parts[((len(subheadings)) * total) // num_sections:]
                html_content += """
                <div>
                {paras}
                </div>
                """.replace('{paras}', ''.join(f'<p>{p}</p>' for p in leftover))
        else:
            # 소제목이 없으면 본문 전체를 단락으로 출력
            html_content += ''.join(f'<p>{p}</p>' for p in raw_parts)

        # 키워드 섹션 추가
        html_content += f"""
        <h3>관련 키워드</h3>
        <p>{', '.join(keywords)}</p>
        """

        return html_content
    
    def post_to_blogger(self, blog_id: str, title: str, content: str, labels: List[str] = None,
                        publish_at_iso: Optional[str] = None) -> Optional[str]:
        """구글 블로거에 포스트 작성 후 공개 URL 반환 (실패 시 None)
        예약 발행: publish_at_iso(ISO8601/RFC3339)가 미래 시간이면 초안 생성 후 해당 시각으로 발행
        """
        try:
            if not self.blogger_service:
                print("❌ Blogger 서비스가 초기화되지 않았습니다.")
                return None
            
            post_body = {
                'kind': 'blogger#post',
                'blog': {
                    'id': blog_id
                },
                'title': title,
                'content': content,
                'labels': labels or []
            }
            
            if publish_at_iso:
                # 초안으로 생성 후 예약 발행
                draft = self.blogger_service.posts().insert(
                    blogId=blog_id,
                    body=post_body,
                    isDraft=True
                ).execute()
                post_id = draft.get('id')
                if not post_id:
                    print("❌ 초안 생성 실패")
                    return None
                pub = self.blogger_service.posts().publish(
                    blogId=blog_id,
                    postId=post_id,
                    publishDate=publish_at_iso
                ).execute()
                url = pub.get('url')
                print(f"✅ 예약 발행 설정 완료: {url} @ {publish_at_iso}")
                return url
            else:
                # 즉시 발행
                post = self.blogger_service.posts().insert(
                    blogId=blog_id,
                    body=post_body,
                    isDraft=False
                ).execute()
                url = post.get('url')
                print(f"✅ 블로그 포스트 작성 완료: {url}")
                return url
            
        except HttpError as error:
            print(f"❌ Blogger API 오류: {error}")
            return None
        except Exception as e:
            print(f"❌ 블로그 포스트 작성 실패: {e}")
            return None
    
    def get_user_blogs(self) -> List[Dict]:
        """사용자의 블로그 목록 가져오기"""
        try:
            if not self.blogger_service:
                return []
            
            blogs = self.blogger_service.blogs().listByUser(userId='self').execute()
            return blogs.get('items', [])
            
        except Exception as e:
            print(f"❌ 블로그 목록 가져오기 실패: {e}")
            return []
    
    def generate_full_auto_package(self, youtube_url: str, target_audience: str = "일반인", blog_id: str = None,
                                   min_len: int = 3000, max_len: int = 4000,
                                   publish_at_iso: Optional[str] = None) -> Dict:
        """완전 자동화된 패키지 생성"""
        print("🚀 YouTube 자동 블로거 시작...")
        
        # 1. YouTube 스크립트 추출
        script_text = self.extract_youtube_script(youtube_url)
        if not script_text:
            return {"error": "YouTube 스크립트 추출 실패"}
        
        # 2. AI로 콘텐츠 분석
        print("📊 콘텐츠 분석 중...")
        analysis = self.analyze_content(script_text, target_audience, desired_min_len=min_len, desired_max_len=max_len)
        if not analysis:
            return {"error": "콘텐츠 분석 실패"}
        
        # 3. 키워드 번역
        print("🌐 키워드 번역 중...")
        english_keywords = self.translate_keywords_to_english(analysis.get('keywords', []))
        
        # 4. 이미지 검색
        print("🖼️ 이미지 검색 중...")
        image_url = None
        for keyword in english_keywords:
            image_url = self.search_pexels_image(keyword)
            if image_url:
                break
        
        # 5. 블로그 포스트 콘텐츠 생성
        print("✍️ 블로그 포스트 생성 중...")
        blog_content = self.create_blog_post_content(analysis, image_url)
        
        # 6. 구글 블로거에 포스트 (선택사항)
        post_url: Optional[str] = None
        if blog_id and self.blogger_service:
            print("📝 구글 블로거에 포스트 중...")
            post_url = self.post_to_blogger(
                blog_id, 
                analysis.get('title', '블로그 포스트'),
                blog_content,
                analysis.get('keywords', []),
                publish_at_iso=publish_at_iso
            )
            # post_url은 실제 공개 URL이거나 None
        
        return {
            "success": True,
            "youtube_url": youtube_url,
            "script": script_text,
            "analysis": analysis,
            "english_keywords": english_keywords,
            "image_url": image_url,
            "blog_content": blog_content,
            "post_url": post_url,
            "target_audience": target_audience
        }
    
    def save_to_files(self, package: Dict, output_dir: str = "auto_blogger_output"):
        """결과를 파일로 저장"""
        os.makedirs(output_dir, exist_ok=True)
        
        # HTML 파일
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{package['analysis'].get('title', '블로그 포스트')}</title>
            <meta name="description" content="{package['analysis'].get('meta_description', '')}">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 40px; }}
                h1 {{ color: #333; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
                h2 {{ color: #555; margin-top: 30px; }}
                h3 {{ color: #666; }}
                img {{ max-width: 100%; height: auto; margin: 20px 0; border-radius: 8px; }}
                .keywords {{ background: #f9f9f9; padding: 15px; border-radius: 5px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            {package['blog_content']}
            <div class="keywords">
                <h3>📊 생성 정보</h3>
                <p><strong>YouTube URL:</strong> {package['youtube_url']}</p>
                <p><strong>타겟:</strong> {package['target_audience']}</p>
                <p><strong>검색 키워드:</strong> {', '.join(package['english_keywords'])}</p>
                {f'<p><strong>이미지 URL:</strong> {package["image_url"]}</p>' if package['image_url'] else ''}
                {f'<p><strong>블로그 포스트:</strong> <a href="{package["post_url"]}" target="_blank">보기</a></p>' if package['post_url'] else ''}
            </div>
        </body>
        </html>
        """
        
        with open(f"{output_dir}/blog_post.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        
        # JSON 파일
        with open(f"{output_dir}/package_data.json", "w", encoding="utf-8") as f:
            json.dump(package, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 파일 저장 완료: {output_dir}/")

def main():
    """메인 함수"""
    print("🎥 YouTube 자동 블로거")
    print("=" * 50)
    
    # Google 인증 설정
    auto_blogger = YouTubeAutoBlogger()
    if not auto_blogger.setup_google_auth():
        print("❌ Google 인증 설정 실패")
        return
    
    # 사용자 입력
    youtube_url = input("YouTube URL을 입력하세요: ").strip()
    target_audience = input("타겟을 선택하세요 (일반인/전문가/여자/남자): ").strip() or "일반인"
    blog_id = input("구글 블로그 ID를 입력하세요 (선택사항): ").strip() or None
    
    # 자동화 패키지 생성
    package = auto_blogger.generate_full_auto_package(youtube_url, target_audience, blog_id)
    
    if package.get("success"):
        print("✅ 자동화 완료!")
        print(f"📝 제목: {package['analysis'].get('title', 'N/A')}")
        print(f"🖼️ 이미지: {'있음' if package['image_url'] else '없음'}")
        print(f"📊 키워드: {len(package['english_keywords'])}개")
        if package['post_url']:
            print(f"🌐 블로그 포스트: {package['post_url']}")
        
        # 파일 저장
        auto_blogger.save_to_files(package)
    else:
        print(f"❌ 오류: {package.get('error', '알 수 없는 오류')}")

if __name__ == "__main__":
    main()

