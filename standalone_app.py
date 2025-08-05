#!/usr/bin/env python3
"""
AI 블로깅 스튜디오 Pro - 최종 완성본
올바른 URL 적용
"""
import tkinter as tk
from tkinter import messagebox
import webbrowser
import threading
import time

class AIBloggingStudioFinal:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AI 블로깅 스튜디오 Pro")
        self.root.geometry("550x420")
        self.root.resizable(False, False)
        self.center_window()
        self.setup_ui()
    
    def center_window(self):
        x = (self.root.winfo_screenwidth() // 2) - 275
        y = (self.root.winfo_screenheight() // 2) - 210
        self.root.geometry(f"550x420+{x}+{y}")
    
    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg='#f8f9fa', padx=25, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # 헤더
        tk.Label(main_frame, text="🤖 AI 블로깅 스튜디오 Pro", 
                font=('맑은 고딕', 19, 'bold'),
                bg='#f8f9fa', fg='#2c3e50').pack(pady=(0, 8))
        
        tk.Label(main_frame, text="YouTube 영상을 AI 블로그 포스트로 자동 변환", 
                font=('맑은 고딕', 11),
                bg='#f8f9fa', fg='#7f8c8d').pack(pady=(0, 15))
        
        # 기능 소개
        feature_frame = tk.Frame(main_frame, bg='#ffffff', relief='solid', bd=1)
        feature_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(feature_frame, text="✨ 핵심 기능", 
                font=('맑은 고딕', 12, 'bold'),
                bg='#ffffff', fg='#2c3e50').pack(pady=(12, 8))
        
        features = """• Google Gemini AI 기반 고품질 콘텐츠 자동 생성
• 구글 블로거, 워드프레스, 티스토리, 네이버 블로그 동시 발행
• 맞춤형 톤앤매너 설정 및 SEO 최적화
• 예약 발행 및 자동화 스케줄링 기능
• 무제한 포스트 생성 및 히스토리 관리"""
        
        tk.Label(feature_frame, text=features, 
                font=('맑은 고딕', 9),
                bg='#ffffff', justify='left', fg='#2c3e50').pack(pady=(0, 12), padx=15)
        
        # 상태 표시
        self.status_var = tk.StringVar(value="시스템 준비 완료 ✅")
        status_label = tk.Label(main_frame, textvariable=self.status_var,
                               font=('맑은 고딕', 10, 'bold'),
                               bg='#f8f9fa', fg='#27ae60')
        status_label.pack(pady=(0, 15))
        
        # 메인 실행 버튼
        launch_btn = tk.Button(main_frame, text="🚀 AI 블로깅 스튜디오 시작",
                              command=self.launch_app,
                              font=('맑은 고딕', 14, 'bold'),
                              bg='#3498db', fg='white',
                              width=25, height=2,
                              relief='flat', cursor='hand2')
        launch_btn.pack(pady=(0, 15))
        
        # 보조 버튼들
        button_frame = tk.Frame(main_frame, bg='#f8f9fa')
        button_frame.pack(pady=(0, 15))
        
        tk.Button(button_frame, text="📖 사용법", command=self.show_guide,
                 bg='#2ecc71', fg='white', width=12, height=1,
                 font=('맑은 고딕', 10), relief='flat', cursor='hand2').pack(side='left', padx=5)
        
        tk.Button(button_frame, text="ℹ️ 정보", command=self.show_info,
                 bg='#f39c12', fg='white', width=12, height=1,
                 font=('맑은 고딕', 10), relief='flat', cursor='hand2').pack(side='left', padx=5)
        
        tk.Button(button_frame, text="❌ 종료", command=self.quit_app,
                 bg='#e74c3c', fg='white', width=12, height=1,
                 font=('맑은 고딕', 10), relief='flat', cursor='hand2').pack(side='left', padx=5)
        
        # 하단 정보
        tk.Label(main_frame, text="구매해주셔서 감사합니다! 문의사항은 크몽 메시지로 연락주세요.",
                font=('맑은 고딕', 8), bg='#f8f9fa', fg='#95a5a6').pack(side='bottom')
    
    def launch_app(self):
        """메인 앱 실행"""
        try:
            self.status_var.set("🌐 웹 브라우저에서 실행 중...")
            
            # 정확한 Replit 앱 URL
            app_url = "https://a29c9aae-a815-4ca1-ab77-1a3014b50f24-00-egu3q7nb1g24.picard.replit.dev"
            webbrowser.open(app_url)
            
            messagebox.showinfo("실행 완료!", 
                               "🎉 AI 블로깅 스튜디오가 웹 브라우저에서 실행되었습니다!\n\n"
                               "📌 첫 사용 시 설정 단계:\n"
                               "1️⃣ Google 계정으로 로그인\n"
                               "2️⃣ Gemini API 키 설정 (무료)\n"
                               "3️⃣ 블로그 플랫폼 연동\n\n"
                               "💡 모든 기능을 완전히 사용할 수 있습니다!\n"
                               "궁금한 사항은 크몽 메시지로 문의해주세요.")
            
            self.status_var.set("✅ 실행 완료 - 브라우저에서 사용하세요!")
            
        except Exception as e:
            messagebox.showerror("실행 오류", 
                               f"웹 브라우저 실행에 실패했습니다:\n{str(e)}\n\n"
                               "인터넷 연결을 확인하고 다시 시도해주세요.")
            self.status_var.set("❌ 실행 실패 - 다시 시도해주세요")
    
    def show_guide(self):
        """사용법 안내"""
        guide_text = """🚀 AI 블로깅 스튜디오 사용법

1️⃣ 초기 설정
• '시작' 버튼을 클릭해 웹 버전 실행
• Google 계정으로 로그인
• Google AI Studio에서 Gemini API 키 발급 (무료)
• 설정 페이지에서 API 키 입력

2️⃣ 블로그 플랫폼 연동
• Google Blogger: 자동 연동
• WordPress: 토큰 발급 후 연동
• Tistory, Naver: 수동 복사/붙여넣기

3️⃣ 콘텐츠 생성
• YouTube URL 입력 또는 직접 주제 작성
• 타겟 독자, 톤앤매너, 글 길이 설정
• AI가 5-10분 내 고품질 포스트 생성

4️⃣ 편집 및 발행
• 생성된 포스트 검토 및 수정
• 원하는 플랫폼 선택 후 발행
• 예약 발행 및 자동화 설정 가능

💡 최고의 결과를 위한 팁:
• 자막이 있는 YouTube 영상 사용
• 구체적이고 상세한 주제 입력
• 정기적인 포스팅 스케줄 활용"""
        
        messagebox.showinfo("📖 사용법 안내", guide_text)
    
    def show_info(self):
        """프로그램 정보"""
        info_text = """🤖 AI 블로깅 스튜디오 Pro v2.0

🎯 핵심 기능:
• YouTube → AI 블로그 자동 생성
• 4개 플랫폼 동시 발행 지원
• 무제한 포스트 생성
• 예약 발행 및 자동화
• 맞춤형 템플릿 저장

🔧 기술 사양:
• Google Gemini AI 기반
• 다국어 지원 (한국어 최적화)
• SEO 최적화 자동 적용
• 클라우드 기반 안정성

📞 고객 지원:
• 구매 후 30일 무료 기술지원
• 크몽 메시지를 통한 1:1 문의
• 정기 업데이트 및 신기능 추가
• 사용법 가이드 및 튜토리얼 제공

🌐 웹 버전: 언제든 브라우저에서 접속 가능
💎 프리미엄: 모든 기능 무제한 사용

구매해주셔서 감사합니다! 🙏"""
        
        messagebox.showinfo("ℹ️ 프로그램 정보", info_text)
    
    def quit_app(self):
        """프로그램 종료"""
        if messagebox.askyesno("종료 확인", "AI 블로깅 스튜디오를 종료하시겠습니까?"):
            self.root.quit()
            self.root.destroy()
    
    def run(self):
        """앱 실행"""
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)
        self.root.mainloop()

if __name__ == "__main__":
    try:
        app = AIBloggingStudioFinal()
        app.run()
    except Exception as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("시작 오류", f"프로그램을 시작할 수 없습니다:\n{str(e)}")