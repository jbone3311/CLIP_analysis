"""
Professional CLIP-based image analyzer.

Refactored version of analysis_interrogate.py with improved architecture,
security integration, and proper error handling.
"""

import requests
import base64
import json
import time
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import logging

from analyzer_base import BaseAnalyzer, track_performance
from input_validation import validate_output_path
from exceptions import (
    CLIPAPIError, NetworkError, handle_api_error,
    safe_error_message, log_error_context
)

logger = logging.getLogger(__name__)

class CLIPAnalyzer(BaseAnalyzer):
    """
    Professional CLIP-based image analyzer.
    
    Provides prompt generation and image analysis using CLIP Interrogator
    with support for multiple analysis modes and comprehensive error handling.
    """
    
    # Available analysis modes
    SUPPORTED_MODES = ['best', 'fast', 'classic', 'negative', 'caption']
    
    def __init__(self, config: Dict[str, Any], name: Optional[str] = None):
        """
        Initialize CLIP analyzer.
        
        Args:
            config: Configuration dictionary containing CLIP settings
            name: Optional name for the analyzer instance
        """
        super().__init__(config, name or "CLIPAnalyzer")
        
        # API configuration
        self.api_base_url = config['api_base_url']
        self.model_name = config.get('model_name', 'ViT-L-14')
        self.timeout = config.get('timeout', 60)
        self.retry_limit = config.get('retry_limit', 3)
        
        # Default modes if not specified
        self.default_modes = config.get('default_modes', ['best', 'fast', 'classic'])
        
        # Rate limiting
        self._last_request_time = 0
        self._min_request_interval = config.get('min_request_interval', 0.1)
        
        logger.info(f"Initialized CLIP analyzer: {self.model_name} at {self.api_base_url}")
    
    def get_required_config_keys(self) -> List[str]:
        """Return required configuration keys for CLIP analyzer."""
        return ['api_base_url']
    
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
    
    def _make_api_request(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make API request with retry logic and rate limiting.
        
        Args:
            endpoint: API endpoint (e.g., 'analyze', 'prompt')
            payload: Request payload
            
        Returns:
            API response data
            
        Raises:
            CLIPAPIError: If API request fails after retries
        """
        url = f"{self.api_base_url.rstrip('/')}/interrogator/{endpoint}"
        headers = {"Content-Type": "application/json"}
        
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
                logger.debug(f"Making CLIP API request to {endpoint} (attempt {attempt + 1}/{self.retry_limit})")
                response = requests.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout
                )
                
                self._last_request_time = time.time()
                
                if response.ok:
                    return response.json()
                else:
                    # Handle specific error responses
                    handle_api_error(response, f"CLIP {endpoint}")
                    
            except (requests.RequestException, CLIPAPIError) as e:
                if attempt == self.retry_limit - 1:  # Last attempt
                    raise CLIPAPIError(
                        f"CLIP API request to {endpoint} failed after {self.retry_limit} attempts: {e}",
                        status_code=getattr(e, 'status_code', None)
                    ) from e
                
                # Exponential backoff
                wait_time = (2 ** attempt) + 1
                logger.warning(f"API request to {endpoint} failed (attempt {attempt + 1}), retrying in {wait_time}s: {e}")
                time.sleep(wait_time)
        
        # This should never be reached due to the raise in the loop
        raise CLIPAPIError(f"Unexpected error in API request retry logic for {endpoint}")
    
    def _analyze_image_content(self, image_base64: str) -> Dict[str, Any]:
        """
        Analyze image content using CLIP.
        
        Args:
            image_base64: Base64 encoded image
            
        Returns:
            Analysis results dictionary
        """
        payload = {
            "image": image_base64,
            "model": self.model_name
        }
        
        try:
            response_data = self._make_api_request("analyze", payload)
            logger.debug("Image analysis completed successfully")
            return response_data
            
        except Exception as e:
            logger.error(f"Image analysis failed: {safe_error_message(e)}")
            raise
    
    def _generate_prompts(self, image_base64: str, modes: List[str]) -> Dict[str, Any]:
        """
        Generate prompts for image using specified modes.
        
        Args:
            image_base64: Base64 encoded image
            modes: List of analysis modes to use
            
        Returns:
            Dictionary mapping modes to their results
        """
        prompt_results = {}
        
        for mode in modes:
            if mode not in self.SUPPORTED_MODES:
                logger.warning(f"Unsupported mode '{mode}', skipping")
                prompt_results[mode] = {
                    "success": False,
                    "error": f"Unsupported mode: {mode}",
                    "error_type": "ValidationError"
                }
                continue
            
            try:
                payload = {
                    "image": image_base64,
                    "model": self.model_name,
                    "mode": mode
                }
                
                response_data = self._make_api_request("prompt", payload)
                
                prompt_results[mode] = {
                    "success": True,
                    "result": response_data
                }
                
                logger.debug(f"Prompt generation for mode '{mode}' completed successfully")
                
            except Exception as e:
                logger.error(f"Prompt generation for mode '{mode}' failed: {safe_error_message(e)}")
                prompt_results[mode] = {
                    "success": False,
                    "error": safe_error_message(e),
                    "error_type": type(e).__name__
                }
        
        return prompt_results
    
    @track_performance
    def analyze_image(self, image_path: Union[str, Path], 
                     modes: Optional[List[str]] = None,
                     include_analysis: bool = True) -> Dict[str, Any]:
        """
        Analyze image using CLIP with specified modes.
        
        Args:
            image_path: Path to image file
            modes: List of analysis modes to use (defaults to configured modes)
            include_analysis: Whether to include content analysis
            
        Returns:
            Analysis results dictionary
            
        Raises:
            CLIPAPIError: If CLIP analysis fails
        """
        image_path = Path(image_path)
        modes = modes or self.default_modes or ['best', 'fast']
        
        # Validate modes
        invalid_modes = [m for m in modes if m not in self.SUPPORTED_MODES]
        if invalid_modes:
            logger.warning(f"Invalid modes detected: {invalid_modes}")
            modes = [m for m in modes if m in self.SUPPORTED_MODES]
        
        if not modes:
            raise CLIPAPIError("No valid analysis modes specified")
        
        logger.info(f"Starting CLIP analysis with modes: {modes}")
        
        try:
            # Encode image
            image_base64 = self._encode_image(image_path)
            logger.debug(f"Image encoded to base64 ({len(image_base64)} characters)")
            
            results = {
                "model": self.model_name,
                "modes_requested": modes,
                "prompts": {},
                "analysis": None
            }
            
            # Generate prompts for each mode
            if modes:
                prompt_results = self._generate_prompts(image_base64, modes)
                results["prompts"] = prompt_results
                
                # Count successful/failed prompts
                successful_modes = [mode for mode, result in prompt_results.items() 
                                  if result.get('success', False)]
                failed_modes = [mode for mode, result in prompt_results.items() 
                               if not result.get('success', True)]
                
                results["successful_modes"] = successful_modes
                results["failed_modes"] = failed_modes
            
            # Perform content analysis if requested
            if include_analysis:
                try:
                    analysis_result = self._analyze_image_content(image_base64)
                    results["analysis"] = {
                        "success": True,
                        "result": analysis_result
                    }
                except Exception as e:
                    logger.error(f"Content analysis failed: {safe_error_message(e)}")
                    results["analysis"] = {
                        "success": False,
                        "error": safe_error_message(e),
                        "error_type": type(e).__name__
                    }
            
            logger.info(f"CLIP analysis completed for {len(modes)} modes")
            return results
            
        except Exception as e:
            error_msg = f"CLIP analysis failed for {image_path}"
            log_error_context(e, {
                'image_path': str(image_path),
                'model': self.model_name,
                'modes': modes
            })
            raise CLIPAPIError(error_msg) from e
    
    def get_supported_modes(self) -> List[str]:
        """
        Get list of supported analysis modes.
        
        Returns:
            List of supported mode names
        """
        return self.SUPPORTED_MODES.copy()
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to CLIP API.
        
        Returns:
            Connection test results
        """
        try:
            # Make a simple request to test connectivity
            test_payload = {"test": True}
            url = f"{self.api_base_url.rstrip('/')}/health"
            
            response = requests.get(url, timeout=5)
            
            return {
                "success": True,
                "status_code": response.status_code,
                "api_base_url": self.api_base_url,
                "response_time": response.elapsed.total_seconds()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": safe_error_message(e),
                "api_base_url": self.api_base_url
            }
    
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
            "api_base_url": self.api_base_url,
            "timeout": self.timeout,
            "retry_limit": self.retry_limit,
            "supported_modes": self.SUPPORTED_MODES,
            "default_modes": self.default_modes
        }