"""
Unit tests for CLIP analyzer module with proper API mocking
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

from src.analyzers.clip_analyzer import (
    analyze_image_with_clip, 
    process_image_with_clip,
    get_authenticated_session
)

class TestCLIPAnalyzer(unittest.TestCase):
    """Test cases for CLIP analyzer functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp()
        self.test_image_path = os.path.join(self.temp_dir, "test_image.jpg")
        
        # Create a valid JPEG image file (minimal valid JPEG)
        with open(self.test_image_path, 'wb') as f:
            # Minimal valid JPEG header
            f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9')
        
        self.api_base_url = "http://localhost:7860"
        self.model_name = "ViT-L-14/openai"
        self.modes = ["best", "fast"]
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    @patch('src.analyzers.clip_analyzer.get_authenticated_session')
    def test_analyze_image_with_clip_success(self, mock_get_session):
        """Test successful CLIP analysis"""
        # Mock authenticated session
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        
        # Mock successful API responses for each mode
        mock_response_best = MagicMock()
        mock_response_best.status_code = 200
        mock_response_best.json.return_value = {
            "status": "success",
            "prompt": "A beautiful landscape with mountains"
        }
        
        mock_response_fast = MagicMock()
        mock_response_fast.status_code = 200
        mock_response_fast.json.return_value = {
            "status": "success",
            "prompt": "Nature scene"
        }
        
        # Return different responses for different modes
        def side_effect(*args, **kwargs):
            if 'best' in str(kwargs.get('json', {}).get('mode', '')):
                return mock_response_best
            return mock_response_fast
        
        mock_session.post.side_effect = side_effect
        
        result = analyze_image_with_clip(
            image_path=self.test_image_path,
            api_base_url=self.api_base_url,
            model=self.model_name,
            modes=self.modes
        )
        
        self.assertEqual(result["status"], "success")
        self.assertIn("results", result)
        self.assertIn("best", result["results"])
        self.assertIn("fast", result["results"])
        self.assertEqual(mock_session.post.call_count, 2)
    
    @patch('src.analyzers.clip_analyzer.get_authenticated_session')
    def test_analyze_image_with_clip_api_error(self, mock_get_session):
        """Test CLIP analysis with API error"""
        # Mock authenticated session
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        
        # Mock API error response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Internal Server Error")
        mock_session.post.return_value = mock_response
        
        result = analyze_image_with_clip(
            image_path=self.test_image_path,
            api_base_url=self.api_base_url,
            model=self.model_name,
            modes=self.modes
        )
        
        self.assertEqual(result["status"], "success")  # Function returns success with error in results
        self.assertIn("results", result)
        # Check that errors are in the results
        for mode in self.modes:
            if mode in result["results"]:
                self.assertEqual(result["results"][mode]["status"], "error")
    
    @patch('src.analyzers.clip_analyzer.get_authenticated_session')
    def test_analyze_image_with_clip_connection_error(self, mock_get_session):
        """Test CLIP analysis with connection error"""
        # Mock authenticated session
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        
        # Mock connection error
        mock_session.post.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        result = analyze_image_with_clip(
            image_path=self.test_image_path,
            api_base_url=self.api_base_url,
            model=self.model_name,
            modes=self.modes
        )
        
        self.assertEqual(result["status"], "success")  # Function returns success with error in results
        self.assertIn("results", result)
    
    @patch('src.analyzers.clip_analyzer.get_authenticated_session')
    def test_analyze_image_with_clip_timeout(self, mock_get_session):
        """Test CLIP analysis with timeout"""
        # Mock authenticated session
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        
        # Mock timeout error
        mock_session.post.side_effect = requests.exceptions.Timeout("Request timed out")
        
        result = analyze_image_with_clip(
            image_path=self.test_image_path,
            api_base_url=self.api_base_url,
            model=self.model_name,
            modes=self.modes
        )
        
        self.assertEqual(result["status"], "success")  # Function returns success with error in results
        self.assertIn("results", result)
    
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
    
    def test_analyze_image_with_clip_no_api_url(self):
        """Test CLIP analysis with no API URL"""
        result = analyze_image_with_clip(
            image_path=self.test_image_path,
            api_base_url="",
            model=self.model_name,
            modes=self.modes
        )
        
        self.assertEqual(result["status"], "error")
        self.assertIn("API base URL not provided", result["message"])
    
    def test_analyze_image_with_clip_no_modes(self):
        """Test CLIP analysis with no modes"""
        result = analyze_image_with_clip(
            image_path=self.test_image_path,
            api_base_url=self.api_base_url,
            model=self.model_name,
            modes=[]
        )
        
        self.assertEqual(result["status"], "error")
        self.assertIn("No analysis modes specified", result["message"])
    
    @patch('src.analyzers.clip_analyzer.get_authenticated_session')
    @patch('src.analyzers.clip_analyzer.db_manager')
    @patch('src.analyzers.clip_analyzer.prompt_image')
    @patch('src.analyzers.clip_analyzer.analyze_image_with_clip')
    def test_process_image_with_clip_success(self, mock_analyze, mock_prompt, mock_db, mock_get_session):
        """Test process_image_with_clip function"""
        # Mock database
        mock_db.get_result_by_md5.return_value = None  # No existing result
        mock_db.insert_result.return_value = None
        
        # Mock prompt generation
        mock_prompt.return_value = {
            "status": "success",
            "prompt": {
                "best": {"status": "success", "prompt": "Test result"},
                "fast": {"status": "success", "prompt": "Test result"}
            }
        }
        
        # Mock analysis
        mock_analyze.return_value = {
            "status": "success",
            "model": self.model_name,
            "modes": self.modes,
            "results": {
                "best": {"status": "success", "prompt": "Test result"},
                "fast": {"status": "success", "prompt": "Test result"}
            }
        }
        
        result = process_image_with_clip(
            image_path=self.test_image_path,
            api_base_url=self.api_base_url,
            model=self.model_name,
            modes=self.modes
        )
        
        self.assertEqual(result["status"], "success")
        self.assertIn("filename", result)
        self.assertIn("analysis_results", result)
        mock_db.insert_result.assert_called()
    
    @patch('src.analyzers.clip_analyzer.get_authenticated_session')
    @patch('src.analyzers.clip_analyzer.db_manager')
    def test_process_image_with_clip_from_database(self, mock_db, mock_get_session):
        """Test process_image_with_clip retrieves from database"""
        # Mock database returning existing result
        existing_result = {
            "file_info": {"filename": "test_image.jpg"},
            "analysis": {"clip": {"best": {"prompt": "Cached result"}}}
        }
        mock_db.get_result_by_md5.return_value = existing_result
        
        result = process_image_with_clip(
            image_path=self.test_image_path,
            api_base_url=self.api_base_url,
            model=self.model_name,
            modes=self.modes,
            force_reprocess=False
        )
        
        self.assertEqual(result["status"], "success")
        self.assertTrue(result.get("from_database", False))
        # Should not call API
        mock_get_session.assert_not_called()
    
    @patch('src.analyzers.clip_analyzer.requests.Session')
    def test_get_authenticated_session_with_password(self, mock_session_class):
        """Test authenticated session creation with password"""
        # Mock session
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        # Mock login response
        mock_login_response = MagicMock()
        mock_login_response.status_code = 200
        mock_session.post.return_value = mock_login_response
        
        # Mock session cookie
        mock_session.cookies = {'connect.sid': 'test_session_id'}
        
        # Mock info endpoint for session validation
        mock_info_response = MagicMock()
        mock_info_response.status_code = 200
        mock_session.get.return_value = mock_info_response
        
        session = get_authenticated_session(self.api_base_url, password="test_password")
        
        self.assertIsNotNone(session)
        mock_session.post.assert_called()
    
    @patch('src.analyzers.clip_analyzer.requests.Session')
    def test_get_authenticated_session_no_password(self, mock_session_class):
        """Test session creation without password"""
        # Mock session
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        session = get_authenticated_session(self.api_base_url, password=None)
        
        self.assertIsNotNone(session)
        # Should not call login endpoint
        mock_session.post.assert_not_called()

if __name__ == '__main__':
    unittest.main() 