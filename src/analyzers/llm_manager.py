import requests
import json
import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from src.utils.logger import get_global_logger
from src.utils.error_handler import handle_errors, ErrorCategory, error_context
from src.utils.debug_utils import debug_function, log_api_calls

load_dotenv()
logger = get_global_logger()

class LLMManager:
    """Manages multiple LLM providers and models"""
    
    def __init__(self):
        # Ollama configuration
        self.ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
        
        # OpenAI configuration
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.openai_url = os.getenv('OPENAI_URL', 'https://api.openai.com/v1')
        
        # Anthropic configuration
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.anthropic_url = os.getenv('ANTHROPIC_URL', 'https://api.anthropic.com/v1')
        
        # Google configuration
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        self.google_url = os.getenv('GOOGLE_URL', 'https://generativelanguage.googleapis.com/v1')
        
        # Grok configuration (xAI)
        self.grok_api_key = os.getenv('GROK_API_KEY')
        self.grok_url = os.getenv('GROK_URL', 'https://api.x.ai/v1')
        
        # Cohere configuration
        self.cohere_api_key = os.getenv('COHERE_API_KEY')
        self.cohere_url = os.getenv('COHERE_URL', 'https://api.cohere.ai/v1')
        
        # Mistral configuration
        self.mistral_api_key = os.getenv('MISTRAL_API_KEY')
        self.mistral_url = os.getenv('MISTRAL_URL', 'https://api.mistral.ai/v1')
        
        # Perplexity configuration
        self.perplexity_api_key = os.getenv('PERPLEXITY_API_KEY')
        self.perplexity_url = os.getenv('PERPLEXITY_URL', 'https://api.perplexity.ai')
        
    @handle_errors(category=ErrorCategory.API)
    def get_ollama_models(self) -> List[Dict[str, Any]]:
        """Get available models from Ollama server"""
        logger.debug(f"Fetching Ollama models from: {self.ollama_url}")
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = []
                for model in data.get('models', []):
                    models.append({
                        'name': model['name'],
                        'type': 'ollama',
                        'url': self.ollama_url,
                        'model_name': model['name'],
                        'size': model.get('size', 'Unknown'),
                        'modified_at': model.get('modified_at', 'Unknown')
                    })
                logger.info(f"Found {len(models)} Ollama models")
                return models
            else:
                logger.warning(f"Failed to get Ollama models: {response.status_code}")
                return []
        except Exception as e:
            logger.warning(f"Could not connect to Ollama server: {e}")
            return []
    
    def get_openai_models(self) -> List[Dict[str, Any]]:
        """Get available OpenAI models"""
        models = [
            {
                'name': 'GPT-4',
                'type': 'openai',
                'url': self.openai_url,
                'model_name': 'gpt-4',
                'api_key_required': True
            },
            {
                'name': 'GPT-4 Turbo',
                'type': 'openai',
                'url': self.openai_url,
                'model_name': 'gpt-4-turbo-preview',
                'api_key_required': True
            },
            {
                'name': 'GPT-3.5 Turbo',
                'type': 'openai',
                'url': self.openai_url,
                'model_name': 'gpt-3.5-turbo',
                'api_key_required': True
            },
            {
                'name': 'GPT-4 Vision',
                'type': 'openai',
                'url': self.openai_url,
                'model_name': 'gpt-4-vision-preview',
                'api_key_required': True
            }
        ]
        return models

    def get_anthropic_models(self) -> List[Dict[str, Any]]:
        """Get available Anthropic models"""
        models = [
            {
                'name': 'Claude 3 Opus',
                'type': 'anthropic',
                'url': self.anthropic_url,
                'model_name': 'claude-3-opus-20240229',
                'api_key_required': True
            },
            {
                'name': 'Claude 3 Sonnet',
                'type': 'anthropic',
                'url': self.anthropic_url,
                'model_name': 'claude-3-sonnet-20240229',
                'api_key_required': True
            },
            {
                'name': 'Claude 3 Haiku',
                'type': 'anthropic',
                'url': self.anthropic_url,
                'model_name': 'claude-3-haiku-20240307',
                'api_key_required': True
            },
            {
                'name': 'Claude 3.5 Sonnet',
                'type': 'anthropic',
                'url': self.anthropic_url,
                'model_name': 'claude-3-5-sonnet-20241022',
                'api_key_required': True
            }
        ]
        return models

    def get_google_models(self) -> List[Dict[str, Any]]:
        """Get available Google models"""
        models = [
            {
                'name': 'Gemini Pro',
                'type': 'google',
                'url': self.google_url,
                'model_name': 'gemini-pro',
                'api_key_required': True
            },
            {
                'name': 'Gemini Pro Vision',
                'type': 'google',
                'url': self.google_url,
                'model_name': 'gemini-pro-vision',
                'api_key_required': True
            },
            {
                'name': 'Gemini Flash',
                'type': 'google',
                'url': self.google_url,
                'model_name': 'gemini-1.5-flash',
                'api_key_required': True
            }
        ]
        return models

    def get_grok_models(self) -> List[Dict[str, Any]]:
        """Get available Grok models (xAI)"""
        models = [
            {
                'name': 'Grok-1',
                'type': 'grok',
                'url': self.grok_url,
                'model_name': 'grok-1',
                'api_key_required': True
            },
            {
                'name': 'Grok-1.5',
                'type': 'grok',
                'url': self.grok_url,
                'model_name': 'grok-1.5',
                'api_key_required': True
            }
        ]
        return models

    def get_cohere_models(self) -> List[Dict[str, Any]]:
        """Get available Cohere models"""
        models = [
            {
                'name': 'Command',
                'type': 'cohere',
                'url': self.cohere_url,
                'model_name': 'command',
                'api_key_required': True
            },
            {
                'name': 'Command R',
                'type': 'cohere',
                'url': self.cohere_url,
                'model_name': 'command-r',
                'api_key_required': True
            },
            {
                'name': 'Command R+',
                'type': 'cohere',
                'url': self.cohere_url,
                'model_name': 'command-r-plus',
                'api_key_required': True
            }
        ]
        return models

    def get_mistral_models(self) -> List[Dict[str, Any]]:
        """Get available Mistral models"""
        models = [
            {
                'name': 'Mistral Large',
                'type': 'mistral',
                'url': self.mistral_url,
                'model_name': 'mistral-large-latest',
                'api_key_required': True
            },
            {
                'name': 'Mistral Medium',
                'type': 'mistral',
                'url': self.mistral_url,
                'model_name': 'mistral-medium-latest',
                'api_key_required': True
            },
            {
                'name': 'Mistral Small',
                'type': 'mistral',
                'url': self.mistral_url,
                'model_name': 'mistral-small-latest',
                'api_key_required': True
            }
        ]
        return models

    def get_perplexity_models(self) -> List[Dict[str, Any]]:
        """Get available Perplexity models"""
        models = [
            {
                'name': 'Sonar Small',
                'type': 'perplexity',
                'url': self.perplexity_url,
                'model_name': 'sonar-small-online',
                'api_key_required': True
            },
            {
                'name': 'Sonar Medium',
                'type': 'perplexity',
                'url': self.perplexity_url,
                'model_name': 'sonar-medium-online',
                'api_key_required': True
            },
            {
                'name': 'Sonar Large',
                'type': 'perplexity',
                'url': self.perplexity_url,
                'model_name': 'sonar-large-online',
                'api_key_required': True
            }
        ]
        return models
    
    @handle_errors(category=ErrorCategory.FILE_IO)
    def load_models_config(self) -> Dict[str, Any]:
        """Load models configuration from JSON file"""
        logger.debug("Loading models configuration")
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'models.json')
            with open(config_path, 'r') as f:
                config = json.load(f)
            logger.info("Models configuration loaded successfully")
            return config
        except Exception as e:
            logger.warning(f"Could not load models config: {e}")
            return {"models": [], "providers": {}}
    
    def get_configured_models(self) -> List[Dict[str, Any]]:
        """Get models from the configuration file"""
        config = self.load_models_config()
        return config.get('models', [])
    
    def get_all_available_models(self) -> List[Dict[str, Any]]:
        """Get all available models from all providers"""
        models = []
        
        # Get Ollama models
        ollama_models = self.get_ollama_models()
        models.extend(ollama_models)
        
        # Get OpenAI models
        openai_models = self.get_openai_models()
        models.extend(openai_models)
        
        # Get Anthropic models
        anthropic_models = self.get_anthropic_models()
        models.extend(anthropic_models)
        
        # Get Google models
        google_models = self.get_google_models()
        models.extend(google_models)
        
        # Get Grok models
        grok_models = self.get_grok_models()
        models.extend(grok_models)
        
        # Get Cohere models
        cohere_models = self.get_cohere_models()
        models.extend(cohere_models)
        
        # Get Mistral models
        mistral_models = self.get_mistral_models()
        models.extend(mistral_models)
        
        # Get Perplexity models
        perplexity_models = self.get_perplexity_models()
        models.extend(perplexity_models)
        
        return models
    
    def load_prompts(self) -> Dict[str, Any]:
        """Load prompts from the prompts.json file"""
        try:
            import os
            import json
            
            # Get the project root directory
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            prompts_file = os.path.join(project_root, 'src', 'config', 'prompts.json')
            
            if os.path.exists(prompts_file):
                with open(prompts_file, 'r', encoding='utf-8') as f:
                    prompts = json.load(f)
                logger.info(f"Loaded {len(prompts)} prompts from {prompts_file}")
                return prompts
            else:
                logger.warning(f"Prompts file not found: {prompts_file}")
                return {}
        except Exception as e:
            logger.error(f"Error loading prompts: {e}")
            return {}
    
    def get_prompt_by_id(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific prompt by ID"""
        prompts = self.load_prompts()
        return prompts.get(prompt_id)
    
    def get_prompts_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all prompts in a specific category"""
        prompts = self.load_prompts()
        return [
            {'id': prompt_id, **prompt_data}
            for prompt_id, prompt_data in prompts.items()
            if prompt_data.get('CATEGORY') == category
        ]
    
    def get_available_prompts(self) -> List[Dict[str, Any]]:
        """Get all available prompts with their IDs"""
        prompts = self.load_prompts()
        return [
            {'id': prompt_id, **prompt_data}
            for prompt_id, prompt_data in prompts.items()
        ]
    
    def test_ollama_connection(self) -> bool:
        """Test connection to Ollama server"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def test_openai_connection(self) -> bool:
        """Test connection to OpenAI API"""
        if not self.openai_api_key:
            return False
        try:
            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json'
            }
            response = requests.get(f"{self.openai_url}/models", headers=headers, timeout=10)
            return response.status_code == 200
        except Exception:
            return False

    def test_anthropic_connection(self) -> bool:
        """Test connection to Anthropic API"""
        if not self.anthropic_api_key:
            return False
        try:
            headers = {
                'x-api-key': self.anthropic_api_key,
                'Content-Type': 'application/json'
            }
            response = requests.get(f"{self.anthropic_url}/models", headers=headers, timeout=10)
            return response.status_code == 200
        except Exception:
            return False

    def test_google_connection(self) -> bool:
        """Test connection to Google API"""
        if not self.google_api_key:
            return False
        try:
            response = requests.get(f"{self.google_url}/models?key={self.google_api_key}", timeout=10)
            return response.status_code == 200
        except Exception:
            return False

    def test_grok_connection(self) -> bool:
        """Test connection to Grok API (xAI)"""
        if not self.grok_api_key:
            return False
        try:
            headers = {
                'Authorization': f'Bearer {self.grok_api_key}',
                'Content-Type': 'application/json'
            }
            response = requests.get(f"{self.grok_url}/models", headers=headers, timeout=10)
            return response.status_code == 200
        except Exception:
            return False

    def test_cohere_connection(self) -> bool:
        """Test connection to Cohere API"""
        if not self.cohere_api_key:
            return False
        try:
            headers = {
                'Authorization': f'Bearer {self.cohere_api_key}',
                'Content-Type': 'application/json'
            }
            response = requests.get(f"{self.cohere_url}/models", headers=headers, timeout=10)
            return response.status_code == 200
        except Exception:
            return False

    def test_mistral_connection(self) -> bool:
        """Test connection to Mistral API"""
        if not self.mistral_api_key:
            return False
        try:
            headers = {
                'Authorization': f'Bearer {self.mistral_api_key}',
                'Content-Type': 'application/json'
            }
            response = requests.get(f"{self.mistral_url}/models", headers=headers, timeout=10)
            return response.status_code == 200
        except Exception:
            return False

    def test_perplexity_connection(self) -> bool:
        """Test connection to Perplexity API"""
        if not self.perplexity_api_key:
            return False
        try:
            headers = {
                'Authorization': f'Bearer {self.perplexity_api_key}',
                'Content-Type': 'application/json'
            }
            response = requests.get(f"{self.perplexity_url}/models", headers=headers, timeout=10)
            return response.status_code == 200
        except Exception:
            return False
    
    def analyze_with_ollama(self, image_path: str, prompt: str, model_name: str) -> Dict[str, Any]:
        """Analyze image using Ollama"""
        try:
            # Encode image to base64
            import base64
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            payload = {
                "model": model_name,
                "prompt": prompt,
                "images": [image_data],
                "stream": False
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "status": "success",
                    "response": result.get('response', ''),
                    "model": model_name,
                    "provider": "ollama"
                }
            else:
                return {
                    "status": "error",
                    "message": f"Ollama API error: {response.status_code}",
                    "model": model_name,
                    "provider": "ollama"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "model": model_name,
                "provider": "ollama"
            }
    
    def analyze_with_openai(self, image_path: str, prompt: str, model_name: str) -> Dict[str, Any]:
        """Analyze image using OpenAI"""
        if not self.openai_api_key:
            return {
                "status": "error",
                "message": "OpenAI API key not configured",
                "model": model_name,
                "provider": "openai"
            }
        
        try:
            # Encode image to base64
            import base64
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            payload = {
                "model": model_name,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 1000
            }
            
            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f"{self.openai_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "status": "success",
                    "response": result['choices'][0]['message']['content'],
                    "model": model_name,
                    "provider": "openai",
                    "usage": result.get('usage', {})
                }
            else:
                return {
                    "status": "error",
                    "message": f"OpenAI API error: {response.status_code} - {response.text}",
                    "model": model_name,
                    "provider": "openai"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "model": model_name,
                "provider": "openai"
            }
    
    def analyze_with_anthropic(self, image_path: str, prompt: str, model_name: str) -> Dict[str, Any]:
        """Analyze image using Anthropic Claude"""
        if not self.anthropic_api_key:
            return {
                "status": "error",
                "message": "Anthropic API key not configured",
                "model": model_name,
                "provider": "anthropic"
            }
        
        try:
            # Encode image to base64
            import base64
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            payload = {
                "model": model_name,
                "max_tokens": 1000,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": image_data
                                }
                            }
                        ]
                    }
                ]
            }
            
            headers = {
                'x-api-key': self.anthropic_api_key,
                'Content-Type': 'application/json',
                'anthropic-version': '2023-06-01'
            }
            
            response = requests.post(
                f"{self.anthropic_url}/messages",
                json=payload,
                headers=headers,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "status": "success",
                    "response": result['content'][0]['text'],
                    "model": model_name,
                    "provider": "anthropic",
                    "usage": result.get('usage', {})
                }
            else:
                return {
                    "status": "error",
                    "message": f"Anthropic API error: {response.status_code} - {response.text}",
                    "model": model_name,
                    "provider": "anthropic"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "model": model_name,
                "provider": "anthropic"
            }

    def analyze_with_google(self, image_path: str, prompt: str, model_name: str) -> Dict[str, Any]:
        """Analyze image using Google Gemini"""
        if not self.google_api_key:
            return {
                "status": "error",
                "message": "Google API key not configured",
                "model": model_name,
                "provider": "google"
            }
        
        try:
            # Encode image to base64
            import base64
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            },
                            {
                                "inline_data": {
                                    "mime_type": "image/jpeg",
                                    "data": image_data
                                }
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "maxOutputTokens": 1000
                }
            }
            
            response = requests.post(
                f"{self.google_url}/models/{model_name}:generateContent?key={self.google_api_key}",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "status": "success",
                    "response": result['candidates'][0]['content']['parts'][0]['text'],
                    "model": model_name,
                    "provider": "google",
                    "usage": result.get('usageMetadata', {})
                }
            else:
                return {
                    "status": "error",
                    "message": f"Google API error: {response.status_code} - {response.text}",
                    "model": model_name,
                    "provider": "google"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "model": model_name,
                "provider": "google"
            }

    def analyze_with_grok(self, image_path: str, prompt: str, model_name: str) -> Dict[str, Any]:
        """Analyze image using Grok (xAI)"""
        if not self.grok_api_key:
            return {
                "status": "error",
                "message": "Grok API key not configured",
                "model": model_name,
                "provider": "grok"
            }
        
        try:
            # Encode image to base64
            import base64
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            payload = {
                "model": model_name,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 1000
            }
            
            headers = {
                'Authorization': f'Bearer {self.grok_api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f"{self.grok_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "status": "success",
                    "response": result['choices'][0]['message']['content'],
                    "model": model_name,
                    "provider": "grok",
                    "usage": result.get('usage', {})
                }
            else:
                return {
                    "status": "error",
                    "message": f"Grok API error: {response.status_code} - {response.text}",
                    "model": model_name,
                    "provider": "grok"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "model": model_name,
                "provider": "grok"
            }

    def analyze_with_cohere(self, image_path: str, prompt: str, model_name: str) -> Dict[str, Any]:
        """Analyze image using Cohere"""
        if not self.cohere_api_key:
            return {
                "status": "error",
                "message": "Cohere API key not configured",
                "model": model_name,
                "provider": "cohere"
            }
        
        try:
            # Encode image to base64
            import base64
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            payload = {
                "model": model_name,
                "message": prompt,
                "image": image_data,
                "max_tokens": 1000
            }
            
            headers = {
                'Authorization': f'Bearer {self.cohere_api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f"{self.cohere_url}/chat",
                json=payload,
                headers=headers,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "status": "success",
                    "response": result['text'],
                    "model": model_name,
                    "provider": "cohere",
                    "usage": result.get('meta', {})
                }
            else:
                return {
                    "status": "error",
                    "message": f"Cohere API error: {response.status_code} - {response.text}",
                    "model": model_name,
                    "provider": "cohere"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "model": model_name,
                "provider": "cohere"
            }

    def analyze_with_mistral(self, image_path: str, prompt: str, model_name: str) -> Dict[str, Any]:
        """Analyze image using Mistral"""
        if not self.mistral_api_key:
            return {
                "status": "error",
                "message": "Mistral API key not configured",
                "model": model_name,
                "provider": "mistral"
            }
        
        try:
            # Encode image to base64
            import base64
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            payload = {
                "model": model_name,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 1000
            }
            
            headers = {
                'Authorization': f'Bearer {self.mistral_api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f"{self.mistral_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "status": "success",
                    "response": result['choices'][0]['message']['content'],
                    "model": model_name,
                    "provider": "mistral",
                    "usage": result.get('usage', {})
                }
            else:
                return {
                    "status": "error",
                    "message": f"Mistral API error: {response.status_code} - {response.text}",
                    "model": model_name,
                    "provider": "mistral"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "model": model_name,
                "provider": "mistral"
            }

    def analyze_with_perplexity(self, image_path: str, prompt: str, model_name: str) -> Dict[str, Any]:
        """Analyze image using Perplexity"""
        if not self.perplexity_api_key:
            return {
                "status": "error",
                "message": "Perplexity API key not configured",
                "model": model_name,
                "provider": "perplexity"
            }
        
        try:
            # Encode image to base64
            import base64
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            payload = {
                "model": model_name,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 1000
            }
            
            headers = {
                'Authorization': f'Bearer {self.perplexity_api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f"{self.perplexity_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "status": "success",
                    "response": result['choices'][0]['message']['content'],
                    "model": model_name,
                    "provider": "perplexity",
                    "usage": result.get('usage', {})
                }
            else:
                return {
                    "status": "error",
                    "message": f"Perplexity API error: {response.status_code} - {response.text}",
                    "model": model_name,
                    "provider": "perplexity"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "model": model_name,
                "provider": "perplexity"
            }

    def analyze_image(self, image_path: str, prompt: str, model_config: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze image using specified model configuration"""
        model_type = model_config.get('type')
        model_name = model_config.get('model_name')
        
        if model_type == 'ollama':
            return self.analyze_with_ollama(image_path, prompt, model_name)
        elif model_type == 'openai':
            return self.analyze_with_openai(image_path, prompt, model_name)
        elif model_type == 'anthropic':
            return self.analyze_with_anthropic(image_path, prompt, model_name)
        elif model_type == 'google':
            return self.analyze_with_google(image_path, prompt, model_name)
        elif model_type == 'grok':
            return self.analyze_with_grok(image_path, prompt, model_name)
        elif model_type == 'cohere':
            return self.analyze_with_cohere(image_path, prompt, model_name)
        elif model_type == 'mistral':
            return self.analyze_with_mistral(image_path, prompt, model_name)
        elif model_type == 'perplexity':
            return self.analyze_with_perplexity(image_path, prompt, model_name)
        else:
            return {
                "status": "error",
                "message": f"Unknown model type: {model_type}",
                "model": model_name,
                "provider": model_type
            } 