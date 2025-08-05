#!/usr/bin/env python3
"""
AI Blogging Studio - Desktop Application Main Entry Point
"""
import os
import sys
import time
import threading
import webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
import socket

# Add current directory and server directory to Python path
current_dir = Path(__file__).parent
server_dir = current_dir / 'server'
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(server_dir))

class AIBloggingStudioApp:
    def __init__(self):
        self.root = tk.Tk()
        self.server_process = None
        self.server_port = 5000
        self.flask_thread = None
        self.setup_window()
        self.setup_database()
        
    def setup_window(self):
        """Setup the main window"""
        self.root.title("🤖 AI 블로깅 스튜디오")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.root.winfo_screenheight() // 2) - (400 // 2)
        self.root.geometry(f"500x400+{x}+{y}")
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Title
        title_label = ttk.Label(main_frame, text="🤖 AI 블로깅 스튜디오", 
                               font=('맑은 고딕', 18, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Subtitle
        subtitle_label = ttk.Label(main_frame, text="YouTube 영상 → AI 블로그 포스트 자동 생성", 
                                  font=('맑은 고딕', 10))
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # Status
        self.status_var = tk.StringVar(value="프로그램 시작 중...")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, 
                                font=('맑은 고딕', 10))
        status_label.grid(row=2, column=0, columnspan=2, pady=(0, 10))
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="🚀 서버 시작", 
                                      command=self.start_server, state='disabled',
                                      width=15)
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.open_button = ttk.Button(button_frame, text="🌐 브라우저 열기", 
                                     command=self.open_browser, state='disabled',
                                     width=15)
        self.open_button.grid(row=0, column=1, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="⏹️ 서버 중지", 
                                     command=self.stop_server, state='disabled',
                                     width=15)
        self.stop_button.grid(row=1, column=0, padx=5, pady=5)
        
        self.quit_button = ttk.Button(button_frame, text="❌ 종료", 
                                     command=self.quit_app,
                                     width=15)
        self.quit_button.grid(row=1, column=1, padx=5, pady=5)
        
        # Info text with scrollbar
        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=5, column=0, columnspan=2, pady=(20, 0), sticky="nsew")
        
        self.info_text = tk.Text(info_frame, height=8, width=60, wrap=tk.WORD,
                                font=('맑은 고딕', 9))
        scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=scrollbar.set)
        
        self.info_text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        info_frame.columnconfigure(0, weight=1)
        info_frame.rowconfigure(0, weight=1)
        
        welcome_text = """✨ AI 블로깅 스튜디오에 오신 것을 환영합니다! ✨

🎯 주요 기능:
• YouTube 영상을 블로그 포스트로 자동 변환
• AI 기반 콘텐츠 생성 (Google Gemini)
• 다중 플랫폼 동시 발행 (Blogger, WordPress, Tistory, Naver)
• 맞춤형 톤앤매너 설정

🚀 사용 방법:
1. '서버 시작' 버튼 클릭
2. 자동으로 브라우저가 열립니다
3. YouTube URL 입력 또는 주제 입력
4. AI가 자동으로 블로그 포스트 생성
5. 원하는 플랫폼에 자동 발행

💡 팁: 처음 사용시 Google 계정 연동이 필요합니다.
"""
        
        self.info_text.insert(tk.END, welcome_text)
        self.info_text.config(state='disabled')
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # Start initialization after a short delay
        self.root.after(1500, self.initialize_app)
    
    def setup_database(self):
        """Setup database environment"""
        try:
            # Create data directory in user's documents
            import os
            data_dir = Path.home() / "Documents" / "AI_Blogging_Studio"
            data_dir.mkdir(parents=True, exist_ok=True)
            
            # Set environment variables
            db_path = data_dir / "ai_blogging_studio.db"
            os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'
            os.environ['SESSION_SECRET'] = 'ai-blogging-studio-desktop-2024-secure-key'
            
            self.log_message("데이터베이스 설정 완료")
            return True
        except Exception as e:
            messagebox.showerror("데이터베이스 오류", f"데이터베이스 설정 실패:\n{e}")
            return False
    
    def log_message(self, message):
        """Add message to info text"""
        try:
            self.info_text.config(state='normal')
            self.info_text.insert(tk.END, f"\n[{time.strftime('%H:%M:%S')}] {message}")
            self.info_text.see(tk.END)
            self.info_text.config(state='disabled')
        except:
            pass
    
    def find_free_port(self):
        """Find a free port for the server"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port
    
    def initialize_app(self):
        """Initialize the application"""
        self.progress.start()
        self.status_var.set("서버 파일 확인 중...")
        
        # Check if server files exist
        if not server_dir.exists():
            self.status_var.set("서버 파일을 찾을 수 없습니다")
            self.log_message("❌ 서버 파일이 없습니다. 설치를 확인해주세요.")
            messagebox.showerror("오류", "서버 파일이 없습니다.\n프로그램을 다시 설치해주세요.")
            self.progress.stop()
            return
        
        # Find free port
        self.server_port = self.find_free_port()
        self.log_message(f"서버 포트 확인: {self.server_port}")
        
        self.status_var.set("초기화 완료 - 서버를 시작할 수 있습니다")
        self.progress.stop()
        self.start_button.config(state='normal')
        self.log_message("✅ 초기화 완료! 서버 시작 버튼을 클릭하세요.")
    
    def start_server(self):
        """Start the Flask server"""
        if self.flask_thread and self.flask_thread.is_alive():
            self.log_message("서버가 이미 실행 중입니다")
            return
        
        try:
            self.status_var.set("서버 시작 중...")
            self.log_message("🚀 Flask 서버 시작 중...")
            self.progress.start()
            
            # Start server in a separate thread
            self.flask_thread = threading.Thread(target=self.run_flask_server, daemon=True)
            self.flask_thread.start()
            
            # Wait for server to start
            self.root.after(4000, self.check_server_status)
            
        except Exception as e:
            self.status_var.set("서버 시작 실패")
            self.log_message(f"❌ 서버 시작 실패: {e}")
            messagebox.showerror("서버 오류", f"서버 시작에 실패했습니다:\n{e}")
            self.progress.stop()
    
    def run_flask_server(self):
        """Run Flask server in background thread"""
        try:
            # Import Flask app from server directory
            import sys
            sys.path.insert(0, str(server_dir))
            
            from main import app
            self.log_message(f"Flask 앱 로드 완료, 포트 {self.server_port} 시작...")
            app.run(host='127.0.0.1', port=self.server_port, debug=False, use_reloader=False, threaded=True)
        except Exception as e:
            self.log_message(f"❌ Flask 서버 오류: {e}")
            print(f"Flask server error: {e}")
    
    def check_server_status(self):
        """Check if server is running"""
        try:
            import requests
            response = requests.get(f'http://127.0.0.1:{self.server_port}', timeout=10)
            if response.status_code == 200:
                self.status_var.set(f"✅ 서버 실행 중 (포트: {self.server_port})")
                self.log_message("✅ 서버가 성공적으로 시작되었습니다!")
                self.progress.stop()
                self.start_button.config(state='disabled')
                self.stop_button.config(state='normal')
                self.open_button.config(state='normal')
                
                # Auto-open browser after a short delay
                self.root.after(2000, self.open_browser)
            else:
                raise Exception(f"HTTP {response.status_code}")
        except Exception as e:
            self.log_message(f"서버 상태 확인 중... ({e})")
            # Retry after a moment
            self.root.after(3000, self.check_server_status)
    
    def open_browser(self):
        """Open the application in web browser"""
        try:
            url = f'http://127.0.0.1:{self.server_port}'
            webbrowser.open(url)
            self.log_message(f"🌐 브라우저에서 {url} 열기")
        except Exception as e:
            self.log_message(f"❌ 브라우저 열기 실패: {e}")
            messagebox.showerror("브라우저 오류", f"브라우저를 열 수 없습니다:\n{e}")
    
    def stop_server(self):
        """Stop the Flask server"""
        try:
            self.status_var.set("서버 중지 중...")
            self.log_message("⏹️ 서버를 중지합니다...")
            
            # Flask server will stop when the thread ends
            if self.flask_thread:
                self.flask_thread = None
            
            self.status_var.set("서버 중지됨")
            self.log_message("✅ 서버가 중지되었습니다")
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
            self.open_button.config(state='disabled')
        except Exception as e:
            self.log_message(f"❌ 서버 중지 오류: {e}")
    
    def quit_app(self):
        """Quit the application"""
        try:
            if self.flask_thread and self.flask_thread.is_alive():
                self.stop_server()
                time.sleep(1)  # Give server time to stop
            
            self.log_message("👋 프로그램을 종료합니다")
            self.root.quit()
            self.root.destroy()
        except Exception as e:
            print(f"Error during quit: {e}")
            self.root.quit()
    
    def run(self):
        """Run the application"""
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.quit_app)
            self.root.mainloop()
        except Exception as e:
            print(f"Application error: {e}")
            messagebox.showerror("프로그램 오류", f"프로그램 실행 중 오류가 발생했습니다:\n{e}")

if __name__ == "__main__":
    try:
        app = AIBloggingStudioApp()
        app.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("치명적 오류", f"프로그램을 시작할 수 없습니다:\n{e}")