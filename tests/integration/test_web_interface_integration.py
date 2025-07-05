"""
Integration tests for web interface
"""

import unittest
import tempfile
import os
import json
import shutil
import threading
import time
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.viewers.web_interface import app

class TestWebInterfaceIntegration(unittest.TestCase):
    """Integration tests for web interface functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = app.test_client()
        self.app.testing = True
        
        # Create temporary directories
        self.temp_dir = tempfile.mkdtemp()
        self.images_dir = os.path.join(self.temp_dir, "Images")
        self.output_dir = os.path.join(self.temp_dir, "Output")
        
        os.makedirs(self.images_dir)
        os.makedirs(self.output_dir)
        
        # Create test image files
        self.test_images = ["test1.jpg", "test2.png", "test3.gif"]
        for img in self.test_images:
            img_path = os.path.join(self.images_dir, img)
            with open(img_path, 'w') as f:
                f.write(f"fake image data for {img}")
        
        # Create test analysis files
        self.test_analyses = ["test1_analysis.json", "test2_analysis.json"]
        for analysis in self.test_analyses:
            analysis_path = os.path.join(self.output_dir, analysis)
            analysis_data = {
                "file_info": {
                    "filename": analysis.replace("_analysis.json", ".jpg"),
                    "directory": "Images",
                    "date_processed": "2024-01-01T12:00:00",
                    "file_size": 1024
                },
                "processing_info": {
                    "status": "complete",
                    "processing_time": 5.2
                },
                "analysis": {
                    "clip": {"best": {"prompt": "test"}},
                    "llm": [{"prompt": "P1", "result": "test"}],
                    "metadata": {"width": 100, "height": 100}
                }
            }
            with open(analysis_path, 'w') as f:
                json.dump(analysis_data, f)
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    @patch('src.viewers.web_interface.UPLOAD_FOLDER')
    @patch('src.viewers.web_interface.OUTPUT_FOLDER')
    def test_full_workflow(self, mock_output, mock_upload):
        """Test complete web interface workflow"""
        mock_upload.__str__ = lambda: self.images_dir
        mock_output.__str__ = lambda: self.output_dir
        
        # Test dashboard
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Image Analysis', response.data)
        
        # Test images page
        response = self.app.get('/images')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Image Gallery', response.data)
        
        # Test results page
        response = self.app.get('/results')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Analysis Results', response.data)
        
        # Test config page
        response = self.app.get('/config')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Configuration', response.data)
        
        # Test process page
        response = self.app.get('/process')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Process Images', response.data)
    
    @patch('src.viewers.web_interface.UPLOAD_FOLDER')
    @patch('src.viewers.web_interface.OUTPUT_FOLDER')
    def test_configuration_workflow(self, mock_output, mock_upload):
        """Test configuration management workflow"""
        mock_upload.__str__ = lambda: self.images_dir
        mock_output.__str__ = lambda: self.output_dir
        
        # Get current config
        response = self.app.get('/config')
        self.assertEqual(response.status_code, 200)
        
        # Update configuration
        test_config = {
            'API_BASE_URL': 'http://test:8000',
            'ENABLE_CLIP_ANALYSIS': True,
            'ENABLE_LLM_ANALYSIS': False,
            'IMAGE_DIRECTORY': 'TestImages',
            'OUTPUT_DIRECTORY': 'TestOutput'
        }
        
        with patch('src.viewers.web_interface.update_config') as mock_update:
            mock_update.return_value = True
            
            response = self.app.post('/config', 
                                   json=test_config,
                                   content_type='application/json')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data['status'], 'success')
            mock_update.assert_called_once_with(test_config)
    
    @patch('src.viewers.web_interface.UPLOAD_FOLDER')
    @patch('src.viewers.web_interface.OUTPUT_FOLDER')
    def test_file_upload_workflow(self, mock_output, mock_upload):
        """Test file upload workflow"""
        mock_upload.__str__ = lambda: self.images_dir
        mock_output.__str__ = lambda: self.output_dir
        
        # Test upload page
        response = self.app.get('/upload')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Upload Images', response.data)
        
        # Test file upload (simulated)
        with patch('werkzeug.utils.secure_filename') as mock_secure:
            mock_secure.return_value = 'test_upload.jpg'
            
            # Create a mock file
            from io import BytesIO
            test_file = (BytesIO(b'test image data'), 'test.jpg')
            
            response = self.app.post('/upload', 
                                   data={'file': test_file},
                                   content_type='multipart/form-data')
            
            # Should redirect after upload
            self.assertIn(response.status_code, [200, 302])
    
    @patch('src.viewers.web_interface.UPLOAD_FOLDER')
    @patch('src.viewers.web_interface.OUTPUT_FOLDER')
    def test_processing_workflow(self, mock_output, mock_upload):
        """Test image processing workflow"""
        mock_upload.__str__ = lambda: self.images_dir
        mock_output.__str__ = lambda: self.output_dir
        
        # Test process page
        response = self.app.get('/process')
        self.assertEqual(response.status_code, 200)
        
        # Test start processing
        with patch('src.viewers.web_interface.process_images_async') as mock_process:
            response = self.app.post('/process')
            
            # Should redirect after starting processing
            self.assertIn(response.status_code, [200, 302])
        
        # Test status endpoint
        response = self.app.get('/status')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('status', data)
    
    @patch('src.viewers.web_interface.UPLOAD_FOLDER')
    @patch('src.viewers.web_interface.OUTPUT_FOLDER')
    def test_results_viewing_workflow(self, mock_output, mock_upload):
        """Test results viewing workflow"""
        mock_upload.__str__ = lambda: self.images_dir
        mock_output.__str__ = lambda: self.output_dir
        
        # Test results page
        response = self.app.get('/results')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Analysis Results', response.data)
        
        # Test viewing specific result
        test_analysis_file = "test1_analysis.json"
        response = self.app.get(f'/result/{test_analysis_file}')
        self.assertEqual(response.status_code, 200)
        
        # Test downloading result
        response = self.app.get(f'/download/{test_analysis_file}')
        self.assertEqual(response.status_code, 200)
        
        # Test API endpoint
        response = self.app.get(f'/api/analysis/{test_analysis_file}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('file_info', data)
    
    @patch('src.viewers.web_interface.UPLOAD_FOLDER')
    @patch('src.viewers.web_interface.OUTPUT_FOLDER')
    def test_error_handling(self, mock_output, mock_upload):
        """Test error handling in web interface"""
        mock_upload.__str__ = lambda: self.images_dir
        mock_output.__str__ = lambda: self.output_dir
        
        # Test non-existent result file
        response = self.app.get('/result/nonexistent.json')
        self.assertIn(response.status_code, [302, 404])  # Should redirect or 404
        
        # Test non-existent download
        response = self.app.get('/download/nonexistent.json')
        self.assertIn(response.status_code, [302, 404])  # Should redirect or 404
        
        # Test invalid API request
        response = self.app.get('/api/analysis/nonexistent.json')
        self.assertEqual(response.status_code, 404)
    
    @patch('src.viewers.web_interface.UPLOAD_FOLDER')
    @patch('src.viewers.web_interface.OUTPUT_FOLDER')
    def test_thumbnail_generation(self, mock_output, mock_upload):
        """Test thumbnail generation in web interface"""
        mock_upload.__str__ = lambda: self.images_dir
        mock_output.__str__ = lambda: self.output_dir
        
        # Test images page with thumbnails
        response = self.app.get('/images')
        self.assertEqual(response.status_code, 200)
        
        # Test results page with thumbnails
        response = self.app.get('/results')
        self.assertEqual(response.status_code, 200)
        
        # Both pages should load without errors even if thumbnail generation fails
        self.assertIn(b'Image Gallery', response.data)
    
    def test_concurrent_access(self):
        """Test concurrent access to web interface"""
        def make_request():
            response = self.app.get('/')
            return response.status_code
        
        # Create multiple threads to simulate concurrent access
        threads = []
        results = []
        
        for i in range(5):
            thread = threading.Thread(target=lambda: results.append(make_request()))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        for result in results:
            self.assertEqual(result, 200)
    
    @patch('src.viewers.web_interface.UPLOAD_FOLDER')
    @patch('src.viewers.web_interface.OUTPUT_FOLDER')
    def test_large_file_handling(self, mock_output, mock_upload):
        """Test handling of large files and directories"""
        mock_upload.__str__ = lambda: self.images_dir
        mock_output.__str__ = lambda: self.output_dir
        
        # Create many test files
        for i in range(100):
            img_path = os.path.join(self.images_dir, f"large_test_{i}.jpg")
            with open(img_path, 'w') as f:
                f.write(f"large image data {i}" * 1000)  # Make files larger
        
        # Test that pages still load
        response = self.app.get('/images')
        self.assertEqual(response.status_code, 200)
        
        # Test that results page still loads
        response = self.app.get('/results')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main() 