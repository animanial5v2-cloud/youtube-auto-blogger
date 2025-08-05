import requests
import logging

class TistoryService:
    def __init__(self):
        self.base_url = "https://www.tistory.com/apis"
    
    def publish_post(self, blog_name, access_token, title, content, is_draft=False):
        """Tistory API has been discontinued since 2021"""
        logging.error("Tistory API has been discontinued since 2021")
        return {
            'error': 'Tistory API가 2021년부터 중단되었습니다. 수동 포스팅을 권장합니다.',
            'manual_guide': f"1. {blog_name}.tistory.com에서 직접 로그인\n2. 새 글 작성에서 제목과 내용 복사/붙여넣기\n3. 수동으로 발행",
            'title': title,
            'content': content
        }
    
    def get_blog_info(self, access_token):
        """Get user's Tistory blog information"""
        try:
            url = f"{self.base_url}/blog/info"
            
            params = {
                'access_token': access_token,
                'output': 'json'
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('tistory', {}).get('status') == '200':
                    blogs = result.get('tistory', {}).get('item', {}).get('blogs', [])
                    return blogs
                else:
                    logging.error(f"Tistory API error: {result.get('tistory', {}).get('error_message')}")
                    return []
            else:
                logging.error(f"Failed to get Tistory blog info: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logging.error(f"Failed to get Tistory blog info: {str(e)}")
            return []