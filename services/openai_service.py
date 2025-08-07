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

고품질 블로그 포스트를 JSON 형식으로 작성하세요:
- 최소 3000자 이상의 전문적이고 상세한 내용
- SEO 최적화된 제목과 구조  
- 실용적 가치와 구체적 예시 풍부하게 포함
- 독자 참여를 유도하는 매력적인 문체

{{
  "title": "클릭하고 싶게 만드는 매력적인 제목 (60자 이내)",
  "content_with_placeholder": "<h1>제목</h1><p>독자의 관심을 즉시 끄는 매력적인 오프닝 문단입니다. 주제의 핵심 가치와 독자가 얻을 수 있는 구체적인 혜택을 명확히 제시합니다.</p><p>주제에 대한 배경 설명과 왜 지금 이 내용이 중요한지에 대한 맥락을 제공합니다.</p>[IMAGE_HERE]<h2>첫 번째 핵심 섹션 (실용적 정보)</h2><p>상세하고 실행 가능한 정보를 체계적으로 제공합니다. 구체적인 단계별 방법론과 실제 적용 사례를 포함합니다...</p><h3>세부 실행 방법</h3><p>독자가 바로 활용할 수 있는 구체적인 팁과 노하우를 제공합니다...</p><h2>두 번째 핵심 섹션 (심화 내용)</h2><p>보다 전문적이고 심화된 내용으로 독자의 이해도를 한 단계 더 끌어올립니다...</p><h2>실제 활용 사례와 결과</h2><p>실제 성공 사례와 구체적인 결과를 통해 신뢰성을 높입니다...</p><h2>마무리 및 실행 계획</h2><p>핵심 내용을 요약하고 독자가 취할 수 있는 구체적인 다음 단계를 제시합니다...</p>",
  "summary": "핵심 가치와 주요 내용을 2-3문장으로 명확히 요약",
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
                "max_tokens": 4096,
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