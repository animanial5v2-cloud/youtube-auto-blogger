import logging
import json
import os
import requests
import gc
import time
import signal
import base64

try:
    import google.generativeai as genai
    from google.generativeai import types
    HAS_GENAI = True
except ImportError:
    genai = None
    types = None
    HAS_GENAI = False

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_GEMINI_API_KEY') or os.getenv('GEMINI_API_KEY')
        if self.api_key and HAS_GENAI:
            genai.configure(api_key=self.api_key)
    
    def generate_text_content(self, api_key, topic, image_url=None, model_name='gemini-1.5-flash', tone='친근한', audience=''):
        """Generate blog content using Gemini API"""
        try:
            if not HAS_GENAI:
                raise ValueError("Google Generative AI library not available")
                
            # Use provided API key or fallback to environment
            effective_api_key = api_key or self.api_key
            if not effective_api_key:
                raise ValueError("Gemini API key is required")
            
            # Configure with the provided API key
            genai.configure(api_key=effective_api_key)
            
            # Initialize model
            model = genai.GenerativeModel(model_name)
            
            # JSON format prompt for consistent output
            prompt = f"""주제: {topic}
톤: {tone}
독자: {audience}

반드시 아래 JSON 형식으로만 응답하세요. 
- 최소 2500자 이상의 풍부하고 상세한 내용 작성
- 구조: 제목 → 소개 → [IMAGE_HERE] → 본문(여러 섹션)
- 실용적 정보와 구체적 예시 포함

{{
  "title": "매력적인 블로그 제목",
  "content_with_placeholder": "<h1>제목</h1><p>매력적인 소개 문단입니다. 독자의 관심을 끌고 본문에서 다룰 내용을 간략히 소개합니다.</p><p>두 번째 소개 문단으로 주제에 대한 배경과 중요성을 설명합니다.</p>[IMAGE_HERE]<h2>첫 번째 주요 섹션</h2><p>상세한 설명과 실용적 정보를 제공합니다...</p><h3>하위 섹션</h3><p>구체적인 예시와 팁을 제공합니다...</p><h2>두 번째 주요 섹션</h2><p>추가적인 상세 정보와 실무 활용법...</p><h2>결론</h2><p>핵심 내용 요약과 실행 방안...</p>",
  "summary": "1-2문장으로 핵심 내용 요약",
  "image_search_keywords": "영어 키워드 3개, 쉼표로 구분",
  "hashtags": "#키워드1 #키워드2 #키워드3"
}}"""
            
            # Prepare content for generation
            content_parts = [prompt]
            
            # Add image if provided
            if image_url and HAS_GENAI and types:
                try:
                    if image_url.startswith('data:'):
                        # Handle data URI
                        header, data = image_url.split(',', 1)
                        mime_type = header.split(';')[0].split(':')[1]
                        image_data = base64.b64decode(data)
                        image_part = types.BlobDict(
                            mime_type=mime_type,
                            data=image_data
                        )
                    else:
                        # Handle regular URL
                        image_response = requests.get(image_url)
                        if image_response.status_code == 200:
                            image_part = types.BlobDict(
                                mime_type='image/jpeg',
                                data=image_response.content
                            )
                        else:
                            raise ValueError(f"Failed to fetch image: {image_response.status_code}")
                    content_parts.append(image_part)
                except Exception as e:
                    logging.warning(f"Failed to process image: {str(e)}")
            
            # Generate content with enhanced retry and memory optimization
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # Force garbage collection before each attempt
                    gc.collect()
                    
                    # Add progressive delay between attempts  
                    if attempt > 0:
                        delay = min(2 ** attempt, 8)  # Cap at 8 seconds
                        time.sleep(delay)
                        logging.info(f"Retrying Gemini API call (attempt {attempt + 1}) after {delay}s delay")
                    
                    # Use very minimal configuration to prevent memory issues
                    if HAS_GENAI:
                        result = model.generate_content(
                            content_parts,
                            generation_config=genai.GenerationConfig(
                                temperature=0.7,
                                max_output_tokens=2048,  # Increased for longer content
                                candidate_count=1
                            )
                        )
                    else:
                        raise ValueError("Google Generative AI library not available")
                    
                    if not result:
                        raise ValueError("Empty result from Gemini API")
                        
                    if not hasattr(result, 'text') or not result.text:
                        logging.error(f"No text in Gemini result: {result}")
                        raise ValueError("Empty text response from Gemini API")
                    
                    generated_text = result.text.strip()
                    if len(generated_text) < 100:  # Sanity check
                        raise ValueError(f"Response too short: {len(generated_text)} characters")
                    
                    logging.info(f"Gemini text generation completed successfully ({len(generated_text)} characters)")
                    
                    # Clear result from memory
                    result = None
                    gc.collect()
                    
                    return self._parse_gemini_json_response(generated_text)
                    
                except (TimeoutError, Exception) as retry_error:
                    error_type = "Timeout" if isinstance(retry_error, TimeoutError) else "API Error"
                    logging.warning(f"Gemini {error_type} attempt {attempt + 1} failed: {str(retry_error)}")
                    
                    # Force cleanup on timeout/error
                    gc.collect()
                    
                    if attempt == max_retries - 1:
                        # Last attempt, raise the error
                        logging.error(f"All Gemini API attempts failed: {str(retry_error)}")
                        if isinstance(retry_error, TimeoutError):
                            raise ValueError("AI 서버 연결이 지연되고 있습니다. 잠시 후 다시 시도해주세요.")
                        else:
                            raise ValueError(f"AI 콘텐츠 생성에 실패했습니다. API 키를 확인해주세요. 오류: {str(retry_error)}")
                    
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
        
        # Remove markdown code blocks first
        import re
        cleaned_text = re.sub(r'```(?:json)?\s*', '', raw_text)
        cleaned_text = re.sub(r'\s*```', '', cleaned_text)
        cleaned_text = cleaned_text.strip()
        
        # Try multiple JSON extraction methods
        json_string = None
        
        # Method 1: Try to find complete JSON with proper brace matching
        start_idx = cleaned_text.find('{')
        if start_idx != -1:
            brace_count = 0
            end_idx = -1
            for i in range(start_idx, len(cleaned_text)):
                if cleaned_text[i] == '{':
                    brace_count += 1
                elif cleaned_text[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_idx = i
                        break
            
            if end_idx != -1:
                json_string = cleaned_text[start_idx:end_idx + 1]
        
        # Method 2: If incomplete JSON, try to fix it by adding missing closing braces
        if not json_string and start_idx != -1:
            partial_json = cleaned_text[start_idx:]
            open_braces = partial_json.count('{')
            close_braces = partial_json.count('}')
            
            if open_braces > close_braces:
                # Add missing closing braces
                missing_braces = open_braces - close_braces
                json_string = partial_json + '}' * missing_braces
        
        # Method 3: Last resort - use regex to find any JSON-like structure
        if not json_string:
            import re
            json_match = re.search(r'\{[^}]*\}', cleaned_text, re.DOTALL)
            if json_match:
                json_string = json_match.group(0)
        
        if not json_string:
            logging.error("No valid JSON structure found")
            logging.error(f"Raw response: {raw_text[:500]}...")
            return self._create_fallback_response(raw_text)
        
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
            logging.error(f"JSON decode error: {str(e)}")
            logging.error(f"Attempted to parse: {json_string[:300]}...")
            return self._create_fallback_response(raw_text)
    
    def _create_fallback_response(self, raw_text):
        """Create fallback response when JSON parsing fails"""
        lines = raw_text.split('\n')
        title_line = next((line.strip() for line in lines if line.strip() and len(line.strip()) > 10), "AI 생성 블로그 포스트")
        content_lines = [line for line in lines if line.strip() and not line.startswith('```')]
        content = '\n'.join(content_lines[:20])  # First 20 meaningful lines
        
        return {
            'title': title_line[:100],
            'content_with_placeholder': f"<h2>{title_line}</h2>\n<p>{content}</p>\n[IMAGE_HERE]",
            'summary': title_line,
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