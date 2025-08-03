import requests
import logging
import base64

class WordPressService:
    def __init__(self):
        self.api_version = "wp/v2"
    
    def publish_post(self, site_url, access_token, title, content, is_draft=False):
        """Publish post to WordPress.com"""
        try:
            if not all([site_url, access_token, title, content]):
                raise ValueError("Missing required parameters for WordPress publishing")
            
            # Ensure site_url format
            if not site_url.startswith('http'):
                site_url = f"https://{site_url}"
            
            url = f"{site_url}/wp-json/{self.api_version}/posts"
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            post_data = {
                'title': title,
                'content': content,
                'status': 'draft' if is_draft else 'publish'
            }
            
            response = requests.post(url, headers=headers, json=post_data, timeout=30)
            
            if response.status_code in [200, 201]:
                result = response.json()
                logging.info(f"Successfully published WordPress post: {result.get('id')}")
                return {
                    'id': result.get('id'),
                    'url': result.get('link'),
                    'title': result.get('title', {}).get('rendered', title),
                    'published': result.get('date')
                }
            else:
                logging.error(f"WordPress API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logging.error(f"Failed to publish to WordPress: {str(e)}")
            return None
    
    def get_sites(self, access_token):
        """Get user's WordPress sites"""
        try:
            url = "https://public-api.wordpress.com/rest/v1.1/me/sites"
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('sites', [])
            else:
                logging.error(f"Failed to get WordPress sites: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logging.error(f"Failed to get WordPress sites: {str(e)}")
            return []