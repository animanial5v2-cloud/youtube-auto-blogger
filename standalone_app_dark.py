#!/usr/bin/env python3
"""
AI 블로깅 스튜디오 Pro - 강제 다크 테마
"""
import tkinter as tk
from tkinter import messagebox
import webbrowser

class AIBloggingStudioDark:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AI 블로깅 스튜디오 Pro")
        self.root.geometry("480x360")
        self.root.resizable(False, False)
        
        # 강제 다크 테마 설정
        self.root.tk_setPalette(background='#1a1a1a', foreground='#ffffff',
                               activeBackground='#333333', activeForeground='#ffffff')
        self.root.configure(bg='#1a1a1a')
        
        self.center_window()
        self.setup_ui()
    
    def center_window(self):
        x = (self.root.winfo_screenwidth() // 2) - 240
        y = (self.root.winfo_screenheight() // 2) - 180
        self.root.geometry(f"480x360+{x}+{y}")
    
    def setup_ui(self):
        # 메인 프레임 - 강제 다크
        main_frame = tk.Frame(self.root, bg='#1a1a1a')
        main_frame.pack(fill='both', expand=True, padx=20, pady=15)
        
        # 제목
        tk.Label(main_frame, text="AI 블로깅 스튜디오 Pro",
                font=('맑은 고딕', 16, 'bold'),
                bg='#1a1a1a', fg='#ffffff').pack(pady=(0, 5))
        
        # 부제목
        tk.Label(main_frame, text="YouTube 영상을 AI 블로그 포스트로 자동 변환",
                font=('맑은 고딕', 9),
                bg='#1a1a1a', fg='#aaaaaa').pack(pady=(0, 15))
        
        # 기능 박스
        feature_frame = tk.LabelFrame(main_frame, text="핵심 기능",
                                     bg='#2a2a2a', fg='#ffffff',
                                     font=('맑은 고딕', 10, 'bold'),
                                     bd=1, relief='solid')
        feature_frame.pack(fill='x', pady=(0, 15), padx=5)
        
        # 기능 목록
        features = [
            "Google Gemini AI 기반 고품질 콘텐츠 자동 생성",
            "구글 블로거, 워드프레스, 티스토리, 네이버 블로그 동시 발행",
            "맞춤형 톤앤매너 설정 및 SEO 최적화",
            "예약 발행 및 자동화 스케줄링 기능",
            "무제한 포스트 생성 및 히스토리 관리"
        ]
        
        for feature in features:
            tk.Label(feature_frame, text=f"• {feature}",
                    font=('맑은 고딕', 8),
                    bg='#2a2a2a', fg='#cccccc',
                    anchor='w').pack(fill='x', padx=10, pady=1)
        
        # 상태
        tk.Label(main_frame, text="시스템 준비 완료",
                font=('맑은 고딕', 9),
                bg='#1a1a1a', fg='#4caf50').pack(pady=(10, 15))
        
        # 시작 버튼
        start_btn = tk.Button(main_frame, text="AI 블로깅 스튜디오 시작",
                             command=self.launch_app,
                             font=('맑은 고딕', 10, 'bold'),
                             bg='#0078d4', fg='#ffffff',
                             activebackground='#106ebe', activeforeground='#ffffff',
                             width=20, height=2,
                             relief='flat', cursor='hand2')
        start_btn.pack(pady=(0, 10))
        
        # 하단 버튼들
        btn_frame = tk.Frame(main_frame, bg='#1a1a1a')
        btn_frame.pack(pady=(5, 10))
        
        buttons = [
            ("사용법", self.show_guide),
            ("정보", self.show_info),
            ("종료", self.quit_app)
        ]
        
        for text, cmd in buttons:
            tk.Button(btn_frame, text=text, command=cmd,
                     bg='#404040', fg='#ffffff',
                     activebackground='#505050', activeforeground='#ffffff',
                     width=8, font=('맑은 고딕', 8),
                     relief='flat', cursor='hand2').pack(side='left', padx=3)
        
        # 하단 텍스트
        tk.Label(main_frame, text="구매해주셔서 감사합니다 • 크몽 메시지로 문의하세요",
                font=('맑은 고딕', 7),
                bg='#1a1a1a', fg='#666666').pack(side='bottom')
    
    def launch_app(self):
        """웹 앱 실행"""
        try:
            url = "https://share-site-forge-animanial5v2.replit.app"
            webbrowser.open(url)
            messagebox.showinfo("실행 완료", "웹 브라우저에서 AI 블로깅 스튜디오가 열렸습니다!")
        except Exception as e:
            messagebox.showerror("오류", f"브라우저 실행 중 오류가 발생했습니다:\n{str(e)}")
    
    def show_guide(self):
        """사용법 안내"""
        guide_text = """AI 블로깅 스튜디오 사용법:

1. YouTube URL 입력 또는 주제 입력
2. 블로그 플랫폼 선택 (Blogger, WordPress 등)
3. AI 모델 및 톤앤매너 설정
4. 자동 포스트 생성 및 발행

자세한 사용법은 웹 애플리케이션에서 확인하세요."""
        
        messagebox.showinfo("사용법", guide_text)
    
    def show_info(self):
        """프로그램 정보"""
        info_text = """AI 블로깅 스튜디오 Pro v1.0

Google Gemini AI 기반 자동 블로그 포스팅 도구
다중 플랫폼 동시 발행 지원

개발: AI 블로깅 스튜디오 팀
문의: 크몽 메시지"""
        
        messagebox.showinfo("프로그램 정보", info_text)
    
    def quit_app(self):
        """프로그램 종료"""
        if messagebox.askquestion("종료", "프로그램을 종료하시겠습니까?") == 'yes':
            self.root.quit()
    
    def run(self):
        """앱 실행"""
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)
        self.root.mainloop()

if __name__ == "__main__":
    try:
        app = AIBloggingStudioDark()
        app.run()
    except Exception as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("시작 오류", f"프로그램을 시작할 수 없습니다:\n{str(e)}")