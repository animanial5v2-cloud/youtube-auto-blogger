# AI Blogging Studio 설치 가이드

## 시스템 요구사항

- **운영체제**: Windows 10 이상, macOS 10.14 이상, Ubuntu 18.04 이상
- **메모리**: 최소 4GB RAM (권장 8GB)
- **저장공간**: 500MB 이상
- **인터넷 연결**: AI 기능 사용 시 필요

## 설치 방법

### Windows 설치

1. `AI Blogging Studio Setup.exe` 파일을 다운로드합니다.
2. 설치 파일을 우클릭하고 "관리자 권한으로 실행"을 선택합니다.
3. 설치 마법사의 안내를 따라 진행합니다.
4. 설치 완료 후 바탕화면 아이콘을 더블클릭하여 실행합니다.

### macOS 설치

1. `AI Blogging Studio.dmg` 파일을 다운로드합니다.
2. DMG 파일을 열고 AI Blogging Studio 앱을 Applications 폴더로 드래그합니다.
3. Launchpad에서 AI Blogging Studio를 찾아 실행합니다.
4. 처음 실행 시 "확인되지 않은 개발자" 경고가 나오면:
   - 시스템 환경설정 → 보안 및 개인정보보호로 이동
   - "확인 없이 열기" 버튼을 클릭합니다.

### Linux 설치

1. `AI-Blogging-Studio.AppImage` 파일을 다운로드합니다.
2. 터미널에서 실행 권한을 부여합니다:
   ```bash
   chmod +x AI-Blogging-Studio.AppImage
   ```
3. AppImage 파일을 더블클릭하거나 터미널에서 실행합니다:
   ```bash
   ./AI-Blogging-Studio.AppImage
   ```

## 초기 설정

### 1. Google API 설정 (필수)

AI 기능을 사용하려면 Google API 키가 필요합니다:

1. [Google Cloud Console](https://console.cloud.google.com/)에 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. 다음 API들을 활성화:
   - Gemini API
   - YouTube Data API v3
   - Blogger API v3
4. API 키 생성:
   - 사용자 인증 정보 → API 키 생성
   - OAuth 2.0 클라이언트 ID 생성 (Blogger 사용 시)

### 2. 플랫폼별 설정

#### Google Blogger
- OAuth 2.0 클라이언트 ID 필요
- 블로그 ID 확인 (Blogger 관리 → 설정 → 기본)

#### WordPress.com
- WordPress.com 계정 필요
- API 토큰 발급 ([developer.wordpress.com](https://developer.wordpress.com/apps/))

#### 네이버 블로그
- 네이버 개발자센터에서 앱 등록
- Client ID 및 Client Secret 발급

#### Tistory
- API가 중단되어 수동 포스팅만 가능
- 생성된 콘텐츠를 복사하여 직접 붙여넣기

## 문제 해결

### 프로그램이 시작되지 않는 경우

1. **Windows**: 
   - 관리자 권한으로 실행
   - Windows Defender 예외 추가
   - .NET Framework 업데이트

2. **macOS**:
   - 시스템 환경설정에서 보안 설정 확인
   - 격리 속성 제거: `xattr -d com.apple.quarantine /Applications/AI\ Blogging\ Studio.app`

3. **Linux**:
   - 실행 권한 확인
   - 필요한 라이브러리 설치: `sudo apt install libnss3 libatk-bridge2.0-0 libgtk-3-0`

### AI 기능이 작동하지 않는 경우

1. 인터넷 연결 확인
2. Google API 키 유효성 확인
3. API 할당량 확인 (Google Cloud Console)
4. 방화벽 설정 확인

### 데이터 백업

프로그램 데이터는 다음 위치에 저장됩니다:
- **Windows**: `%APPDATA%/AI Blogging Studio/data/`
- **macOS**: `~/Library/Application Support/AI Blogging Studio/data/`
- **Linux**: `~/.config/AI Blogging Studio/data/`

## 업데이트

새 버전이 출시되면:
1. 기존 프로그램을 종료
2. 새 설치 파일로 덮어쓰기 설치
3. 기존 데이터는 자동으로 보존됩니다

## 지원

문제가 지속되면 다음 정보와 함께 문의해 주세요:
- 운영체제 및 버전
- 프로그램 버전
- 오류 메시지 스크린샷
- 재현 단계