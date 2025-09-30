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
    
    @patch('src.services.config_service.get_combined_config')
    def test_get_config_with_env_vars(self, mock_get_combined_config):
        """Test getting configuration with environment variables"""
        # Mock the combined config to return our test values
        mock_get_combined_config.return_value = {
            'private': {
                'web_port': 8080
            },
            'public': {
                'clip_config': {
                    'api_base_url': 'http://test:8000',
                    'model_name': 'test-model',
                    'enable_clip_analysis': True,
                    'clip_modes': ['best', 'fast'],
                    'prompt_choices': ['P1', 'P2', 'P3']
                },
                'analysis_features': {
                    'enable_llm_analysis': False,
                    'enable_parallel_processing': False,
                    'enable_metadata_extraction': True,
                    'generate_summaries': True
                }
            }
        }
        
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
        self.assertEqual(config['CLIP_MODES'], ['best', 'fast', 'classic'])
        # The actual default includes more prompt choices
        self.assertIn('P1', config['PROMPT_CHOICES'])
        self.assertIn('P2', config['PROMPT_CHOICES'])
    
    @patch('src.services.config_service.update_private_config')
    @patch('src.services.config_service.update_public_config')
    @patch('src.services.config_service.load_env_file')
    def test_update_config_success(self, mock_load_env, mock_update_public, mock_update_private):
        """Test updating configuration successfully"""
        # Mock the update functions to return success
        mock_update_private.return_value = True
        mock_update_public.return_value = True
        
        config_data = {
            'API_BASE_URL': 'http://new:8000',
            'ENABLE_CLIP_ANALYSIS': True,
            'CLIP_MODES': ['best', 'fast']
        }
        
        result = self.service.update_config(config_data)
        self.assertTrue(result)
        mock_load_env.assert_called_once()
    
    @patch('src.services.config_service.update_private_config')
    @patch('src.services.config_service.update_public_config')
    def test_update_config_error(self, mock_update_public, mock_update_private):
        """Test updating configuration with error"""
        # Mock the update functions to raise an exception
        mock_update_private.side_effect = Exception('File error')
        mock_update_public.return_value = True  # This one succeeds
        
        config_data = {'API_BASE_URL': 'http://test:8000'}
        
        result = self.service.update_config(config_data)
        # The function returns True if at least one update succeeds
        self.assertTrue(result)
    
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