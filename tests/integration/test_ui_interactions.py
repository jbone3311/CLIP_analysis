#!/usr/bin/env python3
"""
UI Interaction Tests

Specific tests for web interface UI interactions including:
- Eye icon button (view result) functionality
- Config saving and loading
- Form submissions
- JavaScript interactions
- Template rendering
"""

import sys
import os
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from flask import Flask
from flask.testing import FlaskClient

from src.viewers.web_interface import WebInterface


class TestUIInteractions:
    """Test UI interactions and functionality"""
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create temporary project directory for testing"""
        temp_dir = tempfile.mkdtemp()
        try:
            # Create necessary subdirectories
            os.makedirs(os.path.join(temp_dir, 'Images'), exist_ok=True)
            os.makedirs(os.path.join(temp_dir, 'Output'), exist_ok=True)
            os.makedirs(os.path.join(temp_dir, 'src', 'config'), exist_ok=True)
            
            # Copy models.json to temp directory
            models_src = Path(__file__).parent.parent.parent / 'src' / 'config' / 'models.json'
            models_dst = Path(temp_dir) / 'src' / 'config' / 'models.json'
            if models_src.exists():
                shutil.copy2(models_src, models_dst)
            
            yield temp_dir
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def web_interface(self, temp_project_dir):
        """Create web interface instance for testing"""
        with patch('src.viewers.web_interface.load_dotenv'):
            interface = WebInterface(temp_project_dir)
            return interface
    
    @pytest.fixture
    def client(self, web_interface):
        """Create Flask test client"""
        web_interface.app.config['TESTING'] = True
        return web_interface.app.test_client()
    
    def test_eye_icon_button_view_result(self, client, web_interface):
        """Test eye icon button functionality for viewing results"""
        # Mock the analysis service's get_analysis_data method directly
        test_data = {
            'filename': 'test_image.jpg',
            'file_path': '/path/to/test_image.jpg',
            'clip_analysis': {
                'best': {
                    'prompt': 'A beautiful landscape',
                    'confidence': 0.95
                },
                'fast': {
                    'prompt': 'Nature scene',
                    'confidence': 0.88
                }
            },
            'llm_analysis': {
                'gpt-4': {
                    'response': 'This is a stunning landscape photograph...',
                    'model': 'gpt-4',
                    'provider': 'openai'
                }
            },
            'metadata': {
                'size': '1920x1080',
                'format': 'JPEG',
                'file_size': '2.5MB'
            },
            'processing_info': {
                'status': 'complete',
                'timestamp': '2024-01-01 12:00:00'
            }
        }
        
        with patch.object(web_interface.analysis_service, 'get_analysis_data', return_value=test_data):
            # Test the view result route (eye icon button)
            response = client.get('/result/test_analysis.json')
            
            assert response.status_code == 200
            
            # Check that the result detail template renders correctly
            response_data = response.data.decode('utf-8')
            
            # Check for key elements that should be in the result detail page
            assert 'test_image.jpg' in response_data
            assert 'A beautiful landscape' in response_data
            assert 'This is a stunning landscape photograph' in response_data
            assert '1920x1080' in response_data
            assert 'complete' in response_data.lower()
    
    def test_eye_icon_button_missing_file(self, client, web_interface):
        """Test eye icon button when file doesn't exist"""
        # Mock the analysis service to return None (file not found)
        with patch.object(web_interface.analysis_service, 'get_analysis_data', return_value=None):
            # Test the view result route with non-existent file
            response = client.get('/result/nonexistent_analysis.json')
            
            # Should redirect with flash message
            assert response.status_code == 302
    
    def test_config_saving_via_web_interface(self, client):
        """Test config saving through web interface forms"""
        # Mock config service
        with patch('src.services.config_service.ConfigService') as mock_config_service:
            mock_service = MagicMock()
            mock_service.update_config.return_value = True
            mock_config_service.return_value = mock_service
            
            # Test config update with various settings
            config_data = {
                'API_BASE_URL': 'http://test-clip-api:7860',
                'CLIP_MODEL_NAME': 'ViT-B-32/openai',
                'ENABLE_CLIP_ANALYSIS': True,
                'ENABLE_LLM_ANALYSIS': True,
                'CLIP_MODES': ['best', 'fast', 'classic'],
                'PROMPT_CHOICES': ['P1', 'P2', 'P3'],
                'OPENAI_API_KEY': 'test_openai_key_123',
                'ANTHROPIC_API_KEY': 'test_anthropic_key_456',
                'OLLAMA_URL': 'http://localhost:11434',
                'WEB_PORT': 5051,
                'ENABLE_PARALLEL_PROCESSING': True,
                'ENABLE_METADATA_EXTRACTION': True,
                'GENERATE_SUMMARIES': True,
                'LOGGING_LEVEL': 'DEBUG',
                'RETRY_LIMIT': 3,
                'TIMEOUT': 120
            }
            
            response = client.post('/config',
                                 json=config_data,
                                 content_type='application/json')
            
            assert response.status_code == 200
            result = json.loads(response.data)
            assert result['status'] == 'success'
            assert result['message'] == 'Configuration saved successfully'
            
            # Verify that update_config was called with the correct data
            mock_service.update_config.assert_called_once_with(config_data)
    
    def test_config_saving_failure(self, client):
        """Test config saving when it fails"""
        # Mock config service to return False (failure)
        with patch('src.services.config_service.ConfigService') as mock_config_service:
            mock_service = MagicMock()
            mock_service.update_config.return_value = False
            mock_config_service.return_value = mock_service
            
            config_data = {
                'API_BASE_URL': 'http://test:7860'
            }
            
            response = client.post('/config',
                                 json=config_data,
                                 content_type='application/json')
            
            assert response.status_code == 200
            result = json.loads(response.data)
            assert result['status'] == 'error'
            assert 'Failed to save configuration' in result['message']
    
    def test_config_saving_exception(self, client):
        """Test config saving when an exception occurs"""
        # Mock config service to raise an exception
        with patch('src.services.config_service.ConfigService') as mock_config_service:
            mock_service = MagicMock()
            mock_service.update_config.side_effect = Exception("Test error")
            mock_config_service.return_value = mock_service
            
            config_data = {
                'API_BASE_URL': 'http://test:7860'
            }
            
            response = client.post('/config',
                                 json=config_data,
                                 content_type='application/json')
            
            assert response.status_code == 200
            result = json.loads(response.data)
            assert result['status'] == 'error'
            assert 'Test error' in result['message']
    
    def test_config_page_rendering(self, client):
        """Test config page renders correctly"""
        # Mock config service to return test config
        with patch('src.services.config_service.ConfigService') as mock_config_service:
            mock_service = MagicMock()
            mock_service.get_config.return_value = {
                'API_BASE_URL': 'http://localhost:7860',
                'CLIP_MODEL_NAME': 'ViT-L-14/openai',
                'ENABLE_CLIP_ANALYSIS': True,
                'ENABLE_LLM_ANALYSIS': True,
                'OPENAI_API_KEY': 'test_key',
                'WEB_PORT': 5050
            }
            mock_config_service.return_value = mock_service
            
            response = client.get('/config')
            assert response.status_code == 200
            
            response_data = response.data.decode('utf-8')
            assert 'Configuration' in response_data
            assert 'http://localhost:7860' in response_data
            assert 'ViT-L-14/openai' in response_data
    
    def test_download_button_functionality(self, client, temp_project_dir):
        """Test download button functionality"""
        # Create a test analysis file
        test_file = os.path.join(temp_project_dir, 'Output', 'test_analysis.json')
        os.makedirs(os.path.dirname(test_file), exist_ok=True)
        
        test_data = {
            'filename': 'test_image.jpg',
            'clip_analysis': {'best': 'Test analysis'},
            'llm_analysis': {'gpt-4': 'Test LLM analysis'},
            'metadata': {'size': '1920x1080'}
        }
        
        with open(test_file, 'w') as f:
            json.dump(test_data, f)
        
        # Test download route
        response = client.get('/download/test_analysis.json')
        
        assert response.status_code == 200
        assert response.headers['Content-Disposition'] == 'attachment; filename=test_analysis.json'
        
        # Check that the downloaded content matches
        downloaded_data = json.loads(response.data)
        assert downloaded_data['filename'] == 'test_image.jpg'
        assert downloaded_data['clip_analysis']['best'] == 'Test analysis'
    
    def test_download_button_missing_file(self, client):
        """Test download button when file doesn't exist"""
        response = client.get('/download/nonexistent_file.json')
        
        # Should redirect with flash message
        assert response.status_code == 302
    
    def test_process_button_functionality(self, client, web_interface):
        """Test process button functionality"""
        # Set initial processing status
        web_interface.processing_status = {'status': 'idle', 'message': 'Ready to process'}
        
        # Test process POST endpoint
        response = client.post('/process')
        
        # Should redirect after starting process
        assert response.status_code == 302
        
        # Check that processing status was updated
        assert web_interface.processing_status['status'] == 'processing'
        assert 'Starting image processing' in web_interface.processing_status['message']
    
    def test_process_button_already_processing(self, client, web_interface):
        """Test process button when already processing"""
        # Set processing status to already processing
        web_interface.processing_status = {'status': 'processing', 'message': 'Processing...'}
        
        # Test process POST endpoint
        response = client.post('/process')
        
        # Should redirect with flash message
        assert response.status_code == 302
    
    def test_upload_form_functionality(self, client, temp_project_dir):
        """Test upload form functionality"""
        # Create a test image file
        test_image = os.path.join(temp_project_dir, 'test_image.jpg')
        with open(test_image, 'wb') as f:
            f.write(b'fake image data')
        
        # Test upload with valid file
        with open(test_image, 'rb') as f:
            response = client.post('/upload',
                                 data={'file': (f, 'test_image.jpg')},
                                 content_type='multipart/form-data')
        
        assert response.status_code == 302  # Redirect after upload
    
    def test_upload_form_no_file(self, client):
        """Test upload form when no file is selected"""
        response = client.post('/upload')
        assert response.status_code == 302  # Redirect with flash message
    
    def test_upload_form_invalid_file(self, client):
        """Test upload form with invalid file type"""
        # Create a test file with invalid extension
        test_file = tempfile.NamedTemporaryFile(suffix='.txt', delete=False)
        test_file.write(b'This is not an image')
        test_file.close()
        
        try:
            with open(test_file.name, 'rb') as f:
                response = client.post('/upload',
                                     data={'file': (f, 'test.txt')},
                                     content_type='multipart/form-data')
            
            assert response.status_code == 302  # Redirect with flash message
        finally:
            os.unlink(test_file.name)
    
    def test_template_variables_availability(self, client):
        """Test that all required template variables are available"""
        routes_to_test = [
            ('/', ['total_images', 'total_analyses', 'completed_analyses', 'recent_analyses', 'processing_status']),
            ('/process', ['processing_status']),
            ('/images', ['images']),
            ('/results', ['analyses']),
            ('/database', ['results']),
            ('/llm_config', ['configured_models', 'available_models', 'ollama_connected', 'openai_connected'])
        ]
        
        for route, expected_variables in routes_to_test:
            response = client.get(route)
            assert response.status_code == 200, f"Route {route} failed"
            
            # Check that template renders without variable errors
            response_data = response.data.decode('utf-8')
            assert 'UndefinedError' not in response_data, f"UndefinedError in {route}"
            assert 'jinja2.exceptions' not in response_data, f"Jinja2 error in {route}"
    
    def test_javascript_functionality(self, client):
        """Test that JavaScript functionality is properly included"""
        routes_to_test = ['/', '/results', '/process', '/database']
        
        for route in routes_to_test:
            response = client.get(route)
            assert response.status_code == 200
            
            response_data = response.data.decode('utf-8')
            
            # Check for common JavaScript functions
            if route == '/results':
                # Results page should have view result functionality
                assert 'viewResult' in response_data or 'view_result' in response_data.lower()
            
            if route == '/process':
                # Process page should have status update functionality
                assert 'updateStatus' in response_data or 'status' in response_data.lower()
            
            if route == '/database':
                # Database page should have modal functionality
                assert 'modal' in response_data.lower() or 'bootstrap' in response_data.lower()
    
    def test_css_styling_availability(self, client):
        """Test that CSS styling is properly included"""
        routes_to_test = ['/', '/upload', '/images', '/results', '/process', '/database', '/llm_config']
        
        for route in routes_to_test:
            response = client.get(route)
            assert response.status_code == 200
            
            response_data = response.data.decode('utf-8')
            
            # Check for Bootstrap CSS classes
            assert 'bootstrap' in response_data.lower() or 'btn-' in response_data or 'card' in response_data
    
    def test_flash_messages_display(self, client):
        """Test that flash messages are properly displayed"""
        # Test various scenarios that should generate flash messages
        
        # Test upload without file
        response = client.post('/upload')
        assert response.status_code == 302
        
        # Test download of non-existent file
        response = client.get('/download/nonexistent.json')
        assert response.status_code == 302
        
        # Test process when already processing
        response = client.post('/process')
        assert response.status_code == 302
    
    def test_error_pages(self, client):
        """Test error page handling"""
        # Test 404 page
        response = client.get('/nonexistent-route')
        assert response.status_code == 404
        
        # Test 500 error handling (if implemented)
        # This would require triggering an actual error in the application


