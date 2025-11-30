"""
Unit tests for refactored web interface
"""

import unittest
import tempfile
import os
import json
from unittest.mock import patch, MagicMock
from src.viewers.web_interface import WebInterface, create_app


class TestWebInterface(unittest.TestCase):
    """Test cases for refactored web interface"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {
            'WEB_PORT': '5050',
            'API_BASE_URL': 'http://localhost:7860'
        })
        self.env_patcher.start()
        
        self.interface = WebInterface(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)
        self.env_patcher.stop()
    
    def test_initialization(self):
        """Test web interface initialization"""
        self.assertIsNotNone(self.interface.app)
        self.assertEqual(self.interface.project_root, self.temp_dir)
        self.assertEqual(self.interface.web_port, 5050)
        self.assertIsNotNone(self.interface.config_service)
        self.assertIsNotNone(self.interface.analysis_service)
        self.assertIsNotNone(self.interface.image_service)
        self.assertIsNotNone(self.interface.db_manager)
        self.assertIsNotNone(self.interface.llm_manager)
    
    def test_create_app(self):
        """Test create_app factory function"""
        app = create_app()
        self.assertIsNotNone(app)
    
    def test_index_route(self):
        """Test index route"""
        with self.interface.app.test_client() as client:
            response = client.get('/')
            self.assertEqual(response.status_code, 200)
    
    def test_upload_route_get(self):
        """Test upload route GET"""
        with self.interface.app.test_client() as client:
            response = client.get('/upload')
            self.assertEqual(response.status_code, 200)
    
    def test_images_route(self):
        """Test images route"""
        with self.interface.app.test_client() as client:
            response = client.get('/images')
            self.assertEqual(response.status_code, 200)
    
    def test_results_route(self):
        """Test results route"""
        with self.interface.app.test_client() as client:
            response = client.get('/results')
            self.assertEqual(response.status_code, 200)
    
    def test_config_route_get(self):
        """Test config route GET"""
        with self.interface.app.test_client() as client:
            response = client.get('/config')
            self.assertEqual(response.status_code, 200)
    
    def test_config_route_post_success(self):
        """Test config route POST success"""
        with patch.object(self.interface.config_service, 'update_config') as mock_update:
            mock_update.return_value = True
            
            with self.interface.app.test_client() as client:
                response = client.post('/config', 
                                     json={'API_BASE_URL': 'http://test:8000'},
                                     content_type='application/json')
                
                self.assertEqual(response.status_code, 200)
                data = json.loads(response.data)
                self.assertEqual(data['status'], 'success')
    
    def test_config_route_post_failure(self):
        """Test config route POST failure"""
        with patch.object(self.interface.config_service, 'update_config') as mock_update:
            mock_update.return_value = False
            
            with self.interface.app.test_client() as client:
                response = client.post('/config', 
                                     json={'API_BASE_URL': 'http://test:8000'},
                                     content_type='application/json')
                
                self.assertEqual(response.status_code, 200)
                data = json.loads(response.data)
                self.assertEqual(data['status'], 'error')
    
    def test_api_analysis_route_success(self):
        """Test API analysis route success"""
        with patch.object(self.interface.analysis_service, 'get_analysis_data') as mock_get:
            mock_get.return_value = {'test': 'data'}
            
            with self.interface.app.test_client() as client:
                response = client.get('/api/analysis/test.json')
                
                self.assertEqual(response.status_code, 200)
                data = json.loads(response.data)
                self.assertEqual(data, {'test': 'data'})
    
    def test_api_analysis_route_not_found(self):
        """Test API analysis route not found"""
        with patch.object(self.interface.analysis_service, 'get_analysis_data') as mock_get:
            mock_get.return_value = None
            
            with self.interface.app.test_client() as client:
                response = client.get('/api/analysis/nonexistent.json')
                
                self.assertEqual(response.status_code, 404)
                data = json.loads(response.data)
                self.assertEqual(data['error'], 'File not found')
    
    def test_api_config_get_route(self):
        """Test API config GET route"""
        with patch.object(self.interface.config_service, 'get_config') as mock_get:
            mock_get.return_value = {'test': 'config'}
            
            with self.interface.app.test_client() as client:
                response = client.get('/api/config')
                
                self.assertEqual(response.status_code, 200)
                data = json.loads(response.data)
                self.assertEqual(data, {'test': 'config'})
    
    def test_api_config_post_route_success(self):
        """Test API config POST route success"""
        with patch.object(self.interface.config_service, 'update_config') as mock_update:
            mock_update.return_value = True
            
            with self.interface.app.test_client() as client:
                response = client.post('/api/config', 
                                     json={'API_BASE_URL': 'http://test:8000'},
                                     content_type='application/json')
                
                self.assertEqual(response.status_code, 200)
                data = json.loads(response.data)
                self.assertEqual(data['status'], 'success')
    
    def test_api_config_post_route_failure(self):
        """Test API config POST route failure"""
        with patch.object(self.interface.config_service, 'update_config') as mock_update:
            mock_update.return_value = False
            
            with self.interface.app.test_client() as client:
                response = client.post('/api/config', 
                                     json={'API_BASE_URL': 'http://test:8000'},
                                     content_type='application/json')
                
                self.assertEqual(response.status_code, 200)
                data = json.loads(response.data)
                self.assertEqual(data['status'], 'error')
    
    def test_api_upload_route_success(self):
        """Test API upload route success"""
        # Create a proper file-like object for testing
        from io import BytesIO
        
        with patch.object(self.interface.image_service, 'save_uploaded_file') as mock_save:
            mock_save.return_value = 'test.jpg'
            
            with self.interface.app.test_client() as client:
                response = client.post('/api/upload', 
                                     data={'file': (BytesIO(b'test image data'), 'test.jpg')},
                                     content_type='multipart/form-data')
                
                self.assertEqual(response.status_code, 200)
                data = json.loads(response.data)
                self.assertEqual(data['status'], 'success')
                self.assertEqual(data['filename'], 'test.jpg')
    
    def test_api_upload_route_no_file(self):
        """Test API upload route no file"""
        with self.interface.app.test_client() as client:
            response = client.post('/api/upload')
            
            self.assertEqual(response.status_code, 400)
            data = json.loads(response.data)
            self.assertEqual(data['error'], 'No file selected')
    
    def test_api_upload_route_invalid_file(self):
        """Test API upload route invalid file"""
        from io import BytesIO
        
        with patch.object(self.interface.image_service, 'save_uploaded_file') as mock_save:
            mock_save.return_value = None
            
            with self.interface.app.test_client() as client:
                response = client.post('/api/upload', 
                                     data={'file': (BytesIO(b'test data'), 'test.txt')},
                                     content_type='multipart/form-data')
                
                self.assertEqual(response.status_code, 400)
                data = json.loads(response.data)
                self.assertEqual(data['error'], 'Invalid file type')
    
    def test_api_status_route(self):
        """Test API status route"""
        with self.interface.app.test_client() as client:
            response = client.get('/api/status')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('status', data)
            self.assertIn('message', data)
    
    @patch('src.viewers.web_interface.webbrowser.open')
    def test_open_browser(self, mock_browser):
        """Test browser opening"""
        self.interface._open_browser()
        mock_browser.assert_called_once_with('http://localhost:5050')
    
    @patch('src.viewers.web_interface.DirectoryProcessor')
    def test_process_images_async_success(self, mock_processor):
        """Test async image processing success"""
        mock_processor_instance = MagicMock()
        mock_processor.return_value = mock_processor_instance
        
        self.interface._process_images_async()
        
        self.assertEqual(self.interface.processing_status['status'], 'completed')
        self.assertEqual(self.interface.processing_status['message'], 'Processing completed successfully!')
        mock_processor_instance.process_directory.assert_called_once()
    
    @patch('src.viewers.web_interface.DirectoryProcessor')
    def test_process_images_async_error(self, mock_processor):
        """Test async image processing error"""
        mock_processor.side_effect = Exception('Processing error')
        
        self.interface._process_images_async()
        
        self.assertEqual(self.interface.processing_status['status'], 'error')
        self.assertIn('Error during processing', self.interface.processing_status['message'])


if __name__ == '__main__':
    unittest.main() 