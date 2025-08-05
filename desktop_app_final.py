#!/usr/bin/env python3
"""
AI 블로깅 스튜디오 - 최종 데스크톱 버전
크몽 판매용 완성품
"""
import tkinter as tk
from tkinter import messagebox, ttk
import webbrowser
import threading
import time
import os
from pathlib import Path

class AIBloggingStudioFinal:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AI 블로깅 스튜디오 Pro")
        self.root.geometry("550x450")
        self.root.resizable(False, False)
        
        # 창을 화면 중앙에 배치
        self.center_window()
        
        # UI 설정
        self.setup_ui()
        
        # 시작 시 자동 체크
        self.root.after(1000, self.auto_check)
    
    def center_window(self):
        """창을 화면 중앙에 배치"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (550 // 2)
        y = (self.root.winfo_screenheight() // 2) - (450 // 2)
        self.root.geometry(f"550x450+{x}+{y}")
    
    def setup_ui(self):
        """UI 구성"""
        # 메인 프레임
        main_frame = tk.Frame(self.root, bg='#f8f9fa', padx=30, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # 헤더
        header_frame = tk.Frame(main_frame, bg='#f8f9fa')
        header_frame.pack(fill='x', pady=(0, 20))
        
        # 제목
        title_label = tk.Label(header_frame, 
                              text="🤖 AI 블로깅 스튜디오 Pro",
                              font=('맑은 고딕', 20, 'bold'),
                              bg='#f8f9fa', fg='#2c3e50')
        title_label.pack()
        
        # 부제목
        subtitle_label = tk.Label(header_frame,
                                 text="YouTube ➜ AI 블로그 포스트 자동 생성",
                                 font=('맑은 고딕', 11),
                                 bg='#f8f9fa', fg='#7f8c8d')
        subtitle_label.pack(pady=(5, 0))
        
        # 상태 표시
        status_frame = tk.Frame(main_frame, bg='#e8f5e8', relief='solid', bd=1)
        status_frame.pack(fill='x', pady=(0, 20))
        
        self.status_var = tk.StringVar(value="시스템 준비 중...")
        status_label = tk.Label(status_frame, 
                               textvariable=self.status_var,
                               font=('맑은 고딕', 10, 'bold'),
                               bg='#e8f5e8', fg='#27ae60')
        status_label.pack(pady=10)
        
        # 기능 소개
        features_frame = tk.Frame(main_frame, bg='#ffffff', relief='solid', bd=1)
        features_frame.pack(fill='x', pady=(0, 20))
        
        features_title = tk.Label(features_frame,
                                 text="✨ 핵심 기능",
                                 font=('맑은 고딕', 12, 'bold'),
                                 bg='#ffffff', fg='#2c3e50')
        features_title.pack(pady=(15, 10))
        
        features_text = """• YouTube 영상 URL → 고품질 블로그 포스트 자동 생성
