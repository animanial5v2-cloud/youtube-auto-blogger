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
        
        // Content Settings Summary
        contentSettingsSummary: "콘텐츠 설정 요약",
        contentSource: "콘텐츠 소스",
        notSpecified: "지정되지 않음",
        
        // Final prompt
        finalPrompt: "최종 프롬프트 (선택적 편집)",
        
        // Placeholders
        aiContentGeneration: "AI 콘텐츠 생성",
        bloggerAccess: "Blogger 접근",
        bloggerBlogId: "Blogger 블로그 ID (숫자)",
        bloggerBlogAddress: "https://yourblog.blogspot.com",
        enterYourBlogTopic: "블로그 주제를 입력하세요...",
        aiDetailedInstructions: "AI에게 전달할 상세한 지시사항을 입력하세요...",
        finalAiInstructions: "AI에게 전달할 최종 지시사항...",
        connectGoogleAccount: "블로그 게시를 위해 Google 계정을 연결하세요",
        loginRequired: "로그인이 필요합니다",
        reviewSettingsCreate: "설정을 검토하고 블로그 콘텐츠를 생성하세요",
        customizeContentStyle: "콘텐츠 스타일과 독자층을 맞춤 설정하세요",
        itBeginners: "예: IT 초보자",
        configureAiConnections: "AI와 블로그 연결을 구성하세요",
        
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
        humorous: "유머러스한",
        
        // Desktop sidebar sections
        runSettings: "Run Settings",
        apiSettings: "API 설정",
        imageSettings: "이미지 설정",
        imageSource: "이미지 소스",
        contentSource: "콘텐츠 소스",
        postingOptions: "포스팅 옵션",
        automation: "자동화 & PC 제어",
        
        // Settings descriptions
        requiredSettings: "필수 설정",
        blogAutoGeneration: "블로그 자동 생성을 위해 필요한 API 키들을 입력하세요",
        geminiApiKeyLink: "Gemini API 키 발급받기",
        googleClientIdLink: "Google Client ID 발급받기",
        bloggerIdDescription: "Blogger 블로그 ID는 블로그 설정에서 확인 가능합니다",
        
        // Placeholders
        geminiApiKeyPlaceholder: "Gemini API 키 (AI 콘텐츠 생성용)",
        googleOauthPlaceholder: "Google OAuth Client ID (Blogger 접근용)",
        bloggerIdPlaceholder: "Blogger 블로그 ID (숫자)",
        blogAddressPlaceholder: "https://yourblog.blogspot.com",
        bloggerIdHelp: "블로그 관리 → 설정 → 기본 → 블로그 ID에서 확인 가능",
        blogAddressHelp: "본인의 Blogger 블로그 주소를 입력하세요",
        
        // Google login
        googleLogin: "Google 로그인",
        
        // Clear history
        clearAllHistory: "기록 전체 삭제",
        
        // Target audience placeholder
        targetAudiencePlaceholder: "예: IT 비전공자",
        
        // Additional labels
        geminiApiKey: "Gemini API 키",
        googleClientId: "Google Client ID",
        blogId: "블로그 ID",
        blogAddress: "블로그 주소",
        
        // Responsibility warning
        responsibilityTitle: "⚠️ 책임감 있는 사용 가이드",
        responsibilityText1: "본 프로그램은 콘텐츠 제작을 돕는",
        responsibilityTool: "'도구'",
        responsibilityText2: "이며, 생성된 콘텐츠의 저작권 및 각종 정책 준수에 대한",
        responsibilityFinal: "최종 책임은 사용자에게 있습니다.",
        responsibilityText3: "AI 생성 및 YouTube 변환 콘텐츠를 그대로 사용할 경우, Google 검색 스팸 정책, 애드센스 정책, 저작권법 등에 위배되어 불이익을 받을 수 있습니다.",
        responsibilityRecommended: "권장 사용법:",
        responsibilityText4: "생성된 콘텐츠는",
        responsibilityDraft: "'초안'",
        responsibilityText5: "으로만 활용하세요. 자신의 지식, 경험, 의견을 충분히 추가하여 독창적인 게시물로 재창조하는 것이 중요합니다.",
        
        // Gemini model options
        geminiSeries25: "Gemini 2.5 Series (멀티모달 텍스트 출력)",
        geminiSeries20: "Gemini 2.0 Series (멀티모달 텍스트 출력)",
        geminiSeries15: "Gemini 1.5 Series (안정 버전)",
        geminiSeries10: "Gemini 1.0 Series",
        geminiSpecialPurpose: "특수 목적 모델 (블로그 생성 불가)",
        geminiDeprecated: "지원 중단된 모델",
        
        // Chat messages
        chatWelcome1: "안녕하세요! AI 자동 블로깅 스튜디오입니다.",
        chatWelcome2: "아래 입력창에 포스팅할 주제, YouTube URL을 입력하거나, 오른쪽 '콘텐츠 소스'에서 동영상 파일을 선택한 후 전송 버튼(➤)을 누르세요.",
        chatWelcome3: "아이디어가 필요하시면 '주제 탐색' 모드를 켜고 대화를 시작할 수 있습니다.",
        topicDiscovery: "주제 탐색",
        chatInputPlaceholder: "여기에 포스팅 주제 또는 YouTube URL을 입력하세요..."
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
        
        // Content Settings Summary
        contentSettingsSummary: "Content Settings Summary",
        contentSource: "Content Source",
        notSpecified: "Not specified",
        
        // Final prompt
        finalPrompt: "Final Prompt (optional edit)",
        
        // Placeholders
        aiContentGeneration: "AI content generation",
        bloggerAccess: "Blogger access",
        bloggerBlogId: "Blogger blog ID (numbers)",
        bloggerBlogAddress: "https://yourblog.blogspot.com",
        enterYourBlogTopic: "Enter your blog topic...",
        aiDetailedInstructions: "Enter detailed instructions for AI...",
        finalAiInstructions: "Final instructions for AI...",
        connectGoogleAccount: "Connect your Google account for blog publishing",
        loginRequired: "Login required",
        reviewSettingsCreate: "Review settings and create your blog content",
        customizeContentStyle: "Customize your content style and audience",
        itBeginners: "e.g., IT beginners",
        configureAiConnections: "Configure your AI and blog connections",
        
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
        humorous: "Humorous",
        
        // Desktop sidebar sections
        runSettings: "Run Settings",
        apiSettings: "API Settings",
        imageSettings: "Image Settings",
        imageSource: "Image Source",
        contentSource: "Content Source",
        postingOptions: "Posting Options",
        automation: "Automation & PC Control",
        
        // Settings descriptions
        requiredSettings: "Required Settings",
        blogAutoGeneration: "Enter the required API keys for automatic blog generation",
        geminiApiKeyLink: "Get Gemini API Key",
        googleClientIdLink: "Get Google Client ID",
        bloggerIdDescription: "Blogger blog ID can be found in blog settings",
        
        // Placeholders
        geminiApiKeyPlaceholder: "Gemini API Key (for AI content generation)",
        googleOauthPlaceholder: "Google OAuth Client ID (for Blogger access)",
        bloggerIdPlaceholder: "Blogger blog ID (numbers)",
        blogAddressPlaceholder: "https://yourblog.blogspot.com",
        bloggerIdHelp: "Check in Blog Management → Settings → Basic → Blog ID",
        blogAddressHelp: "Enter your Blogger blog address",
        
        // Google login
        googleLogin: "Google Login",
        
        // Clear history
        clearAllHistory: "Clear All History",
        
        // Target audience placeholder
        targetAudiencePlaceholder: "e.g., Non-IT people",
        
        // Additional labels
        geminiApiKey: "Gemini API Key",
        googleClientId: "Google Client ID",
        blogId: "Blog ID",
        blogAddress: "Blog Address",
        
        // Responsibility warning
        responsibilityTitle: "⚠️ Responsible Usage Guide",
        responsibilityText1: "This program is a",
        responsibilityTool: "'tool'",
        responsibilityText2: "to help create content, and the",
        responsibilityFinal: "final responsibility for copyright and policy compliance of generated content lies with the user.",
        responsibilityText3: "Using AI-generated and YouTube-converted content as-is may violate Google search spam policies, AdSense policies, copyright laws, etc., and may result in penalties.",
        responsibilityRecommended: "Recommended usage:",
        responsibilityText4: "Use generated content only as a",
        responsibilityDraft: "'draft'",
        responsibilityText5: ". It's important to add your own knowledge, experience, and opinions to recreate it as original content.",
        
        // Gemini model options
        geminiSeries25: "Gemini 2.5 Series (Multimodal text output)",
        geminiSeries20: "Gemini 2.0 Series (Multimodal text output)",
        geminiSeries15: "Gemini 1.5 Series (Stable version)",
        geminiSeries10: "Gemini 1.0 Series",
        geminiSpecialPurpose: "Special purpose models (Cannot generate blogs)",
        geminiDeprecated: "Deprecated models",
        
        // Chat messages
        chatWelcome1: "Hello! This is AI Auto-Blogging Studio.",
        chatWelcome2: "Enter a posting topic or YouTube URL in the input field below, or select a video file from 'Content Source' on the right and press the send button (➤).",
        chatWelcome3: "If you need ideas, you can turn on 'Topic Discovery' mode and start a conversation.",
        topicDiscovery: "Topic Discovery",
        chatInputPlaceholder: "Enter your posting topic or YouTube URL here..."
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
        blogAddress: "Địa chỉ Blog",
        
        // Content Settings Summary
        contentSettingsSummary: "Tóm tắt cài đặt nội dung",
        contentSource: "Nguồn nội dung",
        notSpecified: "Chưa chỉ định",
        
        // Final prompt
        finalPrompt: "Prompt cuối cùng (tùy chọn chỉnh sửa)",
        
        // Placeholders
        aiContentGeneration: "Tạo nội dung AI",
        bloggerAccess: "Truy cập Blogger",
        bloggerBlogId: "ID blog Blogger (số)",
        bloggerBlogAddress: "https://yourblog.blogspot.com",
        enterYourBlogTopic: "Nhập chủ đề blog của bạn...",
        aiDetailedInstructions: "Nhập hướng dẫn chi tiết cho AI...",
        finalAiInstructions: "Hướng dẫn cuối cùng cho AI...",
        connectGoogleAccount: "Kết nối tài khoản Google của bạn để xuất bản blog",
        loginRequired: "Yêu cầu đăng nhập",
        reviewSettingsCreate: "Xem lại cài đặt và tạo nội dung blog của bạn",
        customizeContentStyle: "Tùy chỉnh phong cách nội dung và đối tượng của bạn",
        itBeginners: "ví dụ: Người mới bắt đầu IT",
        configureAiConnections: "Cấu hình AI và kết nối blog của bạn",
        
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
        humorous: "Hài hước",
        
        // Desktop sidebar sections
        runSettings: "Cài đặt Chạy",
        apiSettings: "Cài đặt API",
        imageSettings: "Cài đặt Hình ảnh",
        imageSource: "Nguồn Hình ảnh",
        contentSource: "Nguồn Nội dung",
        postingOptions: "Tùy chọn Đăng bài",
        automation: "Tự động hóa & Điều khiển PC",
        
        // Settings descriptions
        requiredSettings: "Cài đặt Bắt buộc",
        blogAutoGeneration: "Nhập các khóa API cần thiết để tự động tạo blog",
        geminiApiKeyLink: "Nhận Khóa API Gemini",
        googleClientIdLink: "Nhận Google Client ID",
        bloggerIdDescription: "ID blog Blogger có thể tìm thấy trong cài đặt blog",
        
        // Placeholders
        geminiApiKeyPlaceholder: "Khóa API Gemini (để tạo nội dung AI)",
        googleOauthPlaceholder: "Google OAuth Client ID (để truy cập Blogger)",
        bloggerIdPlaceholder: "ID blog Blogger (số)",
        blogAddressPlaceholder: "https://yourblog.blogspot.com",
        bloggerIdHelp: "Kiểm tra trong Quản lý Blog → Cài đặt → Cơ bản → ID Blog",
        blogAddressHelp: "Nhập địa chỉ blog Blogger của bạn",
        
        // Google login
        googleLogin: "Đăng nhập Google",
        
        // Clear history
        clearAllHistory: "Xóa Tất cả Lịch sử",
        
        // Target audience placeholder
        targetAudiencePlaceholder: "ví dụ: Người không chuyên IT",
        
        // Additional labels
        geminiApiKey: "Khóa API Gemini",
        googleClientId: "Google Client ID",
        blogId: "ID Blog",
        blogAddress: "Địa chỉ Blog",
        
        // Responsibility warning
        responsibilityTitle: "⚠️ Hướng dẫn Sử dụng Có trách nhiệm",
        responsibilityText1: "Chương trình này là một",
        responsibilityTool: "'công cụ'",
        responsibilityText2: "để hỗ trợ tạo nội dung, và",
        responsibilityFinal: "trách nhiệm cuối cùng về bản quyền và tuân thủ chính sách của nội dung được tạo thuộc về người dùng.",
        responsibilityText3: "Sử dụng nội dung được tạo bởi AI và chuyển đổi từ YouTube nguyên bản có thể vi phạm chính sách spam tìm kiếm Google, chính sách AdSense, luật bản quyền, v.v., và có thể dẫn đến hình phạt.",
        responsibilityRecommended: "Cách sử dụng được khuyến nghị:",
        responsibilityText4: "Chỉ sử dụng nội dung được tạo làm",
        responsibilityDraft: "'bản thảo'",
        responsibilityText5: ". Điều quan trọng là thêm kiến thức, kinh nghiệm và ý kiến của riêng bạn để tái tạo thành nội dung gốc.",
        
        // Gemini model options
        geminiSeries25: "Gemini 2.5 Series (Đầu ra văn bản đa phương thức)",
        geminiSeries20: "Gemini 2.0 Series (Đầu ra văn bản đa phương thức)",
        geminiSeries15: "Gemini 1.5 Series (Phiên bản ổn định)",
        geminiSeries10: "Gemini 1.0 Series",
        geminiSpecialPurpose: "Mô hình mục đích đặc biệt (Không thể tạo blog)",
        geminiDeprecated: "Mô hình đã ngừng hỗ trợ",
        
        // Chat messages
        chatWelcome1: "Xin chào! Đây là AI Auto-Blogging Studio.",
        chatWelcome2: "Nhập chủ đề bài viết hoặc URL YouTube vào ô nhập bên dưới, hoặc chọn tệp video từ 'Nguồn Nội dung' bên phải và nhấn nút gửi (➤).",
        chatWelcome3: "Nếu bạn cần ý tưởng, bạn có thể bật chế độ 'Khám phá Chủ đề' và bắt đầu cuộc trò chuyện.",
        topicDiscovery: "Khám phá Chủ đề",
        chatInputPlaceholder: "Nhập chủ đề bài viết hoặc URL YouTube của bạn ở đây..."
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
            if (element.tagName === 'OPTGROUP') {
                element.label = translation[key];
            } else {
                element.textContent = translation[key];
            }
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