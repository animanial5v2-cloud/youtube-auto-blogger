from flask import Flask, render_template, request, jsonify, send_file
import os
import json
from datetime import datetime
from google_blogger_automation import GoogleBloggerAutomation
import zipfile
import io

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# OpenAI API 키 (환경 변수에서 가져오거나 직접 설정)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your-openai-api-key-here')

# 전역 변수로 자동화 인스턴스 저장
automation = None

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('google_blogger.html')

@app.route('/api/convert', methods=['POST'])
def convert_youtube_to_blog():
    """유튜브 스크립트를 구글 블로그 포스트로 변환하는 API"""
    try:
        data = request.get_json()
        youtube_url = data.get('youtube_url', '')
        script_text = data.get('script_text', '')
        publish_mode = data.get('publish_mode', 'draft')
        blog_id = data.get('blog_id', None)
        
        if not youtube_url or not script_text:
            return jsonify({'error': '유튜브 URL과 스크립트가 필요합니다.'}), 400
        
        # 자동화 인스턴스 초기화
        global automation
        automation = GoogleBloggerAutomation(OPENAI_API_KEY)
        
        # 블로그 포스트 생성
        result = automation.generate_full_blog_post(
            youtube_url, 
            script_text, 
            blog_id=blog_id,
            publish_mode=publish_mode
        )
        
        # 결과 반환
        return jsonify({
            'success': True,
            'result': result,
            'message': '구글 블로그 포스트가 성공적으로 생성되었습니다!'
        })
        
    except Exception as e:
        return jsonify({'error': f'변환 중 오류가 발생했습니다: {str(e)}'}), 500

@app.route('/api/blogs', methods=['GET'])
def get_blogs():
    """사용자의 구글 블로그 목록 가져오기"""
    try:
        global automation
        if not automation:
            automation = GoogleBloggerAutomation(OPENAI_API_KEY)
        
        # 블로그 목록 가져오기
        blogs = automation.blogger_service.blogs().listByUser(userId='self').execute()
        
        blog_list = []
        if blogs.get('items'):
            for blog in blogs['items']:
                blog_list.append({
                    'id': blog['id'],
                    'name': blog['name'],
                    'url': blog['url'],
                    'description': blog.get('description', '')
                })
        
        return jsonify({
            'success': True,
            'blogs': blog_list
        })
        
    except Exception as e:
        return jsonify({'error': f'블로그 목록 가져오기 실패: {str(e)}'}), 500

@app.route('/api/preview', methods=['POST'])
def preview_content():
    """생성된 콘텐츠 미리보기"""
    try:
        data = request.get_json()
        script_text = data.get('script_text', '')
        
        if not script_text:
            return jsonify({'error': '스크립트가 필요합니다.'}), 400
        
        # 자동화 인스턴스 초기화
        global automation
        automation = GoogleBloggerAutomation(OPENAI_API_KEY)
        
        # 스크립트 분석
        post_data = automation.analyze_youtube_script(script_text)
        
        return jsonify({
            'success': True,
            'post_data': post_data
        })
        
    except Exception as e:
        return jsonify({'error': f'미리보기 중 오류가 발생했습니다: {str(e)}'}), 500

@app.route('/api/publish', methods=['POST'])
def publish_draft():
    """초안을 발행 상태로 변경"""
    try:
        data = request.get_json()
        blog_id = data.get('blog_id')
        post_id = data.get('post_id')
        
        if not blog_id or not post_id:
            return jsonify({'error': '블로그 ID와 포스트 ID가 필요합니다.'}), 400
        
        global automation
        if not automation:
            automation = GoogleBloggerAutomation(OPENAI_API_KEY)
        
        # 포스트 발행
        post = automation.blogger_service.posts().publish(
            blogId=blog_id,
            postId=post_id
        ).execute()
        
        return jsonify({
            'success': True,
            'post': post,
            'message': '포스트가 성공적으로 발행되었습니다!'
        })
        
    except Exception as e:
        return jsonify({'error': f'발행 중 오류가 발생했습니다: {str(e)}'}), 500

@app.route('/api/delete', methods=['POST'])
def delete_post():
    """포스트 삭제"""
    try:
        data = request.get_json()
        blog_id = data.get('blog_id')
        post_id = data.get('post_id')
        
        if not blog_id or not post_id:
            return jsonify({'error': '블로그 ID와 포스트 ID가 필요합니다.'}), 400
        
        global automation
        if not automation:
            automation = GoogleBloggerAutomation(OPENAI_API_KEY)
        
        # 포스트 삭제
        automation.blogger_service.posts().delete(
            blogId=blog_id,
            postId=post_id
        ).execute()
        
        return jsonify({
            'success': True,
            'message': '포스트가 성공적으로 삭제되었습니다!'
        })
        
    except Exception as e:
        return jsonify({'error': f'삭제 중 오류가 발생했습니다: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

