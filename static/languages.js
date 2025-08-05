// 다국어 지원
const languages = {
    ko: {
        // Header
        title: "AI Blogging Studio",
        
        // Sidebar sections
        postingHistory: "포스팅 기록",
        noHistoryRecords: "기록이 없습니다.",
        
        // Settings
        contentGeneration: "콘텐츠 생성 (Gemini)",
        geminiModel: "Gemini 모델",
        writingTone: "글쓰기 톤 & 스타일",
        targetAudience: "타겟 독자층",
        
        // Platform settings
        platformSettings: "플랫폼 설정",
        platform: "플랫폼",
        blogAddress: "블로그 주소",
        
        // Image settings
        imageSettings: "이미지 설정",
        imageSource: "이미지 소스",
        
        // Authentication
        authentication: "인증",
        login: "로그인",
        logout: "로그아웃",
        
        // Content input
        contentInput: "콘텐츠 입력",
        youtubeUrl: "YouTube URL",
        topicInput: "주제 입력",
        generatePost: "포스트 생성",
        
        // Buttons
        start: "시작",
        stop: "정지",
        clear: "지우기",
        preview: "미리보기",
        publish: "발행",
        save: "저장",
        
        // Status messages
        ready: "준비 완료",
        generating: "생성 중...",
        completed: "완료",
        error: "오류",
        
        // Writing tones
        friendly: "친근한",
        professional: "전문적인",
        casual: "캐주얼한",
        formal: "격식있는",
        humorous: "유머러스한"
    },
    
    vi: {
        // Header
        title: "AI Blogging Studio",
        
        // Sidebar sections
        postingHistory: "Lịch sử đăng bài",
        noHistoryRecords: "Không có bản ghi nào.",
        
        // Settings
        contentGeneration: "Tạo nội dung (Gemini)",
        geminiModel: "Mô hình Gemini",
        writingTone: "Giọng điệu & Phong cách viết",
        targetAudience: "Đối tượng mục tiêu",
        
        // API Settings
        apiKey: "Khóa API bắt buộc",
        geminiApiKey: "Khóa API Gemini",
        googleClientId: "ID Khách hàng Google",
        blogId: "ID Blog",
        
        // Platform settings
        platformSettings: "Cài đặt nền tảng",
        platform: "Nền tảng",
        
        // Image settings
        imageSettings: "Cài đặt hình ảnh",
        imageSource: "Nguồn hình ảnh",
        
        // Authentication
        authentication: "Xác thực",
        login: "Đăng nhập",
        logout: "Đăng xuất",
        
        // Content input
        contentInput: "Nhập nội dung",
        youtubeUrl: "URL YouTube",
        topicInput: "Nhập chủ đề",
        generatePost: "Tạo bài viết",
        
        // Buttons
        start: "Bắt đầu",
        stop: "Dừng",
        clear: "Xóa",
        preview: "Xem trước",
        publish: "Xuất bản",
        save: "Lưu",
        next: "Tiếp theo",
        
        // Status messages
        ready: "Sẵn sàng",
        generating: "Đang tạo...",
        completed: "Hoàn thành",
        error: "Lỗi",
        
        // Writing tones
        friendly: "Thân thiện",
        professional: "Chuyên nghiệp",
        casual: "Thoải mái",
        formal: "Trang trọng",
        humorous: "Hài hước"
        
        // Image settings
        imageSettings: "Cài đặt hình ảnh",
        imageSource: "Nguồn hình ảnh",
        
        // Authentication
        authentication: "Xác thực",
        login: "Đăng nhập",
        logout: "Đăng xuất",
        
        // Content input
        contentInput: "Nhập nội dung",
        youtubeUrl: "URL YouTube",
        topicInput: "Nhập chủ đề",
        generatePost: "Tạo bài viết",
        
        // Buttons
        start: "Bắt đầu",
        stop: "Dừng",
        clear: "Xóa",
        preview: "Xem trước",
        publish: "Xuất bản",
        save: "Lưu",
        
        // Status messages
        ready: "Sẵn sàng",
        generating: "Đang tạo...",
        completed: "Hoàn thành",
        error: "Lỗi",
        
        // Writing tones
        friendly: "Thân thiện",
        professional: "Chuyên nghiệp",
        casual: "Thoải mái",
        formal: "Trang trọng",
        humorous: "Hài hước"
    },
    
    en: {
        // Header
        title: "AI Blogging Studio",
        
        // Sidebar sections
        postingHistory: "Posting History",
        noHistoryRecords: "No records available.",
        
        // Settings
        contentGeneration: "Content Generation (Gemini)",
        geminiModel: "Gemini Model",
        writingTone: "Writing Tone & Style",
        targetAudience: "Target Audience",
        
        // Platform settings
        platformSettings: "Platform Settings",
        platform: "Platform",
        blogAddress: "Blog Address",
        
        // API Settings
        apiKey: "Required API Key",
        geminiApiKey: "Gemini API Key",
        googleClientId: "Google Client ID",
        blogId: "Blog ID",
        
        // Image settings
        imageSettings: "Image Settings",
        imageSource: "Image Source",
        
        // Authentication
        authentication: "Authentication",
        login: "Login",
        logout: "Logout",
        
        // Content input
        contentInput: "Content Input",
        youtubeUrl: "YouTube URL",
        topicInput: "Topic Input",
        generatePost: "Generate Post",
        
        // Buttons
        start: "Start",
        stop: "Stop",
        clear: "Clear",
        preview: "Preview",
        publish: "Publish",
        save: "Save",
        next: "Next",
        
        // Status messages
        ready: "Ready",
        generating: "Generating...",
        completed: "Completed",
        error: "Error",
        
        // Writing tones
        friendly: "Friendly",
        professional: "Professional",
        casual: "Casual",
        formal: "Formal",
        humorous: "Humorous"
    }
};

