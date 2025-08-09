# YouTube to Google Blogger Automation

🎥 **유튜브 스크립트를 구글 블로그 포스트로 자동 변환하는 AI 프로그램**

## ✨ 주요 기능

- **AI 기반 스크립트 분석**: 유튜브 스크립트에서 키워드와 주제 추출
- **구글 블로그 자동 포스팅**: Blogger API를 통한 자동 블로그 포스트 생성
- **AI 이미지 생성**: DALL-E를 활용한 콘텐츠 관련 이미지 생성
- **초안/발행 모드**: 검토용 초안 또는 바로 발행 선택 가능
- **웹 인터페이스**: 사용하기 쉬운 웹 기반 인터페이스 제공
- **실시간 미리보기**: 생성 전 콘텐츠 미리보기 기능

## 🚀 설치 및 설정

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. Google Cloud Console 설정(클라이언트 ID/Secret 발급)

아래 순서대로 진행하면 웹 애플리케이션용 OAuth 클라이언트를 생성하고 `credentials.json`을 받을 수 있습니다.

#### 2.1 프로젝트 생성
1. 브라우저로 [Google Cloud Console](https://console.cloud.google.com) 접속
2. 상단 프로젝트 드롭다운 → "새 프로젝트" → 이름 입력(예: "YouTube Auto Blogger") → 만들기

#### 2.2 Blogger API v3 활성화
1. 좌측 메뉴 "API 및 서비스" → "라이브러리"
2. "Blogger API v3" 검색 후 선택 → "사용 설정" 클릭

#### 2.3 OAuth 동의화면 구성
1. "API 및 서비스" → "OAuth 동의화면"
2. 사용자 유형: "외부(External)" 선택 → 만들기
3. 앱 이름/지원 이메일 입력
4. 범위는 기본 프로필/이메일 정도로 시작 가능(필요 시 추후 확장)
5. 테스트 사용자에 본인 Gmail 추가 → 저장

#### 2.4 OAuth 2.0 클라이언트 ID 생성(웹 애플리케이션)
1. "API 및 서비스" → "사용자 인증 정보"
2. "사용자 인증 정보 만들기" → "OAuth 클라이언트 ID"
3. 애플리케이션 유형: "웹 애플리케이션"
4. 승인된 리디렉션 URI 추가(필수)
   - 로컬 개발(Flask 기본): `http://localhost:5000/oauth2callback`
   - Docker 8080: `http://localhost:8080/oauth2callback`
   - 서버 배포: `http://서버IP:8080/oauth2callback` 또는 `https://도메인/oauth2callback`
5. (선택) 승인된 자바스크립트 원본: `http://localhost:5000`
6. 생성 후 JSON 다운로드 → 파일명은 `credentials.json`으로 유지 권장

#### 2.5 프로그램에 적용
- UI에서 `credentials.json 업로드` 버튼으로 업로드 또는 Client ID/Secret 직접 입력 후 "Google 로그인 및 설정" 클릭
- 승인 완료 시 `token.pickle`이 생성되며 이후 자동 로그인 동작

### 3. OpenAI API 키 설정
```bash
# .env 파일 생성
echo "OPENAI_API_KEY=your-openai-api-key-here" > .env
```

### 4. 구글 블로그 준비
1. https://www.blogger.com 접속
2. 새 블로그 생성
3. 블로그 URL 확인

## 📖 사용법

### 1. 프로그램 실행
```bash
python run_google_blogger.py
```

### 2. 웹 인터페이스 접속
브라우저에서 `http://localhost:5000` 접속

---

## 🔍 문제 해결(FAQ)
- 400 redirect_uri_mismatch: 리디렉션 URI가 정확히 일치해야 합니다(슬래시 포함). 콘솔에서 URI를 추가 후 저장하세요.
- 403 access_denied: 테스트 사용자 목록에 본인 Gmail이 포함되어야 합니다(동의화면이 게시 전일 때).
- 로컬 HTTP 오류: 환경변수 `OAUTHLIB_INSECURE_TRANSPORT=1` 설정으로 HTTP 리디렉션 허용(앱에 기본 적용됨).
- 토큰 재설정: UI의 "로그아웃"을 눌러 `token.pickle`을 삭제하고 다시 로그인하세요.

---

## 📷 스크린샷 가이드(자리표시자)
아래 파일명으로 스크린샷을 저장하면, 이 문서에서 자동으로 미리보기가 연결됩니다. 경로: `docs/screenshots/`

1) 프로젝트 선택/생성
![01 Project Select](docs/screenshots/01-project-select.png)

2) Blogger API v3 활성화
![02 Enable Blogger API](docs/screenshots/02-enable-blogger-api.png)

3) OAuth 동의화면 설정(외부 → 테스트 사용자 추가)
![03 OAuth Consent Screen](docs/screenshots/03-oauth-consent.png)

4) OAuth 클라이언트 만들기(웹 애플리케이션)
![04 Create OAuth Client](docs/screenshots/04-create-oauth-client.png)

