#!/usr/bin/env python3
"""
AI Blogging Studio - Standalone Desktop Application
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

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / 'server'))

class AIBloggingStudioApp:
    def __init__(self):
        self.root = tk.Tk()
        self.server_process = None
        self.server_port = 5000
        self.setup_window()
        self.setup_database()
        
    def setup_window(self):
        """Setup the main window"""
        self.root.title("AI Blogging Studio")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (300 // 2)
        self.root.geometry(f"400x300+{x}+{y}")
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Title
        title_label = ttk.Label(main_frame, text="🤖 AI Blogging Studio", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Status
        self.status_var = tk.StringVar(value="준비 중...")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        
        # Buttons
        self.start_button = ttk.Button(main_frame, text="서버 시작", 
                                      command=self.start_server, state='disabled')
        self.start_button.grid(row=3, column=0, padx=(0, 10), pady=5)
        
        self.open_button = ttk.Button(main_frame, text="브라우저에서 열기", 
                                     command=self.open_browser, state='disabled')
        self.open_button.grid(row=3, column=1, padx=(10, 0), pady=5)
        
        self.stop_button = ttk.Button(main_frame, text="서버 중지", 
                                     command=self.stop_server, state='disabled')
        self.stop_button.grid(row=4, column=0, pady=5)
        
        self.quit_button = ttk.Button(main_frame, text="종료", 
                                     command=self.quit_app)
        self.quit_button.grid(row=4, column=1, pady=5)
        
        # Info text
        info_text = tk.Text(main_frame, height=6, width=50, wrap=tk.WORD)
        info_text.grid(row=5, column=0, columnspan=2, pady=(20, 0))
        info_text.insert(tk.END, 
                        "AI 블로깅 스튜디오에 오신 것을 환영합니다!\n\n"
                        "• YouTube 영상을 블로그 포스트로 변환\n"
                        "• AI 기반 콘텐츠 자동 생성\n"
                        "• 다중 플랫폼 블로그 발행\n\n"
                        "서버 시작 버튼을 클릭하여 시작하세요.")
        info_text.config(state='disabled')
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Start initialization
        self.root.after(1000, self.initialize_app)
    
    def setup_database(self):
        """Setup SQLite database"""
        try:
            # Create data directory
            data_dir = Path.home() / "AI_Blogging_Studio" / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            
            # Set database path
            db_path = data_dir / "ai_blogging_studio.db"
            os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'
            os.environ['SESSION_SECRET'] = 'ai-blogging-studio-desktop-2024'
            
            self.status_var.set("데이터베이스 준비 완료")
            return True
        except Exception as e:
            messagebox.showerror("데이터베이스 오류", f"데이터베이스 설정 실패: {e}")
            return False
    
    def initialize_app(self):
        """Initialize the application"""
        self.progress.start()
        
        # Check if server files exist
        server_dir = current_dir / 'server'
        if not server_dir.exists():
            self.status_var.set("서버 파일을 찾을 수 없습니다")
            messagebox.showerror("오류", "서버 파일이 없습니다. 설치 파일을 확인해주세요.")
            return
        
        self.status_var.set("초기화 완료")
        self.progress.stop()
        self.start_button.config(state='normal')
    
    def start_server(self):
        """Start the Flask server"""
        if self.server_process:
            return
        
        try:
            self.status_var.set("서버 시작 중...")
            self.progress.start()
            
            # Start server in a separate thread
            server_thread = threading.Thread(target=self.run_flask_server, daemon=True)
            server_thread.start()
            
            # Wait a moment for server to start
            self.root.after(3000, self.check_server_status)
            
        except Exception as e:
            self.status_var.set("서버 시작 실패")
            messagebox.showerror("서버 오류", f"서버 시작에 실패했습니다: {e}")
            self.progress.stop()
    
    def run_flask_server(self):
        """Run Flask server in background thread"""
        try:
            # Change to server directory
            os.chdir(current_dir / 'server')
            
            # Import Flask app
            from app import app
            app.run(host='127.0.0.1', port=self.server_port, debug=False, use_reloader=False)
        except Exception as e:
            print(f"Flask server error: {e}")
    
    def check_server_status(self):
        """Check if server is running"""
        try:
            import requests
            response = requests.get(f'http://127.0.0.1:{self.server_port}', timeout=5)
            if response.status_code == 200:
                self.status_var.set(f"서버 실행 중 (포트: {self.server_port})")
                self.progress.stop()
                self.start_button.config(state='disabled')
                self.stop_button.config(state='normal')
                self.open_button.config(state='normal')
                
                # Auto-open browser
                self.open_browser()
            else:
                raise Exception("Server not responding")
        except:
            # Retry after a moment
            self.root.after(2000, self.check_server_status)
    
    def open_browser(self):
        """Open the application in web browser"""
        webbrowser.open(f'http://127.0.0.1:{self.server_port}')
    
    def stop_server(self):
        """Stop the Flask server"""
        if self.server_process:
            self.server_process.terminate()
            self.server_process = None
        
        self.status_var.set("서버 중지됨")
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.open_button.config(state='disabled')
    
    def quit_app(self):
        """Quit the application"""
        if self.server_process:
            self.stop_server()
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """Run the application"""
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)
        self.root.mainloop()

if __name__ == "__main__":
    app = AIBloggingStudioApp()
    app.run()