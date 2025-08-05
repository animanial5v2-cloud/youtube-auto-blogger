# 🚀 AI 블로깅 스튜디오 EXE 파일 단계별 생성 가이드

## 📋 사전 준비사항

### 1. Python 설치 확인
윈도우 키 + R → `cmd` → 엔터
```cmd
python --version
```
**결과**: `Python 3.8.0` 이상이 나와야 합니다.

**Python이 없다면:**
1. https://python.org 접속
2. "Download Python" 버튼 클릭
3. 설치 시 **"Add Python to PATH"** 체크 필수!

## 🔧 단계별 EXE 생성 과정

### 1단계: 폴더 준비
1. 다운로드한 `desktop-app` 폴더를 바탕화면에 복사
2. 폴더 안에 다음 파일들이 있는지 확인:
   - `standalone_app.py` ✅
   - `build_exe.py` ✅
   - `requirements_exe.txt` ✅
   - `server/` 폴더 ✅

### 2단계: 명령 프롬프트 열기
1. `desktop-app` 폴더에서 **Shift + 우클릭**
2. **"여기서 PowerShell 창 열기"** 또는 **"여기서 명령 프롬프트 열기"** 클릭

**또는:**
1. 윈도우 키 + R → `cmd` → 엔터
2. `cd 바탕화면\desktop-app` 입력

### 3단계: 필요한 프로그램 설치
```cmd
pip install -r requirements_exe.txt
```

**진행 상황:**
- 약 5-10분 소요
- 인터넷 연결 필요
- 여러 패키지가 설치됨

**설치 완료 메시지:**
```
Successfully installed flask-3.0.0 pyinstaller-6.3.0 ...
```

### 4단계: EXE 파일 생성
```cmd
python build_exe.py
```

**진행 과정:**
1. `✅ PyInstaller already installed` 또는 설치 진행
2. `📦 Installing required packages...`
3. `✅ Spec file created`
4. `🔨 Building EXE file...`
5. `✅ EXE build completed!`

**예상 소요 시간:** 10-15분

### 5단계: 결과 확인
```cmd
dir dist
```

**생성된 파일:**
- `AI_Blogging_Studio.exe` (약 80-120MB)

## 🎯 EXE 파일 테스트

### 실행 방법:
1. `dist` 폴더 열기
2. `AI_Blogging_Studio.exe` 더블클릭
3. **보안 경고** 시: "추가 정보" → "실행"
4. 프로그램 창이 나타나면 **"서버 시작"** 버튼 클릭
5. 브라우저가 자동으로 열리고 AI 블로깅 스튜디오 실행!

## 🛠️ 문제 해결

### 에러 1: "python이 인식되지 않습니다"
**해결:** Python PATH 설정 문제
1. Python 재설치 시 "Add to PATH" 체크
2. 또는 시스템 환경변수에서 Python 경로 추가

### 에러 2: "pip install 실패"
**해결:**
```cmd
python -m pip install --upgrade pip
pip install -r requirements_exe.txt --user
```

### 에러 3: "PyInstaller 빌드 실패"
**해결:**
1. 바이러스 백신 일시 비활성화
2. 관리자 권한으로 명령 프롬프트 실행
3. Windows Defender 실시간 보호 일시 해제

### 에러 4: "EXE 실행 시 오류"
**해결:**
1. Windows Defender에서 파일 예외 추가
2. Visual C++ Redistributable 설치
3. 관리자 권한으로 실행

## 📦 최종 배포 파일 준비

### 크몽 판매용 폴더 구성:
```
AI_블로깅_스튜디오_설치파일/
├── AI_Blogging_Studio.exe     # 메인 실행 파일
├── 사용법.txt                 # 사용 방법 안내
├── 설치가이드.txt             # 설치 방법
└── 라이선스.txt               # 이용 약관
```

### 고객용 안내 메시지:
```
🎉 AI 블로깅 스튜디오 구매 감사합니다!

📁 사용 방법:
1. AI_Blogging_Studio.exe 파일을 원하는 폴더에 저장
2. 파일 더블클릭으로 실행
3. "서버 시작" 버튼 클릭
4. 브라우저에서 자동으로 열림

⚠️ 주의사항:
- 첫 실행 시 보안 경고 → "실행" 클릭
- 바이러스 백신에서 오탐지 시 예외 처리
- Windows 10 이상 권장

💡 AI 기능 사용을 위해 Google API 키가 필요합니다.
(무료 발급 가능, 설정 방법은 프로그램 내 안내 참조)

문의: 크몽 메시지로 연락주세요!
```

## ✅ 성공 확인 체크리스트

- [ ] Python 설치 완료
- [ ] 필요 패키지 설치 완료
- [ ] EXE 파일 생성 완료 (dist/AI_Blogging_Studio.exe)
- [ ] EXE 파일 실행 테스트 완료
- [ ] 서버 시작 버튼 작동 확인
- [ ] 브라우저 자동 실행 확인
- [ ] AI 블로깅 기능 테스트 완료

**모든 단계가 완료되면 크몽에서 판매할 준비가 끝납니다!**

예상 판매가: **30,000원 ~ 50,000원**
- 설치형 프로그램
- 완전한 개인 소유
- 평생 사용 가능
- 데이터 보안 완벽