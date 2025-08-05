import requests
import logging

class NaverService:
    def __init__(self):
        self.base_url = "https://openapi.naver.com/v1"
    
    def publish_post(self, blog_id, client_id, client_secret, title, content, is_draft=False):
        """Publish post to Naver Blog"""
        try:
            if not all([blog_id, client_id, client_secret, title, content]):
                raise ValueError("Missing required parameters for Naver Blog publishing")
            
            url = f"{self.base_url}/blog/writePost.json"
            
            headers = {
                'X-Naver-Client-Id': client_id,
                'X-Naver-Client-Secret': client_secret,
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
            }
            
            data = {
                'blogId': blog_id,
                'title': title,
                'contents': content
            }
            
            response = requests.post(url, headers=headers, data=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('message') == 'success':
                    post_url = result.get('postUrl', f"https://blog.naver.com/{blog_id}")
                    
                    logging.info(f"Successfully published Naver Blog post")
                    return {
                        'id': result.get('postId', 'unknown'),
                        'url': post_url,
                        'title': title,
                        'published': True
                    }
                else:
                    error_msg = result.get('errorMessage', 'Unknown error')
                    logging.error(f"Naver Blog API error: {error_msg}")
                    return None
            else:
                logging.error(f"Naver Blog API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logging.error(f"Failed to publish to Naver Blog: {str(e)}")
            return None
    
    def get_blog_info(self, client_id, client_secret):
        """Get Naver Blog information (Note: Limited API access)"""
        try:
            # Note: Naver Blog API has limited access and may require additional verification
            logging.info("Naver Blog API access is limited and may require additional setup")
            return []
                
        except Exception as e:
            logging.error(f"Failed to get Naver Blog info: {str(e)}")
            return []