// 언어 변경 함수
function changeLanguage(lang) {
    console.log('언어 변경 시도:', lang);
    
    // DOM이 완전히 로드되기를 기다림
    if (document.readyState !== 'complete') {
        setTimeout(() => changeLanguage(lang), 100);
        return;
    }
    
    const elements = document.querySelectorAll('[data-i18n]');
    console.log('번역할 요소 개수:', elements.length);
    
    elements.forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (languages[lang] && languages[lang][key]) {
            if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                element.placeholder = languages[lang][key];
            } else {
                // textContent 대신 innerHTML을 사용하여 더 확실한 변경
                element.innerHTML = languages[lang][key];
            }
            console.log('번역:', key, '→', languages[lang][key]);
            
            // 스타일 강제 업데이트
            element.style.display = 'none';
            element.offsetHeight; // reflow 강제 발생
            element.style.display = '';
        } else {
            console.warn('번역 키 누락:', key, 'for language:', lang);
        }
    });
    
    // 선택 옵션들 번역
    const optionElements = document.querySelectorAll('[data-i18n-option]');
    optionElements.forEach(element => {
        const key = element.getAttribute('data-i18n-option');
        if (languages[lang] && languages[lang][key]) {
            element.textContent = languages[lang][key];
        }
    });
    
    // 모바일 화면 제목들도 번역
    const mobileTitles = document.querySelectorAll('.screen-title');
    mobileTitles.forEach(title => {
        const screenId = title.closest('.mobile-screen')?.id;
        if (screenId) {
            switch(screenId) {
                case 'screen-api-settings':
                    title.textContent = lang === 'vi' ? 'Cài đặt API' : 'API 설정';
                    break;
                case 'screen-login':
                    title.textContent = lang === 'vi' ? 'Đăng nhập Google' : 'Google 로그인';
                    break;
                case 'screen-content-source':
                    title.textContent = lang === 'vi' ? 'Nguồn nội dung' : '콘텐츠 소스';
                    break;
                case 'screen-content-input':
                    title.textContent = lang === 'vi' ? 'Nhập nội dung' : '콘텐츠 입력';
                    break;
                case 'screen-writing-settings':
                    title.textContent = lang === 'vi' ? 'Cài đặt viết' : '글쓰기 설정';
                    break;
                case 'screen-platform-settings':
                    title.textContent = lang === 'vi' ? 'Cài đặt nền tảng' : '플랫폼 설정';
                    break;
                case 'screen-generate':
                    title.textContent = lang === 'vi' ? 'Tạo bài viết' : '생성하기';
                    break;
            }
        }
    });
    
    // 현재 언어 저장
    localStorage.setItem('selectedLanguage', lang);
    console.log('언어 변경 완료:', lang);
    
    // 변경 완료 이벤트 발생
    document.dispatchEvent(new CustomEvent('languageChanged', { detail: { language: lang } }));
}

// 언어 초기화
function initializeLanguage() {
    console.log('언어 시스템 초기화 시작');
    
    // DOM 완전 로드 대기
    const waitForDOM = () => {
        if (document.readyState !== 'complete') {
            setTimeout(waitForDOM, 50);
            return;
        }
        
        const savedLanguage = localStorage.getItem('selectedLanguage') || 'ko';
        console.log('저장된 언어:', savedLanguage);
        
        const languageSelect = document.getElementById('languageSelect');
        const mobileLangSelect = document.getElementById('mobileLangSelect');
        
        // 즉시 언어 적용
        changeLanguage(savedLanguage);
        
        // 데스크톱 언어 선택
        if (languageSelect) {
            languageSelect.value = savedLanguage;
            
            languageSelect.addEventListener('change', (e) => {
                console.log('데스크톱에서 언어 변경:', e.target.value);
                changeLanguage(e.target.value);
                // 모바일 셀렉트도 동기화
                if (mobileLangSelect) {
                    mobileLangSelect.value = e.target.value;
                }
            });
        }
        
        // 모바일 언어 선택
        if (mobileLangSelect) {
            mobileLangSelect.value = savedLanguage;
            
            mobileLangSelect.addEventListener('change', (e) => {
                console.log('모바일에서 언어 변경:', e.target.value);
                changeLanguage(e.target.value);
                // 다른 셀렉트들도 동기화
                if (languageSelect) languageSelect.value = e.target.value;
                const tabletLangSelect = document.getElementById('tabletLangSelect');
                if (tabletLangSelect) tabletLangSelect.value = e.target.value;
            });
        }
        
        // 태블릿 언어 선택
        const tabletLangSelect = document.getElementById('tabletLangSelect');
        if (tabletLangSelect) {
            tabletLangSelect.value = savedLanguage;
            
            tabletLangSelect.addEventListener('change', (e) => {
                console.log('태블릿에서 언어 변경:', e.target.value);
                changeLanguage(e.target.value);
                // 다른 셀렉트들도 동기화
                if (languageSelect) languageSelect.value = e.target.value;
                if (mobileLangSelect) mobileLangSelect.value = e.target.value;
            });
        }
        
        console.log('언어 시스템 초기화 완료');
    };
    
    waitForDOM();
}

// DOM 로드 완료 시 언어 초기화 (script.js에서 호출)
// 자체적으로도 시도
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(initializeLanguage, 2000);
});

// 페이지 완전 로드 시에도 시도
window.addEventListener('load', () => {
    setTimeout(initializeLanguage, 500);
});