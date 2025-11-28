"""
Unit tests for LLM analyzer module with proper API mocking
"""

import unittest
from unittest.mock import patch, MagicMock, Mock
import sys
import os
import tempfile
import shutil
from pathlib import Path
import requests

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.analyzers.llm_analyzer import analyze_image_with_llm, LLMAnalyzer, MODELS, PROMPTS

class TestLLMAnalyzer(unittest.TestCase):
    """Test cases for LLM analyzer functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp()
        self.test_image_path = os.path.join(self.temp_dir, "test_image.jpg")
        
        # Create a valid JPEG image file
        with open(self.test_image_path, 'wb') as f:
            f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9')
        
        self.prompt_ids = ["P1", "P2"]
        self.model_number = 1
        self.debug = False
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    @patch('src.analyzers.llm_analyzer.MODELS', [
        {
            'number': 1,
            'title': 'Test OpenAI Model',
            'api_url': 'https://api.openai.com/v1/chat/completions',
            'api_key': 'test_key_123',
            'model_name': 'gpt-4-vision-preview'
        }
    ])
    @patch('src.analyzers.llm_analyzer.PROMPTS', {
        'P1': {'PROMPT_TEXT': 'Describe this image in detail.', 'TEMPERATURE': 0.7, 'MAX_TOKENS': 1500},
        'P2': {'PROMPT_TEXT': 'What artistic style is this image?', 'TEMPERATURE': 0.7, 'MAX_TOKENS': 1500}
    })
    @patch('src.analyzers.llm_analyzer.LLMAnalyzer.process_image')
    def test_analyze_image_with_llm_success(self, mock_process):
        """Test successful LLM analysis"""
        # Mock process_image to return list of successful responses
        mock_process.return_value = [
            {
                "prompt": "P1",
                "status": "success",
                "result": {
                    "choices": [{"message": {"content": "This is a test image description"}}]
                }
            },
            {
                "prompt": "P2",
                "status": "success",
                "result": {
                    "choices": [{"message": {"content": "Artistic style description"}}]
                }
            }
        ]
        
        result = analyze_image_with_llm(
            image_path_or_directory=self.test_image_path,
            prompt_ids=self.prompt_ids,
            model_number=self.model_number,
            debug=self.debug
        )
        
        self.assertEqual(result["status"], "success")
        self.assertIn("api_responses", result)
        self.assertEqual(len(result["api_responses"]), 2)
        mock_process.assert_called_once()
    
    @patch('src.analyzers.llm_analyzer.MODELS', [
        {
            'number': 1,
            'title': 'Test Model',
            'api_url': 'https://api.test.com',
            'api_key': 'test_key',
            'model_name': 'test-model'
        }
    ])
    def test_analyze_image_with_llm_invalid_model(self):
        """Test LLM analysis with invalid model number"""
        result = analyze_image_with_llm(
            image_path_or_directory=self.test_image_path,
            prompt_ids=self.prompt_ids,
            model_number=999,  # Invalid model number
            debug=self.debug
        )
        
        self.assertEqual(result["status"], "error")
        self.assertIn("Invalid model number", result["message"])
    
    @patch('src.analyzers.llm_analyzer.MODELS', [
        {
            'number': 1,
            'title': 'Test Model',
            'api_url': 'https://api.test.com',
            'api_key': None,  # No API key
            'model_name': 'test-model'
        }
    ])
    def test_analyze_image_with_llm_no_api_key(self):
        """Test LLM analysis with no API key"""
        result = analyze_image_with_llm(
            image_path_or_directory=self.test_image_path,
            prompt_ids=self.prompt_ids,
            model_number=self.model_number,
            debug=self.debug
        )
        
        self.assertEqual(result["status"], "error")
        self.assertIn("No API key provided", result["message"])
    
    @patch('src.analyzers.llm_analyzer.MODELS', [
        {
            'number': 1,
            'title': 'Test Model',
            'api_url': 'https://api.test.com',
            'api_key': 'test_key',
            'model_name': 'test-model'
        }
    ])
    @patch('src.analyzers.llm_analyzer.PROMPTS', {
        'P1': 'Test prompt'
    })
    def test_analyze_image_with_llm_invalid_prompts(self):
        """Test LLM analysis with invalid prompt IDs"""
        result = analyze_image_with_llm(
            image_path_or_directory=self.test_image_path,
            prompt_ids=["INVALID1", "INVALID2"],  # Invalid prompt IDs
            model_number=self.model_number,
            debug=self.debug
        )
        
        self.assertEqual(result["status"], "error")
        self.assertIn("No valid prompts found", result["message"])
    
    @patch('src.analyzers.llm_analyzer.MODELS', [
        {
            'number': 1,
            'title': 'Test Model',
            'api_url': 'https://api.test.com',
            'api_key': 'test_key',
            'model_name': 'test-model'
        }
    ])
    def test_analyze_image_with_llm_invalid_image_path(self):
        """Test LLM analysis with invalid image path"""
        result = analyze_image_with_llm(
            image_path_or_directory="nonexistent_image.jpg",
            prompt_ids=self.prompt_ids,
            model_number=self.model_number,
            debug=self.debug
        )
        
        self.assertEqual(result["status"], "error")
        self.assertIn("Image file not found", result["message"])
    
    @patch('src.analyzers.llm_analyzer.MODELS', [
        {
            'number': 1,
            'title': 'Test OpenAI Model',
            'api_url': 'https://api.openai.com/v1/chat/completions',
            'api_key': 'test_key_123',
            'model_name': 'gpt-4-vision-preview'
        }
    ])
    @patch('src.analyzers.llm_analyzer.PROMPTS', {
        'P1': {'PROMPT_TEXT': 'Describe this image.', 'TEMPERATURE': 0.7, 'MAX_TOKENS': 1500},
        'P2': {'PROMPT_TEXT': 'Analyze the style.', 'TEMPERATURE': 0.7, 'MAX_TOKENS': 1500}
    })
    @patch('src.analyzers.llm_analyzer.LLMAnalyzer.process_image')
    def test_analyze_image_with_llm_api_error(self, mock_process):
        """Test LLM analysis with API error"""
        # Mock all prompts failing
        mock_process.return_value = [
            {
                "prompt": "P1",
                "status": "failed",
                "error": "API request failed: 401 Unauthorized"
            },
            {
                "prompt": "P2",
                "status": "failed",
                "error": "API request failed: 401 Unauthorized"
            }
        ]
        
        result = analyze_image_with_llm(
            image_path_or_directory=self.test_image_path,
            prompt_ids=self.prompt_ids,
            model_number=self.model_number,
            debug=self.debug
        )
        
        # Should return error if all prompts fail
        self.assertEqual(result["status"], "error")
        self.assertIn("All prompts failed", result["message"])
    
    @patch('src.analyzers.llm_analyzer.MODELS', [
        {
            'number': 1,
            'title': 'Test OpenAI Model',
            'api_url': 'https://api.openai.com/v1/chat/completions',
            'api_key': 'test_key_123',
            'model_name': 'gpt-4-vision-preview'
        }
    ])
    @patch('src.analyzers.llm_analyzer.PROMPTS', {
        'P1': {'PROMPT_TEXT': 'Describe this image.', 'TEMPERATURE': 0.7, 'MAX_TOKENS': 1500},
        'P2': {'PROMPT_TEXT': 'Analyze the style.', 'TEMPERATURE': 0.7, 'MAX_TOKENS': 1500}
    })
    @patch('src.analyzers.llm_analyzer.LLMAnalyzer.process_image')
    def test_analyze_image_with_llm_partial_success(self, mock_process):
        """Test LLM analysis with partial success (some prompts fail)"""
        # Mock mixed results - one success, one failure
        mock_process.return_value = [
            {
                "prompt": "P1",
                "status": "success",
                "result": {
                    "choices": [{"message": {"content": "Description of image"}}]
                }
            },
            {
                "prompt": "P2",
                "status": "failed",
                "error": "API error"
            }
        ]
        
        result = analyze_image_with_llm(
            image_path_or_directory=self.test_image_path,
            prompt_ids=self.prompt_ids,
            model_number=self.model_number,
            debug=self.debug
        )
        
        # Should return success even if some prompts fail
        self.assertEqual(result["status"], "success")
        self.assertIn("api_responses", result)
        self.assertEqual(len(result["api_responses"]), 2)
    
    @patch('src.analyzers.llm_analyzer.MODELS', [
        {
            'number': 1,
            'title': 'Test OpenAI Model',
            'api_url': 'https://api.openai.com/v1/chat/completions',
            'api_key': 'test_key_123',
            'model_name': 'gpt-4-vision-preview'
        }
    ])
    @patch('src.analyzers.llm_analyzer.PROMPTS', {
        'P1': {'PROMPT_TEXT': 'Describe this image.', 'TEMPERATURE': 0.7, 'MAX_TOKENS': 1500}
    })
    @patch('src.analyzers.llm_analyzer.LLMAnalyzer.process_image')
    def test_analyze_image_with_llm_debug_mode(self, mock_process):
        """Test LLM analysis in debug mode"""
        # Mock successful API response
        mock_process.return_value = [
            {
                "prompt": "P1",
                "status": "success",
                "result": {
                    "choices": [{"message": {"content": "Debug test response"}}]
                }
            }
        ]
        
        result = analyze_image_with_llm(
            image_path_or_directory=self.test_image_path,
            prompt_ids=["P1"],
            model_number=self.model_number,
            debug=True  # Enable debug mode
        )
        
        self.assertEqual(result["status"], "success")
        self.assertIn("api_responses", result)
        self.assertEqual(len(result["api_responses"]), 1)
        mock_process.assert_called_once()

if __name__ == '__main__':
    unittest.main() 