"""
Unit tests for CLIP analyzer module
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.analyzers.clip_analyzer import analyze_image_with_clip, process_image_with_clip

class TestCLIPAnalyzer(unittest.TestCase):
    """Test cases for CLIP analyzer functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_image_path = "test_image.jpg"
        self.api_base_url = "http://localhost:7860"
        self.model_name = "ViT-L-14/openai"
        self.modes = ["best", "fast"]
    
    @patch('src.analyzers.clip_analyzer.requests.post')
    def test_analyze_image_with_clip_success(self, mock_post):
        """Test successful CLIP analysis"""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "best": {"prompt": "A beautiful landscape"},
            "fast": {"prompt": "Nature scene"}
        }
        mock_post.return_value = mock_response
        
        result = analyze_image_with_clip(
            image_path=self.test_image_path,
            api_base_url=self.api_base_url,
            model=self.model_name,
            modes=self.modes
        )
        
        self.assertEqual(result["status"], "success")
        self.assertIn("best", result["prompt"])
        self.assertIn("fast", result["prompt"])
        mock_post.assert_called_once()
    
    @patch('src.analyzers.clip_analyzer.requests.post')
    def test_analyze_image_with_clip_api_error(self, mock_post):
        """Test CLIP analysis with API error"""
        # Mock API error response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response
        
        result = analyze_image_with_clip(
            image_path=self.test_image_path,
            api_base_url=self.api_base_url,
            model=self.model_name,
            modes=self.modes
        )
        
        self.assertEqual(result["status"], "error")
        self.assertIn("API request failed", result["message"])
    
    @patch('src.analyzers.clip_analyzer.requests.post')
    def test_analyze_image_with_clip_connection_error(self, mock_post):
        """Test CLIP analysis with connection error"""
        # Mock connection error
        mock_post.side_effect = Exception("Connection failed")
        
        result = analyze_image_with_clip(
            image_path=self.test_image_path,
            api_base_url=self.api_base_url,
            model=self.model_name,
            modes=self.modes
        )
        
        self.assertEqual(result["status"], "error")
        self.assertIn("Connection failed", result["message"])
    
    def test_analyze_image_with_clip_invalid_image_path(self):
        """Test CLIP analysis with invalid image path"""
        result = analyze_image_with_clip(
            image_path="nonexistent_image.jpg",
            api_base_url=self.api_base_url,
            model=self.model_name,
            modes=self.modes
        )
        
        self.assertEqual(result["status"], "error")
        self.assertIn("Image file not found", result["message"])
    
    @patch('src.analyzers.clip_analyzer.analyze_image_with_clip')
    def test_process_image_with_clip(self, mock_analyze):
        """Test process_image_with_clip function"""
        # Mock successful analysis
        mock_analyze.return_value = {
            "status": "success",
            "prompt": {"best": {"prompt": "Test result"}}
        }
        
        result = process_image_with_clip(
            image_path=self.test_image_path,
            api_base_url=self.api_base_url,
            model=self.model_name,
            modes=self.modes
        )
        
        self.assertEqual(result["status"], "success")
        mock_analyze.assert_called_once()

if __name__ == '__main__':
    unittest.main() 