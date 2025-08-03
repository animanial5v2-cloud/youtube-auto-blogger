import os
import json
import logging
from flask import render_template, request, jsonify, session
from app import app, db
from models import User, BlogPost, PostQueue
from services.youtube_service import YouTubeService
from services.gemini_service import GeminiService
from services.blogger_service import BloggerService
from datetime import datetime
import uuid

# Initialize services
youtube_service = YouTubeService()
gemini_service = GeminiService()
blogger_service = BloggerService()

def get_or_create_user(session_id=None):
    """Get or create user based on session"""
    if not session_id:
        session_id = session.get('user_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            session['user_id'] = session_id
    
    user = User.query.filter_by(id=session_id).first()
    if not user:
        user = User(id=session_id)
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
        blog_post = BlogPost(
            user_id=user.id,
            title=generated_content.get('title', 'Untitled Post'),
            content=final_content,
            summary=generated_content.get('summary', ''),
            source_type=source_type,
            source_url=source_url,
            gemini_model=gemini_model,
            writing_tone=writing_tone,
            target_audience=target_audience,
            image_source=image_source,
            image_url=image_url
        )
        
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

@app.route('/api/publish', methods=['POST'])
def publish_to_blogger():
    """Publish generated post to Blogger"""
    try:
        user = get_or_create_user()
        data = request.get_json()
        
        post_id = data.get('post_id')
        access_token = data.get('access_token')
        blog_id = data.get('blog_id')
        is_draft = data.get('is_draft', False)
        
        if not all([post_id, access_token, blog_id]):
            return jsonify({'error': 'Missing required parameters'}), 400
        
        # Get post from database
        blog_post = BlogPost.query.filter_by(id=post_id, user_id=user.id).first()
        if not blog_post:
            return jsonify({'error': 'Post not found'}), 404
        
        # Publish to Blogger
        result = blogger_service.publish_post(
            access_token, blog_id, blog_post.title, blog_post.content, is_draft
        )
        
        if result:
            # Update post with Blogger details
            blog_post.blogger_post_id = result.get('id')
            blog_post.blogger_url = result.get('url')
            blog_post.is_draft = is_draft
            blog_post.posted_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'blogger_url': result.get('url'),
                'blogger_post_id': result.get('id')
            })
        else:
            return jsonify({'error': 'Failed to publish to Blogger'}), 500
            
    except Exception as e:
        logging.error(f"Error publishing to Blogger: {str(e)}")
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
        
        queue_item = PostQueue(
            user_id=user.id,
            topic_or_url=topic_or_url
        )
        
        db.session.add(queue_item)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'queue_id': queue_item.id
        })

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
