import requests
import logging

class TistoryService:
    def __init__(self):
        self.base_url = "https://www.tistory.com/apis"
    
    def publish_post(self, blog_name, access_token, title, content, is_draft=False):
        """Publish post to Tistory"""
        try:
            if not all([blog_name, access_token, title, content]):
                raise ValueError("Missing required parameters for Tistory publishing")
            
            url = f"{self.base_url}/post/write"
            
            data = {
                'access_token': access_token,
                'blogName': blog_name,
                'title': title,
                'content': content,
                'visibility': '0' if is_draft else '3',  # 0=private, 3=public
                'output': 'json'
            }
            
            response = requests.post(url, data=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('tistory', {}).get('status') == '200':
                    post_id = result.get('tistory', {}).get('postId')
                    post_url = f"https://{blog_name}.tistory.com/{post_id}"
                    
                    logging.info(f"Successfully published Tistory post: {post_id}")
                    return {
                        'id': post_id,
                        'url': post_url,
                        'title': title,
                        'published': True
                    }
                else:
                    error_msg = result.get('tistory', {}).get('error_message', 'Unknown error')
                    logging.error(f"Tistory API error: {error_msg}")
                    return None
            else:
                logging.error(f"Tistory API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logging.error(f"Failed to publish to Tistory: {str(e)}")
            return None
    
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