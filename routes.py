import os
import json
import logging
from flask import render_template, request, jsonify, session
from app import app, db
from models import User, BlogPost, PostQueue
from services.youtube_service import YouTubeService
from services.gemini_service import GeminiService
from services.openai_service import OpenAIService
from services.gptoss_service import GPTOSSService
from services.blogger_service import BloggerService
from services.wordpress_service import WordPressService
from services.tistory_service import TistoryService
from services.naver_service import NaverService
from datetime import datetime
import uuid

# Initialize services
youtube_service = YouTubeService()
gemini_service = GeminiService()
openai_service = OpenAIService()
gptoss_service = GPTOSSService()
blogger_service = BloggerService()
wordpress_service = WordPressService()
tistory_service = TistoryService()
naver_service = NaverService()

def get_or_create_user(session_id=None):
    """Get or create user based on session"""
    if not session_id:
        session_id = session.get('user_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            session['user_id'] = session_id
    
    user = User.query.filter_by(id=session_id).first()
    if not user:
        user = User()
        user.id = session_id
        db.session.add(user)
        db.session.commit()
    
    return user

def process_image_placement(content, image_url, alt_text="Blog post image"):
    """Unified image processing for consistent placement across all posting methods"""
    if not image_url:
        return content
    
    # Standard image tag with consistent styling
    image_tag = f'<img src="{image_url}" alt="{alt_text}" style="width:100%; height:auto; border-radius:8px; margin: 1em 0;">'
    
    # First try to replace placeholder
    if '[IMAGE_HERE]' in content:
        return content.replace('[IMAGE_HERE]', image_tag)
    
    # If no placeholder found, insert after first paragraph or h1 tag
    import re
    
    # Try to insert after first </p> tag
    first_p_match = re.search(r'</p>', content)
    if first_p_match:
        insert_pos = first_p_match.end()
        return content[:insert_pos] + '\n' + image_tag + '\n' + content[insert_pos:]
    
    # Try to insert after first </h1> tag  
    first_h1_match = re.search(r'</h1>', content)
    if first_h1_match:
        insert_pos = first_h1_match.end()
        return content[:insert_pos] + '\n' + image_tag + '\n' + content[insert_pos:]
    
    # Fallback: insert at beginning
    return image_tag + '\n' + content

def generate_content_with_fallback(api_key, content_input, image_url, model_name, tone, audience, ai_engine='gemini', gptoss_endpoint=None):
    """Enhanced content generation with 3-tier fallback: Gemini -> OpenAI -> GPT-OSS"""
    last_error = None
    
    # Determine which AI engine to try first
    if ai_engine == 'gptoss' and gptoss_endpoint:
        try:
            generated_content = gptoss_service.generate_text_content(
                gptoss_endpoint, content_input, image_url, model_name, tone, audience
            )
            if generated_content and not generated_content.get('error'):
                return generated_content
        except Exception as gptoss_error:
            last_error = gptoss_error
            logging.warning(f"GPT-OSS failed, trying Gemini fallback: {str(gptoss_error)}")
    
    # Try Gemini (primary or fallback)
    if ai_engine != 'openai':
        try:
            generated_content = gemini_service.generate_text_content(
                api_key, content_input, image_url, model_name, tone, audience
            )
            if generated_content and not generated_content.get('error'):
                return generated_content
        except Exception as gemini_error:
            last_error = gemini_error
            logging.warning(f"Gemini failed, trying OpenAI fallback: {str(gemini_error)}")
    
    # Try OpenAI (primary or fallback)
    try:
        generated_content = openai_service.generate_text_content(
            None, content_input, image_url, model_name, tone, audience
        )
        if generated_content and not generated_content.get('error'):
            return generated_content
    except Exception as openai_error:
        last_error = openai_error
        logging.warning(f"OpenAI failed, trying GPT-OSS fallback: {str(openai_error)}")
    
    # Final fallback to GPT-OSS (if not already tried)
    if ai_engine != 'gptoss' and gptoss_endpoint:
        try:
            generated_content = gptoss_service.generate_text_content(
                gptoss_endpoint, content_input, image_url, model_name, tone, audience
            )
            if generated_content and not generated_content.get('error'):
                return generated_content
        except Exception as final_error:
            last_error = final_error
    
    # All services failed
    error_msg = f"모든 AI 서비스 실패. 마지막 오류: {str(last_error) if last_error else '알 수 없음'}"
    logging.error(error_msg)
    raise ValueError("AI 콘텐츠 생성에 실패했습니다. 설정을 확인하고 다시 시도해주세요.")

@app.route('/')
def index():
    """Main application page"""
    return render_template('index.html')

@app.route('/api/settings', methods=['GET', 'POST'])
def handle_settings():
    """Handle user settings"""
    user = get_or_create_user()
    
    if request.method == 'GET':
        return jsonify(user.settings or {})
    
    elif request.method == 'POST':
        data = request.get_json()
        user.settings = data
        db.session.commit()
        return jsonify({'status': 'success'})
    
    return jsonify({'error': 'Method not allowed'}), 405

@app.route('/api/history')
def get_history():
    """Get user's posting history"""
    user = get_or_create_user()
    posts = BlogPost.query.filter_by(user_id=user.id).order_by(BlogPost.created_at.desc()).all()
    
    history = []
    for post in posts:
        history.append({
            'id': post.id,
            'title': post.title,
            'summary': post.summary,
            'source_type': post.source_type,
            'source_url': post.source_url,
            'blogger_url': post.blogger_url,
            'created_at': post.created_at.isoformat(),
            'is_draft': post.is_draft
        })
    
    return jsonify(history)

@app.route('/api/history/<post_id>')
def get_post_detail(post_id):
    """Get detailed post information"""
    user = get_or_create_user()
    post = BlogPost.query.filter_by(id=post_id, user_id=user.id).first()
    
    if not post:
        return jsonify({'error': 'Post not found'}), 404
    
    return jsonify({
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'summary': post.summary,
        'source_type': post.source_type,
        'source_url': post.source_url,
        'blogger_url': post.blogger_url,
        'gemini_model': post.gemini_model,
        'writing_tone': post.writing_tone,
        'target_audience': post.target_audience,
        'image_source': post.image_source,
        'image_url': post.image_url,
        'created_at': post.created_at.isoformat(),
        'is_draft': post.is_draft
    })

@app.route('/api/history', methods=['DELETE'])
def clear_history():
    """Clear user's posting history"""
    user = get_or_create_user()
    BlogPost.query.filter_by(user_id=user.id).delete()
    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/api/test-gptoss', methods=['POST'])
def test_gptoss():
    """Test GPT-OSS connection"""
    try:
        data = request.get_json()
        endpoint = data.get('endpoint', '').strip()
        api_key = data.get('apiKey', '').strip()
        model = data.get('model', 'gpt-oss-20b')
        
        if not endpoint:
            return jsonify({'available': False, 'error': 'Endpoint is required'}), 400
        
        # Test connection using GPT-OSS service
        result = gptoss_service.check_model_availability(endpoint, api_key if api_key else None, model)
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"GPT-OSS test error: {e}")
        return jsonify({'available': False, 'error': str(e)}), 500

