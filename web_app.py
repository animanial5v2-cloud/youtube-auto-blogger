from flask import Flask, render_template, request, jsonify, send_file
import os
import json
from datetime import datetime
from youtube_to_seo_content import YouTubeToSEOContent
import zipfile
import io

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# OpenAI API 키 (환경 변수에서 가져오거나 직접 설정)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your-openai-api-key-here')

# 전역 변수로 변환기 인스턴스 저장
converter = None

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')

@app.route('/api/convert', methods=['POST'])
def convert_youtube_to_seo():
    """유튜브 스크립트를 SEO 콘텐츠로 변환하는 API"""
    try:
        data = request.get_json()
        youtube_url = data.get('youtube_url', '')
        script_text = data.get('script_text', '')
        
        if not youtube_url or not script_text:
            return jsonify({'error': '유튜브 URL과 스크립트가 필요합니다.'}), 400
        
        # 변환기 초기화
        global converter
        converter = YouTubeToSEOContent(OPENAI_API_KEY)
        
        # SEO 패키지 생성
        package = converter.generate_full_package(youtube_url, script_text)
        
        # 결과 반환
        return jsonify({
            'success': True,
            'package': package,
            'message': 'SEO 콘텐츠가 성공적으로 생성되었습니다!'
        })
        
    except Exception as e:
        return jsonify({'error': f'변환 중 오류가 발생했습니다: {str(e)}'}), 500

@app.route('/api/download', methods=['POST'])
def download_package():
    """생성된 패키지를 ZIP 파일로 다운로드"""
    try:
        data = request.get_json()
        package = data.get('package', {})
        
        if not package:
            return jsonify({'error': '패키지 데이터가 없습니다.'}), 400
        
        # ZIP 파일 생성
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # HTML 파일 추가
            if 'seo_content' in package and 'html_content' in package['seo_content']:
                zip_file.writestr('blog_post.html', package['seo_content']['html_content'])
            
            # 분석 결과 JSON 추가
            if 'analysis' in package:
                zip_file.writestr('analysis.json', json.dumps(package['analysis'], ensure_ascii=False, indent=2))
            
            # 소셜미디어 콘텐츠 JSON 추가
            if 'social_media' in package:
                zip_file.writestr('social_media.json', json.dumps(package['social_media'], ensure_ascii=False, indent=2))
            
            # 이미지 URL 텍스트 파일 추가
            if 'images' in package:
                image_content = ""
                for i, img_url in enumerate(package['images']):
                    image_content += f"Image {i+1}: {img_url}\n"
                zip_file.writestr('images.txt', image_content)
            
            # README 파일 추가
            readme_content = """
# SEO 콘텐츠 패키지

이 패키지는 유튜브 스크립트를 분석하여 생성된 SEO 최적화된 콘텐츠를 포함합니다.

## 포함된 파일들:
- blog_post.html: SEO 최적화된 블로그 포스트
- analysis.json: 키워드 및 분석 결과
- social_media.json: 소셜미디어용 콘텐츠
- images.txt: 생성된 이미지 URL들

## 사용법:
1. blog_post.html을 웹사이트에 업로드
2. analysis.json의 키워드를 활용하여 추가 SEO 최적화
3. social_media.json의 콘텐츠를 각 플랫폼에 게시
4. images.txt의 이미지 URL을 다운로드하여 사용

생성 시간: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            zip_file.writestr('README.txt', readme_content)
        
        zip_buffer.seek(0)
        
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'seo_package_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
        )
        
    except Exception as e:
        return jsonify({'error': f'다운로드 중 오류가 발생했습니다: {str(e)}'}), 500

@app.route('/api/preview', methods=['POST'])
def preview_content():
    """생성된 콘텐츠 미리보기"""
    try:
        data = request.get_json()
        package = data.get('package', {})
        
        if not package:
            return jsonify({'error': '패키지 데이터가 없습니다.'}), 400
        
        # HTML 콘텐츠 추출
        html_content = ""
        if 'seo_content' in package and 'html_content' in package['seo_content']:
            html_content = package['seo_content']['html_content']
        
        return jsonify({
            'success': True,
            'html_content': html_content,
            'analysis': package.get('analysis', {}),
            'social_media': package.get('social_media', {}),
            'images': package.get('images', [])
        })
        
    except Exception as e:
        return jsonify({'error': f'미리보기 중 오류가 발생했습니다: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
