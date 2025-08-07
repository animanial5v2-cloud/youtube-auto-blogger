document.addEventListener('DOMContentLoaded', () => {
    // --- GLOBAL STATE & CONFIG ---
    const GOOGLE_API_SCOPES = 'https://www.googleapis.com/auth/blogger https://www.googleapis.com/auth/cloud-platform';
    let tokenClient;
    let accessToken = null;
    let isGisLoaded = false;
    let postingHistory = [];
    let isGenerating = false;
    let loopIntervalId = null;
    let isTopicDiscoveryMode = false;
    let postQueue = [];
    let currentQueueIndex = 0;
    
    // A temporary store for generated content before it's approved
    const generatedContentStore = {};

    // --- DOM ELEMENTS ---
    const themeToggleBtn = document.getElementById('themeToggleBtn');
    const loginBtn = document.getElementById('loginBtn');
    const authStatus = document.getElementById('authStatus');

    // Settings (Right Sidebar)
    const apiKeyInput = document.getElementById('apiKey');
    const clientIdInput = document.getElementById('clientId');
    const blogIdInput = document.getElementById('blogId');
    const blogAddressInput = document.getElementById('blogAddress');
    const geminiModelSelect = document.getElementById('geminiModel');
    const modelCompatibilityWarning = document.getElementById('modelCompatibilityWarning');
    const writingToneSelect = document.getElementById('writingTone');
    const targetAudienceSelect = document.getElementById('targetAudience');
    const imageSourceRadios = document.querySelectorAll('input[name="imageSource"]');
    const pexelsConfig = document.getElementById('pexelsConfig');
    const pexelsApiKeyInput = document.getElementById('pexelsApiKey');
    const aiImageConfig = document.getElementById('aiImageConfig');
    const aiImageModelSelect = document.getElementById('aiImageModel');
    const gcpProjectGroup = document.getElementById('gcpProjectGroup');
    const gcpProjectIdInput = document.getElementById('gcpProjectId');
    const uploadConfig = document.getElementById('uploadConfig');
    const userImageUpload = document.getElementById('userImageUpload');
    const imagePreviewContainer = document.getElementById('imagePreviewContainer');
    const imagePreview = document.getElementById('imagePreview');
    const removeImageBtn = document.getElementById('removeImageBtn');
    const youtubeSourceTypeRadios = document.querySelectorAll('input[name="youtubeSourceType"]');
    const youtubeAudioWarning = document.getElementById('youtubeAudioWarning');
    const videoUploadConfig = document.getElementById('videoUploadConfig');
    const userVideoUpload = document.getElementById('userVideoUpload');
    const videoFileInfo = document.getElementById('videoFileInfo');
    const videoFileName = document.getElementById('videoFileName');
    const removeVideoBtn = document.getElementById('removeVideoBtn');
    const previewBeforePostCheckbox = document.getElementById('previewBeforePost');
    // postAsDraft checkbox removed

    // Automation & PC Control
    const loopIntervalSelect = document.getElementById('loopInterval');
    const startLoopBtn = document.getElementById('startLoopBtn');
    const stopLoopBtn = document.getElementById('stopLoopBtn');
    const shutdownPcBtn = document.getElementById('shutdownPcBtn');
    const cancelShutdownBtn = document.getElementById('cancelShutdownBtn');
    const postQueueContainer = document.getElementById('postQueueContainer');

    // Chat
    const chatContainer = document.getElementById('chatContainer');
    const chatForm = document.getElementById('chatForm');
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    const topicDiscoveryBtn = document.getElementById('topicDiscoveryBtn');
    const addToQueueFromChatBtn = document.getElementById('addToQueueFromChatBtn');

    // History (Left Sidebar)
    const historyList = document.getElementById('historyList');
    const clearHistoryBtn = document.getElementById('clearHistoryBtn');

    // Modal
    const previewModal = document.getElementById('previewModal');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const cancelPostBtn = document.getElementById('cancelPostBtn');
    const approvePostBtn = document.getElementById('approvePostBtn');
    const previewTitleInput = document.getElementById('previewTitle');
    const previewBodyTextarea = document.getElementById('previewBody');
    
    // --- INITIALIZATION ---
    function loadGisScript() {
        const script = document.createElement('script');
        script.src = 'https://accounts.google.com/gsi/client';
        script.async = true;
        script.defer = true;
        script.onload = () => { isGisLoaded = true; console.log('Google GIS client loaded.'); };
        script.onerror = () => { console.error('Failed to load Google GIS client.'); };
        document.head.appendChild(script);
    }

    function initializeCollapsibles() {
        document.querySelectorAll('.collapsible-section').forEach(details => {
            const id = details.id;
            if (!id) return;
    
            if (localStorage.getItem(id + '-collapsed') === 'true') {
                details.open = false;
            } else {
                details.open = true;
            }
    
            details.addEventListener('toggle', () => {
                localStorage.setItem(id + '-collapsed', !details.open);
            });
        });
    }

    // --- EVENT LISTENERS ---
    themeToggleBtn.addEventListener('click', toggleTheme);
    loginBtn.addEventListener('click', handleAuthClick);
    chatForm.addEventListener('submit', handleChatSubmit);
    chatContainer.addEventListener('click', handleChatContainerClick);
    topicDiscoveryBtn.addEventListener('click', toggleTopicDiscoveryMode);
    
    // Settings
    geminiModelSelect.addEventListener('change', checkModelCompatibility);
    imageSourceRadios.forEach(radio => radio.addEventListener('change', handleImageSourceChange));
    aiImageModelSelect.addEventListener('change', handleAiImageModelChange);
    youtubeSourceTypeRadios.forEach(radio => radio.addEventListener('change', handleYoutubeSourceChange));
    userImageUpload.addEventListener('change', handleImageUpload);
    removeImageBtn.addEventListener('click', handleRemoveImage);
    userVideoUpload.addEventListener('change', handleVideoUpload);
    removeVideoBtn.addEventListener('click', handleRemoveVideo);

    // Automation & PC Control
    addToQueueFromChatBtn.addEventListener('click', handleAddToQueueFromChat);
    startLoopBtn.addEventListener('click', startLoop);
    stopLoopBtn.addEventListener('click', stopLoop);
    shutdownPcBtn.addEventListener('click', shutdownPC);
    cancelShutdownBtn.addEventListener('click', cancelShutdown);

    // History
    clearHistoryBtn.addEventListener('click', (e) => {
        e.preventDefault();
        handleClearHistory();
    });

    // Modal
    closeModalBtn.addEventListener('click', () => previewModal.classList.add('hidden'));
    cancelPostBtn.addEventListener('click', () => previewModal.classList.add('hidden'));
    approvePostBtn.addEventListener('click', handleApprovePost);

    // --- THEME & UI ---
    function setInitialTheme() {
        const savedTheme = localStorage.getItem('theme') || 'dark';
        document.body.setAttribute('data-theme', savedTheme);
        themeToggleBtn.textContent = savedTheme === 'dark' ? '☀️' : '🌙';
    }

    function toggleTheme() {
        const currentTheme = document.body.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.body.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        themeToggleBtn.textContent = newTheme === 'dark' ? '☀️' : '🌙';
    }

    // --- SETTINGS PERSISTENCE ---
    const settingsToPersist = {
        apiKey: apiKeyInput,
        clientId: clientIdInput,
        blogId: blogIdInput,
        blogAddress: blogAddressInput,
        pexelsApiKey: pexelsApiKeyInput,
        gcpProjectId: gcpProjectIdInput,
        geminiModel: geminiModelSelect,
        writingTone: writingToneSelect,
        targetAudience: targetAudienceSelect,
        aiImageModel: aiImageModelSelect,
        previewBeforePost: {
            get: () => previewBeforePostCheckbox.checked,
            set: (value) => { previewBeforePostCheckbox.checked = value; }
        },

    };

    function saveSettings() {
        const settings = {};
        for (const key in settingsToPersist) {
            if (settingsToPersist[key]) {
                 settings[key] = typeof settingsToPersist[key].get === 'function' ? settingsToPersist[key].get() : settingsToPersist[key].value;
            }
        }
        localStorage.setItem('autoBloggerSettings', JSON.stringify(settings));
    }

    function loadSettings() {
        const savedSettings = localStorage.getItem('autoBloggerSettings');
        if (savedSettings) {
            const settings = JSON.parse(savedSettings);
            for (const key in settings) {
                if (settingsToPersist[key] && settings[key] !== null && settings[key] !== undefined) {
                    if (typeof settingsToPersist[key].set === 'function') {
                        settingsToPersist[key].set(settings[key]);
                    } else {
                        settingsToPersist[key].value = settings[key];
                    }
                }
            }
        }
        const savedImageSource = localStorage.getItem('autoBloggerImageSource');
        if (savedImageSource) {
            const radioToSelect = document.querySelector(`input[name="imageSource"][value="${savedImageSource}"]`);
            if(radioToSelect) {
                radioToSelect.checked = true;
                handleImageSourceChange();
            }
        }
        const savedYoutubeSource = localStorage.getItem('autoBloggerYoutubeSource');
        if (savedYoutubeSource) {
            const radioToSelect = document.querySelector(`input[name="youtubeSourceType"][value="${savedYoutubeSource}"]`);
            if(radioToSelect) {
                radioToSelect.checked = true;
                handleYoutubeSourceChange();
            }
        }
        handleAiImageModelChange();
    }

    Object.values(settingsToPersist).forEach(item => {
        if (!item) return;
        const element = item.get ? (item === settingsToPersist.previewBeforePost ? previewBeforePostCheckbox : postAsDraftCheckbox) : item;
        element.addEventListener('input', saveSettings);
        element.addEventListener('change', saveSettings);
    });
    
    imageSourceRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            localStorage.setItem('autoBloggerImageSource', e.target.value);
            handleImageSourceChange();
        });
    });
    
    youtubeSourceTypeRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            localStorage.setItem('autoBloggerYoutubeSource', e.target.value);
            handleYoutubeSourceChange();
        });
    });

    // --- MODEL COMPATIBILITY ---
    function checkModelCompatibility() {
        const selectedModel = geminiModelSelect.value;
        // This set is now only for providing a non-blocking warning.
        const SPECIAL_PURPOSE_MODELS = new Set([
            'gemini-live-2.5-flash-preview',
            'gemini-2.5-flash-preview-native-audio-dialog',
            'gemini-2.5-flash-exp-native-audio-thinking-dialog',
            'gemini-2.5-flash-preview-tts',
            'gemini-2.5-pro-preview-tts',
            'gemini-2.0-flash-preview-image-generation',
            'gemini-2.0-flash-live-001'
        ]);

        const isSpecialPurpose = SPECIAL_PURPOSE_MODELS.has(selectedModel);
        const isLoggedIn = !!accessToken;

        if (isLoggedIn) {
            setChatInputEnabled(true); // Always enable if logged in.
        }

        if (isSpecialPurpose) {
            modelCompatibilityWarning.classList.remove('hidden');
            let warningText = '';
            if (selectedModel.includes('tts')) warningText = 'TTS 전용 모델입니다.';
            else if (selectedModel.includes('live')) warningText = '실시간 음성/영상 상호작용 전용 모델입니다.';
            else if (selectedModel.includes('image-generation')) warningText = '대화형 이미지 생성 전용 모델입니다.';
            else if (selectedModel.includes('audio')) warningText = '대화형 오디오 출력 전용 모델입니다.';
            else warningText = '특수 목적용 모델입니다.';
            modelCompatibilityWarning.textContent = `ℹ️ 정보: ${warningText} 선택됨. 일반 포스팅 생성에 적합하지 않을 수 있습니다.`;
        } else {
            modelCompatibilityWarning.classList.add('hidden');
            modelCompatibilityWarning.textContent = '';
        }
    }

    // --- IMAGE & VIDEO SOURCE & UPLOAD ---
    function handleImageSourceChange() {
        const selectedSource = document.querySelector('input[name="imageSource"]:checked').value;
        pexelsConfig.classList.toggle('hidden', selectedSource !== 'pexels');
        aiImageConfig.classList.toggle('hidden', selectedSource !== 'ai');
        uploadConfig.classList.toggle('hidden', selectedSource !== 'upload');
    }

    function handleAiImageModelChange() {
        const selectedModel = aiImageModelSelect.value;
        gcpProjectGroup.classList.toggle('hidden', !selectedModel.startsWith('imagen'));
        saveSettings();
    }
    
    function handleYoutubeSourceChange() {
        const sourceType = document.querySelector('input[name="youtubeSourceType"]:checked').value;
        const isAudioOrVideo = sourceType === 'audio' || sourceType === 'videoFile';
        youtubeAudioWarning.classList.toggle('hidden', !isAudioOrVideo);
        videoUploadConfig.classList.toggle('hidden', sourceType !== 'videoFile');
        updateTopicDiscoveryModeUI();
    }

    function handleImageUpload(event) {
        const file = event.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            imagePreviewContainer.classList.remove('hidden');
        };
        reader.readAsDataURL(file);
    }

    function handleRemoveImage() {
        userImageUpload.value = '';
        imagePreview.src = '#';
        imagePreviewContainer.classList.add('hidden');
    }

    function handleVideoUpload(event) {
        const file = event.target.files[0];
        if (!file) return;
        videoFileName.textContent = file.name;
        videoFileInfo.classList.remove('hidden');
        updateTopicDiscoveryModeUI();
        
        // Remove auto-trigger for video processing - respect preview settings
        if (accessToken && !isTopicDiscoveryMode) {
            addChatMessage('ai', '📹 동영상이 업로드되었습니다. 주제를 입력하고 전송 버튼을 눌러 포스팅을 생성해주세요.', true);
        }
    }

    function handleRemoveVideo() {
        userVideoUpload.value = '';
        videoFileName.textContent = '';
        videoFileInfo.classList.add('hidden');
        updateTopicDiscoveryModeUI();
    }

    // --- AUTHENTICATION ---
    function handleAuthClick() {
        if (!isGisLoaded) {
            updateAuthStatus('error', 'Google 인증 라이브러리 로딩 중...');
            return;
        }
        const clientIdVal = clientIdInput.value.trim();
        if (!clientIdVal) {
            updateAuthStatus('error', 'OAuth 클라이언트 ID를 입력하세요.');
            return;
        }
        if (accessToken) {
            google.accounts.oauth2.revoke(accessToken, () => {
                accessToken = null;
                updateAuthStatus('logged_out');
            });
        } else {
            tokenClient = window.google.accounts.oauth2.initTokenClient({
                client_id: clientIdVal,
                scope: GOOGLE_API_SCOPES,
                callback: handleTokenResponse,
            });
            tokenClient.requestAccessToken({ prompt: 'consent' });
        }
    }

    function handleTokenResponse(response) {
        if (response.error) {
            updateAuthStatus('error', `인증 오류: ${response.error}`);
            return;
        }
        accessToken = response.access_token;
        updateAuthStatus('logged_in');
    }

    function updateAuthStatus(status, message = '') {
        authStatus.classList.remove('hidden', 'success', 'error');
        const loginBtnText = loginBtn.querySelector('span');
        switch (status) {
            case 'logged_in':
                authStatus.classList.add('success');
                authStatus.textContent = '✅ 로그인 성공';
                if(loginBtnText) loginBtnText.textContent = 'Google 로그아웃';
                setChatInputEnabled(true);
                // Reset content source to default (transcript)
                const transcriptRadio = document.querySelector('input[name="youtubeSourceType"][value="transcript"]');
                if (transcriptRadio) {
                    transcriptRadio.checked = true;
                    handleYoutubeSourceTypeChange();
                }
                break;
            case 'logged_out':
                authStatus.classList.add('error');
                authStatus.textContent = '로그아웃됨';
                if(loginBtnText) loginBtnText.textContent = 'Google 로그인';
                setChatInputEnabled(false);
                stopLoop();
                break;
            case 'error':
                authStatus.classList.add('error');
                authStatus.textContent = `❌ ${message}`;
                setChatInputEnabled(false);
                stopLoop();
                break;
        }
        authStatus.classList.remove('hidden');
    }

    // --- CHAT & GENERATION LOGIC ---
    function setChatInputEnabled(enabled, placeholderText = null) {
        chatInput.disabled = !enabled;
        sendBtn.disabled = !enabled;
        addToQueueFromChatBtn.disabled = !enabled;
        topicDiscoveryBtn.disabled = !enabled;
        
        if (placeholderText) {
            chatInput.placeholder = placeholderText;
        } else if (enabled) {
            updateTopicDiscoveryModeUI();
        } else {
            // Check if we have API key
            const apiKey = apiKeyInput ? apiKeyInput.value.trim() : '';
            if (apiKey && accessToken) {
                chatInput.placeholder = "잠시만 기다려주세요...";
            } else if (apiKey) {
                chatInput.placeholder = "Google 로그인을 완료해주세요.";
            } else if (accessToken) {
                chatInput.placeholder = "Gemini API 키를 입력해주세요.";
            } else {
                chatInput.placeholder = "API 키를 입력하고 Google 인증을 완료해주세요.";
            }
        }
        
        startLoopBtn.disabled = !enabled;
    }

    function addChatMessage(sender, content, isHtml = false) {
        const messageEl = document.createElement('div');
        messageEl.classList.add('chat-message', sender);
        const bubbleEl = document.createElement('div');
        bubbleEl.classList.add('chat-bubble');
        if (isHtml) bubbleEl.innerHTML = content;
        else bubbleEl.textContent = content;
        messageEl.appendChild(bubbleEl);
        chatContainer.appendChild(messageEl);
        chatContainer.scrollTop = chatContainer.scrollHeight;
        return messageEl;
    }

    async function handleChatSubmit(e) {
        if (e) e.preventDefault();
        const userInput = chatInput.value.trim();
        if (!userInput || isGenerating) return;

        if (!validateInputs(isTopicDiscoveryMode)) return;

        addChatMessage('user', userInput);
        chatInput.value = '';
        
        setChatInputEnabled(false, "잠시만 기다려주세요...");
        isGenerating = true;

        try {
            if (isTopicDiscoveryMode) {
                await handleTopicDiscoveryChat(userInput);
            } else {
                await handlePostGeneration(userInput);
            }
        } catch (error) {
            console.error("Chat Submit Error:", error);
            addChatMessage('ai', `😔 앗, 문제가 생겼어요: ${error.message}`, true);
        } finally {
            isGenerating = false;
            setChatInputEnabled(true);
            chatInput.focus();
        }
    }

    async function handleTopicDiscoveryChat(userInput) {
        const thinkingMessage = addChatMessage('ai', '생성 중...');
        const requestBody = { 
            apiKey: apiKeyInput.value.trim(), 
            message: userInput,
            modelName: geminiModelSelect.value,
            tone: writingToneSelect.value,
            audience: targetAudienceSelect.value.trim()
        };

        const response = await fetch('/chat-for-topic', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            let errorMessage;
            try {
                // Clone response to avoid "body stream already read" error
                const responseClone = response.clone();
                const errorData = await responseClone.json();
                errorMessage = errorData.error || 'AI와 대화하는 중에 문제가 발생했습니다.';
            } catch (jsonError) {
                try {
                    const text = await response.text();
                    errorMessage = `서버 연결에 문제가 발생했습니다 (${response.status})`;
                    console.error('Server response:', text);
                } catch (textError) {
                    errorMessage = `응답 처리 중 오류가 발생했습니다 (${response.status})`;
                }
            }
            throw new Error(errorMessage);
        }

        let data;
        try {
            // Clone response to prevent "body stream already read" error
            const responseClone = response.clone();
            data = await responseClone.json();
        } catch (jsonParseError) {
            console.error('JSON parse error in handleTopicDiscoveryChat:', jsonParseError);
            try {
                const textResponse = await response.text();
                console.error('Response text:', textResponse);
                throw new Error('서버에서 올바르지 않은 응답을 받았습니다. 다시 시도해주세요.');
            } catch (textError) {
                throw new Error('응답을 읽는 중 오류가 발생했습니다. 네트워크 상태를 확인해주세요.');
            }
        }
        // Parse multiple topic suggestions for AI discovery mode
        let aiResponseHtml;
        if (isTopicDiscoveryMode && data.reply.includes('1. **') && data.reply.includes('2. **')) {
            // Multiple topic suggestions detected
            const suggestions = parseTopicSuggestions(data.reply);
            aiResponseHtml = `
                <div class="topic-suggestions-container">
                    <p class="topic-instruction">🎯 <strong>AI가 추천한 주제들입니다. 원하는 주제를 선택해서 포스팅하세요:</strong></p>
                    ${suggestions.map((suggestion, index) => `
                        <div class="topic-suggestion-item">
                            <h4>${suggestion.title}</h4>
                            <p class="topic-description">${suggestion.description}</p>
                            <button class="button-primary post-from-topic-btn" data-topic="${escapeHtml(suggestion.title + ' - ' + suggestion.description)}">
                                📝 이 주제로 포스팅하기
                            </button>
                        </div>
                    `).join('')}
                    <div class="topic-re-search-section">
                        <p class="re-search-instruction">💡 <strong>마음에 드는 주제가 없나요?</strong></p>
                        <button class="button-secondary topic-re-search-btn" data-keyword="${escapeHtml(userInput)}">
                            🔄 다른 주제 추천받기
                        </button>
                        <p class="re-search-help-text">같은 키워드로 새로운 주제들을 다시 검색합니다</p>
                    </div>
                </div>
            `;
        } else {
            // Single response or regular conversation
            aiResponseHtml = `
                <p>${escapeHtml(data.reply).replace(/\n/g, '<br>')}</p>
                ${isTopicDiscoveryMode ? `
                    <div class="topic-suggestion-actions">
                        <button class="button-secondary post-from-topic-btn" data-topic="${escapeHtml(data.reply)}">✅ 이 내용으로 포스팅하기</button>
                        <button class="button-secondary topic-re-search-btn" data-keyword="${escapeHtml(userInput)}">🔄 다른 주제 추천받기</button>
                    </div>
                    <p class="re-search-help-text">같은 키워드로 새로운 주제들을 다시 검색합니다</p>
                ` : ''}
            `;
        }
        thinkingMessage.querySelector('.chat-bubble').innerHTML = aiResponseHtml;
    }

    async function handlePostGeneration(topicOrUrl) {
        const thinkingMessage = addChatMessage('ai', `🤖 AI가 열심히 콘텐츠를 만들고 있어요: "${topicOrUrl.substring(0, 50)}..."`);
        
        const youtubeSourceType = document.querySelector('input[name="youtubeSourceType"]:checked').value;
        const videoFile = userVideoUpload.files[0];
        const isYoutubeUrl = topicOrUrl.includes('youtube.com/') || topicOrUrl.includes('youtu.be/');
        const imageSource = document.querySelector('input[name="imageSource"]:checked').value;

        let endpoint;
        const fetchOptions = { method: 'POST' };
        let requestBody;

        if (youtubeSourceType === 'videoFile' && videoFile) {
            endpoint = '/generate-post-from-video';
            const formData = new FormData();
            formData.append('video', videoFile);
            formData.append('topic', topicOrUrl);
            fetchOptions.body = formData;
        } else if (isYoutubeUrl) {
            endpoint = '/generate-post-from-youtube';
            requestBody = { urls: [topicOrUrl], youtubeSourceType };
        } else {
            endpoint = '/generate-post';
            requestBody = { topic: topicOrUrl };
        }

        const commonData = {
            apiKey: apiKeyInput.value.trim(),
            modelName: geminiModelSelect.value,
            imageSource: imageSource,
            aiImageModel: aiImageModelSelect.value,
            gcpProjectId: gcpProjectIdInput.value.trim(),
            pexelsApiKey: pexelsApiKeyInput.value.trim(),
            accessToken: accessToken,
            tone: writingToneSelect.value,
            audience: targetAudienceSelect.value.trim(),
            uploadedImageUrl: (imageSource === 'upload' && userImageUpload.files[0]) ? imagePreview.src : null
        };

        if (requestBody) { // JSON request
            Object.assign(requestBody, commonData);
            fetchOptions.headers = { 'Content-Type': 'application/json' };
            fetchOptions.body = JSON.stringify(requestBody);
        } else { // FormData request
            for (const key in commonData) {
                if (commonData[key] !== null) {
                    fetchOptions.body.append(key, commonData[key]);
                }
            }
        }

        const response = await fetch(endpoint, fetchOptions);
        if (!response.ok) {
            let errorMessage;
            try {
                // Clone response to avoid "body stream already read" error
                const responseClone = response.clone();
                const errorData = await responseClone.json();
                errorMessage = errorData.error || '알 수 없는 오류가 발생했습니다.';
            } catch (jsonError) {
                // HTML 응답인 경우 (404 등)
                try {
                    const text = await response.text();
                    if (response.status === 404) {
                        errorMessage = '요청한 기능을 찾을 수 없습니다. 서버 상태를 확인해주세요.';
                    } else {
                        errorMessage = `서버 연결 문제가 발생했습니다 (${response.status})`;
                    }
                    console.error('Server response:', text);
                } catch (textError) {
                    errorMessage = `응답 처리 중 오류가 발생했습니다 (${response.status})`;
                }
            }
            throw new Error(errorMessage);
        }

        let data;
        try {
            // Clone response to prevent "body stream already read" error
            const responseClone = response.clone();
            data = await responseClone.json();
        } catch (jsonParseError) {
            console.error('JSON parse error:', jsonParseError);
            // Try to get text response for debugging
            try {
                const textResponse = await response.text();
                console.error('Response text:', textResponse);
                throw new Error('서버에서 올바르지 않은 응답을 받았습니다. 다시 시도해주세요.');
            } catch (textError) {
                throw new Error('응답을 읽는 중 오류가 발생했습니다. 네트워크 상태를 확인해주세요.');
            }
        }
        
        // Check if response has error field
        if (data.error) {
            throw new Error(data.error);
        }
        
        if (!data.title || !data.body) {
             throw new Error("AI가 콘텐츠를 만들었지만 내용이 비어있네요. 다시 시도해보세요.");
        }
        
        thinkingMessage.remove(); // Remove "thinking" message

        // Check preview setting consistently for all posting methods
        if (previewBeforePostCheckbox.checked) {
            // Show preview for ALL posting methods when enabled
            const contentId = `content-${Date.now()}`;
            generatedContentStore[contentId] = { title: data.title, body: data.body };
            const previewText = data.body.replace(/<[^>]+>/g, '').substring(0, 200);
            const aiResponseHtml = `
                <p>✅ 포스트 초안이 생성되었습니다.</p>
                <div class="generated-post-container">
                    <h3>${data.title}</h3>
                    <div class="generated-post-body-preview">${previewText}...</div>
                    <div class="generated-post-actions">
                        <button class="button-primary show-preview-btn" data-content-id="${contentId}">미리보기 및 포스팅</button>
                    </div>
                </div>
            `;
            addChatMessage('ai', aiResponseHtml, true);
        } else {
            // Post directly for ALL posting methods when preview is disabled
            addChatMessage('ai', `✅ '발행 전 미리보기' 기능이 꺼져있습니다. "${data.title}" 포스트를 생성하여 즉시 발행합니다...`, true);
            await postToBloggerAndHandleResult(data.title, data.body, false);
        }
        return data; // Return data for loop processing
    }
    
    function handleChatContainerClick(event) {
        if (event.target.classList.contains('show-preview-btn')) {
            const contentId = event.target.dataset.contentId;
            const content = generatedContentStore[contentId];
            if (content) {
                previewTitleInput.value = content.title;
                previewBodyTextarea.value = content.body;
                approvePostBtn.dataset.contentId = contentId;
                previewModal.classList.remove('hidden');
            }
        } else if (event.target.classList.contains('post-from-topic-btn')) {
            const topic = event.target.dataset.topic;
            chatInput.value = topic;
            toggleTopicDiscoveryMode();
            chatInput.focus();
            addChatMessage('ai', `<strong>'${topic.substring(0, 50)}...'</strong> 주제로 포스팅을 준비합니다. 내용을 확인하고 전송 버튼을 누르세요.`, true);
        } else if (event.target.classList.contains('topic-re-search-btn')) {
            const keyword = event.target.dataset.keyword;
            handleTopicReSearch(keyword);
        }
    }

    function validateInputs(isDiscoveryMode = false, skipFileValidation = false) {
        if (!accessToken) { alert('Google 계정으로 먼저 로그인해주세요.'); return false; }
        if (!apiKeyInput.value.trim()) { alert('Gemini API 키를 입력해주세요.'); return false; }

        if (!isDiscoveryMode) {
            if (!blogIdInput.value.trim()) { alert('대상 블로그 ID를 입력해주세요.'); return false; }
            if (!blogAddressInput.value.trim()) { alert('블로그 주소를 입력해주세요.'); return false; }
            
            const imageSource = document.querySelector('input[name="imageSource"]:checked').value;
            if (imageSource === 'pexels' && !pexelsApiKeyInput.value.trim()) { alert('Pexels API 키를 입력해주세요.'); return false; }
            if (imageSource === 'ai' && aiImageModelSelect.value.startsWith('imagen') && !gcpProjectIdInput.value.trim()) { alert('Google Imagen 모델을 사용하려면 GCP Project ID를 입력해주세요.'); return false; }
            
            if (!skipFileValidation) {
                if (imageSource === 'upload' && !userImageUpload.files[0]) { alert('업로드할 이미지를 선택해주세요.'); return false; }
                const youtubeSourceType = document.querySelector('input[name="youtubeSourceType"]:checked').value;
                if (youtubeSourceType === 'videoFile' && !userVideoUpload.files[0]) {
                    alert('업로드할 동영상 파일을 선택해주세요.');
                    return false;
                }
            }
        }
        return true;
    }

    function parseTopicSuggestions(text) {
        const topics = [];
        const lines = text.split('\n');
        let currentTopic = null;
        
        for (const line of lines) {
            const trimmed = line.trim();
            
            // Check if this is a numbered topic (1. **title**, 2. **title**, etc.)
            const topicMatch = trimmed.match(/^\d+\.\s*\*\*(.+?)\*\*/);
            if (topicMatch) {
                if (currentTopic) {
                    topics.push(currentTopic);
                }
                currentTopic = {
                    title: topicMatch[1],
                    description: ''
                };
            } else if (currentTopic && trimmed && !trimmed.startsWith('#')) {
                // Add to description if we have a current topic and it's not empty/header
                if (currentTopic.description) {
                    currentTopic.description += ' ';
                }
                currentTopic.description += trimmed;
            }
        }
        
        // Add the last topic
        if (currentTopic) {
            topics.push(currentTopic);
        }
        
        return topics;
    }
    
    async function handleTopicReSearch(keyword) {
        if (isGenerating) return;
        
        isGenerating = true;
        setChatInputEnabled(false);
        
        try {
            const thinkingMessage = addChatMessage('ai', '새로운 주제들을 찾고 있습니다...');
            const requestBody = { 
                apiKey: apiKeyInput.value.trim(), 
                message: keyword + " (다른 관점의 새로운 주제 추천)",
                modelName: geminiModelSelect.value,
                tone: writingToneSelect.value,
                audience: targetAudienceSelect.value.trim()
            };

            const response = await fetch('/chat-for-topic', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestBody)
            });

            if (!response.ok) {
                let errorMessage;
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.error || '새 주제 검색 중 문제가 발생했습니다.';
                } catch (jsonError) {
                    errorMessage = `서버 연결에 문제가 발생했습니다 (${response.status})`;
                }
                throw new Error(errorMessage);
            }

            const data = await response.json();
            
            // Parse and display new topic suggestions
            let aiResponseHtml;
            if (data.reply.includes('1. **') && data.reply.includes('2. **')) {
                const suggestions = parseTopicSuggestions(data.reply);
                aiResponseHtml = `
                    <div class="topic-suggestions-container">
                        <p class="topic-instruction">🎯 <strong>새로운 주제 추천입니다. 원하는 주제를 선택해서 포스팅하세요:</strong></p>
                        ${suggestions.map((suggestion, index) => `
                            <div class="topic-suggestion-item">
                                <h4>${suggestion.title}</h4>
                                <p class="topic-description">${suggestion.description}</p>
                                <button class="button-primary post-from-topic-btn" data-topic="${escapeHtml(suggestion.title + ' - ' + suggestion.description)}">
                                    📝 이 주제로 포스팅하기
                                </button>
                            </div>
                        `).join('')}
                        <div class="topic-re-search-section">
                            <p class="re-search-instruction">💡 <strong>마음에 드는 주제가 없나요?</strong></p>
                            <button class="button-secondary topic-re-search-btn" data-keyword="${escapeHtml(keyword)}">
                                🔄 다른 주제 추천받기
                            </button>
                            <p class="re-search-help-text">같은 키워드로 새로운 주제들을 다시 검색합니다</p>
                        </div>
                    </div>
                `;
            } else {
                aiResponseHtml = `
                    <p>${escapeHtml(data.reply).replace(/\n/g, '<br>')}</p>
                    <div class="topic-suggestion-actions">
                        <button class="button-secondary post-from-topic-btn" data-topic="${escapeHtml(data.reply)}">✅ 이 내용으로 포스팅하기</button>
                        <button class="button-secondary topic-re-search-btn" data-keyword="${escapeHtml(keyword)}">🔄 다른 주제 추천받기</button>
                    </div>
                `;
            }
            thinkingMessage.querySelector('.chat-bubble').innerHTML = aiResponseHtml;
            
        } catch (error) {
            console.error("Topic Re-search Error:", error);
            addChatMessage('ai', `😔 새 주제 검색 중 문제가 생겼어요: ${error.message}`, true);
        } finally {
            isGenerating = false;
            setChatInputEnabled(true);
        }
    }

    function toggleTopicDiscoveryMode() {
        isTopicDiscoveryMode = !isTopicDiscoveryMode;
        updateTopicDiscoveryModeUI();
    }

    function updateTopicDiscoveryModeUI() {
        const youtubeSourceType = document.querySelector('input[name="youtubeSourceType"]:checked').value;
        const videoFileSelected = userVideoUpload.files.length > 0;

        if (isTopicDiscoveryMode) {
            topicDiscoveryBtn.classList.add('active');
            chatInput.placeholder = "Gemini와 대화하며 주제를 찾아보세요...";
        } else {
            topicDiscoveryBtn.classList.remove('active');
            if (youtubeSourceType === 'videoFile' && videoFileSelected) {
                chatInput.placeholder = "선택된 동영상을 요약할 주제를 여기에 입력하세요...";
            } else {
                chatInput.placeholder = "여기에 포스팅 주제 또는 YouTube URL을 입력하세요...";
            }
        }
    }

    // --- MODAL & POSTING ---
    async function handleApprovePost() {
        const contentId = approvePostBtn.dataset.contentId;
        const contentData = generatedContentStore[contentId];
        if (!contentData) {
            addChatMessage('ai', `❌ 포스팅 오류: 원본 콘텐츠를 찾을 수 없습니다.`, true);
            previewModal.classList.add('hidden');
            return;
        }

        const title = previewTitleInput.value;
        const content = previewBodyTextarea.value;

        approvePostBtn.disabled = true;
        approvePostBtn.textContent = '포스팅 중...';

        try {
            await postToBloggerAndHandleResult(title, content, false);
            
            // If this was a queue item, continue to next item
            if (contentId.startsWith('queue-content-') && loopIntervalId) {
                currentQueueIndex++; // Move to next queue item
            }
        } finally {
            previewModal.classList.add('hidden');
            approvePostBtn.disabled = false;
            approvePostBtn.textContent = '승인 및 공개 포스팅';
            delete generatedContentStore[contentId];
        }
    }

    async function postToBloggerAndHandleResult(title, content, isDraft) {
        try {
            const result = await postToBlogger(title, content, isDraft);
            const postUrl = result.url;
            addChatMessage('ai', `🎉 포스팅 성공! <a href="${postUrl}" target="_blank">여기서 확인하세요</a>.`, true);
            addHistoryEntry(title, postUrl);
        } catch (error) {
            console.error("Blogger Post Error:", error);
            const errorMessage = error.apiResponse ? JSON.stringify(error.apiResponse.error.message) : error.message;
            addChatMessage('ai', `❌ Blogger 포스팅 실패: ${errorMessage}`, true);
            throw error; // Re-throw to be caught by the loop handler
        }
    }

    // --- AUTOMATION & PC CONTROL ---
    function handleAddToQueueFromChat() {
        const topicOrUrl = chatInput.value.trim();
        if (!topicOrUrl) {
            alert('큐에 추가할 주제나 URL을 입력하세요.');
            return;
        }
        const queueItems = postQueueContainer.querySelectorAll('.queue-item');
        if (queueItems.length >= 5) {
            alert('최대 5개의 항목만 큐에 추가할 수 있습니다.');
            return;
        }
        
        addQueueItemToDisplay(topicOrUrl);
        chatInput.value = '';
        chatInput.focus();
        addChatMessage('ai', `✅ <strong>"${topicOrUrl.substring(0, 50)}..."</strong> 항목이 포스팅 큐에 추가되었습니다.`, true);
    }

    function addQueueItemToDisplay(text) {
        const queueItem = document.createElement('div');
        queueItem.className = 'form-group queue-item';
        queueItem.innerHTML = `
            <input type="text" class="queue-input" value="${escapeHtml(text)}" readonly>
            <button class="button-icon remove-queue-item-btn" title="큐에서 제거">&times;</button>
        `;
        postQueueContainer.appendChild(queueItem);

        queueItem.querySelector('.remove-queue-item-btn').addEventListener('click', () => {
            queueItem.remove();
        });
    }

    function startLoop() {
        // For loops, we skip file validation as it's not supported.
        if (!validateInputs(false, true)) return;

        const queueInputs = postQueueContainer.querySelectorAll('.queue-input');
        // Use a temporary variable for the new queue.
        const newQueue = Array.from(queueInputs).map(input => input.value.trim()).filter(value => value);

        if (newQueue.length === 0) {
            alert('큐에 포스팅할 항목을 하나 이상 입력해주세요.');
            return;
        }

        stopLoop(); // Clear any existing loop. This will reset the global postQueue.

        // Now, assign the new queue to the global variable.
        postQueue = newQueue;
        currentQueueIndex = 0;

        const interval = parseInt(loopIntervalSelect.value, 10);
        addChatMessage('ai', `🔁 총 ${postQueue.length}개의 포스트를 ${interval / 60000}분 간격으로 일괄 포스팅 시작합니다.`, true);

        processQueueItem(); // Process the first item immediately
        loopIntervalId = setInterval(processQueueItem, interval);

        startLoopBtn.disabled = true;
        stopLoopBtn.disabled = false;
        addToQueueFromChatBtn.disabled = true;
        postQueueContainer.querySelectorAll('input, button').forEach(el => el.disabled = true);
    }

    async function processQueueItem() {
        if (isGenerating) {
            console.log("Queue: Generation in progress, skipping interval.");
            return;
        }
        if (currentQueueIndex >= postQueue.length) {
            addChatMessage('ai', '✅ 모든 큐 작업이 완료되었습니다. 일괄 포스팅을 중지합니다.', true);
            stopLoop();
            return;
        }

        const itemToProcess = postQueue[currentQueueIndex];
        addChatMessage('ai', `➡️ 큐 작업 ${currentQueueIndex + 1}/${postQueue.length} 처리 중: "${itemToProcess.substring(0, 50)}..."`, true);
        
        isGenerating = true;
        try {
            const generatedData = await generatePostFromQueueItem(itemToProcess);
            if (generatedData) {
                // Apply preview setting consistently for queue items
                if (previewBeforePostCheckbox.checked) {
                    // Show preview for queue items when enabled
                    const contentId = `queue-content-${Date.now()}`;
                    generatedContentStore[contentId] = { title: generatedData.title, body: generatedData.body };
                    const previewText = generatedData.body.replace(/<[^>]+>/g, '').substring(0, 200);
                    const aiResponseHtml = `
                        <p>✅ 큐 아이템 ${currentQueueIndex + 1}/${postQueue.length} 포스트가 생성되었습니다.</p>
                        <div class="generated-post-container">
                            <h3>${generatedData.title}</h3>
                            <div class="generated-post-body-preview">${previewText}...</div>
                            <div class="generated-post-actions">
                                <button class="button-primary show-preview-btn" data-content-id="${contentId}">미리보기 및 포스팅</button>
                            </div>
                        </div>
                    `;
                    addChatMessage('ai', aiResponseHtml, true);
                    addChatMessage('ai', `⚠️ 미리보기가 활성화되어 일괄 포스팅이 일시정지됩니다. 승인 후 다음 항목으로 진행됩니다.`, true);
                } else {
                    // Post directly for queue items when preview is disabled
                    addChatMessage('ai', `✅ 미리보기 OFF: 큐 아이템 ${currentQueueIndex + 1} "${generatedData.title}" 즉시 발행합니다.`, true);
                    await postToBloggerAndHandleResult(generatedData.title, generatedData.body, false);
                }
            }
        } catch (error) {
            console.error("Queue Processing Error:", error);
            addChatMessage('ai', `❌ 큐 작업 실패로 인해 일괄 포스팅을 중단합니다. 오류: ${error.message}`, true);
            stopLoop();
            return;
        } finally {
            isGenerating = false;
        }

        currentQueueIndex++;
    }

    async function generatePostFromQueueItem(topicOrUrl) {
        const isYoutubeUrl = topicOrUrl.includes('youtube.com/') || topicOrUrl.includes('youtu.be/');
        const imageSource = document.querySelector('input[name="imageSource"]:checked').value;
        
        const youtubeSourceType = isYoutubeUrl ? document.querySelector('input[name="youtubeSourceType"]:checked').value : 'transcript';
        if (youtubeSourceType === 'videoFile') {
            throw new Error("일괄 포스팅 큐는 동영상 파일 업로드를 지원하지 않습니다.");
        }

        let endpoint;
        let requestBody;

        if (isYoutubeUrl) {
            endpoint = '/generate-post-from-youtube';
            requestBody = { urls: [topicOrUrl], youtubeSourceType };
        } else {
            endpoint = '/generate-post';
            requestBody = { topic: topicOrUrl };
        }

        const commonData = {
            apiKey: apiKeyInput.value.trim(),
            modelName: geminiModelSelect.value,
            imageSource: imageSource,
            aiImageModel: aiImageModelSelect.value,
            gcpProjectId: gcpProjectIdInput.value.trim(),
            pexelsApiKey: pexelsApiKeyInput.value.trim(),
            accessToken: accessToken,
            tone: writingToneSelect.value,
            audience: targetAudienceSelect.value.trim(),
            uploadedImageUrl: null // Image upload is not supported in queue mode
        };
        
        Object.assign(requestBody, commonData);

        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(`백엔드 서버 오류 (${response.status}): ${errorData.error || '알 수 없는 오류'}`);
        }
        return await response.json();
    }

    function stopLoop() {
        if (loopIntervalId) {
            clearInterval(loopIntervalId);
            loopIntervalId = null;
            if (postQueue.length > 0) {
                 addChatMessage('ai', `⏹️ 일괄 포스팅을 중지했습니다.`, true);
            }
        }
        startLoopBtn.disabled = false;
        stopLoopBtn.disabled = true;
        
        if (accessToken) {
            addToQueueFromChatBtn.disabled = false;
        }
        if(postQueueContainer) {
            postQueueContainer.querySelectorAll('input, button').forEach(el => el.disabled = false);
        }
        
        postQueue = [];
        currentQueueIndex = 0;
        isGenerating = false; // Ensure flag is reset
    }

    async function shutdownPC() {
        const queueCount = postQueueContainer.querySelectorAll('.queue-input').length;
        if (queueCount === 0) {
            alert("PC 종료를 예약하려면 먼저 큐에 항목을 추가해야 합니다.");
            return;
        }
        const interval = parseInt(loopIntervalSelect.value, 10);
        const totalTimeMs = interval * queueCount;
        const delayInSeconds = (totalTimeMs / 1000) + 300; // Add 5 min buffer
        const confirmationMessage = `총 ${queueCount}개의 작업이 완료된 후 (약 ${Math.round(delayInSeconds / 60)}분 후) PC를 종료하시겠습니까?`;

        if (confirm(confirmationMessage)) {
            try {
                await fetch('/shutdown-pc', { 
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ delay: delayInSeconds })
                });
                addChatMessage('ai', `🖥️ PC 종료가 예약되었습니다. (약 ${Math.round(delayInSeconds / 60)}분 후)`, true);
            } catch (error) {
                addChatMessage('ai', `❌ PC 종료 예약 실패: ${error.message}`, true);
            }
        }
    }

    async function cancelShutdown() {
        try {
            await fetch('/cancel-shutdown', { method: 'POST' });
            addChatMessage('ai', '✅ PC 종료가 취소되었습니다.', true);
        } catch (error) {
            addChatMessage('ai', `❌ 종료 취소 실패: ${error.message}`, true);
        }
    }

    // --- HISTORY ---
    function loadHistory() {
        const savedHistory = localStorage.getItem('postingHistory');
        if (savedHistory) postingHistory = JSON.parse(savedHistory);
        renderHistory();
    }

    function saveHistory() {
        localStorage.setItem('postingHistory', JSON.stringify(postingHistory));
    }

    function renderHistory() {
        historyList.innerHTML = '';
        if (postingHistory.length === 0) {
            historyList.innerHTML = '<li class="history-placeholder">기록이 없습니다.</li>';
            clearHistoryBtn.style.display = 'none';
        } else {
            postingHistory.slice(0, 50).forEach(item => {
                const li = document.createElement('li');
                li.className = 'history-item';
                li.innerHTML = `
                    <span class="history-title" title="${item.title}">${item.title}</span>
                    <div class="history-details">
                        <span class="history-date">${new Date(item.date).toLocaleDateString('ko-KR')}</span>
                        <a href="${item.url}" target="_blank" class="history-link">보기</a>
                    </div>`;
                historyList.appendChild(li);
            });
            clearHistoryBtn.style.display = 'block';
        }
    }

    function addHistoryEntry(title, url) {
        const newEntry = { title, url, date: new Date().toISOString() };
        postingHistory.unshift(newEntry);
        if (postingHistory.length > 50) postingHistory.pop(); 
        saveHistory();
        renderHistory();
    }

    function handleClearHistory() {
        if (confirm('정말로 모든 포스팅 기록을 삭제하시겠습니까?')) {
            postingHistory = [];
            saveHistory();
            renderHistory();
        }
    }

    // --- API CALLS ---
    async function postToBlogger(title, content, isDraft = true) {
        const BLOG_ID = blogIdInput.value.trim();
        if (!BLOG_ID) throw new Error("블로그 ID가 비어있습니다. 설정을 확인해주세요.");
        
        const API_URL = `https://www.googleapis.com/blogger/v3/blogs/${BLOG_ID}/posts/?isDraft=${isDraft}`;
        const postData = { kind: "blogger#post", blog: { id: BLOG_ID }, title, content };

        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${accessToken}`, 'Content-Type': 'application/json' },
            body: JSON.stringify(postData),
        });
        
        const result = await response.json();
        if (!response.ok) {
            const error = new Error(`Blogger API 오류 (${result.error.code}): ${result.error.message}`);
            error.apiResponse = result;
            throw error;
        }

        if (!result.url) {
            console.warn("Blogger API did not return a post URL. Falling back to editor link.");
            result.url = `https://www.blogger.com/blog/post/edit/${BLOG_ID}/${result.id}`;
        }
        
        return result;
    }

    // --- HELPERS ---
    function escapeHtml(unsafe) {
        if (typeof unsafe !== 'string') return '';
        return unsafe.replace(/&/g, "&amp;").replace(/</g, "<").replace(/>/g, ">").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
    }

    // --- KICKSTART ---
    setInitialTheme();
    loadGisScript();
    initializeCollapsibles();
    loadHistory();
    loadSettings();
    handleImageSourceChange();
    handleYoutubeSourceChange();
    setChatInputEnabled(false);
    checkModelCompatibility();
});
