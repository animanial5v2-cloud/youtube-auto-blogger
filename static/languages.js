// 다국어 지원
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
        
        // Platform settings
        platformSettings: "Cài đặt nền tảng",
        platform: "Nền tảng",
        blogAddress: "Địa chỉ blog",
        
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
    const elements = document.querySelectorAll('[data-i18n]');
    elements.forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (translations[lang] && translations[lang][key]) {
            if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                element.placeholder = translations[lang][key];
            } else {
                element.textContent = translations[lang][key];
            }
        }
    });
    
    // 선택 옵션들 번역
    const optionElements = document.querySelectorAll('[data-i18n-option]');
    optionElements.forEach(element => {
        const key = element.getAttribute('data-i18n-option');
        if (translations[lang] && translations[lang][key]) {
            element.textContent = translations[lang][key];
        }
    });
    
    // 현재 언어 저장
    localStorage.setItem('selectedLanguage', lang);
}

// 언어 초기화
function initializeLanguage() {
    const savedLanguage = localStorage.getItem('selectedLanguage') || 'ko';
    const languageSelect = document.getElementById('languageSelect');
    
    if (languageSelect) {
        languageSelect.value = savedLanguage;
        changeLanguage(savedLanguage);
        
        languageSelect.addEventListener('change', (e) => {
            changeLanguage(e.target.value);
        });
    }
}

// DOM 로드 완료 시 언어 초기화
document.addEventListener('DOMContentLoaded', initializeLanguage);