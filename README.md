# YouTube to SEO Content Generator

🎥 **유튜브 스크립트를 SEO 최적화된 블로그 포스트로 변환하는 AI 프로그램**

## ✨ 주요 기능

- **AI 기반 스크립트 분석**: 유튜브 스크립트에서 키워드와 주제 추출
- **SEO 최적화된 콘텐츠 생성**: 검색엔진에 최적화된 블로그 포스트 자동 생성
- **AI 이미지 생성**: DALL-E를 활용한 콘텐츠 관련 이미지 생성
- **소셜미디어 콘텐츠**: Instagram, Twitter, LinkedIn, Facebook용 포스트 자동 생성
- **웹 인터페이스**: 사용하기 쉬운 웹 기반 인터페이스 제공
- **패키지 다운로드**: 생성된 모든 콘텐츠를 ZIP 파일로 다운로드

## 🚀 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. OpenAI API 키 설정
```bash
# 환경 변수로 설정
export OPENAI_API_KEY="your-openai-api-key-here"

# 또는 .env 파일 생성
echo "OPENAI_API_KEY=your-openai-api-key-here" > .env
```

### 3. 웹 애플리케이션 실행
```bash
python web_app.py
```

### 4. 브라우저에서 접속
```
http://localhost:5000
```

## ☁️ Docker 배포(서버/클라우드)

1) 이미지 빌드

```bash
docker build -t youtube-auto-blogger:latest .
```

2) 컨테이너 실행

```bash
docker run -d --name auto-blogger -p 8080:8080 \
  -e OAUTHLIB_INSECURE_TRANSPORT=1 \
  -e OPENAI_API_KEY=YOUR_KEY \
  -e PEXELS_API_KEY=YOUR_PEXELS_KEY \
  -v $(pwd)/data:/app \
  youtube-auto-blogger:latest
```

3) 접속: `http://YOUR_SERVER:8080`

4) Google OAuth
 - `credentials.json` 업로드 또는 클라우드용 Client ID/Secret 입력
 - OAuth Redirect URI: `http(s)://YOUR_SERVER:8080/oauth2callback`

지속성: 컨테이너에 `-v`로 마운트한 폴더에 `token.pickle`/`credentials.json`이 보관됩니다.

### GitHub Actions로 자동 빌드/푸시

1) 저장소 Secrets 설정
   - `DOCKERHUB_USERNAME`: 도커허브 사용자명
   - `DOCKERHUB_TOKEN`: Personal Access Token
   - (선택) `DOCKER_IMAGE`: `user/repo:tag` 형태 커스텀 경로

2) main/master 브랜치 푸시 시 자동으로 이미지가 빌드되어 푸시됩니다.

### GHCR로 이미지 푸시(선택)
이 저장소에는 GHCR(GitHub Container Registry) 푸시용 워크플로우도 포함되어 있습니다.

- 푸시 태그: `ghcr.io/<owner>/<repo>:latest`
- 사용 예시:
```bash
docker pull ghcr.io/<owner>/<repo>:latest
docker run -d -p 8080:8080 \
  -e OPENAI_API_KEY="your-openai-api-key" \
  -e PEXELS_API_KEY="your-pexels-api-key" \
  -v $(pwd)/data:/app/data \
  ghcr.io/<owner>/<repo>:latest
```

## ⚡ 원클릭 배포(SSH VPS: Lightsail 등)

GitHub Actions의 `Deploy to VPS (Lightsail/Any SSH host)` 워크플로우로 원격 서버에 배포할 수 있습니다.

1) 저장소 Secrets 추가
   - `VPS_HOST`: 서버 IP 또는 도메인
   - `VPS_USER`: SSH 사용자명(예: ubuntu)
   - `VPS_SSH_KEY`: 개인키(private key) 내용 전체
   - (선택) `VPS_PORT`: SSH 포트(기본 22)
   - (선택) `OPENAI_API_KEY`, `PEXELS_API_KEY`

2) Actions → `Deploy to VPS (Lightsail/Any SSH host)` → Run workflow → 실행
   - `image`를 비우면 기본 `ghcr.io/<owner>/<repo>:latest` 사용
   - 기본 포트는 8080 → `http://서버IP:8080`

서버 측에서는 자동으로 Docker 설치(없을 경우), 이미지 Pull, 컨테이너 재시작이 수행됩니다. 데이터는 `$HOME/pab-data`에 유지됩니다.


## 📖 사용법

### 1. 유튜브 URL 입력
- 유튜브 영상의 URL을 입력합니다
- 예: `https://www.youtube.com/watch?v=VIDEO_ID`

### 2. 스크립트 입력
- 유튜브 영상의 스크립트를 텍스트로 입력합니다
- YouTube Studio에서 자동 생성된 자막을 사용하거나 수동으로 입력할 수 있습니다

### 3. 콘텐츠 유형 선택
- 블로그 포스트
- 기사
- 리뷰
- 튜토리얼

### 4. AI 생성 시작
- "SEO 콘텐츠 생성하기" 버튼을 클릭합니다
- AI가 스크립트를 분석하고 SEO 최적화된 콘텐츠를 생성합니다

### 5. 결과 확인 및 다운로드
- 생성된 콘텐츠를 미리보기로 확인
- SEO 분석 결과 확인
- 소셜미디어용 콘텐츠 확인
- 전체 패키지를 ZIP 파일로 다운로드

## 📁 생성되는 파일들

### blog_post.html
- SEO 최적화된 HTML 블로그 포스트
- H1, H2, H3 태그 포함
- 메타 설명 및 키워드 최적화

### analysis.json
- 추출된 주요 키워드
- 롱테일 키워드
- 주요 주제 및 서브 주제
- 타겟 독자 분석

### social_media.json
- Instagram용 포스트 (해시태그 포함)
- Twitter용 포스트 (280자 이내)
- LinkedIn용 포스트 (전문적 톤)
- Facebook용 포스트

### images.txt
- DALL-E로 생성된 이미지 URL들
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
- 웹사이트 최적화 서비스

### 4. 제휴 마케팅
- 호스팅 서비스 제휴
- 도메인 등록 서비스 제휴
- SEO 도구 제휴

## 🔧 기술 스택

- **Backend**: Python, Flask
- **AI**: OpenAI GPT-3.5-turbo, DALL-E
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

- **블로거**: 유튜브 콘텐츠를 블로그 포스트로 변환
- **마케터**: 소셜미디어 마케팅 콘텐츠 생성
- **콘텐츠 크리에이터**: 다양한 플랫폼용 콘텐츠 제작
- **SEO 전문가**: 클라이언트를 위한 SEO 최적화 콘텐츠 생성

## 🔒 보안 및 개인정보

- OpenAI API 키는 서버에 안전하게 저장
- 사용자 데이터는 로컬에서만 처리
- 개인정보 수집하지 않음

## 📞 지원

문제가 있거나 기능 요청이 있으시면 이슈를 등록해주세요.

## 📄 라이선스

MIT License

---

**🎉 이제 유튜브 스크립트를 SEO 최적화된 콘텐츠로 쉽게 변환할 수 있습니다!**
