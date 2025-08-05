const { contextBridge, ipcRenderer } = require('electron');

// 메인 프로세스와 렌더러 프로세스 간 안전한 통신을 위한 API 노출
contextBridge.exposeInMainWorld('electronAPI', {
    // 앱 정보
    getAppVersion: () => process.env.npm_package_version || '1.0.0',
    
    // 플랫폼 정보
    getPlatform: () => process.platform,
    
    // 환경 변수 (보안을 위해 제한적으로)
    getEnvironment: () => ({
        isDesktop: true,
        nodeEnv: process.env.NODE_ENV || 'production'
    })
});