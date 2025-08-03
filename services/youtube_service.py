import logging
import re
import requests
from urllib.parse import urlparse, parse_qs
import os

class YouTubeService:
    def __init__(self):
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')
    
    def extract_video_id(self, url):
        """Extract video ID from YouTube URL"""
        try:
            if 'youtu.be' in url:
                return url.split('/')[-1].split('?')[0]
            elif 'youtube.com' in url:
                parsed = urlparse(url)
                if 'watch' in parsed.path:
                    return parse_qs(parsed.query).get('v', [None])[0]
                elif 'embed' in parsed.path:
                    return parsed.path.split('/')[-1]
            return None
        except Exception:
            return None
    
    def extract_transcript(self, url, settings=None):
        """Extract transcript from YouTube video with improved error handling"""
        try:
            # Try multiple methods for transcript extraction
            transcript_text = None
            
            # Method 1: Try youtube-transcript-api (most reliable)
            try:
                from youtube_transcript_api import YouTubeTranscriptApi
                video_id = self.extract_video_id(url)
                if video_id:
                    logging.info(f"Attempting transcript extraction for video ID: {video_id}")
                    
                    # Try multiple languages
                    languages = ['ko', 'en', 'auto']
                    for lang in languages:
                        try:
                            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
                            transcript_text = ' '.join([item['text'] for item in transcript_list])
                            logging.info(f"Successfully extracted transcript in language: {lang}")
                            break
                        except Exception as lang_error:
                            logging.warning(f"Failed to get transcript in {lang}: {str(lang_error)}")
                            continue
                            
            except ImportError:
                logging.warning("youtube-transcript-api not available, trying alternative methods")
            except Exception as e:
                logging.warning(f"youtube-transcript-api failed: {str(e)}")
            
            # Method 2: Try using YouTube API for video metadata if transcript fails
            if not transcript_text and self.youtube_api_key:
                try:
                    video_id = self.extract_video_id(url)
                    if video_id:
                        api_url = f"https://www.googleapis.com/youtube/v3/videos"
                        params = {
                            'id': video_id,
                            'part': 'snippet',
                            'key': self.youtube_api_key
                        }
                        response = requests.get(api_url, params=params)
                        if response.status_code == 200:
                            data = response.json()
                            if data.get('items'):
                                video_info = data['items'][0]['snippet']
                                title = video_info.get('title', '')
                                description = video_info.get('description', '')
                                transcript_text = f"Video Title: {title}\n\nDescription: {description}"
                                logging.info("Using video metadata as fallback content")
                except Exception as e:
                    logging.warning(f"YouTube API fallback failed: {str(e)}")
            
            # Method 3: Extract from URL patterns (last resort)
            if not transcript_text:
                try:
                    # Try to get basic video info from URL
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        # Extract title from page if possible
                        title_match = re.search(r'<title>(.*?)</title>', response.text)
                        if title_match:
                            title = title_match.group(1).replace(' - YouTube', '')
                            transcript_text = f"Content analysis based on video: {title}"
                            logging.info("Using video title as minimal content source")
                except Exception as e:
                    logging.warning(f"URL scraping fallback failed: {str(e)}")
            
            return transcript_text
            
        except Exception as e:
            logging.error(f"All transcript extraction methods failed: {str(e)}")
            # Return None to let the calling function handle this gracefully
            return None
    
    def fetch_image_from_pexels(self, keywords, api_key):
        """Fetch image from Pexels API"""
        try:
            if not api_key or not keywords:
                return None
                
            # Flatten keywords if it's a list of lists
            if isinstance(keywords, list) and len(keywords) > 0 and isinstance(keywords[0], list):
                keywords = keywords[0]
            
            for keyword in keywords:
                try:
                    search_term = keyword.strip() if isinstance(keyword, str) else ' '.join(keyword)
                    if not search_term:
                        continue
                        
                    url = "https://api.pexels.com/v1/search"
                    headers = {"Authorization": api_key}
                    params = {
                        "query": search_term,
                        "per_page": 15,
                        "orientation": "landscape"
                    }
                    
                    response = requests.get(url, headers=headers, params=params, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        photos = data.get('photos', [])
                        if photos:
                            # Return the first suitable image
                            photo = photos[0]
                            return photo['src']['large2x']
                            
                except Exception as e:
                    logging.warning(f"Pexels search failed for keyword '{keyword}': {str(e)}")
                    continue
            
            return None
            
        except Exception as e:
            logging.error(f"Pexels image fetch failed: {str(e)}")
            return None
