# AI Blogging Studio - Desktop Version

AI 자동 블로깅 스튜디오의 데스크톱 설치 버전입니다.

## 특징

- 🖥️ Windows, Mac, Linux 지원
- 🚀 설치형 프로그램 (.exe, .dmg, .AppImage)
- 💾 로컬 데이터베이스 (SQLite)
- 🔐 개인 정보 보호 (로컬 저장)
- 🌐 인터넷 연결 시 AI 기능 사용 가능

## 개발 환경 설정

### 필요 사항
- Node.js (18.0.0 이상)
- Python (3.8 이상)
- npm 또는 yarn

### 설치 및 실행

1. 의존성 설치:
```bash
npm install
pip install -r server/requirements.txt
```

2. 개발 모드 실행:
```bash
npm start
```

3. 배포용 빌드:
```bash
npm run dist
```

## 빌드 출력물

- **Windows**: `dist/AI Blogging Studio Setup.exe`
- **Mac**: `dist/AI Blogging Studio.dmg`
- **Linux**: `dist/AI Blogging Studio.AppImage`

## 사용법

1. 설치 프로그램 실행
2. AI Blogging Studio 실행
3. Google Client ID 입력 (AI 기능 사용 시)
4. YouTube URL 또는 주제 입력하여 블로그 포스트 생성

## 판매용 패키징

크몽에서 판매할 때는 다음 파일들을 패키징하세요:

```
AI_Blogging_Studio_Desktop/
├── AI Blogging Studio Setup.exe  (Windows 설치 파일)
├── 사용자_매뉴얼.pdf             (사용법 안내)
├── 설치_가이드.pdf               (설치 방법)
└── 라이선스.txt                  (이용 약관)
```

## 라이선스

개인 및 상업적 사용 가능