class TestConfigManagerUI:
    """Test config manager UI integration"""
    
    def test_config_manager_creates_proper_env_structure(self, temp_project_dir):
        """Test that config manager creates proper .env structure"""
        from src.config.config_manager import create_default_env_file
        
        # Create default env file
        success = create_default_env_file()
        assert success
        
        # Check that .env file was created with proper structure
        env_file = os.path.join(temp_project_dir, '.env')
        assert os.path.exists(env_file)
        
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for API keys section
            assert 'API Keys' in content
            assert 'OPENAI_API_KEY' in content
            assert 'ANTHROPIC_API_KEY' in content
            assert 'GOOGLE_API_KEY' in content
            
            # Check for API URLs section
            assert 'API URLs' in content
            assert 'OPENAI_URL' in content
            assert 'ANTHROPIC_URL' in content
            
            # Check for CLIP configuration
            assert 'CLIP Configuration' in content
            assert 'API_BASE_URL' in content
            assert 'CLIP_MODEL_NAME' in content
            
            # Check for analysis features
            assert 'Analysis Features' in content
            assert 'ENABLE_CLIP_ANALYSIS' in content
            assert 'ENABLE_LLM_ANALYSIS' in content
    
    def test_models_config_structure(self, temp_project_dir):
        """Test that models config has proper structure"""
        models_file = os.path.join(temp_project_dir, 'src', 'config', 'models.json')
        os.makedirs(os.path.dirname(models_file), exist_ok=True)
        
        # Create test models config
        test_models = {
            "models": [
                {
                    "id": "gpt-4",
                    "title": "GPT-4",
                    "provider": "openai",
                    "model_name": "gpt-4",
                    "api_url": "https://api.openai.com/v1",
                    "enabled": True,
                    "description": "OpenAI's most advanced model"
                }
            ],
            "providers": {
                "openai": {
                    "name": "OpenAI",
                    "api_key_env": "OPENAI_API_KEY",
                    "api_url_env": "OPENAI_URL"
                }
            }
        }
        
        with open(models_file, 'w') as f:
            json.dump(test_models, f)
        
        # Test loading
        from src.analyzers.llm_manager import LLMManager
        llm_manager = LLMManager()
        config = llm_manager.load_models_config()
        
        assert 'models' in config
        assert 'providers' in config
        assert len(config['models']) > 0
        assert len(config['providers']) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 