@app.route('/api/generate', methods=['POST'])
def generate_blog_post():
    """Generate blog post from topic or YouTube URL"""
    try:
        user = get_or_create_user()
        data = request.get_json()
        
        topic_or_url = data.get('input', '').strip()
        settings = data.get('settings', {})
        
        if not topic_or_url:
            return jsonify({'error': 'Input is required'}), 400
        
        # Extract settings
        gemini_api_key = settings.get('apiKey', '').strip() or os.getenv('GOOGLE_GEMINI_API_KEY') or os.getenv('GEMINI_API_KEY')
        gemini_model = settings.get('geminiModel', 'gemini-1.5-pro')
        writing_tone = settings.get('writingTone', '친근한 (Friendly)')
        target_audience = settings.get('targetAudience', '')
        image_source = settings.get('imageSource', 'none')
        ai_engine = settings.get('aiEngine', 'gemini')
        gptoss_endpoint = settings.get('gptossEndpoint', '').strip()
        gptoss_api_key = settings.get('gptossApiKey', '').strip()
        
        # Validate AI engine requirements
        if ai_engine == 'gemini' and not gemini_api_key:
            return jsonify({'error': 'Gemini API key is required'}), 400
        elif ai_engine == 'gptoss' and not gptoss_endpoint:
            return jsonify({'error': 'GPT-OSS endpoint is required'}), 400
        
        # Determine content source
        content_text = ""
        source_type = "topic"
        source_url = None
        
        # Check if input is a YouTube URL
        if 'youtube.com' in topic_or_url or 'youtu.be' in topic_or_url:
            logging.info(f"Processing YouTube URL: {topic_or_url}")
            source_type = "youtube"
            source_url = topic_or_url
            
            # Extract transcript with improved error handling
            try:
                transcript = youtube_service.extract_transcript(topic_or_url, settings)
                if transcript:
                    content_text = transcript
                    topic_or_url = f"YouTube video transcript analysis"
                else:
                    # Fallback: use URL as topic for general content generation
                    logging.warning("No transcript available, generating content based on video topic")
                    content_text = f"Generate content about this YouTube video: {topic_or_url}"
            except Exception as e:
                logging.error(f"YouTube processing failed: {str(e)}")
                return jsonify({'error': f'YouTube processing failed: {str(e)}'}), 400
        else:
            content_text = topic_or_url
        
        # Handle image generation/fetching
        image_url = None
        if image_source == 'pexels':
            pexels_api_key = settings.get('pexelsApiKey')
            if pexels_api_key and pexels_api_key != 'test-key':
                # Extract keywords for image search
                keywords = [topic_or_url.split()[:3]]  # Simple keyword extraction
                image_url = youtube_service.fetch_image_from_pexels(keywords, pexels_api_key)
            else:
                logging.warning("Pexels API key not provided or invalid, skipping image fetch")
        elif image_source == 'ai':
            gcp_project_id = settings.get('gcpProjectId')
            access_token = data.get('accessToken')
            if gcp_project_id and access_token:
                image_url = gemini_service.generate_ai_image(gcp_project_id, topic_or_url, access_token)
        elif image_source == 'upload':
            image_url = data.get('uploadedImageUrl')
        
        # Generate content using unified system with fallback
        generated_content = generate_content_with_fallback(
            gemini_api_key, content_text, image_url, gemini_model, writing_tone, target_audience, ai_engine, gptoss_endpoint or gptoss_api_key
        )
        
        if not generated_content:
            return jsonify({'error': 'Failed to generate content'}), 500
        
        # Process image placement using unified function
        final_content = generated_content.get('content_with_placeholder', '')
        alt_text = generated_content.get('image_search_keywords', 'Blog post image')
        final_content = process_image_placement(final_content, image_url, alt_text)
        
        # Save to database
        blog_post = BlogPost()
        blog_post.user_id = user.id
        blog_post.title = generated_content.get('title', 'Untitled Post')
        blog_post.content = final_content
        blog_post.summary = generated_content.get('summary', '')
        blog_post.source_type = source_type
        blog_post.source_url = source_url
        blog_post.gemini_model = gemini_model
        blog_post.writing_tone = writing_tone
        blog_post.target_audience = target_audience
        blog_post.image_source = image_source
        blog_post.image_url = image_url
        
        db.session.add(blog_post)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'post_id': blog_post.id,
            'title': blog_post.title,
            'content': blog_post.content,
            'summary': blog_post.summary,
            'hashtags': generated_content.get('hashtags', ''),
            'keywords': generated_content.get('image_search_keywords', ''),
            'created_at': blog_post.created_at.isoformat()
        })
        
    except Exception as e:
        logging.error(f"Error generating blog post: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/chat-for-topic', methods=['POST'])
def chat_for_topic():
    """Chat with AI for topic discovery"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        api_key = data.get('apiKey', '').strip() or os.getenv('GOOGLE_GEMINI_API_KEY') or os.getenv('GEMINI_API_KEY')
        model_name = data.get('modelName', 'gemini-1.5-pro')
        tone = data.get('tone', '친근한 (Friendly)')
        audience = data.get('audience', '')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        if not api_key:
            return jsonify({'error': 'Gemini API key is required'}), 400
        
        # Use unified content generation for topic discovery
        try:
            prompt = f"""당신은 전문 블로그 주제 컨설턴트입니다. 주어진 설정에 맞춰 주제를 추천해주세요.

**글쓰기 톤 & 스타일:** {tone}
**타겟 독자:** {audience or '일반 대중'}

질문: "{message}"

위 설정을 고려하여 다음 형식으로 3가지 구체적인 주제를 제안해주세요:

1. [구체적 주제명] - 간단한 이유
2. [구체적 주제명] - 간단한 이유  
3. [구체적 주제명] - 간단한 이유

각 제안은 SEO 친화적이고 바로 포스팅 가능해야 하며, 설정된 글쓰기 톤과 타겟 독자에게 적합해야 합니다."""
            
            # Use unified system with lightweight response for topic discovery
            response = gemini_service.generate_text_content(
                api_key, prompt, None, model_name, tone, audience
            )
            
            if response and response.get('title'):
                # Extract just the content for topic discovery
                reply_text = response.get('content_with_placeholder', '').replace('<h1>', '').replace('</h1>', '').replace('<p>', '').replace('</p>', '').replace('<h2>', '').replace('</h2>', '').strip()
                return jsonify({'reply': reply_text})
            else:
                return jsonify({'error': 'AI가 응답을 생성하지 못했습니다. 다시 시도해주세요.'}), 500
                
        except Exception as e:
            logging.error(f"Unified API error in chat-for-topic: {str(e)}")
            return jsonify({'error': f'AI 대화 중 오류가 발생했습니다: {str(e)}'}), 500
            
    except Exception as e:
        logging.error(f"Error in chat-for-topic: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/generate-post-from-youtube', methods=['POST'])
def generate_post_from_youtube():
    """Generate blog post from YouTube URLs"""
    try:
        user = get_or_create_user()
        data = request.get_json()
        
        urls = data.get('urls', [])
        if not urls:
            return jsonify({'error': 'YouTube URLs are required'}), 400
        
        # Extract settings from request data
        gemini_api_key = data.get('apiKey', '').strip() or os.getenv('GOOGLE_GEMINI_API_KEY') or os.getenv('GEMINI_API_KEY')
        gemini_model = data.get('modelName', 'gemini-1.5-pro')
        writing_tone = data.get('tone', '친근한 (Friendly)')
        target_audience = data.get('audience', '')
        image_source = data.get('imageSource', 'none')
        pexels_api_key = data.get('pexelsApiKey', '').strip()
        youtube_source_type = data.get('youtubeSourceType', 'transcript')
        ai_engine = data.get('aiEngine', 'gemini')
        gptoss_endpoint = data.get('gptossEndpoint', '').strip()
        gptoss_api_key = data.get('gptossApiKey', '').strip()
        
        if not gemini_api_key:
            return jsonify({'error': 'Gemini API key is required'}), 400
        
        # Process first URL (for queue processing, there's typically only one)
        youtube_url = urls[0]
        logging.info(f"Processing YouTube URL: {youtube_url}")
        
        # Extract transcript using consistent method
        try:
            transcript = youtube_service.extract_transcript(youtube_url, {})
            if not transcript:
                transcript = f"YouTube video analysis: {youtube_url}"
        except Exception as e:
            logging.warning(f"Transcript extraction failed: {str(e)}")
            transcript = f"YouTube video analysis: {youtube_url}"
        
        # Handle image generation/fetching using unified method
        image_url = None
        if image_source == 'pexels' and pexels_api_key and pexels_api_key != 'test-key':
            keywords = transcript.split()[:3]  # Use first 3 words as keywords
            image_url = youtube_service.fetch_image_from_pexels(keywords, pexels_api_key)

        elif image_source == 'upload':
            image_url = data.get('uploadedImageUrl')
        
        # Generate content using unified system with fallback
        generated_content = generate_content_with_fallback(
            gemini_api_key, transcript, image_url, gemini_model, writing_tone, target_audience, ai_engine, gptoss_endpoint or gptoss_api_key
        )
        
        if not generated_content:
            return jsonify({'error': 'Failed to generate content'}), 500
        
        # Process image placement using unified function
        final_content = generated_content.get('content_with_placeholder', '')
        alt_text = generated_content.get('image_search_keywords', 'Blog post image')
        final_content = process_image_placement(final_content, image_url, alt_text)
        
        # Save to database with retry mechanism
        max_retries = 3
        blog_post = None
        for attempt in range(max_retries):
            try:
                blog_post = BlogPost()
                blog_post.user_id = user.id
                blog_post.title = generated_content.get('title', 'Untitled Post')
                blog_post.content = final_content
                blog_post.summary = generated_content.get('summary', '')
                blog_post.source_type = "youtube"
                blog_post.source_url = youtube_url
                blog_post.gemini_model = gemini_model
                blog_post.writing_tone = writing_tone
                blog_post.target_audience = target_audience
                blog_post.image_source = image_source
                blog_post.image_url = image_url
                
                db.session.add(blog_post)
                db.session.commit()
                break  # Success, exit retry loop
                
            except Exception as db_error:
                logging.warning(f"Database save attempt {attempt + 1} failed: {str(db_error)}")
                db.session.rollback()
                
                if attempt == max_retries - 1:
                    # Last attempt failed, raise the error
                    raise db_error
                else:
                    # Retry after a short delay
                    import time
                    time.sleep(1)
        
        # Return response data with proper error handling
        response_data = {
            'title': blog_post.title if blog_post else 'Untitled Post',
            'body': blog_post.content if blog_post else '',
            'summary': blog_post.summary if blog_post else '',
            'hashtags': generated_content.get('hashtags', '') if generated_content else '',
            'keywords': generated_content.get('image_search_keywords', '') if generated_content else '',
            'post_id': blog_post.id if blog_post else None,
            'created_at': blog_post.created_at.isoformat() if blog_post and blog_post.created_at else ''
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logging.error(f"Error generating post from YouTube: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/generate-post', methods=['POST'])
def generate_post():
    """Generate blog post from topic"""
    try:
        user = get_or_create_user()
        data = request.get_json()
        
        topic = data.get('topic', '').strip()
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
        
        # Extract settings from request data
        gemini_api_key = data.get('apiKey', '').strip()
        gemini_model = data.get('modelName', 'gemini-1.5-pro')
        writing_tone = data.get('tone', '친근한 (Friendly)')
        target_audience = data.get('audience', '')
        image_source = data.get('imageSource', 'none')
        pexels_api_key = data.get('pexelsApiKey', '').strip()
        ai_engine = data.get('aiEngine', 'gemini')
        gptoss_endpoint = data.get('gptossEndpoint', '').strip()
        gptoss_api_key = data.get('gptossApiKey', '').strip()
        
        # Validate AI engine requirements
        if ai_engine == 'gemini' and not gemini_api_key:
            return jsonify({'error': 'Gemini API key is required'}), 400
        elif ai_engine == 'gptoss' and not gptoss_endpoint:
            return jsonify({'error': 'GPT-OSS endpoint is required'}), 400
        
        # Handle image generation/fetching using unified method
        image_url = None
        if image_source == 'pexels' and pexels_api_key and pexels_api_key != 'test-key':
            keywords = topic.split()[:3]  # Use first 3 words as keywords
            image_url = youtube_service.fetch_image_from_pexels(keywords, pexels_api_key)

        elif image_source == 'upload':
            image_url = data.get('uploadedImageUrl')
        
        # Generate content using unified system with fallback
        generated_content = generate_content_with_fallback(
            gemini_api_key, topic, image_url, gemini_model, writing_tone, target_audience, ai_engine, gptoss_endpoint or gptoss_api_key
        )
        
        if not generated_content:
            return jsonify({'error': 'Failed to generate content'}), 500
        
        # Process image placement using unified function
        final_content = generated_content.get('content_with_placeholder', '')
        alt_text = generated_content.get('image_search_keywords', 'Blog post image')
        final_content = process_image_placement(final_content, image_url, alt_text)
        
        # Save to database with retry mechanism
        max_retries = 3
        blog_post = None
        for attempt in range(max_retries):
            try:
                blog_post = BlogPost()
                blog_post.user_id = user.id
                blog_post.title = generated_content.get('title', 'Untitled Post')
                blog_post.content = final_content
                blog_post.summary = generated_content.get('summary', '')
                blog_post.source_type = "topic"
                blog_post.source_url = None
                blog_post.gemini_model = gemini_model
                blog_post.writing_tone = writing_tone
                blog_post.target_audience = target_audience
                blog_post.image_source = image_source
                blog_post.image_url = image_url
                
                db.session.add(blog_post)
                db.session.commit()
                break  # Success, exit retry loop
                
            except Exception as db_error:
                logging.warning(f"Database save attempt {attempt + 1} failed: {str(db_error)}")
                db.session.rollback()
                
                if attempt == max_retries - 1:
                    # Last attempt failed, raise the error
                    raise db_error
                else:
                    # Retry after a short delay
                    import time
                    time.sleep(1)
        
        # Return response data with proper error handling
        response_data = {
            'title': blog_post.title if blog_post else 'Untitled Post',
            'body': blog_post.content if blog_post else '',
            'content': blog_post.content if blog_post else '',  # Alias for compatibility
            'summary': blog_post.summary if blog_post else '',
            'hashtags': generated_content.get('hashtags', '') if generated_content else '',
            'keywords': generated_content.get('image_search_keywords', '') if generated_content else '',
            'post_id': blog_post.id if blog_post else None,
            'created_at': blog_post.created_at.isoformat() if blog_post and blog_post.created_at else ''
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logging.error(f"Error generating post from topic: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/generate-post-from-video', methods=['POST'])
def generate_post_from_video():
    """Generate blog post from uploaded video file"""
    try:
        user = get_or_create_user()
        
        # Check if video file is uploaded
        if 'video' not in request.files:
            return jsonify({'error': 'No video file uploaded'}), 400
        
        video_file = request.files['video']
        if video_file.filename == '':
            return jsonify({'error': 'No video file selected'}), 400
        
        # Get form data
        topic = request.form.get('topic', '').strip()
        gemini_api_key = request.form.get('apiKey', '').strip() or os.getenv('GOOGLE_GEMINI_API_KEY') or os.getenv('GEMINI_API_KEY')
        gemini_model = request.form.get('modelName', 'gemini-1.5-pro')
        writing_tone = request.form.get('tone', '친근한 (Friendly)')
        target_audience = request.form.get('audience', '')
        image_source = request.form.get('imageSource', 'none')
        pexels_api_key = request.form.get('pexelsApiKey', '').strip()
        ai_engine = request.form.get('aiEngine', 'gemini')
        gptoss_endpoint = request.form.get('gptossEndpoint', '').strip()
        gptoss_api_key = request.form.get('gptossApiKey', '').strip()
        
        # Validate AI engine requirements
        if ai_engine == 'gemini' and not gemini_api_key:
            return jsonify({'error': 'Gemini API key is required'}), 400
        elif ai_engine == 'gptoss' and not gptoss_endpoint:
            return jsonify({'error': 'GPT-OSS endpoint is required'}), 400
        
        if not topic:
            topic = f"동영상 파일에서 추출된 콘텐츠 ({video_file.filename})"
        
        # Validate file size before processing to prevent memory issues
        if hasattr(video_file, 'content_length') and video_file.content_length:
            file_size_mb = video_file.content_length / (1024 * 1024)
            if file_size_mb > 200:  # Further reduced limit for stability
                return jsonify({'error': f'동영상 파일이 너무 큽니다. 최대 200MB까지 지원됩니다. (현재: {file_size_mb:.1f}MB)'}), 400
        
        # Save uploaded video temporarily with improved error handling
        import tempfile
        import os
        
        temp_dir = tempfile.gettempdir()
        # Use UUID to avoid filename conflicts
        import uuid
        safe_filename = f"temp_video_{user.id}_{uuid.uuid4().hex[:8]}_{video_file.filename}"
        temp_video_path = os.path.join(temp_dir, safe_filename)
        
        try:
            video_file.save(temp_video_path)
            logging.info(f"Video file saved temporarily: {temp_video_path}")
            
            # Verify file was saved correctly
            if not os.path.exists(temp_video_path) or os.path.getsize(temp_video_path) == 0:
                raise ValueError(f"동영상 파일 저장에 실패했습니다: {video_file.filename}")
            
            # Enhanced video content analysis
            file_size_mb = round(os.path.getsize(temp_video_path) / (1024 * 1024), 2)
            video_content = f"""
**동영상 파일 정보:**
- 파일명: {video_file.filename}
- 파일 크기: {file_size_mb} MB
- 주제: {topic}

**콘텐츠 생성 지침:**
다음 동영상에 대해 전문적이고 상세한 블로그 포스트를 작성해주세요:

1. **동영상 개요**: 주제와 목적을 명확히 설명
2. **주요 내용 분석**: 핵심 메시지와 정보를 체계적으로 정리
3. **시각적 요소**: 중요한 장면이나 그래픽 요소 설명
4. **실용적 가치**: 시청자/독자가 얻을 수 있는 구체적 이익
5. **결론 및 요약**: 핵심 포인트 재정리

동영상을 직접 시청하지 않아도 완전히 이해할 수 있도록 2500자 이상의 풍부하고 전문적인 내용으로 작성해주세요.
각 섹션마다 구체적인 예시, 데이터, 실용적 팁을 포함하여 독자에게 실질적 가치를 제공해야 합니다.
"""
            
            # Handle image generation/fetching
            image_url = None
            if image_source == 'pexels':
                if pexels_api_key:
                    keywords = topic.split()[:5]  # Use topic words as keywords
                    image_url = youtube_service.fetch_image_from_pexels(keywords, pexels_api_key)
            elif image_source == 'ai':
                gcp_project_id = request.form.get('gcpProjectId')
                access_token = request.form.get('accessToken')
                if gcp_project_id and access_token:
                    image_url = gemini_service.generate_ai_image(gcp_project_id, topic, access_token)
            elif image_source == 'upload':
                image_url = request.form.get('uploadedImageUrl')
            
            # Generate content using Gemini with enhanced error handling and memory management
            import gc
            gc.collect()  # Free memory before API call
            
            try:
                # Generate content using unified system with fallback
                generated_content = generate_content_with_fallback(
                    gemini_api_key, video_content, image_url, gemini_model, writing_tone, target_audience, ai_engine, gptoss_endpoint or gptoss_api_key
                )
                
                if not generated_content:
                    raise ValueError("AI가 빈 응답을 반환했습니다")
                    
            except Exception as ai_error:
                logging.error(f"AI content generation failed for video: {str(ai_error)}")
                error_message = str(ai_error)
                
                if "timeout" in error_message.lower() or "지연" in error_message:
                    return jsonify({'error': '서버 연결이 지연되고 있습니다. 파일 크기를 줄이거나 잠시 후 다시 시도해주세요.'}), 503
                else:
                    return jsonify({'error': f'AI 콘텐츠 생성 중 오류가 발생했습니다: {error_message}'}), 500
            
            # Process image placement using unified function
            final_content = generated_content.get('content_with_placeholder', '')
            alt_text = generated_content.get('image_search_keywords', 'Blog post image')
            final_content = process_image_placement(final_content, image_url, alt_text)
            
            # Add hashtags if not already included in content
            hashtags = generated_content.get('hashtags', '')
            if hashtags and hashtags not in final_content:
                hashtag_section = f'<hr><p><strong>관련 키워드:</strong> {hashtags}</p>'
                final_content += hashtag_section
            
            # Save to database with retry mechanism
            max_retries = 3
            blog_post = None
            for attempt in range(max_retries):
                try:
                    blog_post = BlogPost()
                    blog_post.user_id = user.id
                    blog_post.title = generated_content.get('title', 'Untitled Post')
                    blog_post.content = final_content
                    blog_post.summary = generated_content.get('summary', '')
                    blog_post.source_type = "video_file"
                    blog_post.source_file_name = video_file.filename
                    blog_post.gemini_model = gemini_model
                    blog_post.writing_tone = writing_tone
                    blog_post.target_audience = target_audience
                    blog_post.image_source = image_source
                    blog_post.image_url = image_url
                    
                    db.session.add(blog_post)
                    db.session.commit()
                    break  # Success, exit retry loop
                    
                except Exception as db_error:
                    logging.warning(f"Database save attempt {attempt + 1} failed: {str(db_error)}")
                    db.session.rollback()
                    
                    if attempt == max_retries - 1:
                        raise db_error
                    else:
                        import time
                        time.sleep(1)
            
            # Return response data with proper error handling
            response_data = {
                'title': blog_post.title if blog_post else 'Untitled Post',
                'body': blog_post.content if blog_post else '',
                'summary': blog_post.summary if blog_post else '',
                'hashtags': generated_content.get('hashtags', '') if generated_content else '',
                'keywords': generated_content.get('image_search_keywords', '') if generated_content else '',
                'post_id': blog_post.id if blog_post else None,
                'created_at': blog_post.created_at.isoformat() if blog_post and blog_post.created_at else ''
            }
            
            return jsonify(response_data)
            
        finally:
            # Enhanced cleanup with multiple retry attempts
            cleanup_attempts = 3
            for attempt in range(cleanup_attempts):
                try:
                    if 'temp_video_path' in locals() and os.path.exists(temp_video_path):
                        os.remove(temp_video_path)
                        logging.info(f"Temporary video file removed: {temp_video_path}")
                        break
                except Exception as cleanup_error:
                    logging.warning(f"Cleanup attempt {attempt + 1} failed: {cleanup_error}")
                    if attempt < cleanup_attempts - 1:
                        import time
                        time.sleep(0.5)  # Brief wait before retry
                    else:
                        logging.error(f"Failed to remove temporary file after {cleanup_attempts} attempts: {temp_video_path}")
        
    except Exception as e:
        logging.error(f"Error generating post from video: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/publish', methods=['POST'])
def publish_to_platform():
    """Publish generated post to selected platform"""
    platform = 'unknown'  # Initialize platform variable
    try:
        user = get_or_create_user()
        data = request.get_json()
        
        post_id = data.get('post_id')
        platform = data.get('platform', 'blogger')
        is_draft = data.get('is_draft', False)
        
        if not post_id:
            return jsonify({'error': 'Post ID is required'}), 400
        
        # Get post from database
        blog_post = BlogPost.query.filter_by(id=post_id, user_id=user.id).first()
        if not blog_post:
            return jsonify({'error': 'Post not found'}), 404
        
        result = None
        
        # Publish to selected platform
        if platform == 'blogger':
            access_token = data.get('access_token')
            blog_id = data.get('blog_id')
            
            if not all([access_token, blog_id]):
                return jsonify({'error': 'Missing Blogger credentials'}), 400
                
            result = blogger_service.publish_post(
                access_token, blog_id, blog_post.title, blog_post.content, is_draft
            )
            
        elif platform == 'wordpress':
            site_url = data.get('site_url')
            access_token = data.get('access_token')
            
            if not all([site_url, access_token]):
                return jsonify({'error': 'Missing WordPress credentials'}), 400
                
            result = wordpress_service.publish_post(
                site_url, access_token, blog_post.title, blog_post.content, is_draft
            )
            
        elif platform == 'tistory':
            blog_name = data.get('blog_name')
            
            if not blog_name:
                return jsonify({'error': 'Tistory 블로그명이 필요합니다'}), 400
                
            result = tistory_service.publish_post(
                blog_name, None, blog_post.title, blog_post.content, is_draft
            )
            
            # Tistory API is discontinued, return manual guide
            if result and 'error' in result:
                return jsonify({
                    'status': 'manual_required',
                    'platform': 'tistory',
                    'message': result['error'],
                    'manual_guide': result['manual_guide'],
                    'blog_url': f"https://{blog_name}.tistory.com/manage/newpost/",
                    'title': result['title'],
                    'content': result['content']
                }), 202  # 202 Accepted but requires manual action
            
        elif platform == 'naver':
            blog_id = data.get('blog_id')
            client_id = data.get('client_id')
            client_secret = data.get('client_secret')
            
            if not all([blog_id, client_id, client_secret]):
                return jsonify({'error': 'Missing Naver Blog credentials'}), 400
                
            result = naver_service.publish_post(
                blog_id, client_id, client_secret, blog_post.title, blog_post.content, is_draft
            )
            
        else:
            return jsonify({'error': f'Unsupported platform: {platform}'}), 400
        
        if result:
            # Update post with platform details
            blog_post.platform = platform
            blog_post.platform_post_id = result.get('id')
            blog_post.blogger_url = result.get('url')  # Keep for backward compatibility
            blog_post.is_draft = is_draft
            blog_post.posted_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'platform': platform,
                'post_url': result.get('url'),
                'post_id': result.get('id'),
                'blogger_url': result.get('url')  # Keep for backward compatibility
            })
        else:
            return jsonify({'error': f'Failed to publish to {platform}'}), 500
            
    except Exception as e:
        platform_name = platform if 'platform' in locals() and platform else 'unknown platform'
        logging.error(f"Error publishing to {platform_name}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/queue', methods=['GET', 'POST'])
def handle_queue():
    """Handle post queue operations"""
    user = get_or_create_user()
    
    if request.method == 'GET':
        queue_items = PostQueue.query.filter_by(user_id=user.id).order_by(PostQueue.created_at.asc()).all()
        return jsonify([{
            'id': item.id,
            'topic_or_url': item.topic_or_url,
            'status': item.status,
            'created_at': item.created_at.isoformat(),
            'error_message': item.error_message
        } for item in queue_items])
    
    elif request.method == 'POST':
        data = request.get_json()
        topic_or_url = data.get('topic_or_url', '').strip()
        
        if not topic_or_url:
            return jsonify({'error': 'Topic or URL is required'}), 400
        
        queue_item = PostQueue()
        queue_item.user_id = user.id
        queue_item.topic_or_url = topic_or_url
        
        db.session.add(queue_item)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'queue_id': queue_item.id
        })
    
    return jsonify({'error': 'Method not allowed'}), 405

@app.route('/api/queue/<queue_id>', methods=['DELETE'])
def delete_queue_item(queue_id):
    """Delete item from queue"""
    user = get_or_create_user()
    queue_item = PostQueue.query.filter_by(id=queue_id, user_id=user.id).first()
    
    if not queue_item:
        return jsonify({'error': 'Queue item not found'}), 404
    
    db.session.delete(queue_item)
    db.session.commit()
    
    return jsonify({'status': 'success'})

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500
