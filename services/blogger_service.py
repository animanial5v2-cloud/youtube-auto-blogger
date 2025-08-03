import logging
import requests
import json

class BloggerService:
    def __init__(self):
        self.base_url = "https://www.googleapis.com/blogger/v3"
    
    def publish_post(self, access_token, blog_id, title, content, is_draft=False):
        """Publish post to Blogger"""
        try:
            if not all([access_token, blog_id, title, content]):
                raise ValueError("Missing required parameters for publishing")
            
            url = f"{self.base_url}/blogs/{blog_id}/posts"
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            post_data = {
                'title': title,
                'content': content
            }
            
            # Add draft parameter if needed
            params = {}
            if is_draft:
                params['isDraft'] = 'true'
            
            response = requests.post(url, headers=headers, json=post_data, params=params, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                logging.info(f"Successfully published post: {result.get('id')}")
                return {
                    'id': result.get('id'),
                    'url': result.get('url'),
                    'title': result.get('title'),
                    'published': result.get('published')
                }
            else:
                logging.error(f"Blogger API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logging.error(f"Failed to publish to Blogger: {str(e)}")
            return None
    
    def get_blogs(self, access_token):
        """Get user's blogs"""
        try:
            url = f"{self.base_url}/users/self/blogs"
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return response.json().get('items', [])
            else:
                logging.error(f"Failed to get blogs: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logging.error(f"Failed to get blogs: {str(e)}")
            return []
