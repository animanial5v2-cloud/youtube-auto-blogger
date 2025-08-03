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
    const targetAudienceInput = document.getElementById('targetAudience');
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
    const postAsDraftCheckbox = document.getElementById('postAsDraft');
    
    // Platform selection elements
    const platformSelect = document.getElementById('platformSelect');

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
    themeToggleBtn?.addEventListener('click', toggleTheme);
    loginBtn?.addEventListener('click', handleAuthClick);
    chatForm?.addEventListener('submit', handleChatSubmit);
    chatContainer?.addEventListener('click', handleChatContainerClick);
    topicDiscoveryBtn?.addEventListener('click', toggleTopicDiscoveryMode);
    
    // Settings
    geminiModelSelect?.addEventListener('change', checkModelCompatibility);
    imageSourceRadios?.forEach(radio => radio.addEventListener('change', handleImageSourceChange));
    aiImageModelSelect?.addEventListener('change', handleAiImageModelChange);
    youtubeSourceTypeRadios?.forEach(radio => radio.addEventListener('change', handleYoutubeSourceChange));
    userImageUpload?.addEventListener('change', handleImageUpload);
    removeImageBtn?.addEventListener('click', handleRemoveImage);
    userVideoUpload?.addEventListener('change', handleVideoUpload);
    removeVideoBtn?.addEventListener('click', handleRemoveVideo);
    platformSelect?.addEventListener('change', handlePlatformChange);

    // Automation & PC Control
    addToQueueFromChatBtn?.addEventListener('click', handleAddToQueueFromChat);
    startLoopBtn?.addEventListener('click', startLoop);
    stopLoopBtn?.addEventListener('click', stopLoop);
    shutdownPcBtn?.addEventListener('click', shutdownPC);
    cancelShutdownBtn?.addEventListener('click', cancelShutdown);

    // History
    clearHistoryBtn?.addEventListener('click', (e) => {
        e.preventDefault();
        handleClearHistory();
    });

    // Modal
    closeModalBtn?.addEventListener('click', () => previewModal?.classList.add('hidden'));
    cancelPostBtn?.addEventListener('click', () => previewModal?.classList.add('hidden'));
    approvePostBtn?.addEventListener('click', handleApprovePost);

    // --- THEME & UI ---
    function setInitialTheme() {
        const savedTheme = localStorage.getItem('theme') || 'dark';
        document.body.setAttribute('data-theme', savedTheme);
        if (themeToggleBtn) {
            themeToggleBtn.textContent = savedTheme === 'dark' ? '☀️' : '🌙';
        }
    }

    function toggleTheme() {
        const currentTheme = document.body.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.body.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        if (themeToggleBtn) {
            themeToggleBtn.textContent = newTheme === 'dark' ? '☀️' : '🌙';
        }
    }

    // --- SETTINGS PERSISTENCE ---
    async function saveSettings() {
        const settings = {
            apiKey: apiKeyInput?.value || '',
            clientId: clientIdInput?.value || '',
            blogId: blogIdInput?.value || '',
            blogAddress: blogAddressInput?.value || '',
            pexelsApiKey: pexelsApiKeyInput?.value || '',
            gcpProjectId: gcpProjectIdInput?.value || '',
            geminiModel: geminiModelSelect?.value || 'gemini-1.5-pro-latest',
            writingTone: writingToneSelect?.value || '친근한 (Friendly)',
            targetAudience: targetAudienceInput?.value || '',
            aiImageModel: aiImageModelSelect?.value || 'imagen-2',
            previewBeforePost: previewBeforePostCheckbox?.checked || false,
            postAsDraft: postAsDraftCheckbox?.checked || false,
        };

        try {
            const response = await fetch('/api/settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(settings)
            });
            
            if (!response.ok) {
                console.error('Failed to save settings');
            }
        } catch (error) {
            console.error('Error saving settings:', error);
        }
    }

    async function loadSettings() {
        try {
            const response = await fetch('/api/settings');
            if (response.ok) {
                const settings = await response.json();
                
                if (apiKeyInput) apiKeyInput.value = settings.apiKey || '';
                if (clientIdInput) clientIdInput.value = settings.clientId || '';
                if (blogIdInput) blogIdInput.value = settings.blogId || '';
                if (blogAddressInput) blogAddressInput.value = settings.blogAddress || '';
                if (pexelsApiKeyInput) pexelsApiKeyInput.value = settings.pexelsApiKey || '';
                if (gcpProjectIdInput) gcpProjectIdInput.value = settings.gcpProjectId || '';
                if (geminiModelSelect) geminiModelSelect.value = settings.geminiModel || 'gemini-1.5-pro-latest';
                if (writingToneSelect) writingToneSelect.value = settings.writingTone || '친근한 (Friendly)';
                if (targetAudienceInput) targetAudienceInput.value = settings.targetAudience || '';
                if (aiImageModelSelect) aiImageModelSelect.value = settings.aiImageModel || 'imagen-2';
                if (previewBeforePostCheckbox) previewBeforePostCheckbox.checked = settings.previewBeforePost || false;
                if (postAsDraftCheckbox) postAsDraftCheckbox.checked = settings.postAsDraft || false;
            }
        } catch (error) {
            console.error('Error loading settings:', error);
        }
        
        // Load saved radio button states from localStorage
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

    // Add event listeners for auto-save
    [apiKeyInput, clientIdInput, blogIdInput, blogAddressInput, pexelsApiKeyInput, 
     gcpProjectIdInput, geminiModelSelect, writingToneSelect, targetAudienceInput, 
     aiImageModelSelect, previewBeforePostCheckbox, postAsDraftCheckbox].forEach(element => {
        if (element) {
            element.addEventListener('input', saveSettings);
            element.addEventListener('change', saveSettings);
        }
    });
    
    imageSourceRadios?.forEach(radio => {
        radio.addEventListener('change', (e) => {
            localStorage.setItem('autoBloggerImageSource', e.target.value);
            handleImageSourceChange();
        });
    });
    
    youtubeSourceTypeRadios?.forEach(radio => {
        radio.addEventListener('change', (e) => {
            localStorage.setItem('autoBloggerYoutubeSource', e.target.value);
            handleYoutubeSourceChange();
        });
    });

    // --- HISTORY MANAGEMENT ---
    async function loadHistory() {
        try {
            const response = await fetch('/api/history');
            if (response.ok) {
                const history = await response.json();
                postingHistory = history;
                updateHistoryDisplay();
            }
        } catch (error) {
            console.error('Error loading history:', error);
        }
    }

    function updateHistoryDisplay() {
        if (!historyList) return;
        
        historyList.innerHTML = '';
        
        if (postingHistory.length === 0) {
            const placeholder = document.createElement('li');
            placeholder.className = 'history-placeholder';
            placeholder.textContent = '기록이 없습니다.';
            historyList.appendChild(placeholder);
            return;
        }
        
        postingHistory.forEach(post => {
            const item = document.createElement('li');
            item.className = 'history-item';
            item.innerHTML = `
                <span class="history-title">${post.title}</span>
                <div class="history-details">
                    <span>${new Date(post.created_at).toLocaleDateString()}</span>
                    ${post.blogger_url ? `<a href="${post.blogger_url}" target="_blank" class="history-link">View Post</a>` : ''}
                </div>
            `;
            historyList.appendChild(item);
        });
    }

    async function handleClearHistory() {
        if (!confirm('모든 포스팅 기록을 삭제하시겠습니까?')) return;
        
        try {
            const response = await fetch('/api/history', { method: 'DELETE' });
            if (response.ok) {
                postingHistory = [];
                updateHistoryDisplay();
                addChatMessage('ai', '포스팅 기록이 모두 삭제되었습니다.');
            }
        } catch (error) {
            console.error('Error clearing history:', error);
            addChatMessage('ai', '기록 삭제 중 오류가 발생했습니다.');
        }
    }

    // --- CHAT FUNCTIONALITY ---
    function addChatMessage(type, content) {
        if (!chatContainer) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${type}`;
        
        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'chat-bubble';
        
        if (typeof content === 'string') {
            bubbleDiv.innerHTML = content;
        } else {
            bubbleDiv.appendChild(content);
        }
        
        messageDiv.appendChild(bubbleDiv);
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    async function handleChatSubmit(e) {
        e.preventDefault();
        
        if (!chatInput || isGenerating) return;
        
        const input = chatInput.value.trim();
        if (!input) return;
        
        // Add user message
        addChatMessage('user', input);
        chatInput.value = '';
        
        if (isTopicDiscoveryMode) {
            handleTopicDiscoveryChat(input);
        } else {
            await handleContentGeneration(input);
        }
    }

    function handleTopicDiscoveryChat(input) {
        // Simple topic discovery responses
        const responses = [
            "흥미로운 주제네요! 다음과 같은 관련 주제들은 어떠신가요?",
            "그 주제에 대해 더 구체적으로 어떤 부분에 초점을 맞추고 싶으신가요?",
            "좋은 아이디어입니다. 타겟 독자층을 염두에 두고 어떤 접근 방식을 원하시나요?"
        ];
        
        const randomResponse = responses[Math.floor(Math.random() * responses.length)];
        addChatMessage('ai', randomResponse);
    }

    async function handleContentGeneration(input) {
        setGeneratingState(true);
        
        try {
            const settings = await getCurrentSettings();
            
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    input: input,
                    settings: settings,
                    accessToken: accessToken
                })
            });
            
            if (response.ok) {
                const result = await response.json();
                
                if (previewBeforePostCheckbox?.checked) {
                    showPreviewModal(result);
                } else {
                    await publishPost(result.post_id);
                }
                
                // Reload history
                await loadHistory();
                
            } else {
                const error = await response.json();
                addChatMessage('ai', `오류가 발생했습니다: ${error.error}`);
            }
            
        } catch (error) {
            console.error('Content generation error:', error);
            addChatMessage('ai', '콘텐츠 생성 중 오류가 발생했습니다.');
        } finally {
            setGeneratingState(false);
        }
    }

    async function getCurrentSettings() {
        const response = await fetch('/api/settings');
        return response.ok ? await response.json() : {};
    }

    function setGeneratingState(generating) {
        isGenerating = generating;
        if (sendBtn) sendBtn.disabled = generating;
        if (chatInput) chatInput.disabled = generating;
        
        if (generating) {
            addChatMessage('ai', '콘텐츠를 생성하고 있습니다... 잠시만 기다려주세요.');
        }
    }

    // --- MODAL FUNCTIONALITY ---
    function showPreviewModal(result) {
        if (!previewModal) return;
        
        generatedContentStore.currentPost = result;
        
        if (previewTitleInput) previewTitleInput.value = result.title;
        if (previewBodyTextarea) previewBodyTextarea.value = result.content;
        
        previewModal.classList.remove('hidden');
    }

    async function handleApprovePost() {
        if (!generatedContentStore.currentPost) return;
        
        const postId = generatedContentStore.currentPost.post_id;
        await publishPost(postId);
        
        if (previewModal) previewModal.classList.add('hidden');
        generatedContentStore.currentPost = null;
    }

    async function publishPost(postId) {
        const selectedPlatform = document.getElementById('platformSelect')?.value || 'blogger';
        
        // Validate platform-specific requirements
        let publishData = {
            post_id: postId,
            platform: selectedPlatform,
            is_draft: postAsDraftCheckbox?.checked || false
        };
        
        if (selectedPlatform === 'blogger') {
            if (!accessToken || !document.getElementById('bloggerBlogId')?.value) {
                addChatMessage('ai', 'Google 로그인과 Blogger 블로그 ID가 필요합니다.');
                return;
            }
            publishData.access_token = accessToken;
            publishData.blog_id = document.getElementById('bloggerBlogId').value;
            
        } else if (selectedPlatform === 'wordpress') {
            const siteUrl = document.getElementById('wordpressSite')?.value;
            const token = document.getElementById('wordpressToken')?.value;
            if (!siteUrl || !token) {
                addChatMessage('ai', 'WordPress 사이트 주소와 API 토큰이 필요합니다.');
                return;
            }
            publishData.site_url = siteUrl;
            publishData.access_token = token;
            
        } else if (selectedPlatform === 'tistory') {
            const blogName = document.getElementById('tistoryBlogName')?.value;
            const token = document.getElementById('tistoryAccessToken')?.value;
            if (!blogName || !token) {
                addChatMessage('ai', 'Tistory 블로그명과 Access Token이 필요합니다.');
                return;
            }
            publishData.blog_name = blogName;
            publishData.access_token = token;
            
        } else if (selectedPlatform === 'naver') {
            const blogId = document.getElementById('naverBlogId')?.value;
            const clientId = document.getElementById('naverClientId')?.value;
            const clientSecret = document.getElementById('naverClientSecret')?.value;
            if (!blogId || !clientId || !clientSecret) {
                addChatMessage('ai', '네이버 블로그 ID, Client ID, Client Secret이 필요합니다.');
                return;
            }
            publishData.blog_id = blogId;
            publishData.client_id = clientId;
            publishData.client_secret = clientSecret;
        }
        
        try {
            const response = await fetch('/api/publish', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(publishData)
            });
            
            if (response.ok) {
                const result = await response.json();
                const platformName = {
                    'blogger': 'Blogger',
                    'wordpress': 'WordPress',
                    'tistory': 'Tistory',
                    'naver': '네이버 블로그'
                }[selectedPlatform] || selectedPlatform;
                
                addChatMessage('ai', `${platformName}에 게시물이 성공적으로 업로드되었습니다! <a href="${result.post_url}" target="_blank">확인하기</a>`);
            } else {
                const error = await response.json();
                addChatMessage('ai', `업로드 실패: ${error.error}`);
            }
            
        } catch (error) {
            console.error('Publish error:', error);
            addChatMessage('ai', '업로드 중 오류가 발생했습니다.');
        }
    }

    // --- UI HANDLERS ---
    function handleImageSourceChange() {
        const selected = document.querySelector('input[name="imageSource"]:checked')?.value;
        
        [pexelsConfig, aiImageConfig, uploadConfig].forEach(config => {
            config?.classList.add('hidden');
        });
        
        if (selected === 'pexels' && pexelsConfig) {
            pexelsConfig.classList.remove('hidden');
        } else if (selected === 'ai' && aiImageConfig) {
            aiImageConfig.classList.remove('hidden');
        } else if (selected === 'upload' && uploadConfig) {
            uploadConfig.classList.remove('hidden');
        }
    }

    function handleAiImageModelChange() {
        const model = aiImageModelSelect?.value;
        if (gcpProjectGroup) {
            gcpProjectGroup.style.display = model === 'imagen-2' ? 'block' : 'none';
        }
    }

    function handleYoutubeSourceChange() {
        const selected = document.querySelector('input[name="youtubeSourceType"]:checked')?.value;
        
        if (youtubeAudioWarning) {
            youtubeAudioWarning.style.display = selected === 'audio' ? 'block' : 'none';
        }
        
        if (videoUploadConfig) {
            videoUploadConfig.style.display = selected === 'videoFile' ? 'block' : 'none';
        }
    }

    function handlePlatformChange() {
        const selected = document.getElementById('platformSelect')?.value;
        const configs = ['bloggerConfig', 'wordpressConfig', 'tistoryConfig', 'naverConfig'];
        
        // Hide all platform configs
        configs.forEach(configId => {
            const config = document.getElementById(configId);
            if (config) config.classList.add('hidden');
        });
        
        // Show selected platform config
        const selectedConfig = document.getElementById(`${selected}Config`);
        if (selectedConfig) {
            selectedConfig.classList.remove('hidden');
        }
    }

    function handleImageUpload(e) {
        const file = e.target.files[0];
        if (!file) return;
        
        const reader = new FileReader();
        reader.onload = (event) => {
            if (imagePreview && imagePreviewContainer) {
                imagePreview.src = event.target.result;
                imagePreviewContainer.classList.remove('hidden');
            }
        };
        reader.readAsDataURL(file);
    }

    function handleRemoveImage() {
        if (userImageUpload) userImageUpload.value = '';
        if (imagePreviewContainer) imagePreviewContainer.classList.add('hidden');
    }

    function handleVideoUpload(e) {
        const file = e.target.files[0];
        if (!file) return;
        
        if (videoFileName && videoFileInfo) {
            videoFileName.textContent = file.name;
            videoFileInfo.classList.remove('hidden');
        }
    }

    function handleRemoveVideo() {
        if (userVideoUpload) userVideoUpload.value = '';
        if (videoFileInfo) videoFileInfo.classList.add('hidden');
    }

    function checkModelCompatibility() {
        const selectedModel = geminiModelSelect?.value;
        const specialPurposeModels = new Set([
            'gemini-live-2.5-flash-preview',
            'gemini-2.5-flash-preview-native-audio-dialog',
            'gemini-2.5-flash-exp-native-audio-thinking-dialog',
            'gemini-2.5-flash-preview-tts',
            'gemini-2.5-pro-preview-tts',
            'gemini-2.0-flash-preview-image-generation',
            'gemini-2.0-flash-live-001'
        ]);

        const isSpecialPurpose = specialPurposeModels.has(selectedModel);

        if (accessToken) {
            setChatInputEnabled(true);
        }

        if (modelCompatibilityWarning) {
            if (isSpecialPurpose) {
                modelCompatibilityWarning.classList.remove('hidden');
                let warningText = '';
                if (selectedModel?.includes('tts')) warningText = 'TTS 전용 모델입니다.';
                else if (selectedModel?.includes('live')) warningText = '실시간 음성/영상 상호작용 전용 모델입니다.';
                else if (selectedModel?.includes('image-generation')) warningText = '대화형 이미지 생성 전용 모델입니다.';
                else if (selectedModel?.includes('audio')) warningText = '대화형 오디오 출력 전용 모델입니다.';
                else warningText = '특수 목적용 모델입니다.';
                
                warningText += ' 블로그 생성에 적합하지 않을 수 있습니다.';
                modelCompatibilityWarning.textContent = warningText;
            } else {
                modelCompatibilityWarning.classList.add('hidden');
            }
        }
    }

    function setChatInputEnabled(enabled) {
        if (chatInput) {
            chatInput.disabled = !enabled;
            chatInput.placeholder = enabled ? 
                '여기에 포스팅 주제 또는 YouTube URL을 입력하세요...' : 
                'Google 로그인이 필요합니다.';
        }
        if (sendBtn) sendBtn.disabled = !enabled;
        if (addToQueueFromChatBtn) addToQueueFromChatBtn.disabled = !enabled;
    }

    function toggleTopicDiscoveryMode() {
        isTopicDiscoveryMode = !isTopicDiscoveryMode;
        if (topicDiscoveryBtn) {
            topicDiscoveryBtn.classList.toggle('active', isTopicDiscoveryMode);
        }
        
        const message = isTopicDiscoveryMode ? 
            '주제 탐색 모드가 활성화되었습니다. 아이디어를 자유롭게 대화해보세요!' :
            '주제 탐색 모드가 비활성화되었습니다.';
        addChatMessage('ai', message);
    }

    // --- GOOGLE AUTH ---
    function handleAuthClick() {
        if (!isGisLoaded) {
            console.error('Google GIS client not loaded yet.');
            return;
        }
        
        if (!clientIdInput?.value) {
            addChatMessage('ai', 'Google Client ID를 먼저 입력해주세요.');
            return;
        }
        
        if (accessToken) {
            // Logout
            accessToken = null;
            updateAuthStatus('로그아웃되었습니다.', 'error');
            setChatInputEnabled(false);
            return;
        }
        
        // Initialize token client
        tokenClient = google.accounts.oauth2.initTokenClient({
            client_id: clientIdInput.value,
            scope: GOOGLE_API_SCOPES,
            callback: (response) => {
                if (response.access_token) {
                    accessToken = response.access_token;
                    updateAuthStatus('Google 계정에 로그인되었습니다.', 'success');
                    setChatInputEnabled(true);
                    checkModelCompatibility();
                } else {
                    updateAuthStatus('로그인에 실패했습니다.', 'error');
                }
            },
        });
        
        tokenClient.requestAccessToken();
    }

    function updateAuthStatus(message, type) {
        if (!authStatus || !loginBtn) return;
        
        authStatus.textContent = message;
        authStatus.className = `status-box ${type}`;
        authStatus.classList.remove('hidden');
        
        loginBtn.innerHTML = accessToken ? 
            '<span>로그아웃</span>' : 
            '<svg aria-hidden="true" class="google-icon" viewBox="0 0 24 24"><path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"></path><path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"></path><path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.5 1 10.22 1 12s.43 3.5 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"></path><path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"></path></svg><span>Google 로그인</span>';
    }

    // --- QUEUE FUNCTIONALITY ---
    function handleAddToQueueFromChat() {
        const input = chatInput?.value.trim();
        if (!input) return;
        
        addToQueue(input);
        if (chatInput) chatInput.value = '';
    }

    async function addToQueue(topicOrUrl) {
        try {
            const response = await fetch('/api/queue', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ topic_or_url: topicOrUrl })
            });
            
            if (response.ok) {
                addChatMessage('ai', `"${topicOrUrl}"이(가) 대기열에 추가되었습니다.`);
                await loadQueue();
            }
        } catch (error) {
            console.error('Error adding to queue:', error);
        }
    }

    async function loadQueue() {
        try {
            const response = await fetch('/api/queue');
            if (response.ok) {
                postQueue = await response.json();
                updateQueueDisplay();
            }
        } catch (error) {
            console.error('Error loading queue:', error);
        }
    }

    function updateQueueDisplay() {
        if (!postQueueContainer) return;
        
        postQueueContainer.innerHTML = '';
        
        if (postQueue.length === 0) {
            postQueueContainer.innerHTML = '<p>대기열이 비어있습니다.</p>';
            return;
        }
        
        postQueue.forEach((item, index) => {
            const div = document.createElement('div');
            div.className = 'queue-item';
            div.innerHTML = `
                <span>${item.topic_or_url}</span>
                <span class="queue-status ${item.status}">${item.status}</span>
                <button onclick="removeFromQueue('${item.id}')">×</button>
            `;
            postQueueContainer.appendChild(div);
        });
    }

    async function removeFromQueue(queueId) {
        try {
            const response = await fetch(`/api/queue/${queueId}`, { method: 'DELETE' });
            if (response.ok) {
                await loadQueue();
            }
        } catch (error) {
            console.error('Error removing from queue:', error);
        }
    }

    // Make removeFromQueue available globally
    window.removeFromQueue = removeFromQueue;

    // --- LOOP AND AUTOMATION ---
    function startLoop() {
        // Implementation for automated posting loop
        addChatMessage('ai', '자동 포스팅 루프 기능은 개발 중입니다.');
    }

    function stopLoop() {
        if (loopIntervalId) {
            clearInterval(loopIntervalId);
            loopIntervalId = null;
        }
        addChatMessage('ai', '자동 포스팅이 중지되었습니다.');
    }

    function shutdownPC() {
        addChatMessage('ai', 'PC 자동 종료 기능은 웹 환경에서 지원되지 않습니다.');
    }

    function cancelShutdown() {
        addChatMessage('ai', '예약된 종료가 취소되었습니다.');
    }

    // --- MISSING FUNCTIONS ---
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
        }
    }

    function toggleTopicDiscoveryMode() {
        isTopicDiscoveryMode = !isTopicDiscoveryMode;
        const topicDiscoveryBtn = document.getElementById('topicDiscoveryBtn');
        if (topicDiscoveryBtn) {
            if (isTopicDiscoveryMode) {
                topicDiscoveryBtn.textContent = '일반 모드로 전환';
                topicDiscoveryBtn.classList.add('active');
                addChatMessage('ai', '주제 발견 모드가 활성화되었습니다. YouTube 링크나 주제를 입력하면 관련 블로그 포스팅 주제를 제안해드립니다.');
            } else {
                topicDiscoveryBtn.textContent = '주제 발견 모드';
                topicDiscoveryBtn.classList.remove('active');
                addChatMessage('ai', '일반 모드로 돌아왔습니다.');
            }
        }
    }

    // Add event listener for chat container clicks
    if (chatContainer) {
        chatContainer.addEventListener('click', handleChatContainerClick);
    }

    // Make functions globally available
    window.handleChatContainerClick = handleChatContainerClick;
    window.toggleTopicDiscoveryMode = toggleTopicDiscoveryMode;

    // --- PLATFORM HANDLERS ---
    function handlePlatformChange() {
        const selectedPlatform = document.getElementById('platformSelect')?.value || 'blogger';
        
        // Hide all platform configs
        const allConfigs = document.querySelectorAll('.platform-config');
        allConfigs.forEach(config => config.classList.add('hidden'));
        
        // Show selected platform config
        const selectedConfig = document.getElementById(`${selectedPlatform}Config`);
        if (selectedConfig) {
            selectedConfig.classList.remove('hidden');
        }
    }

    // --- INITIALIZATION ---
    setInitialTheme();
    initializeCollapsibles();
    loadGisScript();
    loadSettings();
    loadHistory();
    loadQueue();
    checkModelCompatibility();
    
    // Add platform change listener
    const platformSelect = document.getElementById('platformSelect');
    if (platformSelect) {
        platformSelect.addEventListener('change', handlePlatformChange);
        handlePlatformChange(); // Initialize display
    }
});
