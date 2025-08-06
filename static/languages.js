// 다국어 지원을 위한 언어 데이터
const languages = {
    ko: {
        // 헤더 및 네비게이션
        postingHistory: "포스팅 기록",
        clearAllHistory: "기록 전체 삭제",
        contentGeneration: "콘텐츠 생성 (Gemini)",
        runSettings: "실행 설정",
        
        // Gemini 설정
        geminiModel: "Gemini 모델",
        geminiSeries25: "Gemini 2.5 Series (멀티모달 텍스트 출력)",
        geminiSeries20: "Gemini 2.0 Series (멀티모달 텍스트 출력)",
        geminiSeries15: "Gemini 1.5 Series (안정 버전)",
        geminiSeries10: "Gemini 1.0 Series",
        geminiSpecialPurpose: "특수 목적 모델 (블로그 생성 불가)",
        geminiDeprecated: "지원 중단된 모델",
        
        writingTone: "글쓰기 톤 & 스타일",
        professional: "전문적인",
        friendly: "친근한",
        humorous: "유머러스한",
        persuasive: "설득적인",
        
        targetAudience: "타겟 독자",
        audiencePlaceholder: "예: IT 비전공자",
        
        // 책임감 있는 사용 가이드
        responsibleUseGuide: "⚠️ 책임감 있는 사용 가이드",
        responsibilityWarning: "본 프로그램은 콘텐츠 제작을 돕는 '도구'이며, 생성된 콘텐츠의 저작권 및 각종 정책 준수에 대한 최종 책임은 사용자에게 있습니다.",
        policyWarning: "AI 생성 및 YouTube 변환 콘텐츠를 그대로 사용할 경우, Google 검색 스팸 정책, 애드센스 정책, 저작권법 등에 위배되어 불이익을 받을 수 있습니다.",
        recommendedUsage: "권장 사용법: 생성된 콘텐츠는 '초안'으로만 활용하세요. 자신의 지식, 경험, 의견을 충분히 추가하여 독창적인 게시물로 재창조하는 것이 중요합니다.",
        
        // 로그인 및 인증
        googleLogin: "Google 로그인",
        
        // 메인 채팅 영역
        welcomeMessage: "안녕하세요! AI 자동 블로깅 스튜디오입니다.",
        instructionMessage: "아래 입력창에 포스팅할 주제, YouTube URL을 입력하거나, 오른쪽 '콘텐츠 소스'에서 동영상 파일을 선택한 후 전송 버튼(➤)을 누르세요.",
        topicDiscoveryMessage: "아이디어가 필요하시면 '주제 탐색' 모드를 켜고 대화를 시작할 수 있습니다.",
        
        topicDiscovery: "주제 탐색",
        topicDiscoveryMode: "주제 탐색",
        send: "➤",
        chatInputPlaceholder: "주제, YouTube URL, 또는 질문을 입력하세요...",
        
        // API 설정
        apiSettings: "API 설정",
        requiredSettings: "필수 설정",
        apiKeyNote: "자동 블로그 포스팅을 위해 아래 API 키들을 입력해주세요.",
        
        geminiApiKey: "Gemini API Key",
        geminiApiKeyPlaceholder: "AI 콘텐츠 생성을 위한 Gemini API 키",
        getGeminiKey: "➤ Gemini API Key 받기",
        
        googleClientId: "Google Client ID",
        googleClientIdPlaceholder: "Blogger 로그인을 위한 Google OAuth ID",
        checkBlogManagement: "★ Blog Management에서 확인 가능",
        
        blogId: "Blog ID",
        blogIdPlaceholder: "Blogger 블로그 ID (숫자)",
        
        blogAddress: "Blog Address",
        blogAddressPlaceholder: "https://yourblog.blogspot.com",
        blogAddressNote: "블로그 주소를 정확히 입력하세요 (https:// 포함)",
        
        // 이미지 소스
        imageSource: "이미지 소스",
        selectImageSource: "이미지 소스 선택",
        aiGenerated: "AI 생성 이미지",
        pexelsStock: "Pexels 무료 스톡",
        noImage: "이미지 없음",
        
        pexelsApiKey: "Pexels API Key",
        pexelsApiKeyPlaceholder: "Pexels 무료 이미지를 위한 API 키",
        getPexelsKey: "➤ Pexels API Key 받기",
        
        // 콘텐츠 소스
        contentSource: "콘텐츠 소스",
        uploadFile: "파일 업로드",
        supportedFormats: "지원 형식: 텍스트, 문서, 동영상, 오디오",
        
        sourceLanguage: "소스 언어",
        outputLanguage: "출력 언어",
        autoDetect: "자동 감지",
        korean: "한국어",
        english: "영어",
        japanese: "일본어",
        chinese: "중국어",
        vietnamese: "베트남어",
        
        // 공통
        noRecords: "기록이 없습니다."
    },
    
    en: {
        // Header and Navigation
        postingHistory: "Posting History",
        clearAllHistory: "Clear All History",
        contentGeneration: "Content Generation (Gemini)",
        runSettings: "Run Settings",
        
        // Gemini Settings
        geminiModel: "Gemini Model",
        geminiSeries25: "Gemini 2.5 Series (Multimodal Text Output)",
        geminiSeries20: "Gemini 2.0 Series (Multimodal Text Output)",
        geminiSeries15: "Gemini 1.5 Series (Stable Version)",
        geminiSeries10: "Gemini 1.0 Series",
        geminiSpecialPurpose: "Special Purpose Models (No Blog Generation)",
        geminiDeprecated: "Deprecated Models",
        
        writingTone: "Writing Tone & Style",
        professional: "Professional",
        friendly: "Friendly",
        humorous: "Humorous",
        persuasive: "Persuasive",
        
        targetAudience: "Target Audience",
        audiencePlaceholder: "e.g., Non-IT professionals",
        
        // Responsible Use Guide
        responsibleUseGuide: "⚠️ Responsible Use Guide",
        responsibilityWarning: "This program is a 'tool' to help with content creation, and the final responsibility for copyright and policy compliance of the generated content lies with the user.",
        policyWarning: "Using AI-generated and YouTube conversion content as-is may violate Google search spam policies, AdSense policies, copyright laws, etc., and may result in penalties.",
        recommendedUsage: "Recommended usage: Use generated content only as a 'draft'. It's important to add your own knowledge, experience, and opinions to recreate it as original content.",
        
        // Login and Authentication
        googleLogin: "Google Login",
        
        // Main Chat Area
        welcomeMessage: "Hello! This is AI Auto-Blogging Studio.",
        instructionMessage: "Enter a posting topic or YouTube URL in the input field below, or select a video file from 'Content Source' on the right and press the send button (➤).",
        topicDiscoveryMessage: "If you need ideas, you can turn on 'Topic Discovery' mode and start a conversation.",
        
        topicDiscovery: "Topic Discovery",
        topicDiscoveryMode: "Topic Discovery",
        send: "➤",
        chatInputPlaceholder: "Enter topic, YouTube URL, or question...",
        
        // API Settings
        apiSettings: "API Settings",
        requiredSettings: "Required Settings",
        apiKeyNote: "Please enter the API keys below for automatic blog posting.",
        
        geminiApiKey: "Gemini API Key",
        geminiApiKeyPlaceholder: "Gemini API key for AI content generation",
        getGeminiKey: "➤ Get Gemini API Key",
        
        googleClientId: "Google Client ID",
        googleClientIdPlaceholder: "Google OAuth ID for Blogger login",
        checkBlogManagement: "★ Check in Blog Management",
        
        blogId: "Blog ID",
        blogIdPlaceholder: "Blogger blog ID (numbers)",
        
        blogAddress: "Blog Address",
        blogAddressPlaceholder: "https://yourblog.blogspot.com",
        blogAddressNote: "Enter your blog address accurately (including https://)",
        
        // Image Source
        imageSource: "Image Source",
        selectImageSource: "Select Image Source",
        aiGenerated: "AI Generated Images",
        pexelsStock: "Pexels Free Stock",
        noImage: "No Image",
        
        pexelsApiKey: "Pexels API Key",
        pexelsApiKeyPlaceholder: "API key for Pexels free images",
        getPexelsKey: "➤ Get Pexels API Key",
        
        // Content Source
        contentSource: "Content Source",
        uploadFile: "Upload File",
        supportedFormats: "Supported formats: Text, Documents, Videos, Audio",
        
        sourceLanguage: "Source Language",
        outputLanguage: "Output Language",
        autoDetect: "Auto Detect",
        korean: "Korean",
        english: "English",
        japanese: "Japanese",
        chinese: "Chinese",
        vietnamese: "Vietnamese",
        
        // Common
        noRecords: "No records available."
    },
    
    vi: {
        // Header and Navigation
        postingHistory: "Lịch sử đăng bài",
        clearAllHistory: "Xóa tất cả lịch sử",
        contentGeneration: "Tạo nội dung (Gemini)",
        runSettings: "Cài đặt chạy",
        
        // Gemini Settings
        geminiModel: "Mô hình Gemini",
        geminiSeries25: "Gemini 2.5 Series (Đầu ra văn bản đa phương thức)",
        geminiSeries20: "Gemini 2.0 Series (Đầu ra văn bản đa phương thức)",
        geminiSeries15: "Gemini 1.5 Series (Phiên bản ổn định)",
        geminiSeries10: "Gemini 1.0 Series",
        geminiSpecialPurpose: "Mô hình mục đích đặc biệt (Không tạo blog)",
        geminiDeprecated: "Mô hình đã ngừng hỗ trợ",
        
        writingTone: "Giọng điệu & Phong cách viết",
        professional: "Chuyên nghiệp",
        friendly: "Thân thiện",
        humorous: "Hài hước",
        persuasive: "Thuyết phục",
        
        targetAudience: "Đối tượng mục tiêu",
        audiencePlaceholder: "VD: Người không chuyên IT",
        
        // Responsible Use Guide
        responsibleUseGuide: "⚠️ Hướng dẫn sử dụng có trách nhiệm",
        responsibilityWarning: "Chương trình này là 'công cụ' hỗ trợ tạo nội dung, và trách nhiệm cuối cùng về bản quyền và tuân thủ chính sách của nội dung được tạo thuộc về người dùng.",
        policyWarning: "Sử dụng nội dung được tạo bởi AI và chuyển đổi YouTube nguyên trạng có thể vi phạm chính sách spam tìm kiếm Google, chính sách AdSense, luật bản quyền, v.v., và có thể dẫn đến hậu quả bất lợi.",
        recommendedUsage: "Cách sử dụng được khuyến nghị: Chỉ sử dụng nội dung được tạo làm 'bản thảo'. Quan trọng là thêm kiến thức, kinh nghiệm và ý kiến của bạn để tái tạo thành nội dung độc đáo.",
        
        // Login and Authentication
        googleLogin: "Đăng nhập Google",
        
        // Main Chat Area
        welcomeMessage: "Xin chào! Đây là AI Auto-Blogging Studio.",
        instructionMessage: "Nhập chủ đề đăng bài hoặc YouTube URL vào ô nhập bên dưới, hoặc chọn file video từ 'Nguồn nội dung' bên phải và nhấn nút gửi (➤).",
        topicDiscoveryMessage: "Nếu bạn cần ý tưởng, bạn có thể bật chế độ 'Khám phá chủ đề' và bắt đầu cuộc trò chuyện.",
        
        topicDiscovery: "Khám phá chủ đề",
        topicDiscoveryMode: "Khám phá chủ đề",
        send: "➤",
        chatInputPlaceholder: "Nhập chủ đề, YouTube URL, hoặc câu hỏi...",
        
        // API Settings
        apiSettings: "Cài đặt API",
        requiredSettings: "Cài đặt bắt buộc",
        apiKeyNote: "Vui lòng nhập các khóa API bên dưới để đăng blog tự động.",
        
        geminiApiKey: "Khóa API Gemini",
        geminiApiKeyPlaceholder: "Khóa API Gemini để tạo nội dung AI",
        getGeminiKey: "➤ Lấy khóa API Gemini",
        
        googleClientId: "ID khách hàng Google",
        googleClientIdPlaceholder: "ID OAuth Google để đăng nhập Blogger",
        checkBlogManagement: "★ Kiểm tra trong Quản lý Blog",
        
        blogId: "ID Blog",
        blogIdPlaceholder: "ID blog Blogger (số)",
        
        blogAddress: "Địa chỉ Blog",
        blogAddressPlaceholder: "https://yourblog.blogspot.com",
        blogAddressNote: "Nhập địa chỉ blog chính xác (bao gồm https://)",
        
        // Image Source
        imageSource: "Nguồn hình ảnh",
        selectImageSource: "Chọn nguồn hình ảnh",
        aiGenerated: "Hình ảnh tạo bởi AI",
        pexelsStock: "Pexels miễn phí",
        noImage: "Không có hình ảnh",
        
        pexelsApiKey: "Khóa API Pexels",
        pexelsApiKeyPlaceholder: "Khóa API cho hình ảnh miễn phí Pexels",
        getPexelsKey: "➤ Lấy khóa API Pexels",
        
        // Content Source
        contentSource: "Nguồn nội dung",
        uploadFile: "Tải file lên",
        supportedFormats: "Định dạng hỗ trợ: Văn bản, Tài liệu, Video, Âm thanh",
        
        sourceLanguage: "Ngôn ngữ nguồn",
        outputLanguage: "Ngôn ngữ đầu ra",
        autoDetect: "Tự động phát hiện",
        korean: "Tiếng Hàn",
        english: "Tiếng Anh",
        japanese: "Tiếng Nhật",
        chinese: "Tiếng Trung",
        vietnamese: "Tiếng Việt",
        
        // Common
        noRecords: "Không có bản ghi nào."
    }
};

