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
        import tempfile
        import shutil
        
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp()
        self.test_image_path = os.path.join(self.temp_dir, "test_image.jpg")
        
        # Create a dummy image file
        with open(self.test_image_path, 'wb') as f:
            f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9')
        
        self.api_base_url = "http://localhost:7860"
        self.model_name = "ViT-L-14/openai"
        self.modes = ["best", "fast"]
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
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
        self.assertIn("prompt", result)
        self.assertIn("best", result["prompt"])
        self.assertIn("fast", result["prompt"])
        mock_post.assert_called()
    
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
        # The function returns different error messages based on the error type
        self.assertIn("error", result["message"].lower())
    
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
        # The function returns different error messages based on the error type
        self.assertIn("error", result["message"].lower())
    
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