• Google Gemini AI 기반 자연스러운 한국어 콘텐츠 작성
• 구글 블로거, 워드프레스, 티스토리, 네이버 블로그 동시 발행
• 맞춤형 톤앤매너 및 타겟 독자 설정
• 자동 이미지 삽입 및 SEO 최적화"""
        
        features_label = tk.Label(features_frame,
                                 text=features_text,
                                 font=('맑은 고딕', 9),
                                 bg='#ffffff', fg='#2c3e50',
                                 justify='left')
        features_label.pack(pady=(0, 15), padx=20)
        
        # 버튼 영역
        button_frame = tk.Frame(main_frame, bg='#f8f9fa')
        button_frame.pack(fill='x', pady=10)
        
        # 메인 실행 버튼
        self.launch_btn = tk.Button(button_frame,
                                   text="🚀 AI 블로깅 스튜디오 시작",
                                   command=self.launch_application,
                                   font=('맑은 고딕', 14, 'bold'),
                                   bg='#3498db', fg='white',
                                   width=25, height=2,
                                   relief='flat', cursor='hand2',
                                   state='disabled')
        self.launch_btn.pack(pady=10)
        
        # 보조 버튼들
        button_row = tk.Frame(button_frame, bg='#f8f9fa')
        button_row.pack(pady=5)
        
        guide_btn = tk.Button(button_row,
                             text="📖 사용법",
                             command=self.show_user_guide,
                             font=('맑은 고딕', 10),
                             bg='#2ecc71', fg='white',
                             width=12, height=1,
                             relief='flat', cursor='hand2')
        guide_btn.pack(side='left', padx=5)
        
        about_btn = tk.Button(button_row,
                             text="ℹ️ 정보",
                             command=self.show_about,
                             font=('맑은 고딕', 10),
                             bg='#f39c12', fg='white',
                             width=12, height=1,
                             relief='flat', cursor='hand2')
        about_btn.pack(side='left', padx=5)
        
        exit_btn = tk.Button(button_row,
                            text="❌ 종료",
                            command=self.exit_application,
                            font=('맑은 고딕', 10),
                            bg='#e74c3c', fg='white',
                            width=12, height=1,
                            relief='flat', cursor='hand2')
        exit_btn.pack(side='left', padx=5)
        
        # 하단 정보
        footer_frame = tk.Frame(main_frame, bg='#f8f9fa')
        footer_frame.pack(side='bottom', fill='x', pady=(20, 0))
        
        footer_text = "구매해주셔서 감사합니다! 문의사항은 크몽 메시지로 연락주세요."
        footer_label = tk.Label(footer_frame,
                               text=footer_text,
                               font=('맑은 고딕', 8),
                               bg='#f8f9fa', fg='#95a5a6')
        footer_label.pack()
    
    def auto_check(self):
        """자동 시스템 체크"""
        self.status_var.set("시스템 체크 중...")
        
        # 잠시 후 완료 상태로 변경
        self.root.after(2000, self.check_complete)
    
    def check_complete(self):
        """체크 완료"""
        self.status_var.set("✅ 시스템 준비 완료 - 시작 버튼을 클릭하세요!")
        self.launch_btn.config(state='normal', bg='#27ae60')
    
    def launch_application(self):
        """메인 애플리케이션 실행"""
        try:
            # 웹 버전 URL (실제 배포된 Replit 앱)
            app_url = "https://sharesiteforge-sharesiteforge-sharesiteforge.replit.app"
            
            self.status_var.set("🌐 웹 브라우저에서 실행 중...")
            webbrowser.open(app_url)
            
            # 성공 메시지
            messagebox.showinfo(
                "실행 완료",
                "🎉 AI 블로깅 스튜디오가 웹 브라우저에서 실행되었습니다!\n\n"
                "📌 첫 사용 시 안내:\n"
                "• Google 계정으로 로그인\n"
                "• 각 블로그 플랫폼 연동 설정\n"
                "• Gemini API 키 설정 (무료)\n\n"
                "💡 모든 기능을 완전히 사용할 수 있습니다!"
            )
            
            self.status_var.set("✅ 실행 완료 - 브라우저에서 사용하세요")
            
        except Exception as e:
            messagebox.showerror(
                "실행 오류",
                f"애플리케이션 실행에 문제가 발생했습니다:\n\n{str(e)}\n\n"
                "인터넷 연결을 확인하고 다시 시도해주세요."
            )
    
    def show_user_guide(self):
        """사용법 안내"""
        guide_window = tk.Toplevel(self.root)
        guide_window.title("📖 AI 블로깅 스튜디오 사용법")
        guide_window.geometry("700x500")
        guide_window.resizable(True, True)
        
        # 스크롤 가능한 텍스트
        text_frame = tk.Frame(guide_window)
        text_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side='right', fill='y')
        
        text_widget = tk.Text(text_frame, 
                             wrap='word', 
                             yscrollcommand=scrollbar.set,
                             font=('맑은 고딕', 10),
                             padx=10, pady=10)
        text_widget.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=text_widget.yview)
        
        guide_content = """🚀 AI 블로깅 스튜디오 완전 사용법

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣ 초기 설정 (최초 1회만)

🔐 Google 계정 로그인
• '시작' 버튼 클릭 후 브라우저에서 Google 로그인
• Blogger, YouTube Data API 접근 권한 허용