// 언어 시스템 클래스
class LanguageSystem {
    constructor() {
        this.currentLanguage = 'ko'; // 기본 언어
        this.initializeLanguageSystem();
    }
    
    initializeLanguageSystem() {
        console.log('언어 시스템 초기화 시작');
        
        // 저장된 언어 설정 불러오기
        const savedLanguage = localStorage.getItem('selectedLanguage') || 'ko';
        console.log('저장된 언어:', savedLanguage);
        
        this.setLanguage(savedLanguage);
        
        // 언어 선택 드롭다운 이벤트 리스너 추가
        this.attachLanguageSelector();
        
        console.log('언어 시스템 초기화 완료');
    }
    
    setLanguage(languageCode) {
        console.log('언어 변경:', languageCode);
        
        if (!languages[languageCode]) {
            console.error('지원하지 않는 언어:', languageCode);
            languageCode = 'ko'; // 기본값으로 대체
        }
        
        this.currentLanguage = languageCode;
        localStorage.setItem('selectedLanguage', languageCode);
        
        // UI 텍스트 업데이트
        this.updateUITexts();
        
        // 언어 선택 드롭다운 업데이트
        this.updateLanguageSelector();
    }
    
    updateUITexts() {
        const currentLang = languages[this.currentLanguage];
        
        // data-i18n 속성을 가진 모든 요소 업데이트
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            if (currentLang[key]) {
                if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                    element.placeholder = currentLang[key];
                } else if (element.tagName === 'OPTION') {
                    element.textContent = currentLang[key];
                } else if (element.tagName === 'OPTGROUP') {
                    element.label = currentLang[key];
                } else {
                    element.textContent = currentLang[key];
                }
            }
        });
        
        // data-i18n-placeholder 속성을 가진 요소들 업데이트
        document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
            const key = element.getAttribute('data-i18n-placeholder');
            if (currentLang[key]) {
                element.placeholder = currentLang[key];
            }
        });
        
        // data-i18n-title 속성을 가진 요소들 업데이트
        document.querySelectorAll('[data-i18n-title]').forEach(element => {
            const key = element.getAttribute('data-i18n-title');
            if (currentLang[key]) {
                element.title = currentLang[key];
            }
        });
    }
    
    updateLanguageSelector() {
        const languageSelect = document.getElementById('languageSelect');
        if (languageSelect) {
            languageSelect.value = this.currentLanguage;
        }
    }
    
    attachLanguageSelector() {
        const languageSelect = document.getElementById('languageSelect');
        if (languageSelect) {
            languageSelect.addEventListener('change', (e) => {
                this.setLanguage(e.target.value);
            });
        }
    }
    
    getText(key) {
        return languages[this.currentLanguage][key] || key;
    }
}

// 전역 언어 시스템 인스턴스
let languageSystem;

// DOM이 로드되면 언어 시스템 초기화
document.addEventListener('DOMContentLoaded', function() {
    console.log('언어 초기화 시작');
    languageSystem = new LanguageSystem();
});

// 전역 함수로 노출
window.setLanguage = function(languageCode) {
    if (languageSystem) {
        languageSystem.setLanguage(languageCode);
    }
};

window.getText = function(key) {
    return languageSystem ? languageSystem.getText(key) : key;
};