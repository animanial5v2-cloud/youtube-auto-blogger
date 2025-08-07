import logging
import json
import os
import requests
from typing import Optional, Dict, Any

class GPTOSSService:
    """
    GPT-OSS Local Model Service
    Supports both local Ollama and remote hosted GPT-OSS endpoints
    """
    
    def __init__(self):
        # Default to local Ollama setup
        self.base_url = os.getenv('GPTOSS_BASE_URL', 'http://localhost:11434')
        self.api_key = os.getenv('GPTOSS_API_KEY')  # For hosted solutions
        self.timeout = 60  # Longer timeout for local models
        
    def generate_text_content(self, api_key: str, topic: str, image_url: Optional[str] = None, 
                            model_name: str = 'gpt-oss-20b', tone: str = '친근한', 
                            audience: str = '') -> Dict[str, Any]:
        """
        Generate blog content using GPT-OSS model
        
        Args:
            api_key: API key (for hosted solutions) or endpoint URL
            topic: Content topic
            image_url: Optional image URL
            model_name: GPT-OSS model name (gpt-oss-20b or gpt-oss-120b)
            tone: Writing tone
            audience: Target audience
            
        Returns:
            Dict containing generated content
        """
        try:
            # Use provided API key/URL or fallback to environment
            effective_endpoint = api_key if api_key and api_key.startswith('http') else self.base_url
            effective_api_key = api_key if api_key and not api_key.startswith('http') else self.api_key
            
            # Prepare the prompt
            prompt = f"""주제: {topic}
톤: {tone}
독자: {audience or '일반 대중'}

한국어로 고품질 블로그 포스트를 작성해주세요.
반드시 아래 JSON 형식으로만 응답하세요.
- 최소 3000자 이상의 전문적이고 상세한 내용 작성
- SEO 최적화된 제목과 구조
- 실용적 가치와 구체적 예시 풍부하게 포함
- 독자 참여를 유도하는 매력적인 문체
- 크몽 고객을 위한 상업적 품질

{{
  "title": "클릭하고 싶게 만드는 매력적인 제목 (60자 이내)",
  "content_with_placeholder": "<h1>제목</h1><p>독자의 관심을 즉시 끄는 매력적인 오프닝 문단입니다. 주제의 핵심 가치와 독자가 얻을 수 있는 구체적인 혜택을 명확히 제시합니다.</p><p>주제에 대한 배경 설명과 왜 지금 이 내용이 중요한지에 대한 맥락을 제공합니다.</p>[IMAGE_HERE]<h2>첫 번째 핵심 섹션 (실용적 정보)</h2><p>상세하고 실행 가능한 정보를 체계적으로 제공합니다. 구체적인 단계별 방법론과 실제 적용 사례를 포함합니다...</p><h3>세부 실행 방법</h3><p>독자가 바로 활용할 수 있는 구체적인 팁과 노하우를 제공합니다...</p><h2>두 번째 핵심 섹션 (심화 내용)</h2><p>보다 전문적이고 심화된 내용으로 독자의 이해도를 한 단계 더 끌어올립니다...</p><h2>실제 활용 사례와 결과</h2><p>실제 성공 사례와 구체적인 결과를 통해 신뢰성을 높입니다...</p><h2>마무리 및 실행 계획</h2><p>핵심 내용을 요약하고 독자가 취할 수 있는 구체적인 다음 단계를 제시합니다...</p>",
  "summary": "핵심 가치와 주요 내용을 2-3문장으로 명확히 요약",
  "image_search_keywords": "영어 키워드 3개, 쉼표로 구분",
  "hashtags": "#키워드1 #키워드2 #키워드3 #키워드4 #키워드5"
}}

반드시 위 JSON 형식으로만 응답하고, 다른 설명은 포함하지 마세요."""

            # Try Ollama format first
            success, result = self._try_ollama_request(effective_endpoint, model_name, prompt)
            if success:
                return result
                
            # Try OpenAI-compatible format
            success, result = self._try_openai_compatible_request(effective_endpoint, effective_api_key or "", model_name, prompt)
            if success:
                return result
                
            # Try hosted GPT-OSS service format
            success, result = self._try_hosted_gptoss_request(effective_endpoint, effective_api_key or "", model_name, prompt)
            if success:
                return result
                
            raise Exception("All GPT-OSS request methods failed")
            
        except Exception as e:
            logging.error(f"GPT-OSS generation failed: {e}")
            return {
                'error': f'GPT-OSS 콘텐츠 생성 실패: {str(e)}',
                'title': f'{topic} - GPT-OSS 생성 실패',
                'content': f'<h1>{topic}</h1><p>GPT-OSS 모델을 사용한 콘텐츠 생성에 실패했습니다.</p><p>오류: {str(e)}</p><p>설정을 확인하고 다시 시도해주세요.</p>',
                'summary': 'GPT-OSS 생성 실패',
                'image_search_keywords': 'error, failed, gpt-oss',
                'hashtags': '#GPT-OSS #오류 #실패'
            }

    def _try_ollama_request(self, base_url: str, model_name: str, prompt: str):
        """Try Ollama API format"""
        try:
            url = f"{base_url}/api/generate"
            payload = {
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 4096
                }
            }
            
            response = requests.post(url, json=payload, timeout=self.timeout)
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('response', '')
                return True, self._parse_json_response(content)
                
        except Exception as e:
            logging.debug(f"Ollama request failed: {e}")
            
        return False, {}

    def _try_openai_compatible_request(self, base_url: str, api_key: str, model_name: str, prompt: str):
        """Try OpenAI-compatible API format"""
        try:
            url = f"{base_url}/v1/chat/completions"
            headers = {"Content-Type": "application/json"}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
                
            payload = {
                "model": model_name,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 4096,
                "temperature": 0.7
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                return True, self._parse_json_response(content)
                
        except Exception as e:
            logging.debug(f"OpenAI-compatible request failed: {e}")
            
        return False, {}

    def _try_hosted_gptoss_request(self, base_url: str, api_key: str, model_name: str, prompt: str):
        """Try hosted GPT-OSS service format"""
        try:
            url = f"{base_url}/api/v1/generate"
            headers = {"Content-Type": "application/json"}
            if api_key:
                headers["X-API-Key"] = api_key
                
            payload = {
                "model": model_name,
                "prompt": prompt,
                "max_length": 4096,
                "temperature": 0.7
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('generated_text', result.get('text', ''))
                return True, self._parse_json_response(content)
                
        except Exception as e:
            logging.debug(f"Hosted GPT-OSS request failed: {e}")
            
        return False, {}

    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """Parse JSON response from model output"""
        try:
            # Try to extract JSON from response
            content = content.strip()
            
            # Look for JSON block
            if '```json' in content:
                start = content.find('```json') + 7
                end = content.find('```', start)
                content = content[start:end].strip()
            elif '{' in content and '}' in content:
                start = content.find('{')
                end = content.rfind('}') + 1
                content = content[start:end]
                
            parsed = json.loads(content)
            
            # Validate required fields
            required_fields = ['title', 'content_with_placeholder', 'summary', 'image_search_keywords', 'hashtags']
            for field in required_fields:
                if field not in parsed:
                    parsed[field] = f"Missing {field}"
                    
            return parsed
            
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON response: {e}")
            return {
                'title': 'JSON 파싱 오류',
                'content_with_placeholder': f'<h1>응답 파싱 실패</h1><p>모델 응답: {content[:500]}...</p>',
                'summary': 'JSON 형식 오류',
                'image_search_keywords': 'error, parsing, json',
                'hashtags': '#오류 #파싱실패'
            }

    def check_model_availability(self, endpoint: str, api_key: str = None, model_name: str = 'gpt-oss-20b') -> Dict[str, Any]:
        """Check if GPT-OSS model is available at the given endpoint"""
        try:
            # Try a simple health check
            test_prompt = "Hello, respond with just 'OK' in JSON format: {\"status\": \"OK\"}"
            
            success, result = self._try_ollama_request(endpoint, model_name, test_prompt)
            if success:
                return {"available": True, "method": "ollama", "model": model_name}
                
            success, result = self._try_openai_compatible_request(endpoint, api_key or "", model_name, test_prompt)
            if success:
                return {"available": True, "method": "openai_compatible", "model": model_name}
                
            success, result = self._try_hosted_gptoss_request(endpoint, api_key or "", model_name, test_prompt)
            if success:
                return {"available": True, "method": "hosted_gptoss", "model": model_name}
                
            return {"available": False, "error": "No compatible API found"}
            
        except Exception as e:
            return {"available": False, "error": str(e)}

    def list_available_models(self, endpoint: str, api_key: str = None) -> list:
        """List available GPT-OSS models"""
        models = []
        
        # Common GPT-OSS model names
        common_models = ['gpt-oss-20b', 'gpt-oss-120b']
        
        for model in common_models:
            check = self.check_model_availability(endpoint, api_key, model)
            if check.get('available', False):
                models.append({
                    'name': model,
                    'display_name': f"GPT-OSS {model.split('-')[-1].upper()}",
                    'method': check.get('method', 'unknown')
                })
                
        return models if models else [{'name': 'gpt-oss-20b', 'display_name': 'GPT-OSS 20B (기본값)', 'method': 'unknown'}]