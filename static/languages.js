// 다국어 지원 시스템
const translations = {
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
        contentInput: "콘텐츠 소스",
        contentInputSubtitle: "콘텐츠 생성 방법을 선택하세요",
        youtubeUrl: "YouTube URL",
        topicInput: "주제 입력",
        promptInput: "프롬프트 입력",
        generatePost: "포스트 생성",
        
        // API Settings
        apiKey: "필수 API 키",
        geminiApiKey: "Gemini API 키",
        googleClientId: "Google Client ID",
        blogId: "블로그 ID",
        
        // Buttons
        start: "시작",
        stop: "정지",
        clear: "지우기",
        preview: "미리보기",
        publish: "발행",
        save: "저장",
        next: "다음",
        
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
    
    en: {
        // Header
        title: "AI Blogging Studio",
        
        // Sidebar sections
        postingHistory: "Posting History",
        noHistoryRecords: "No records found.",
        
        // Settings
        contentGeneration: "Content Generation (Gemini)",
        geminiModel: "Gemini Model",
        writingTone: "Writing Tone & Style",
        targetAudience: "Target Audience",
        
        // Platform settings
        platformSettings: "Platform Settings",
        platform: "Platform",
        blogAddress: "Blog Address",
        
        // Image settings
        imageSettings: "Image Settings",
        imageSource: "Image Source",
        
        // Authentication
        authentication: "Authentication",
        login: "Login",
        logout: "Logout",
        
        // Content input
        contentInput: "Content Source",
        contentInputSubtitle: "Choose your content generation method",
        youtubeUrl: "YouTube URL",
        topicInput: "Topic Input",
        promptInput: "Prompt Input",
        generatePost: "Generate Post",
        
        // API Settings
        apiKey: "Required API Keys",
        geminiApiKey: "Gemini API Key",
        googleClientId: "Google Client ID",
        blogId: "Blog ID",
        
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
        
        // Platform settings
        platformSettings: "Cài đặt nền tảng",
        platform: "Nền tảng",
        blogAddress: "Địa chỉ Blog",
        
        // Image settings
        imageSettings: "Cài đặt hình ảnh",
        imageSource: "Nguồn hình ảnh",
        
        // Authentication
        authentication: "Xác thực",
        login: "Đăng nhập",
        logout: "Đăng xuất",
        
        // Content input
        contentInput: "Nguồn nội dung",
        contentInputSubtitle: "Chọn phương pháp tạo nội dung",
        youtubeUrl: "URL YouTube",
        topicInput: "Nhập chủ đề",
        promptInput: "Nhập prompt",
        generatePost: "Tạo bài viết",
        
        // API Settings
        apiKey: "Khóa API bắt buộc",
        geminiApiKey: "Khóa API Gemini",
        googleClientId: "ID Khách hàng Google",
        blogId: "ID Blog",
        
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
    }
};

// 언어 변경 함수
function changeLanguage(lang) {
    const translation = translations[lang];
    if (!translation) {
        console.error('Language not supported:', lang);
        return;
    }
    
    console.log('언어 변경:', lang);
    
    // data-i18n 속성을 가진 모든 요소 번역
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (translation[key]) {
            element.textContent = translation[key];
        }
    });
    
    // data-i18n-option 속성을 가진 option 요소들 번역
    document.querySelectorAll('option[data-i18n-option]').forEach(option => {
        const key = option.getAttribute('data-i18n-option');
        if (translation[key]) {
            option.textContent = translation[key];
        }
    });
    
    // placeholder 번역 (data-i18n-placeholder 속성 추가 시)
    document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
        const key = element.getAttribute('data-i18n-placeholder');
        if (translation[key]) {
            element.placeholder = translation[key];
        }
    });
    
    // 현재 언어 저장
    localStorage.setItem('selectedLanguage', lang);
    
    // 변경 완료 이벤트 발생
    document.dispatchEvent(new CustomEvent('languageChanged', { detail: { language: lang } }));
}

// 언어 초기화
let isLanguageInitialized = false;

function initializeLanguage() {
    if (isLanguageInitialized) {
        console.log('언어 시스템 이미 초기화됨');
        return;
    }
    
    console.log('언어 시스템 초기화 시작');
    
    const savedLanguage = localStorage.getItem('selectedLanguage') || 'ko';
    console.log('저장된 언어:', savedLanguage);
    
    const languageSelect = document.getElementById('languageSelect');
    const mobileLangSelect = document.getElementById('mobileLangSelect');
    const tabletLangSelect = document.getElementById('tabletLangSelect');
    
    // 즉시 언어 적용
    changeLanguage(savedLanguage);
    
    // 이벤트 리스너 중복 방지
    if (languageSelect && !languageSelect.hasAttribute('data-listener-added')) {
        languageSelect.value = savedLanguage;
        languageSelect.setAttribute('data-listener-added', 'true');
        
        languageSelect.addEventListener('change', (e) => {
            console.log('데스크톱에서 언어 변경:', e.target.value);
            changeLanguage(e.target.value);
            // 모바일 셀렉트 동기화
            const mobileSelect = document.getElementById('mobileLangSelect');
            if (mobileSelect) mobileSelect.value = e.target.value;
        });
    }
    
    if (mobileLangSelect && !mobileLangSelect.hasAttribute('data-listener-added')) {
        mobileLangSelect.value = savedLanguage;
        mobileLangSelect.setAttribute('data-listener-added', 'true');
        
        mobileLangSelect.addEventListener('change', (e) => {
            console.log('모바일에서 언어 변경:', e.target.value);
            changeLanguage(e.target.value);
            // 데스크톱 셀렉트 동기화
            if (languageSelect) languageSelect.value = e.target.value;
        });
    }
    
    isLanguageInitialized = true;
    console.log('언어 시스템 초기화 완료');
}

// DOM 로드 완료 시 언어 초기화 (한번만 실행)
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        if (!isLanguageInitialized) {
            initializeLanguage();
        }
    }, 1000);
});