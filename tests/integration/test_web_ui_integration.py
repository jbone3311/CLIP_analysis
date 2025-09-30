#!/usr/bin/env python3
"""
Web UI Integration Tests

Tests for web interface functionality including:
- Config saving and loading
- UI interactions (eye icon button, etc.)
- Template rendering
- Route functionality
- Database integration
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
from src.database.db_manager import DatabaseManager
from src.analyzers.llm_manager import LLMManager


class TestWebUIIntegration:
    """Test web UI integration functionality"""
    
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
    
    @pytest.fixture
    def sample_env_content(self):
        """Sample .env file content for testing"""
        return """# Test Environment Configuration
API_BASE_URL=http://localhost:7860
CLIP_MODEL_NAME=ViT-L-14/openai
ENABLE_CLIP_ANALYSIS=True
ENABLE_LLM_ANALYSIS=True
OPENAI_API_KEY=test_openai_key
ANTHROPIC_API_KEY=test_anthropic_key
OLLAMA_URL=http://localhost:11434
WEB_PORT=5050
"""
    
    def test_web_interface_creation(self, temp_project_dir):
        """Test that web interface can be created successfully"""
        with patch('src.viewers.web_interface.load_dotenv'):
            interface = WebInterface(temp_project_dir)
            
            assert interface is not None
            assert interface.app is not None
            assert interface.processing_status == {'status': 'idle', 'message': 'Ready to process'}
            assert interface.analysis_service is not None
            assert interface.image_service is not None
            assert interface.db_manager is not None
            assert interface.llm_manager is not None
    
    def test_routes_registration(self, web_interface):
        """Test that all routes are properly registered"""
        routes = list(web_interface.app.url_map.iter_rules())
        route_endpoints = [route.endpoint for route in routes if route.endpoint != 'static']
        
        # Check for essential routes
        expected_routes = ['index', 'upload', 'images', 'results', 'process', 'database', 'llm_config']
        for route in expected_routes:
            assert route in route_endpoints, f"Route '{route}' not found in registered routes"
    
    def test_dashboard_route(self, client):
        """Test dashboard route functionality"""
        response = client.get('/')
        assert response.status_code == 200
        
        # Check that template renders without errors
        assert b'Dashboard' in response.data or b'dashboard' in response.data.lower()
    
    def test_process_route_template_variables(self, client):
        """Test that process route passes correct template variables"""
        response = client.get('/process')
        assert response.status_code == 200
        
        # Check that processing_status is available in template
        assert b'Processing Control' in response.data
    
    def test_config_saving_functionality(self, temp_project_dir, sample_env_content):
        """Test config saving and loading functionality"""
        # Create a test .env file
        env_file = os.path.join(temp_project_dir, '.env')
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(sample_env_content)
        
        # Test config loading
        with patch.dict(os.environ, {}, clear=True):
            with patch('src.config.config_manager.load_dotenv'):
                # Test that .env file can be read
                assert os.path.exists(env_file)
                
                # Read the content to verify it was created correctly
                with open(env_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    assert 'API_BASE_URL' in content
                    assert 'http://localhost:7860' in content
    
    def test_config_update_via_web_interface(self, client, temp_project_dir):
        """Test config update through web interface"""
        # Mock the config service
        with patch('src.services.config_service.ConfigService') as mock_config_service:
            mock_service = MagicMock()
            mock_service.update_config.return_value = True
            mock_config_service.return_value = mock_service
            
            # Test config update endpoint
            config_data = {
                'API_BASE_URL': 'http://test:7860',
                'CLIP_MODEL_NAME': 'test-model'
            }
            
            response = client.post('/config', 
                                 json=config_data,
                                 content_type='application/json')
            
            assert response.status_code == 200
            result = json.loads(response.data)
            assert result['status'] == 'success'
            assert result['message'] == 'Configuration saved successfully'
    
    def test_eye_icon_button_functionality(self, client):
        """Test eye icon button (view result) functionality"""
        # Mock the analysis service
        with patch('src.services.analysis_service.AnalysisService') as mock_analysis_service:
            mock_service = MagicMock()
            mock_service.get_analysis_data.return_value = {
                'filename': 'test.jpg',
                'clip_analysis': {'best': 'Test analysis'},
                'llm_analysis': {'gpt-4': 'Test LLM analysis'},
                'metadata': {'size': '1024x768'}
            }
            mock_analysis_service.return_value = mock_service
            
            # Test view result route
            response = client.get('/result/test_analysis.json')
            assert response.status_code == 200
            
            # Check that template renders with data
            assert b'test.jpg' in response.data
    
    def test_download_functionality(self, client, temp_project_dir):
        """Test download functionality"""
        # Create a test file
        test_file = os.path.join(temp_project_dir, 'Output', 'test_analysis.json')
        os.makedirs(os.path.dirname(test_file), exist_ok=True)
        with open(test_file, 'w') as f:
            json.dump({'test': 'data'}, f)
        
        # Test download route
        response = client.get('/download/test_analysis.json')
        assert response.status_code == 200
        assert response.headers['Content-Disposition'] == 'attachment; filename=test_analysis.json'
    
    def test_upload_functionality(self, client, temp_project_dir):
        """Test file upload functionality"""
        # Create a test image file
        test_image = os.path.join(temp_project_dir, 'test_image.jpg')
        with open(test_image, 'wb') as f:
            f.write(b'fake image data')
        
        # Test upload endpoint
        with open(test_image, 'rb') as f:
            response = client.post('/upload',
                                 data={'file': (f, 'test_image.jpg')},
                                 content_type='multipart/form-data')
        
        assert response.status_code == 302  # Redirect after upload
    
    def test_database_route_with_data(self, client):
        """Test database route with mock data"""
        # Mock the database manager
        with patch('src.database.db_manager.DatabaseManager') as mock_db_manager:
            mock_db = MagicMock()
            mock_db.get_all_results.return_value = [
                {
                    'id': 1,
                    'filename': 'test1.jpg',
                    'directory': 'Images',
                    'model': 'ViT-L-14/openai',
                    'modes': ['best', 'fast'],
                    'has_prompts': True,
                    'has_analysis': True,
                    'md5': '1234567890abcdef',
                    'date_added': '2024-01-01 12:00:00'
                }
            ]
            mock_db_manager.return_value = mock_db
            
            response = client.get('/database')
            assert response.status_code == 200
            
            # Check that database data is displayed
            assert b'test1.jpg' in response.data
            assert b'ViT-L-14/openai' in response.data
    
    def test_llm_config_route(self, client):
        """Test LLM config route functionality"""
        response = client.get('/llm-config')
        assert response.status_code == 200
        
        # Check that LLM config template renders
        assert b'LLM Configuration' in response.data or b'llm-config' in response.data.lower()
    
    def test_status_endpoint(self, client):
        """Test processing status endpoint"""
        response = client.get('/status')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'status' in data
        assert 'message' in data
    
    def test_process_post_endpoint(self, client):
        """Test process POST endpoint"""
        response = client.post('/process')
        assert response.status_code == 302  # Redirect after starting process
    
    def test_template_rendering_without_errors(self, client):
        """Test that all templates render without Jinja2 errors"""
        routes_to_test = ['/', '/upload', '/images', '/results', '/process', '/database', '/llm_config']
        
        for route in routes_to_test:
            response = client.get(route)
            assert response.status_code == 200, f"Route {route} failed with status {response.status_code}"
            
            # Check for common template errors
            assert b'UndefinedError' not in response.data, f"UndefinedError in route {route}"
            assert b'jinja2.exceptions' not in response.data, f"Jinja2 error in route {route}"
    
    def test_api_routes_functionality(self, client):
        """Test API routes functionality"""
        # Test API routes that should exist
        api_routes = [
            '/api/upload',
            '/api/process',
            '/api/status',
            '/api/results',
            '/api/database/results'
        ]
        
        for route in api_routes:
            response = client.get(route)
            # Should not return 404 (route should exist)
            assert response.status_code != 404, f"API route {route} not found"
    
    def test_error_handling(self, client):
        """Test error handling in web interface"""
        # Test non-existent route
        response = client.get('/nonexistent-route')
        assert response.status_code == 404
        
        # Test invalid file download
        response = client.get('/download/nonexistent-file.json')
        assert response.status_code == 302  # Should redirect with flash message
    
    def test_flash_messages(self, client):
        """Test flash message functionality"""
        # Test upload without file
        response = client.post('/upload')
        assert response.status_code == 302  # Should redirect with flash message
    
    def test_processing_status_integration(self, web_interface, client):
        """Test processing status integration"""
        # Set processing status
        web_interface.processing_status = {
            'status': 'processing',
            'message': 'Processing images...'
        }
        
        # Check that status is reflected in templates
        response = client.get('/process')
        assert response.status_code == 200
        assert b'Processing in progress' in response.data
    
    def test_database_integration(self, web_interface, client):
        """Test database integration in web interface"""
        # Mock database operations
        with patch.object(web_interface.db_manager, 'get_all_results') as mock_get_results:
            mock_get_results.return_value = [
                {
                    'id': 1,
                    'filename': 'test.jpg',
                    'status': 'complete'
                }
            ]
            
            response = client.get('/database')
            assert response.status_code == 200
            assert b'test.jpg' in response.data
    
    def test_llm_manager_integration(self, web_interface, client):
        """Test LLM manager integration in web interface"""
        # Mock LLM manager operations
        with patch.object(web_interface.llm_manager, 'get_configured_models') as mock_get_models:
            mock_get_models.return_value = [
                {
                    'id': 'gpt-4',
                    'title': 'GPT-4',
                    'provider': 'openai',
                    'enabled': True
                }
            ]
            
            response = client.get('/llm-config')
            assert response.status_code == 200


class TestConfigManagerIntegration:
    """Test config manager integration with web interface"""
    
    def test_config_manager_creates_env_file(self, temp_project_dir):
        """Test that config manager creates .env file correctly"""
        from src.config.config_manager import create_default_env_file
        
        # Create default env file
        success = create_default_env_file()
        assert success
        
        # Check that .env file was created
        env_file = os.path.join(temp_project_dir, '.env')
        assert os.path.exists(env_file)
        
        # Check content
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'API_BASE_URL' in content
            assert 'OPENAI_API_KEY' in content
            assert 'ENABLE_CLIP_ANALYSIS' in content
    
    def test_models_config_loading(self, temp_project_dir):
        """Test that models config can be loaded"""
        # Create models.json if it doesn't exist
        models_file = os.path.join(temp_project_dir, 'src', 'config', 'models.json')
        os.makedirs(os.path.dirname(models_file), exist_ok=True)
        
        test_models = {
            "models": [
                {
                    "id": "test-model",
                    "title": "Test Model",
                    "provider": "test-provider",
                    "model_name": "test",
                    "enabled": True
                }
            ]
        }
        
        with open(models_file, 'w') as f:
            json.dump(test_models, f)
        
        # Test loading
        llm_manager = LLMManager()
        config = llm_manager.load_models_config()
        assert 'models' in config
        assert len(config['models']) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 