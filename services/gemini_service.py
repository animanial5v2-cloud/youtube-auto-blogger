import logging
import json
import os
import requests
import google.generativeai as genai

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if self.api_key:
            genai.configure(api_key=self.api_key)
    
    def generate_text_content(self, api_key, topic, image_url=None, model_name='gemini-1.5-pro-latest', tone='친근한', audience=''):
        """Generate blog content using Gemini API"""
        try:
            # Use provided API key or fallback to environment
            effective_api_key = api_key or self.api_key
            if not effective_api_key:
                raise ValueError("Gemini API key is required")
            
            # Configure with the provided API key
            genai.configure(api_key=effective_api_key)
            
            # Initialize model
            model = genai.GenerativeModel(model_name)
            
            # Check if this is YouTube content to adjust the prompt
            is_youtube_content = "YouTube video" in topic or len(topic) > 1000
            content_length_instruction = """

**[콘텐츠 길이 요구사항]**
- YouTube 영상 기반 콘텐츠의 경우: 최소 2500-4000자 이상의 상세하고 풍부한 콘텐츠를 작성해야 합니다.
- 일반 주제의 경우: 최소 1500-2500자 이상의 완성도 높은 콘텐츠를 작성해야 합니다.
- 영상에서 제공된 모든 주요 정보, 데이터, 사례를 빠짐없이 포함해야 합니다.
- 각 섹션마다 구체적인 설명과 예시를 충분히 포함해야 합니다.
- 독자가 영상을 보지 않아도 완전히 이해할 수 있을 정도로 상세하게 작성해야 합니다.""" if is_youtube_content else """

**[콘텐츠 길이 요구사항]**
- 최소 1500-2500자 이상의 완성도 높은 콘텐츠를 작성해야 합니다.
- 각 섹션마다 구체적인 설명과 예시를 충분히 포함해야 합니다."""
            
            # Prepare the prompt
            prompt = f"""당신은 전문 SEO 콘텐츠 작가입니다. 주어진 지침에 따라 블로그 게시물을 생성하고, 반드시 지정된 JSON 형식으로만 응답해야 합니다.

**주제:** "{topic}"
**글쓰기 톤 & 스타일:** {tone}
**타겟 독자:** {audience or '일반 대중'}{content_length_instruction}

**[매우 중요] 출력 형식:**
- 당신의 전체 응답은 반드시 아래 구조를 따르는 단일 JSON 객체여야 합니다.
- JSON 외부에는 어떠한 설명이나 추가 텍스트도 포함해서는 안 됩니다.

```json
{{
  "title": "SEO에 최적화된, 흥미로운 한글 제목",
  "content_with_placeholder": "본문의 내용과 흐름을 고려하여, 이미지가 들어갈 가장 적절한 위치에 '[IMAGE_HERE]' 라는 문자열을 **반드시 단 한 번만 포함**시킨 전체 글 내용. 서론, 본론(여러 세부 섹션으로 나누어), 결론을 포함하여 상세하고 풍부하게 작성해야 합니다. YouTube 영상의 경우 영상에서 언급된 모든 주요 포인트, 데이터, 사례를 빠짐없이 포함해야 합니다.",
  "image_search_keywords": "블로그 글의 핵심 내용을 가장 잘 나타내는, Pexels에서 검색할 **영어 검색어 목록**. 쉼표(,)로 구분된 3-4개의 키워드를 제공해주세요.",
  "summary": "블로그 글의 내용을 1~2 문장으로 요약한 내용."
}}
```

**[필수 규칙]**
1. `content_with_placeholder` 필드에 '[IMAGE_HERE]'를 포함하는 것은 선택이 아닌 **필수 요구사항**입니다.
2. HTML 구조: 본문 내용은 `<h2>`, `<h3>`, `<p>`, `<ul>`, `<li>`, `<blockquote>`, `<strong>`, `<em>` 등의 태그를 사용하여 의미적으로 구조화해야 합니다.
3. 세부 구성: 서론 → 여러 개의 본론 섹션(각각 `<h2>` 또는 `<h3>` 제목 포함) → 결론 순서로 구성해야 합니다.
4. 영상 기반 콘텐츠: YouTube 영상에서 언급된 모든 정보를 빠짐없이 포함하고, 각 포인트마다 충분한 설명과 맥락을 제공해야 합니다.
{f'5. **이미지 문맥:** 제공된 이미지를 분석하여, "[IMAGE_HERE]" 플레이스홀더를 이미지 내용과 가장 관련이 깊은 문단 바로 뒤에 배치해야 합니다.' if image_url else ''}"""
            
            # Prepare content for generation
            content_parts = [prompt]
            
            # Add image if provided
            if image_url:
                try:
                    # Convert data URI to generative part 
                    image_part = self._data_uri_to_generative_part(image_url)
                    content_parts.append(image_part)
                except Exception as e:
                    logging.warning(f"Failed to process image: {str(e)}")
            
            # Generate content
            result = model.generate_content(content_parts)
            generated_text = result.text
            
            logging.info("Gemini text generation completed successfully")
            return self._parse_gemini_json_response(generated_text)
            
        except Exception as e:
            logging.error(f"Gemini API error: {str(e)}")
            raise
    
    def _data_uri_to_generative_part(self, uri):
        """Convert data URI to Gemini generative part"""
        import re
        match = re.match(r'^data:(.+);base64,(.+)$', uri)
        if not match:
            raise ValueError('Invalid data URI format')
        
        mime_type, data = match.groups()
        return {
            'inline_data': {
                'mime_type': mime_type,
                'data': data
            }
        }
    
    def _parse_gemini_json_response(self, raw_text):
        """Parse JSON response from Gemini output"""
        logging.info("Parsing JSON from Gemini response...")
        
        # Find JSON object boundaries
        json_start = raw_text.find('{')
        json_end = raw_text.rfind('}')
        
        if json_start == -1 or json_end == -1 or json_end < json_start:
            logging.error("No valid JSON object found in Gemini response")
            logging.error(f"Raw response: {raw_text}")
            raise ValueError("AI response does not contain valid JSON")
        
        json_string = raw_text[json_start:json_end + 1]
        
        try:
            parsed = json.loads(json_string)
            logging.info("JSON parsing successful")
            return parsed
        except json.JSONDecodeError as e:
            logging.error(f"JSON parsing failed: {str(e)}")
            logging.error(f"Extracted JSON string: {json_string}")
            logging.error(f"Raw response: {raw_text}")
            raise ValueError("AI response is not valid JSON format")
    
    def generate_ai_image(self, project_id, topic, access_token):
        """Generate AI image using Google Imagen 2"""
        try:
            if not all([project_id, access_token]):
                logging.warning("Missing project ID or access token for AI image generation")
                return None
            
            api_endpoint = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{project_id}/locations/us-central1/publishers/google/models/imagegeneration@006:predict"
            
            prompt = f"A high-quality, photorealistic, cinematic style image representing the concept of '{topic}', suitable for a professional blog post header."
            
            payload = {
                "instances": [{"prompt": prompt}],
                "parameters": {"sampleCount": 1}
            }
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(api_endpoint, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                prediction = result.get('predictions', [{}])[0]
                
                if prediction and prediction.get('bytesBase64Encoded'):
                    logging.info("AI image generation completed successfully")
                    return f"data:image/png;base64,{prediction['bytesBase64Encoded']}"
                else:
                    logging.warning("Imagen 2 API did not return image data")
                    return None
            else:
                logging.error(f"Imagen 2 API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logging.error(f"AI image generation failed: {str(e)}")
            return None