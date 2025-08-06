import logging
import json
import os
import requests

class OpenAIService:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.base_url = "https://api.openai.com/v1/chat/completions"
    
    def generate_text_content(self, api_key, topic, image_url=None, model_name='gpt-3.5-turbo', tone='친근한', audience=''):
        """Generate blog content using OpenAI API as fallback"""
        try:
            # Use provided API key or fallback to environment
            effective_api_key = api_key or self.api_key
            if not effective_api_key:
                raise ValueError("OpenAI API key is required")
            
            # Prepare the prompt
            prompt = f"""주제: {topic}
톤: {tone}
독자: {audience or '일반 대중'}

다음 JSON 형식으로만 응답해주세요:
{{
  "title": "매력적인 블로그 제목",
  "content_with_placeholder": "HTML 태그로 구조화된 블로그 글 내용 (최소 1500자, [IMAGE_HERE] 플레이스홀더 포함)",
  "summary": "1-2문장 요약",
  "image_search_keywords": "영어 키워드 3개, 쉼표로 구분",
  "hashtags": "#키워드1 #키워드2 #키워드3"
}}

반드시 위 JSON 형식으로만 응답하고, 다른 설명은 포함하지 마세요."""

            headers = {
                'Authorization': f'Bearer {effective_api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "model": model_name,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 2000,
                "temperature": 0.7
            }
            
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code != 200:
                raise ValueError(f"OpenAI API error: {response.status_code}")
            
            result = response.json()
            content = result['choices'][0]['message']['content'].strip()
            
            # Parse JSON response
            try:
                parsed_content = json.loads(content)
                
                # Validate required fields
                if not parsed_content.get('title'):
                    parsed_content['title'] = f"{topic}에 대한 블로그 포스트"
                if not parsed_content.get('content_with_placeholder'):
                    parsed_content['content_with_placeholder'] = f"<h2>{topic}</h2><p>AI가 생성한 콘텐츠입니다.</p>[IMAGE_HERE]"
                if not parsed_content.get('summary'):
                    parsed_content['summary'] = parsed_content['title']
                if not parsed_content.get('image_search_keywords'):
                    parsed_content['image_search_keywords'] = f"{topic}, blog, content"
                if not parsed_content.get('hashtags'):
                    parsed_content['hashtags'] = f"#{topic} #블로그 #콘텐츠"
                
                return parsed_content
                
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    'title': f"{topic}에 대한 블로그 포스트",
                    'content_with_placeholder': f"<h2>{topic}</h2><p>{content}</p>[IMAGE_HERE]",
                    'summary': f"{topic}에 대한 블로그 포스트",
                    'image_search_keywords': f"{topic}, blog, content",
                    'hashtags': f"#{topic} #블로그 #콘텐츠"
                }
                
        except Exception as e:
            logging.error(f"OpenAI API error: {str(e)}")
            # Provide simple fallback content if OpenAI fails too
            return {
                'title': f"{topic}에 대한 블로그 포스트",
                'content_with_placeholder': f"<h2>{topic}</h2><p>이 주제에 대한 유용한 정보를 제공하는 블로그 포스트입니다.</p>[IMAGE_HERE]<p>자세한 내용은 직접 작성해주세요.</p>",
                'summary': f"{topic}에 대한 정보",
                'image_search_keywords': f"{topic}, blog, information",
                'hashtags': f"#{topic} #블로그 #정보"
            }