5) 승인된 리디렉션 URI 입력
![05 Redirect URI](docs/screenshots/05-redirect-uri.png)

6) credentials.json 다운로드
![06 Download Credentials](docs/screenshots/06-download-credentials.png)

7) 프로그램에서 credentials.json 업로드
![07 Upload in App](docs/screenshots/07-upload-credentials-ui.png)

8) 로그인 승인 완료
![08 Login Success](docs/screenshots/08-login-success.png)

팁
- 이미지는 1280px 이상 권장, 민감 정보(Client Secret)는 마스킹 후 캡처하세요.
- 파일명은 그대로 두면 링크가 자동으로 연결됩니다.

### 3. 블로그 선택
- "블로그 목록 새로고침" 버튼 클릭
- 사용할 블로그 선택

### 4. 발행 모드 선택
- **초안**: 검토 후 발행 (권장)
- **바로 발행**: 즉시 공개

### 5. 콘텐츠 입력
- YouTube URL 입력
- 스크립트 텍스트 붙여넣기
- "미리보기" 버튼으로 생성 전 확인

### 6. 블로그 포스트 생성
- "블로그 포스트 생성하기" 버튼 클릭
- AI가 스크립트를 분석하고 블로그 포스트 생성
- 이미지 자동 생성 및 추가

## 🔧 주요 기능 상세

### AI 스크립트 분석
- 주요 키워드 추출
- SEO 최적화된 제목 생성
- 블로그 포스트 구조화
- 태그 및 카테고리 자동 설정

### 구글 블로그 자동화
- Blogger API v3 활용
- 초안/발행 모드 지원
- 이미지 자동 추가
- 태그 및 메타데이터 설정

### 이미지 생성
- DALL-E를 활용한 AI 이미지 생성
- 포스트 주제에 맞는 이미지 자동 생성
- 메인 이미지 및 섹션별 이미지

## 💰 수익화 전략

### 1. 프리미엄 기능 제공
- 고급 SEO 분석
- 더 많은 이미지 생성
- 맞춤형 템플릿
- API 접근 권한

### 2. 구독 모델
- 월간/연간 구독
- 사용량 기반 과금
- 팀 플랜 제공

### 3. 부가 서비스
- 콘텐츠 편집 서비스
- SEO 컨설팅
- 블로그 최적화 서비스

### 4. 제휴 마케팅
- 구글 애드센스 제휴
- 호스팅 서비스 제휴
- 도메인 등록 서비스 제휴

## 🔧 기술 스택

- **Backend**: Python, Flask
- **AI**: OpenAI GPT-3.5-turbo, DALL-E
- **Google API**: Blogger API v3, OAuth 2.0
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **이미지 처리**: Pillow (PIL)

## 📈 SEO 최적화 기능

### 키워드 분석
- 주요 키워드 추출
- 롱테일 키워드 발견
- 키워드 밀도 최적화

### 콘텐츠 구조화
- H1, H2, H3 태그 최적화
- 메타 설명 생성
- 내부/외부 링크 제안

### 이미지 최적화
- SEO 친화적인 이미지 생성
- Alt 텍스트 자동 생성
- 이미지 파일명 최적화

## 🎯 타겟 사용자

- **블로거**: 유튜브 콘텐츠를 블로그로 확장
- **마케터**: 콘텐츠 마케팅 자동화
- **콘텐츠 크리에이터**: 다중 플랫폼 콘텐츠 제작
- **SEO 전문가**: 클라이언트를 위한 자동화 서비스

## 🔒 보안 및 개인정보

- OpenAI API 키는 서버에 안전하게 저장
- 구글 OAuth 2.0 인증 사용
- 사용자 데이터는 로컬에서만 처리
- 개인정보 수집하지 않음

## 📁 파일 구조

```
ShareSiteForge/
├── google_blogger_automation.py    # 구글 블로그 자동화 핵심 클래스
├── google_blogger_web.py          # 웹 인터페이스
├── run_google_blogger.py          # 실행 스크립트
├── requirements.txt               # 의존성 패키지
├── .env                          # 환경 변수 (OpenAI API 키)
├── client_secrets.json           # 구글 API 인증 파일
├── templates/
│   └── google_blogger.html      # 웹 인터페이스 템플릿
└── README_GOOGLE_BLOGGER.md     # 이 파일
```

## 🚨 주의사항

### 구글 API 할당량
- Blogger API v3는 일일 할당량이 있습니다
- 과도한 사용 시 할당량 초과 가능

### OpenAI API 비용
- GPT-3.5-turbo 사용 시 토큰당 비용 발생
- DALL-E 이미지 생성 시 추가 비용

### 인증 파일 보안
- `client_secrets.json` 파일은 절대 공개하지 마세요
- `.env` 파일도 안전하게 보관하세요

## 📞 지원

문제가 있거나 기능 요청이 있으시면 이슈를 등록해주세요.

## 📄 라이선스

MIT License

---

**🎉 이제 유튜브 스크립트를 구글 블로그 포스트로 자동 변환할 수 있습니다!**


