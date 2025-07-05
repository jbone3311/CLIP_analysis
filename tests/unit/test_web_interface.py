"""
Unit tests for web interface module
"""

import unittest
import tempfile
import os
import json
import shutil
from unittest.mock import patch, MagicMock, mock_open
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.viewers.web_interface import (
    app, get_config, update_config, create_thumbnail, 
    get_thumbnail_data_url, allowed_file, get_analysis_files, 
    get_image_files, process_images_async
)

class TestWebInterface(unittest.TestCase):
    """Test cases for web interface functionality"""
    
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
        
        # Create test image file
        self.test_image_path = os.path.join(self.images_dir, "test.jpg")
        with open(self.test_image_path, 'w') as f:
            f.write("fake image data")
        
        # Create test analysis file
        self.test_analysis_path = os.path.join(self.output_dir, "test_analysis.json")
        test_analysis_data = {
            "file_info": {
                "filename": "test.jpg",
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
        with open(self.test_analysis_path, 'w') as f:
            json.dump(test_analysis_data, f)
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_allowed_file(self):
        """Test file extension validation"""
        self.assertTrue(allowed_file("test.jpg"))
        self.assertTrue(allowed_file("test.png"))
        self.assertTrue(allowed_file("test.jpeg"))
        self.assertTrue(allowed_file("test.gif"))
        self.assertTrue(allowed_file("test.bmp"))
        self.assertTrue(allowed_file("test.tiff"))
        self.assertTrue(allowed_file("test.webp"))
        
        self.assertFalse(allowed_file("test.txt"))
        self.assertFalse(allowed_file("test.pdf"))
        self.assertFalse(allowed_file("test"))
        self.assertFalse(allowed_file(""))
    
    @patch('src.viewers.web_interface.UPLOAD_FOLDER')
    @patch('src.viewers.web_interface.OUTPUT_FOLDER')
    def test_get_image_files(self, mock_output, mock_upload):
        """Test getting image files with thumbnails"""
        mock_upload.__str__ = lambda: self.images_dir
        mock_output.__str__ = lambda: self.output_dir
        
        image_files = get_image_files()
        
        self.assertEqual(len(image_files), 1)
        self.assertEqual(image_files[0]['filename'], 'test.jpg')
        self.assertEqual(image_files[0]['path'], 'test.jpg')
        self.assertIn('thumbnail', image_files[0])
    
    @patch('src.viewers.web_interface.OUTPUT_FOLDER')
    def test_get_analysis_files(self, mock_output):
        """Test getting analysis files with thumbnails"""
        mock_output.__str__ = lambda: self.output_dir
        
        analysis_files = get_analysis_files()
        
        self.assertEqual(len(analysis_files), 1)
        self.assertEqual(analysis_files[0]['filename'], 'test_analysis.json')
        self.assertEqual(analysis_files[0]['original_image'], 'test.jpg')
        self.assertEqual(analysis_files[0]['status'], 'complete')
        self.assertIn('thumbnail', analysis_files[0])
    
    def test_get_config(self):
        """Test configuration loading"""
        with patch.dict(os.environ, {
            'API_BASE_URL': 'http://test:8000',
            'CLIP_MODEL_NAME': 'test-model',
            'ENABLE_CLIP_ANALYSIS': 'True',
            'ENABLE_LLM_ANALYSIS': 'False',
            'IMAGE_DIRECTORY': 'TestImages',
            'OUTPUT_DIRECTORY': 'TestOutput',
            'CLIP_MODES': 'best,fast',
            'PROMPT_CHOICES': 'P1,P2',
            'LOGGING_LEVEL': 'DEBUG',
            'RETRY_LIMIT': '10',
            'TIMEOUT': '120'
        }):
            config = get_config()
            
            self.assertEqual(config['API_BASE_URL'], 'http://test:8000')
            self.assertEqual(config['CLIP_MODEL_NAME'], 'test-model')
            self.assertTrue(config['ENABLE_CLIP_ANALYSIS'])
            self.assertFalse(config['ENABLE_LLM_ANALYSIS'])
            self.assertEqual(config['IMAGE_DIRECTORY'], 'TestImages')
            self.assertEqual(config['OUTPUT_DIRECTORY'], 'TestOutput')
            self.assertEqual(config['CLIP_MODES'], ['best', 'fast'])
            self.assertEqual(config['PROMPT_CHOICES'], ['P1', 'P2'])
            self.assertEqual(config['LOGGING_LEVEL'], 'DEBUG')
            self.assertEqual(config['RETRY_LIMIT'], 10)
            self.assertEqual(config['TIMEOUT'], 120)
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('src.viewers.web_interface.load_dotenv')
    def test_update_config_success(self, mock_load_dotenv, mock_file):
        """Test successful configuration update"""
        mock_file.return_value.__enter__.return_value.readlines.return_value = [
            "API_BASE_URL=http://old:8000\n",
            "ENABLE_CLIP_ANALYSIS=True\n"
        ]
        
        config_data = {
            'API_BASE_URL': 'http://new:9000',
            'ENABLE_CLIP_ANALYSIS': False,
            'NEW_SETTING': 'test_value'
        }
        
        result = update_config(config_data)
        
        self.assertTrue(result)
        mock_file.assert_called()
        mock_load_dotenv.assert_called()
    
    @patch('builtins.open', side_effect=Exception("File error"))
    def test_update_config_failure(self, mock_file):
        """Test configuration update failure"""
        config_data = {'API_BASE_URL': 'http://test:8000'}
        
        result = update_config(config_data)
        
        self.assertFalse(result)
    
    @patch('PIL.Image.open')
    def test_create_thumbnail_success(self, mock_image_open):
        """Test successful thumbnail creation"""
        mock_img = MagicMock()
        mock_img.mode = 'RGB'
        mock_img.thumbnail = MagicMock()
        mock_image_open.return_value.__enter__.return_value = mock_img
        
        result = create_thumbnail("test.jpg")
        
        self.assertIsNotNone(result)
        mock_img.thumbnail.assert_called_once()
    
    @patch('PIL.Image.open', side_effect=Exception("Image error"))
    def test_create_thumbnail_failure(self, mock_image_open):
        """Test thumbnail creation failure"""
        result = create_thumbnail("test.jpg")
        
        self.assertIsNone(result)
    
    def test_get_thumbnail_data_url(self):
        """Test thumbnail data URL generation"""
        with patch('src.viewers.web_interface.create_thumbnail') as mock_create:
            mock_create.return_value = "base64_data"
            
            result = get_thumbnail_data_url("test.jpg")
            
            self.assertEqual(result, "data:image/jpeg;base64,base64_data")
    
    def test_get_thumbnail_data_url_none(self):
        """Test thumbnail data URL with None thumbnail"""
        with patch('src.viewers.web_interface.create_thumbnail') as mock_create:
            mock_create.return_value = None
            
            result = get_thumbnail_data_url("test.jpg")
            
            self.assertIsNone(result)
    
    def test_index_route(self):
        """Test main dashboard route"""
        with patch('src.viewers.web_interface.get_analysis_files') as mock_analyses, \
             patch('src.viewers.web_interface.get_image_files') as mock_images:
            
            mock_analyses.return_value = []
            mock_images.return_value = []
            
            response = self.app.get('/')
            
            self.assertEqual(response.status_code, 200)
    
    def test_upload_route_get(self):
        """Test upload page route"""
        response = self.app.get('/upload')
        
        self.assertEqual(response.status_code, 200)
    
    def test_images_route(self):
        """Test images page route"""
        with patch('src.viewers.web_interface.get_image_files') as mock_images:
            mock_images.return_value = []
            
            response = self.app.get('/images')
            
            self.assertEqual(response.status_code, 200)
    
    def test_results_route(self):
        """Test results page route"""
        with patch('src.viewers.web_interface.get_analysis_files') as mock_analyses:
            mock_analyses.return_value = []
            
            response = self.app.get('/results')
            
            self.assertEqual(response.status_code, 200)
    
    def test_config_route_get(self):
        """Test config page route"""
        with patch('src.viewers.web_interface.get_config') as mock_config:
            mock_config.return_value = {}
            
            response = self.app.get('/config')
            
            self.assertEqual(response.status_code, 200)
    
    def test_config_route_post_success(self):
        """Test config update route success"""
        with patch('src.viewers.web_interface.update_config') as mock_update:
            mock_update.return_value = True
            
            response = self.app.post('/config', 
                                   json={'API_BASE_URL': 'http://test:8000'},
                                   content_type='application/json')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data['status'], 'success')
    
    def test_config_route_post_failure(self):
        """Test config update route failure"""
        with patch('src.viewers.web_interface.update_config') as mock_update:
            mock_update.return_value = False
            
            response = self.app.post('/config', 
                                   json={'API_BASE_URL': 'http://test:8000'},
                                   content_type='application/json')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data['status'], 'error')
    
    def test_process_route_get(self):
        """Test process page route"""
        response = self.app.get('/process')
        
        self.assertEqual(response.status_code, 200)
    
    def test_status_route(self):
        """Test status route"""
        response = self.app.get('/status')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('status', data)
    
    @patch('src.viewers.web_interface.DirectoryProcessor')
    def test_process_images_async_success(self, mock_processor):
        """Test successful background processing"""
        mock_instance = MagicMock()
        mock_processor.return_value = mock_instance
        
        process_images_async()
        
        mock_processor.assert_called_once()
        mock_instance.process_directory.assert_called_once()
    
    @patch('src.viewers.web_interface.DirectoryProcessor', side_effect=Exception("Processing error"))
    def test_process_images_async_failure(self, mock_processor):
        """Test background processing failure"""
        process_images_async()
        
        # The function should handle the exception and not raise it
        mock_processor.assert_called_once()

if __name__ == '__main__':
    unittest.main() 