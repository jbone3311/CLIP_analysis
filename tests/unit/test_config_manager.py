"""
Unit tests for config manager module
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os
from pathlib import Path
import tempfile
import shutil

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.config.config_manager import (
    get_config_value,
    get_all_config,
    save_config_file,
    load_config_file,
    load_env_file
)

class TestConfigManager(unittest.TestCase):
    """Test cases for config manager functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_env_path = os.path.join(self.temp_dir, ".env")
        
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    @patch('src.config.config_manager.requests.get')
    def test_validate_api_key_success(self, mock_get):
        """Test successful API key validation"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = validate_api_key("test_api_key", "https://api.test.com")
        self.assertTrue(result)
        mock_get.assert_called_once()
    
    @patch('src.config.config_manager.requests.get')
    def test_validate_api_key_failure(self, mock_get):
        """Test failed API key validation"""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        result = validate_api_key("invalid_api_key", "https://api.test.com")
        self.assertFalse(result)
    
    @patch('src.config.config_manager.requests.get')
    def test_validate_api_key_connection_error(self, mock_get):
        """Test API key validation with connection error"""
        mock_get.side_effect = Exception("Connection failed")
        
        result = validate_api_key("test_api_key", "https://api.test.com")
        self.assertFalse(result)
    
    @patch('src.config.config_manager.requests.post')
    def test_test_clip_connection_success(self, mock_post):
        """Test successful CLIP connection"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_post.return_value = mock_response
        
        result = test_clip_connection("http://localhost:7860")
        self.assertTrue(result)
        mock_post.assert_called_once()
    
    @patch('src.config.config_manager.requests.post')
    def test_test_clip_connection_failure(self, mock_post):
        """Test failed CLIP connection"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        result = test_clip_connection("http://localhost:7860")
        self.assertFalse(result)
    
    @patch('src.config.config_manager.requests.post')
    def test_test_llm_connection_success(self, mock_post):
        """Test successful LLM connection"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"choices": [{"message": {"content": "test"}}]}
        mock_post.return_value = mock_response
        
        result = test_llm_connection("https://api.openai.com/v1/chat/completions", "test_key", "gpt-4")
        self.assertTrue(result)
        mock_post.assert_called_once()
    
    @patch('src.config.config_manager.requests.post')
    def test_test_llm_connection_failure(self, mock_post):
        """Test failed LLM connection"""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response
        
        result = test_llm_connection("https://api.openai.com/v1/chat/completions", "invalid_key", "gpt-4")
        self.assertFalse(result)
    
    def test_save_config(self):
        """Test saving configuration to .env file"""
        config = {
            "API_BASE_URL": "http://localhost:7860",
            "CLIP_MODEL_NAME": "ViT-L-14/openai",
            "ENABLE_CLIP_ANALYSIS": "True"
        }
        
        with patch('builtins.open', mock_open()) as mock_file:
            save_config(config, self.test_env_path)
            mock_file.assert_called_once_with(self.test_env_path, 'w', encoding='utf-8')
    
    def test_load_config(self):
        """Test loading configuration from .env file"""
        env_content = """API_BASE_URL=http://localhost:7860
CLIP_MODEL_NAME=ViT-L-14/openai
ENABLE_CLIP_ANALYSIS=True"""
        
        with patch('builtins.open', mock_open(read_data=env_content)):
            config = load_config(self.test_env_path)
            
        self.assertEqual(config["API_BASE_URL"], "http://localhost:7860")
        self.assertEqual(config["CLIP_MODEL_NAME"], "ViT-L-14/openai")
        self.assertEqual(config["ENABLE_CLIP_ANALYSIS"], "True")
    
    def test_load_config_file_not_found(self):
        """Test loading configuration when file doesn't exist"""
        config = load_config("nonexistent.env")
        self.assertIsInstance(config, dict)
        self.assertEqual(len(config), 0)
    
    @patch('builtins.input', side_effect=['y', 'http://localhost:7860', 'ViT-L-14/openai'])
    @patch('src.config.config_manager.test_clip_connection', return_value=True)
    @patch('src.config.config_manager.save_config')
    def test_main_interactive_setup(self, mock_save, mock_test, mock_input):
        """Test interactive configuration setup"""
        with patch('builtins.open', mock_open()):
            main()
        
        mock_save.assert_called()
        mock_test.assert_called()

if __name__ == '__main__':
    unittest.main() 