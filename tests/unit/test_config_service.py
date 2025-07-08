"""
Unit tests for ConfigService
"""

import unittest
import tempfile
import os
from unittest.mock import patch, mock_open
from src.services.config_service import ConfigService


class TestConfigService(unittest.TestCase):
    """Test cases for ConfigService"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.service = ConfigService(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @patch.dict(os.environ, {
        'API_BASE_URL': 'http://test:8000',
        'CLIP_MODEL_NAME': 'test-model',
        'ENABLE_CLIP_ANALYSIS': 'True',
        'ENABLE_LLM_ANALYSIS': 'False',
        'WEB_PORT': '8080',
        'CLIP_MODES': 'best,fast',
        'PROMPT_CHOICES': 'P1,P2,P3'
    })
    def test_get_config_with_env_vars(self):
        """Test getting configuration with environment variables"""
        config = self.service.get_config()
        
        self.assertEqual(config['API_BASE_URL'], 'http://test:8000')
        self.assertEqual(config['CLIP_MODEL_NAME'], 'test-model')
        self.assertTrue(config['ENABLE_CLIP_ANALYSIS'])
        self.assertFalse(config['ENABLE_LLM_ANALYSIS'])
        self.assertEqual(config['WEB_PORT'], 8080)
        self.assertEqual(config['CLIP_MODES'], ['best', 'fast'])
        self.assertEqual(config['PROMPT_CHOICES'], ['P1', 'P2', 'P3'])
    
    @patch.dict(os.environ, {}, clear=True)
    def test_get_config_defaults(self):
        """Test getting configuration with default values"""
        config = self.service.get_config()
        
        self.assertEqual(config['API_BASE_URL'], 'http://localhost:7860')
        self.assertEqual(config['CLIP_MODEL_NAME'], 'ViT-L-14/openai')
        self.assertTrue(config['ENABLE_CLIP_ANALYSIS'])
        self.assertTrue(config['ENABLE_LLM_ANALYSIS'])
        self.assertEqual(config['WEB_PORT'], 5050)
        self.assertEqual(config['CLIP_MODES'], ['best', 'fast', 'classic', 'negative', 'caption'])
        self.assertEqual(config['PROMPT_CHOICES'], ['P1', 'P2'])
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('src.services.config_service.load_dotenv')
    def test_update_config_success(self, mock_load_dotenv, mock_file):
        """Test updating configuration successfully"""
        # Mock existing .env file content
        mock_file.return_value.__enter__.return_value.readlines.return_value = [
            'EXISTING_KEY=existing_value\n',
            'API_BASE_URL=old_url\n'
        ]
        
        config_data = {
            'API_BASE_URL': 'http://new:8000',
            'ENABLE_CLIP_ANALYSIS': True,
            'CLIP_MODES': ['best', 'fast']
        }
        
        result = self.service.update_config(config_data)
        self.assertTrue(result)
        mock_load_dotenv.assert_called_once()
    
    @patch('builtins.open', side_effect=Exception('File error'))
    def test_update_config_error(self, mock_file):
        """Test updating configuration with error"""
        config_data = {'API_BASE_URL': 'http://test:8000'}
        
        result = self.service.update_config(config_data)
        self.assertFalse(result)
    
    def test_get_processing_config(self):
        """Test getting processing configuration"""
        with patch.object(self.service, 'get_config') as mock_get_config:
            mock_get_config.return_value = {
                'API_BASE_URL': 'http://test:8000',
                'CLIP_MODEL_NAME': 'test-model',
                'ENABLE_CLIP_ANALYSIS': True,
                'ENABLE_LLM_ANALYSIS': True,
                'ENABLE_PARALLEL_PROCESSING': False,
                'ENABLE_METADATA_EXTRACTION': True,
                'IMAGE_DIRECTORY': 'Images',
                'OUTPUT_DIRECTORY': 'Output',
                'CLIP_MODES': ['best', 'fast'],
                'PROMPT_CHOICES': ['P1', 'P2'],
                'DEBUG': False,
                'FORCE_REPROCESS': False,
                'GENERATE_SUMMARIES': True
            }
            
            config = self.service.get_processing_config()
            
            self.assertEqual(config['API_BASE_URL'], 'http://test:8000')
            self.assertEqual(config['CLIP_MODEL_NAME'], 'test-model')
            self.assertTrue(config['ENABLE_CLIP_ANALYSIS'])
            self.assertEqual(config['IMAGE_DIRECTORY'], os.path.join(self.temp_dir, 'Images'))
            self.assertEqual(config['OUTPUT_DIRECTORY'], os.path.join(self.temp_dir, 'Output'))
    
    def test_validate_config_valid(self):
        """Test validating valid configuration"""
        config_data = {
            'API_BASE_URL': 'http://test:8000',
            'CLIP_MODEL_NAME': 'test-model',
            'WEB_PORT': '8080'
        }
        
        result = self.service.validate_config(config_data)
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_validate_config_missing_required(self):
        """Test validating configuration with missing required fields"""
        config_data = {
            'WEB_PORT': '8080'
        }
        
        result = self.service.validate_config(config_data)
        self.assertFalse(result['valid'])
        self.assertIn('API_BASE_URL is required', result['errors'])
        self.assertIn('CLIP_MODEL_NAME is required', result['errors'])
    
    def test_validate_config_invalid_port(self):
        """Test validating configuration with invalid port"""
        config_data = {
            'API_BASE_URL': 'http://test:8000',
            'CLIP_MODEL_NAME': 'test-model',
            'WEB_PORT': '99999'  # Invalid port
        }
        
        result = self.service.validate_config(config_data)
        self.assertFalse(result['valid'])
        self.assertIn('WEB_PORT must be between 1024 and 65535', result['errors'])
    
    def test_validate_config_non_numeric_port(self):
        """Test validating configuration with non-numeric port"""
        config_data = {
            'API_BASE_URL': 'http://test:8000',
            'CLIP_MODEL_NAME': 'test-model',
            'WEB_PORT': 'invalid'
        }
        
        result = self.service.validate_config(config_data)
        self.assertFalse(result['valid'])
        self.assertIn('WEB_PORT must be a valid number', result['errors'])
    
    def test_validate_config_empty_values(self):
        """Test validating configuration with empty values"""
        config_data = {
            'API_BASE_URL': '',
            'CLIP_MODEL_NAME': '',
            'WEB_PORT': '8080'
        }
        
        result = self.service.validate_config(config_data)
        self.assertFalse(result['valid'])
        self.assertIn('API_BASE_URL is required', result['errors'])
        self.assertIn('CLIP_MODEL_NAME is required', result['errors'])


if __name__ == '__main__':
    unittest.main() 