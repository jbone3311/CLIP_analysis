"""
Unit tests for LLM analyzer module
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.analyzers.llm_analyzer import analyze_image_with_llm, MODELS

class TestLLMAnalyzer(unittest.TestCase):
    """Test cases for LLM analyzer functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        import tempfile
        import shutil
        
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp()
        self.test_image_path = os.path.join(self.temp_dir, "test_image.jpg")
        
        # Create a dummy image file
        with open(self.test_image_path, 'wb') as f:
            f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9')
        
        self.prompt_ids = ["P1", "P2"]
        self.model_number = 1
        self.debug = False
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @patch('src.analyzers.llm_analyzer.MODELS', [
        {
            'number': 1,
            'title': 'Test Model',
            'api_url': 'https://api.test.com',
            'api_key': 'test_key',
            'model_name': 'test-model'
        }
    ])
    def test_models_structure(self, mock_models):
        """Test that MODELS has the expected structure"""
        self.assertIsInstance(mock_models, list)
        self.assertGreater(len(mock_models), 0)
        
        for model in mock_models:
            self.assertIn('number', model)
            self.assertIn('title', model)
            self.assertIn('api_url', model)
            self.assertIn('api_key', model)
            self.assertIn('model_name', model)
    
    @patch('src.analyzers.llm_analyzer.MODELS', [
        {
            'number': 1,
            'title': 'Test Model',
            'api_url': 'https://api.test.com',
            'api_key': 'test_key',
            'model_name': 'test-model'
        }
    ])
    @patch('src.analyzers.llm_analyzer.requests.post')
    def test_analyze_image_with_llm_success(self, mock_models, mock_post):
        """Test successful LLM analysis"""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "This is a test image description"}}]
        }
        mock_post.return_value = mock_response
        
        result = analyze_image_with_llm(
            image_path_or_directory=self.test_image_path,
            prompt_ids=self.prompt_ids,
            model_number=self.model_number,
            debug=self.debug
        )
        
        self.assertEqual(result["status"], "success")
        self.assertIn("api_responses", result)
        mock_post.assert_called()
    
    @patch('src.analyzers.llm_analyzer.MODELS', [
        {
            'number': 1,
            'title': 'Test Model',
            'api_url': 'https://api.test.com',
            'api_key': 'test_key',
            'model_name': 'test-model'
        }
    ])
    @patch('src.analyzers.llm_analyzer.requests.post')
    def test_analyze_image_with_llm_api_error(self, mock_models, mock_post):
        """Test LLM analysis with API error"""
        # Mock API error response
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_post.return_value = mock_response
        
        result = analyze_image_with_llm(
            image_path_or_directory=self.test_image_path,
            prompt_ids=self.prompt_ids,
            model_number=self.model_number,
            debug=self.debug
        )
        
        self.assertEqual(result["status"], "error")
        self.assertIn("API request failed", result["message"])
    
    @patch('src.analyzers.llm_analyzer.MODELS', [
        {
            'number': 1,
            'title': 'Test Model',
            'api_url': 'https://api.test.com',
            'api_key': 'test_key',
            'model_name': 'test-model'
        }
    ])
    @patch('src.analyzers.llm_analyzer.requests.post')
    def test_analyze_image_with_llm_connection_error(self, mock_models, mock_post):
        """Test LLM analysis with connection error"""
        # Mock connection error
        mock_post.side_effect = Exception("Connection failed")
        
        result = analyze_image_with_llm(
            image_path_or_directory=self.test_image_path,
            prompt_ids=self.prompt_ids,
            model_number=self.model_number,
            debug=self.debug
        )
        
        self.assertEqual(result["status"], "error")
        self.assertIn("Connection failed", result["message"])
    
    @patch('src.analyzers.llm_analyzer.MODELS', [
        {
            'number': 1,
            'title': 'Test Model',
            'api_url': 'https://api.test.com',
            'api_key': 'test_key',
            'model_name': 'test-model'
        }
    ])
    def test_analyze_image_with_llm_invalid_model(self, mock_models):
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
            'api_key': 'test_key',
            'model_name': 'test-model'
        }
    ])
    def test_analyze_image_with_llm_invalid_image_path(self, mock_models):
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
            'title': 'Test Model',
            'api_url': 'https://api.test.com',
            'api_key': 'test_key',
            'model_name': 'test-model'
        }
    ])
    @patch('src.analyzers.llm_analyzer.requests.post')
    def test_analyze_image_with_llm_debug_mode(self, mock_models, mock_post):
        """Test LLM analysis in debug mode"""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Debug test response"}}]
        }
        mock_post.return_value = mock_response
        
        result = analyze_image_with_llm(
            image_path_or_directory=self.test_image_path,
            prompt_ids=self.prompt_ids,
            model_number=self.model_number,
            debug=True  # Enable debug mode
        )
        
        self.assertEqual(result["status"], "success")
        # Debug mode should include additional information
        self.assertIn("api_responses", result)

if __name__ == '__main__':
    unittest.main() 