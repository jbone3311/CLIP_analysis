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
        self.test_image_path = "test_image.jpg"
        self.prompt_ids = ["P1", "P2"]
        self.model_number = 1
        self.debug = False
    
    def test_models_structure(self):
        """Test that MODELS has the expected structure"""
        self.assertIsInstance(MODELS, list)
        self.assertGreater(len(MODELS), 0)
        
        for model in MODELS:
            self.assertIn('number', model)
            self.assertIn('title', model)
            self.assertIn('api_url', model)
            self.assertIn('api_key', model)
            self.assertIn('model_name', model)
    
    @patch('src.analyzers.llm_analyzer.requests.post')
    def test_analyze_image_with_llm_success(self, mock_post):
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
    
    @patch('src.analyzers.llm_analyzer.requests.post')
    def test_analyze_image_with_llm_api_error(self, mock_post):
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
    
    @patch('src.analyzers.llm_analyzer.requests.post')
    def test_analyze_image_with_llm_connection_error(self, mock_post):
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
    
    @patch('src.analyzers.llm_analyzer.requests.post')
    def test_analyze_image_with_llm_debug_mode(self, mock_post):
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