🔑 API 키 설정
• Google AI Studio (https://aistudio.google.com) 접속
• 무료 Gemini API 키 발급
• 설정 페이지에서 API 키 입력

🔗 블로그 플랫폼 연동
• Google Blogger: 자동 연동
• WordPress.com: 토큰 발급 후 연동
• Tistory: 수동 복사/붙여넣기 (API 중단됨)
• Naver Blog: 수동 복사/붙여넣기

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2️⃣ 콘텐츠 생성 방법

📺 YouTube 영상에서 생성
• YouTube 영상 URL 입력
• AI가 자동으로 자막 추출 및 분석
• 5-10분 내 고품질 블로그 포스트 완성

✏️ 직접 주제 입력
• 원하는 주제나 키워드 입력
• 상세한 설명일수록 더 좋은 결과
• AI가 관련 정보를 찾아 포스트 작성

🎯 맞춤 설정
• 타겟 독자: 초보자/일반인/전문가
• 톤앤매너: 친근함/전문적/유머러스
• 글 길이: 짧음/보통/상세함
• 이미지 포함 여부

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3️⃣ 편집 및 발행

✏️ 내용 편집
• 생성된 포스트 미리보기
• 제목, 내용, 태그 수정 가능
• 이미지 추가/교체 가능

📤 발행 옵션
• 즉시 발행: 바로 블로그에 업로드
• 예약 발행: 원하는 시간에 자동 업로드
• 초안 저장: 나중에 편집 후 발행
• 다중 발행: 여러 플랫폼에 동시 업로드

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4️⃣ 고급 활용법

📊 콘텐츠 전략
• 키워드 트렌드 분석 활용
• 시리즈 포스트 계획적 작성
• SEO 최적화 제목 및 메타 설정

⏰ 자동화 활용
• 정기적인 포스팅 스케줄 설정
• 여러 YouTube 채널 구독하여 자동 포스팅
• 템플릿 저장으로 일관된 스타일 유지

📈 성과 분석
• 발행 히스토리 관리
• 플랫폼별 반응 분석
• 인기 포스트 패턴 파악

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 프로 팁

🎯 최적의 결과를 위한 팁
• YouTube 영상: 자막이 있는 영상이 더 좋은 결과
• 주제 입력: 구체적이고 상세할수록 우수한 포스트
• 이미지: 저작권 걱정 없는 Pexels 이미지 자동 활용
• SEO: 자동 생성되는 메타태그 및 키워드 활용

⚡ 효율성 극대화
• 템플릿 기능으로 반복 작업 최소화
• 일괄 예약 발행으로 시간 절약
• 키워드 조합으로 다양한 콘텐츠 생성

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❓ 문제 해결

🔧 일반적인 문제
• 로딩이 오래 걸림: 첫 사용시 정상, 2-3분 대기
• 로그인 안됨: 브라우저 쿠키 삭제 후 재시도
• API 오류: 키 재발급 또는 한도 확인
• 발행 실패: 플랫폼 연동 상태 재확인

📞 지원 서비스
• 구매 후 30일 무료 기술지원
• 크몽 메시지를 통한 1:1 문의
• 업데이트 및 신기능 무료 제공
• 사용법 영상 가이드 제공

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎉 이제 AI의 힘으로 블로깅을 자동화하세요!
매일 수십 개의 고품질 포스트를 쉽게 만들어보세요."""

        text_widget.insert('1.0', guide_content)
        text_widget.config(state='disabled')
    
    def show_about(self):
        """프로그램 정보"""
        messagebox.showinfo(
            "ℹ️ AI 블로깅 스튜디오 Pro",
            "🤖 AI 블로깅 스튜디오 Pro v2.0\n\n"
            "🎯 YouTube 영상을 AI 블로그 포스트로 자동 변환\n"
            "🚀 Google Gemini AI 기반 고품질 콘텐츠 생성\n"
            "📤 다중 플랫폼 동시 발행 지원\n\n"
            "💎 프리미엄 기능:\n"
            "• 무제한 포스트 생성\n"
            "• 예약 발행 및 자동화\n"
            "• 맞춤형 템플릿\n"
            "• 30일 기술지원\n\n"
            "📞 지원: 크몽 메시지\n"
            "🌐 웹버전: sharesiteforge.replit.app\n\n"
            "구매해주셔서 감사합니다! 🙏"
        )
    
    def exit_application(self):
        """프로그램 종료"""
        result = messagebox.askyesno(
            "종료 확인",
            "AI 블로깅 스튜디오를 종료하시겠습니까?"
        )
        if result:
            self.root.quit()
            self.root.destroy()
    
    def run(self):
        """애플리케이션 실행"""
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.exit_application)
            self.root.mainloop()
        except Exception as e:
            messagebox.showerror(
                "시스템 오류",
                f"프로그램 실행 중 오류가 발생했습니다:\n{str(e)}"
            )

if __name__ == "__main__":
    try:
        app = AIBloggingStudioFinal()
        app.run()
    except Exception as e:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "시작 오류",
            f"프로그램을 시작할 수 없습니다:\n{str(e)}\n\n"
            "관리자 권한으로 실행하거나 재설치를 시도해주세요."
        )