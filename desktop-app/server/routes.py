import os
import json
import logging
from flask import render_template, request, jsonify, session
from app import app, db
from models import User, BlogPost, PostQueue
from services.youtube_service import YouTubeService
from services.gemini_service import GeminiService
from services.blogger_service import BloggerService
from services.wordpress_service import WordPressService
from services.tistory_service import TistoryService
from services.naver_service import NaverService
from datetime import datetime
import uuid

# Initialize services
youtube_service = YouTubeService()
gemini_service = GeminiService()
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
        gemini_api_key = os.getenv('GEMINI_API_KEY', settings.get('apiKey', ''))
        gemini_model = settings.get('geminiModel', 'gemini-1.5-pro-latest')
        writing_tone = settings.get('writingTone', '친근한 (Friendly)')
        target_audience = settings.get('targetAudience', '')
        image_source = settings.get('imageSource', 'none')
        
        if not gemini_api_key:
            return jsonify({'error': 'Gemini API key is required'}), 400
        
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
            if pexels_api_key:
                # Extract keywords for image search
                keywords = [topic_or_url.split()[:3]]  # Simple keyword extraction
                image_url = youtube_service.fetch_image_from_pexels(keywords, pexels_api_key)
        elif image_source == 'ai':
            gcp_project_id = settings.get('gcpProjectId')
            access_token = data.get('accessToken')
            if gcp_project_id and access_token:
                image_url = gemini_service.generate_ai_image(gcp_project_id, topic_or_url, access_token)
        elif image_source == 'upload':
            image_url = data.get('uploadedImageUrl')
        
        # Generate content using Gemini
        logging.info("Generating content with Gemini...")
        generated_content = gemini_service.generate_text_content(
            gemini_api_key, content_text, image_url, gemini_model, writing_tone, target_audience
        )
        
        if not generated_content:
            return jsonify({'error': 'Failed to generate content'}), 500
        
        # Process image placement
        final_content = generated_content.get('content_with_placeholder', '')
        if image_url and '[IMAGE_HERE]' in final_content:
            alt_text = generated_content.get('image_search_keywords', 'Blog post image')
            image_tag = f'<img src="{image_url}" alt="{alt_text}" style="width:100%; height:auto; border-radius:8px; margin: 1em 0;">'
            final_content = final_content.replace('[IMAGE_HERE]', image_tag)
        elif image_url:
            # Insert image at the beginning if placeholder not found
            alt_text = generated_content.get('image_search_keywords', 'Blog post image')
            image_tag = f'<img src="{image_url}" alt="{alt_text}" style="width:100%; height:auto; border-radius:8px; margin: 1em 0;">'
            final_content = image_tag + final_content
        
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
            'created_at': blog_post.created_at.isoformat()
        })
        
    except Exception as e:
        logging.error(f"Error generating blog post: {str(e)}")
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
        gemini_api_key = data.get('apiKey', '').strip()
        gemini_model = data.get('modelName', 'gemini-1.5-pro-latest')
        writing_tone = data.get('tone', '친근한 (Friendly)')
        target_audience = data.get('audience', '')
        image_source = data.get('imageSource', 'none')
        pexels_api_key = data.get('pexelsApiKey', '').strip()
        youtube_source_type = data.get('youtubeSourceType', 'transcript')
        
        if not gemini_api_key:
            return jsonify({'error': 'Gemini API key is required'}), 400
        
        # Process first URL (for queue processing, there's typically only one)
        youtube_url = urls[0]
        logging.info(f"Processing YouTube URL: {youtube_url}")
        
        # Extract transcript
        transcript = youtube_service.extract_transcript(youtube_url)
        if not transcript:
            return jsonify({'error': 'Failed to extract transcript from YouTube video'}), 400
        
        # Handle image generation/fetching
        image_url = None
        if image_source == 'pexels' and pexels_api_key:
            # Extract keywords from video content for image search
            keywords = transcript.split()[:10]  # Use first 10 words as keywords
            image_url = youtube_service.fetch_image_from_pexels(keywords, pexels_api_key)
        
        # Generate content using Gemini
        generated_content = gemini_service.generate_text_content(
            gemini_api_key, transcript, image_url, gemini_model, writing_tone, target_audience
        )
        
        if not generated_content:
            return jsonify({'error': 'Failed to generate content'}), 500
        
        # Process image placement
        final_content = generated_content.get('content_with_placeholder', '')
        if image_url and '[IMAGE_HERE]' in final_content:
            alt_text = generated_content.get('image_search_keywords', 'Blog post image')
            image_tag = f'<img src="{image_url}" alt="{alt_text}" style="width:100%; height:auto; border-radius:8px; margin: 1em 0;">'
            final_content = final_content.replace('[IMAGE_HERE]', image_tag)
        elif image_url:
            alt_text = generated_content.get('image_search_keywords', 'Blog post image')
            image_tag = f'<img src="{image_url}" alt="{alt_text}" style="width:100%; height:auto; border-radius:8px; margin: 1em 0;">'
            final_content = image_tag + final_content
        
        # Save to database
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
        
        return jsonify({
            'title': blog_post.title,
            'body': blog_post.content,
            'summary': blog_post.summary,
            'post_id': blog_post.id,
            'created_at': blog_post.created_at.isoformat()
        })
        
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
        gemini_model = data.get('modelName', 'gemini-1.5-pro-latest')
        writing_tone = data.get('tone', '친근한 (Friendly)')
        target_audience = data.get('audience', '')
        image_source = data.get('imageSource', 'none')
        pexels_api_key = data.get('pexelsApiKey', '').strip()
        
        if not gemini_api_key:
            return jsonify({'error': 'Gemini API key is required'}), 400
        
        # Handle image generation/fetching
        image_url = None
        if image_source == 'pexels' and pexels_api_key:
            keywords = topic.split()[:5]  # Use first 5 words as keywords
            image_url = youtube_service.fetch_image_from_pexels(keywords, pexels_api_key)
        
        # Generate content using Gemini
        generated_content = gemini_service.generate_text_content(
            gemini_api_key, topic, image_url, gemini_model, writing_tone, target_audience
        )
        
        if not generated_content:
            return jsonify({'error': 'Failed to generate content'}), 500
        
        # Process image placement
        final_content = generated_content.get('content_with_placeholder', '')
        if image_url and '[IMAGE_HERE]' in final_content:
            alt_text = generated_content.get('image_search_keywords', 'Blog post image')
            image_tag = f'<img src="{image_url}" alt="{alt_text}" style="width:100%; height:auto; border-radius:8px; margin: 1em 0;">'
            final_content = final_content.replace('[IMAGE_HERE]', image_tag)
        elif image_url:
            alt_text = generated_content.get('image_search_keywords', 'Blog post image')
            image_tag = f'<img src="{image_url}" alt="{alt_text}" style="width:100%; height:auto; border-radius:8px; margin: 1em 0;">'
            final_content = image_tag + final_content
        
        # Save to database
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
        
        return jsonify({
            'title': blog_post.title,
            'body': blog_post.content,
            'summary': blog_post.summary,
            'post_id': blog_post.id,
            'created_at': blog_post.created_at.isoformat()
        })
        
    except Exception as e:
        logging.error(f"Error generating post from topic: {str(e)}")
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
