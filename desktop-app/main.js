const { app, BrowserWindow, Menu, dialog, shell } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

let mainWindow;
let serverProcess;
const PORT = 5000;

// Flask 서버 시작
function startFlaskServer() {
    const pythonPath = process.platform === 'win32' ? 'python' : 'python3';
    const serverPath = path.join(__dirname, 'server');
    
    return new Promise((resolve, reject) => {
        serverProcess = spawn(pythonPath, ['-m', 'gunicorn', '--bind', `127.0.0.1:${PORT}`, 'main:app'], {
            cwd: serverPath,
            env: {
                ...process.env,
                PYTHONPATH: serverPath,
                SESSION_SECRET: 'desktop-app-secret-key-' + Math.random().toString(36).substring(7)
            }
        });

        serverProcess.stdout.on('data', (data) => {
            console.log(`Flask: ${data}`);
        });

        serverProcess.stderr.on('data', (data) => {
            console.error(`Flask Error: ${data}`);
        });

        serverProcess.on('close', (code) => {
            console.log(`Flask server exited with code ${code}`);
        });

        // 서버 시작 대기
        setTimeout(() => {
            resolve();
        }, 3000);
    });
}

// 메인 윈도우 생성
function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        },
        icon: path.join(__dirname, 'assets', 'icon.png'),
        title: 'AI Blogging Studio',
        show: false
    });

    // 로딩 화면 표시
    mainWindow.loadFile(path.join(__dirname, 'loading.html'));
    
    mainWindow.once('ready-to-show', () => {
        mainWindow.show();
    });

    // Flask 서버 시작 후 메인 앱 로드
    startFlaskServer().then(() => {
        setTimeout(() => {
            mainWindow.loadURL(`http://127.0.0.1:${PORT}`);
        }, 2000);
    }).catch((error) => {
        console.error('Failed to start Flask server:', error);
        dialog.showErrorBox('서버 시작 실패', 'Flask 서버를 시작할 수 없습니다.');
    });

    // 외부 링크는 기본 브라우저에서 열기
    mainWindow.webContents.setWindowOpenHandler(({ url }) => {
        shell.openExternal(url);
        return { action: 'deny' };
    });

    // 메뉴 설정
    createMenu();
}

// 애플리케이션 메뉴 생성
function createMenu() {
    const template = [
        {
            label: '파일',
            submenu: [
                {
                    label: '새로고침',
                    accelerator: 'F5',
                    click: () => {
                        mainWindow.reload();
                    }
                },
                {
                    label: '개발자 도구',
                    accelerator: 'F12',
                    click: () => {
                        mainWindow.webContents.toggleDevTools();
                    }
                },
                { type: 'separator' },
                {
                    label: '종료',
                    accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
                    click: () => {
                        app.quit();
                    }
                }
            ]
        },
        {
            label: '도움말',
            submenu: [
                {
                    label: 'AI Blogging Studio 정보',
                    click: () => {
                        dialog.showMessageBox(mainWindow, {
                            type: 'info',
                            title: 'AI Blogging Studio',
                            message: 'AI Auto-Blogging Studio v1.0.0',
                            detail: 'YouTube 영상과 주제를 기반으로 자동으로 블로그 포스트를 생성하는 AI 도구입니다.'
                        });
                    }
                }
            ]
        }
    ];

    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
}

// 앱 준비 완료
app.whenReady().then(() => {
    createWindow();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

// 모든 윈도우가 닫혔을 때
app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

// 앱 종료 시 서버 프로세스 종료
app.on('before-quit', () => {
    if (serverProcess) {
        serverProcess.kill();
    }
});

app.on('will-quit', () => {
    if (serverProcess) {
        serverProcess.kill();
    }
});