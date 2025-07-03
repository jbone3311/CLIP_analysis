"""
Professional LLM-based image analyzer.

Refactored version of analysis_LLM.py with improved architecture,
security integration, and proper error handling.
"""

import json
import base64
import requests
import time
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import logging

from analyzer_base import BaseAnalyzer, track_performance
from input_validation import validate_prompt_input, validate_output_path
from exceptions import (
    LLMAPIError, AuthenticationError, RateLimitError, 
    handle_api_error, safe_error_message, log_error_context
)

logger = logging.getLogger(__name__)

class LLMAnalyzer(BaseAnalyzer):
    """
    Professional LLM-based image analyzer.
    
    Supports multiple LLM providers (OpenAI, Anthropic, etc.) with 
    configurable prompts, retry logic, and comprehensive error handling.
    """
    
    def __init__(self, config: Dict[str, Any], name: Optional[str] = None):
        """
        Initialize LLM analyzer.
        
        Args:
            config: Configuration dictionary containing LLM settings
            name: Optional name for the analyzer instance
        """
        super().__init__(config, name or "LLMAnalyzer")
        
        # Load prompts configuration
        self.prompts = self._load_prompts()
        
        # API configuration
        self.api_url = config['api_url']
        self.api_key = config.get('api_key', '')
        self.model_name = config['model_name']
        self.timeout = config.get('timeout', 60)
        self.retry_limit = config.get('retry_limit', 3)
        
        # Rate limiting
        self._last_request_time = 0
        self._min_request_interval = config.get('min_request_interval', 0.1)
        
        logger.info(f"Initialized LLM analyzer: {self.model_name}")
    
    def get_required_config_keys(self) -> List[str]:
        """Return required configuration keys for LLM analyzer."""
        return ['api_url', 'model_name']
    
    def _load_prompts(self) -> Dict[str, Dict[str, Any]]:
        """
        Load prompts from configuration or file.
        
        Returns:
            Dictionary of prompt configurations
        """
        prompts_file = self.config.get('prompts_file', 'LLM_Prompts.json')
        
        try:
            if Path(prompts_file).exists():
                with open(prompts_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning(f"Prompts file {prompts_file} not found, using default prompts")
                return self._get_default_prompts()
                
        except Exception as e:
            logger.error(f"Failed to load prompts from {prompts_file}: {e}")
            return self._get_default_prompts()
    
    def _get_default_prompts(self) -> Dict[str, Dict[str, Any]]:
        """Return default prompt configurations."""
        return {
            "DETAILED_DESCRIPTION": {
                "TITLE": "Detailed Image Description",
                "PROMPT_TEXT": "Provide a comprehensive and accurate description of this image. "
                              "Include details about the main subjects, setting, colors, mood, and any notable features.",
                "TEMPERATURE": 0.7,
                "MAX_TOKENS": 1000
            },
            "CREATIVE_ANALYSIS": {
                "TITLE": "Creative Analysis",
                "PROMPT_TEXT": "Analyze this image from an artistic perspective. "
                              "Discuss composition, style, emotional impact, and creative elements.",
                "TEMPERATURE": 0.8,
                "MAX_TOKENS": 800
            }
        }
    
    def _encode_image(self, image_path: Path) -> str:
        """
        Encode image to base64 string efficiently.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Base64 encoded image string
            
        Raises:
            FileOperationError: If image encoding fails
        """
        try:
            with open(image_path, "rb") as image_file:
                # Read in chunks for memory efficiency
                chunks = []
                while True:
                    chunk = image_file.read(8192)
                    if not chunk:
                        break
                    chunks.append(chunk)
                
                image_data = b''.join(chunks)
                return base64.b64encode(image_data).decode("utf-8")
                
        except Exception as e:
            from exceptions import FileOperationError
            raise FileOperationError(
                f"Failed to encode image: {e}",
                file_path=str(image_path),
                operation="base64_encoding"
            ) from e
    
    def _prepare_request_payload(self, image_base64: str, prompt_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare API request payload.
        
        Args:
            image_base64: Base64 encoded image
            prompt_config: Prompt configuration dictionary
            
        Returns:
            Request payload dictionary
        """
        return {
            "model": self.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_config['PROMPT_TEXT']},
                        {
                            "type": "image_url", 
                            "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                        }
                    ]
                }
            ],
            "temperature": prompt_config.get('TEMPERATURE', 0.7),
            "max_tokens": prompt_config.get('MAX_TOKENS', 1000)
        }
    
    def _make_api_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make API request with retry logic and rate limiting.
        
        Args:
            payload: Request payload
            
        Returns:
            API response data
            
        Raises:
            LLMAPIError: If API request fails after retries
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        for attempt in range(self.retry_limit):
            try:
                # Rate limiting
                current_time = time.time()
                time_since_last = current_time - self._last_request_time
                if time_since_last < self._min_request_interval:
                    sleep_time = self._min_request_interval - time_since_last
                    logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
                    time.sleep(sleep_time)
                
                # Make request
                logger.debug(f"Making LLM API request (attempt {attempt + 1}/{self.retry_limit})")
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )
                
                self._last_request_time = time.time()
                
                if response.ok:
                    return response.json()
                else:
                    # Handle specific error responses
                    handle_api_error(response, "LLM analysis")
                    
            except (requests.RequestException, LLMAPIError) as e:
                if attempt == self.retry_limit - 1:  # Last attempt
                    raise LLMAPIError(
                        f"LLM API request failed after {self.retry_limit} attempts: {e}",
                        status_code=getattr(e, 'status_code', None)
                    ) from e
                
                # Exponential backoff
                wait_time = (2 ** attempt) + 1
                logger.warning(f"API request failed (attempt {attempt + 1}), retrying in {wait_time}s: {e}")
                time.sleep(wait_time)
        
        # This should never be reached due to the raise in the loop
        raise LLMAPIError("Unexpected error in API request retry logic")
    
    @track_performance
    def analyze_image(self, image_path: Union[str, Path], prompts: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze image using LLM with specified prompts.
        
        Args:
            image_path: Path to image file
            prompts: List of prompt IDs to use (defaults to all available)
            
        Returns:
            Analysis results dictionary
            
        Raises:
            LLMAPIError: If LLM analysis fails
        """
        image_path = Path(image_path)
        prompts = prompts or list(self.prompts.keys())
        
        logger.info(f"Starting LLM analysis with {len(prompts)} prompts: {prompts}")
        
        try:
            # Encode image
            image_base64 = self._encode_image(image_path)
            logger.debug(f"Image encoded to base64 ({len(image_base64)} characters)")
            
            results = []
            
            for prompt_id in prompts:
                try:
                    # Validate prompt
                    if prompt_id not in self.prompts:
                        logger.warning(f"Unknown prompt ID: {prompt_id}, skipping")
                        continue
                    
                    prompt_config = self.prompts[prompt_id]
                    validated_prompt = validate_prompt_input(prompt_config['PROMPT_TEXT'])
                    
                    # Update config with validated prompt
                    safe_prompt_config = prompt_config.copy()
                    safe_prompt_config['PROMPT_TEXT'] = validated_prompt
                    
                    # Prepare and make request
                    payload = self._prepare_request_payload(image_base64, safe_prompt_config)
                    response_data = self._make_api_request(payload)
                    
                    results.append({
                        "prompt_id": prompt_id,
                        "prompt_title": prompt_config.get('TITLE', prompt_id),
                        "success": True,
                        "response": response_data
                    })
                    
                    logger.info(f"Successfully processed prompt: {prompt_id}")
                    
                except Exception as e:
                    logger.error(f"Failed to process prompt {prompt_id}: {safe_error_message(e)}")
                    results.append({
                        "prompt_id": prompt_id,
                        "prompt_title": self.prompts.get(prompt_id, {}).get('TITLE', prompt_id),
                        "success": False,
                        "error": safe_error_message(e),
                        "error_type": type(e).__name__
                    })
            
            return {
                "model": self.model_name,
                "prompt_results": results,
                "total_prompts": len(prompts),
                "successful_prompts": sum(1 for r in results if r.get('success', False)),
                "failed_prompts": sum(1 for r in results if not r.get('success', True))
            }
            
        except Exception as e:
            error_msg = f"LLM analysis failed for {image_path}"
            log_error_context(e, {
                'image_path': str(image_path),
                'model': self.model_name,
                'prompts': prompts
            })
            raise LLMAPIError(error_msg) from e
    
    def get_available_prompts(self) -> Dict[str, str]:
        """
        Get available prompts with their titles.
        
        Returns:
            Dictionary mapping prompt IDs to titles
        """
        return {
            prompt_id: config.get('TITLE', prompt_id)
            for prompt_id, config in self.prompts.items()
        }
    
    def add_custom_prompt(self, prompt_id: str, title: str, prompt_text: str, 
                         temperature: float = 0.7, max_tokens: int = 1000) -> None:
        """
        Add a custom prompt configuration.
        
        Args:
            prompt_id: Unique identifier for the prompt
            title: Human-readable title
            prompt_text: The actual prompt text
            temperature: LLM temperature setting
            max_tokens: Maximum tokens to generate
        """
        validated_text = validate_prompt_input(prompt_text)
        
        self.prompts[prompt_id] = {
            'TITLE': title,
            'PROMPT_TEXT': validated_text,
            'TEMPERATURE': temperature,
            'MAX_TOKENS': max_tokens
        }
        
        logger.info(f"Added custom prompt: {prompt_id} - {title}")
    
    def save_results(self, results: Dict[str, Any], output_path: Union[str, Path]) -> None:
        """
        Save analysis results to file.
        
        Args:
            results: Analysis results to save
            output_path: Path where to save results
            
        Raises:
            FileOperationError: If saving fails
        """
        try:
            validated_path = validate_output_path(str(output_path))
            
            with open(validated_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Results saved to: {validated_path}")
            
        except Exception as e:
            from exceptions import FileOperationError
            raise FileOperationError(
                f"Failed to save results: {e}",
                file_path=str(output_path),
                operation="save_json"
            ) from e
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model configuration.
        
        Returns:
            Model information dictionary
        """
        return {
            "model_name": self.model_name,
            "api_url": self.api_url,
            "timeout": self.timeout,
            "retry_limit": self.retry_limit,
            "available_prompts": len(self.prompts),
            "has_api_key": bool(self.api_key)
        }