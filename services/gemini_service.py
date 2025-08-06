import logging
import json
import os
import requests
try:
    import google.generativeai as genai
except ImportError:
    genai = None

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if self.api_key and genai:
            genai.configure(api_key=self.api_key)
    
    def generate_text_content(self, api_key, topic, image_url=None, model_name='gemini-1.5-pro-latest', tone='친근한', audience=''):
        """Generate blog content using Gemini API"""
        try:
            if not genai:
                raise ValueError("Google Generative AI library not available")
                
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

**[콘텐츠 길이 요구사항 - 매우 중요]**
- 모든 콘텐츠는 최소 2500-4000자 이상으로 작성해야 합니다.
- YouTube 영상 기반: 영상의 모든 정보, 데이터, 사례를 상세히 포함 (4000자 이상)
- 일반 주제: 주제에 대한 포괄적이고 심화된 내용 작성 (2500-3500자 이상)
- 각 섹션은 최소 300-500자씩 충분한 설명과 구체적인 예시 포함
- 서론(300자) + 본론 4-6개 섹션(각 500-800자) + 결론(300자) 구조 필수
- 독자가 해당 주제의 전문가가 될 수 있을 정도로 상세하고 실용적인 정보 제공
- 관련 통계, 사례, 팁, 주의사항 등을 풍부하게 포함해야 합니다."""
            
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
  "content_with_placeholder": "본문의 내용과 흐름을 고려하여, 이미지가 들어갈 가장 적절한 위치에 '[IMAGE_HERE]' 라는 문자열을 **반드시 단 한 번만 포함**시킨 전체 글 내용. **반드시 2500자 이상으로 작성해야 하며**, 다음 구조를 따라야 합니다: 1) 서론(300-400자), 2) 본론 4-6개 섹션(각 섹션마다 500-800자씩, h2 또는 h3 제목 포함), 3) 결론(300-400자), 4) **마지막에 반드시 해시태그 섹션을 포함**해야 합니다 (예: <hr><p><strong>관련 키워드:</strong> #키워드1 #키워드2 #키워드3 #키워드4 #키워드5</p>). 각 섹션은 구체적인 예시, 통계, 사례, 실용적인 팁을 포함해야 하며, 단순한 설명이 아닌 깊이 있는 분석과 정보를 제공해야 합니다. YouTube 영상의 경우 영상에서 언급된 모든 정보를 빠짐없이 상세히 포함해야 합니다.",
  "image_search_keywords": "블로그 글의 핵심 내용을 가장 잘 나타내는, Pexels에서 검색할 **영어 검색어 목록**. 쉼표(,)로 구분된 3-4개의 키워드를 제공해주세요.",
  "summary": "블로그 글의 내용을 1~2 문장으로 요약한 내용.",
  "hashtags": "블로그 글의 주제와 관련된 5-8개의 한국어 해시태그. 각 해시태그는 #으로 시작하고 공백으로 구분됩니다. 예: #구글 #검색엔진 #기술혁신 #인터넷역사 #실리콘밸리"
}}
```

**[필수 규칙]**
1. **글자 수 준수**: `content_with_placeholder`는 반드시 2500자 이상이어야 합니다. 이는 절대 타협할 수 없는 요구사항입니다.
2. **구조화**: `<h2>`, `<h3>`, `<p>`, `<ul>`, `<li>`, `<blockquote>`, `<strong>`, `<em>` 등의 태그를 사용하여 의미적으로 구조화해야 합니다.
3. **섹션별 분량**: 서론(300-400자) + 본론 4-6개 섹션(각 500-800자) + 결론(300-400자) + 해시태그 섹션으로 구성하여 전체 2500자 이상 확보
4. **상세도**: 각 섹션마다 구체적인 예시, 통계, 데이터, 사례 연구, 실용적인 팁, 주의사항을 포함해야 합니다.
5. **전문성**: 독자가 해당 주제에 대해 전문적인 지식을 얻을 수 있을 정도로 심도 있게 작성해야 합니다.
6. **이미지 포함**: '[IMAGE_HERE]'를 포함하는 것은 선택이 아닌 **필수 요구사항**입니다.
7. **해시태그 필수**: 글 하단에 관련 키워드 해시태그 섹션을 반드시 포함해야 합니다.
{f'7. **이미지 문맥:** 제공된 이미지를 분석하여, "[IMAGE_HERE]" 플레이스홀더를 이미지 내용과 가장 관련이 깊은 문단 바로 뒤에 배치해야 합니다.' if image_url else ''}

**중요**: 만약 생성된 콘텐츠가 2500자 미만이라면, 각 섹션에 더 많은 세부사항, 예시, 설명을 추가하여 반드시 2500자 이상으로 확장해야 합니다."""
            
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
            
            # Generate content with retry and timeout handling
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    import time
                    # Add small delay between attempts
                    if attempt > 0:
                        time.sleep(2 ** attempt)  # Exponential backoff
                    
                    result = model.generate_content(
                        content_parts,
                        generation_config=genai.GenerationConfig(
                            temperature=0.7,
                            top_p=0.8,
                            top_k=40,
                            max_output_tokens=8192,
                            candidate_count=1
                        )
                    )
                    
                    if not result or not result.text:
                        raise ValueError("Empty response from Gemini API")
                    
                    generated_text = result.text
                    logging.info("Gemini text generation completed successfully")
                    return self._parse_gemini_json_response(generated_text)
                    
                except Exception as retry_error:
                    logging.warning(f"Gemini API attempt {attempt + 1} failed: {str(retry_error)}")
                    if attempt == max_retries - 1:
                        # Last attempt, raise the error
                        logging.error(f"All Gemini API attempts failed: {str(retry_error)}")
                        raise ValueError(f"Gemini API 연결에 실패했습니다. API 키를 확인해주세요. 오류: {str(retry_error)}")
                    
        except Exception as e:
            logging.error(f"Gemini API error: {str(e)}")
            raise ValueError(f"AI 콘텐츠 생성에 실패했습니다. API 키와 인터넷 연결을 확인해주세요.")
    
    def _data_uri_to_generative_part(self, uri):
        """Convert data URI to Gemini generative part"""
        import re
        import base64
        match = re.match(r'^data:(.+);base64,(.+)$', uri)
        if not match:
            raise ValueError('Invalid data URI format')
        
        mime_type, base64_data = match.groups()
        # Decode base64 data to bytes
        image_data = base64.b64decode(base64_data)
        
        # Return proper Part object for Gemini
        if genai and hasattr(genai, 'types'):
            return genai.types.BlobDict({
                'mime_type': mime_type,
                'data': image_data
            })
        else:
            return {
                'mime_type': mime_type,
                'data': image_data
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
            
            # Validate required fields
            if not parsed.get('title') or not parsed.get('content_with_placeholder'):
                logging.warning("Missing required fields in AI response")
                # Create fallback content if fields are missing
                if not parsed.get('title'):
                    parsed['title'] = "AI 생성 블로그 포스트"
                if not parsed.get('content_with_placeholder'):
                    parsed['content_with_placeholder'] = raw_text.replace(json_string, '').strip()
                    if not parsed['content_with_placeholder']:
                        parsed['content_with_placeholder'] = "AI가 생성한 콘텐츠입니다."
                if not parsed.get('summary'):
                    parsed['summary'] = parsed['title']
                if not parsed.get('image_search_keywords'):
                    parsed['image_search_keywords'] = "blog, content, article"
            
            return parsed
        except json.JSONDecodeError as e:
            logging.error(f"JSON parsing failed: {str(e)}")
            logging.error(f"Extracted JSON string: {json_string}")
            
            # Fallback: create basic content structure from raw response
            logging.info("Creating fallback content structure")
            lines = raw_text.split('\n')
            title = next((line.strip() for line in lines if line.strip() and len(line.strip()) > 10), "AI 생성 블로그 포스트")
            
            return {
                'title': title[:100],  # Limit title length
                'content_with_placeholder': f"<h2>{title}</h2>\n<p>{raw_text}</p>\n[IMAGE_HERE]",
                'summary': title,
                'image_search_keywords': "blog, content, article"
            }
    
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