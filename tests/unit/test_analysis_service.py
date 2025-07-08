"""
Unit tests for AnalysisService
"""

import unittest
import tempfile
import os
import json
from unittest.mock import patch, MagicMock
from src.services.analysis_service import AnalysisService


class TestAnalysisService(unittest.TestCase):
    """Test cases for AnalysisService"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.output_folder = os.path.join(self.temp_dir, 'output')
        self.upload_folder = os.path.join(self.temp_dir, 'upload')
        
        os.makedirs(self.output_folder, exist_ok=True)
        os.makedirs(self.upload_folder, exist_ok=True)
        
        self.service = AnalysisService(self.output_folder, self.upload_folder)
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_get_analysis_files_empty(self):
        """Test getting analysis files when directory is empty"""
        files = self.service.get_analysis_files()
        self.assertEqual(files, [])
    
    def test_get_analysis_files_with_data(self):
        """Test getting analysis files with valid data"""
        # Create a mock analysis file
        analysis_data = {
            'file_info': {
                'filename': 'test.jpg',
                'directory': self.upload_folder,
                'date_processed': '2023-01-01T12:00:00',
                'file_size': 1024
            },
            'processing_info': {
                'status': 'complete',
                'processing_time': 1.5
            },
            'analysis': {
                'clip': {'best': [{'text': 'test'}]},
                'llm': [{'status': 'success'}],
                'metadata': {'width': 100, 'height': 100}
            }
        }
        
        analysis_file = os.path.join(self.output_folder, 'test_analysis.json')
        with open(analysis_file, 'w') as f:
            json.dump(analysis_data, f)
        
        files = self.service.get_analysis_files()
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0]['filename'], 'test_analysis.json')
        self.assertEqual(files[0]['original_image'], 'test.jpg')
        self.assertEqual(files[0]['status'], 'complete')
        self.assertEqual(files[0]['has_clip'], True)
        self.assertEqual(files[0]['has_llm'], True)
        self.assertEqual(files[0]['has_metadata'], True)
    
    def test_get_analysis_data_success(self):
        """Test getting analysis data successfully"""
        analysis_data = {'test': 'data'}
        analysis_file = os.path.join(self.output_folder, 'test_analysis.json')
        with open(analysis_file, 'w') as f:
            json.dump(analysis_data, f)
        
        result = self.service.get_analysis_data('test_analysis.json')
        self.assertEqual(result, analysis_data)
    
    def test_get_analysis_data_not_found(self):
        """Test getting analysis data when file doesn't exist"""
        result = self.service.get_analysis_data('nonexistent.json')
        self.assertIsNone(result)
    
    def test_get_analysis_data_invalid_json(self):
        """Test getting analysis data with invalid JSON"""
        analysis_file = os.path.join(self.output_folder, 'invalid_analysis.json')
        with open(analysis_file, 'w') as f:
            f.write('invalid json')
        
        result = self.service.get_analysis_data('invalid_analysis.json')
        self.assertIsNone(result)
    
    def test_get_analysis_stats(self):
        """Test getting analysis statistics"""
        # Create mock analysis files
        for i in range(3):
            analysis_data = {
                'file_info': {'filename': f'test{i}.jpg'},
                'processing_info': {
                    'status': 'complete' if i < 2 else 'processing'
                }
            }
            analysis_file = os.path.join(self.output_folder, f'test{i}_analysis.json')
            with open(analysis_file, 'w') as f:
                json.dump(analysis_data, f)
        
        stats = self.service.get_analysis_stats()
        self.assertEqual(stats['total_analyses'], 3)
        self.assertEqual(stats['completed_analyses'], 2)
        self.assertEqual(stats['pending_analyses'], 1)
    
    @patch('src.services.analysis_service.Image.open')
    def test_create_thumbnail_success(self, mock_image):
        """Test creating thumbnail successfully"""
        mock_img = MagicMock()
        mock_img.mode = 'RGB'
        mock_img.thumbnail.return_value = None
        mock_img.save.return_value = None
        mock_image.return_value.__enter__.return_value = mock_img
        
        result = self.service._create_thumbnail('test.jpg')
        self.assertIsNotNone(result)
    
    @patch('src.services.analysis_service.Image.open')
    def test_create_thumbnail_error(self, mock_image):
        """Test creating thumbnail with error"""
        mock_image.side_effect = Exception('Image error')
        
        result = self.service._create_thumbnail('test.jpg')
        self.assertIsNone(result)
    
    def test_get_thumbnail_data_url_success(self):
        """Test getting thumbnail data URL successfully"""
        with patch.object(self.service, '_create_thumbnail') as mock_create:
            mock_create.return_value = 'base64_data'
            
            result = self.service._get_thumbnail_data_url('test.jpg')
            self.assertEqual(result, 'data:image/jpeg;base64,base64_data')
    
    def test_get_thumbnail_data_url_none(self):
        """Test getting thumbnail data URL with None thumbnail"""
        with patch.object(self.service, '_create_thumbnail') as mock_create:
            mock_create.return_value = None
            
            result = self.service._get_thumbnail_data_url('test.jpg')
            self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main() 