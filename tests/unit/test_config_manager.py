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
    load_env_file,
    validate_api_key,
    check_clip_connection,
    check_llm_connection,
    validate_config,
    setup_initial_config
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
    
    @patch('requests.get')
    def test_validate_api_key_success(self, mock_get):
        """Test successful API key validation"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = validate_api_key("test_api_key", "https://api.test.com")
        self.assertTrue(result)
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_validate_api_key_failure(self, mock_get):
        """Test failed API key validation"""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        result = validate_api_key("invalid_api_key", "https://api.test.com")
        self.assertFalse(result)
    
    @patch('requests.get')
    def test_validate_api_key_connection_error(self, mock_get):
        """Test API key validation with connection error"""
        mock_get.side_effect = Exception("Connection failed")
        
        result = validate_api_key("test_api_key", "https://api.test.com")
        self.assertFalse(result)
    
    @patch('requests.get')
    def test_test_clip_connection_success(self, mock_get):
        """Test successful CLIP connection"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = check_clip_connection("http://localhost:7860")
        self.assertTrue(result)
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_test_clip_connection_failure(self, mock_get):
        """Test failed CLIP connection"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        result = check_clip_connection("http://localhost:7860")
        self.assertFalse(result)
    
    @patch('requests.post')
    def test_test_llm_connection_success(self, mock_post):
        """Test successful LLM connection"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"choices": [{"message": {"content": "test"}}]}
        mock_post.return_value = mock_response
        
        result = check_llm_connection("https://api.openai.com/v1", "test_key", "gpt-4")
        self.assertTrue(result)
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_test_llm_connection_failure(self, mock_post):
        """Test failed LLM connection"""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response
        
        result = check_llm_connection("https://api.openai.com/v1", "invalid_key", "gpt-4")
        self.assertFalse(result)
    
    def test_save_config(self):
        """Test saving configuration to config.json file"""
        config = {
            "clip_config": {
                "api_url": "http://localhost:7860",
                "model_name": "ViT-L-14/openai"
            }
        }
        
        with patch('builtins.open', mock_open()) as mock_file:
            result = save_config_file(config, self.temp_dir)
            self.assertTrue(result)
            mock_file.assert_called()
    
    def test_load_config(self):
        """Test loading configuration from config.json file"""
        config_content = '{"clip_config": {"api_url": "http://localhost:7860", "model_name": "ViT-L-14/openai"}}'
        
        with patch('builtins.open', mock_open(read_data=config_content)), \
             patch('os.path.exists', return_value=True):
            config = load_config_file(self.temp_dir)
            
        self.assertIn("clip_config", config)
        self.assertEqual(config["clip_config"]["api_url"], "http://localhost:7860")
    
    def test_load_config_file_not_found(self):
        """Test loading configuration when file doesn't exist"""
        with patch('os.path.exists', return_value=False):
            config = load_config_file(self.temp_dir)
        self.assertIsInstance(config, dict)
    
    @patch('builtins.input', side_effect=['y', 'http://localhost:7860', 'ViT-L-14/openai'])
    @patch('src.config.config_manager.check_clip_connection', return_value=True)
    def test_main_interactive_setup(self, mock_test, mock_input):
        """Test interactive configuration setup"""
        result = setup_initial_config(self.temp_dir)
        self.assertTrue(result)
        # The function may or may not call check_clip_connection depending on user input
        # Just verify the setup completed successfully

if __name__ == '__main__':
    unittest.main() 