"""
Unit tests for ImageService
"""

import unittest
import tempfile
import os
from unittest.mock import patch, MagicMock
from src.services.image_service import ImageService


class TestImageService(unittest.TestCase):
    """Test cases for ImageService"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.upload_folder = os.path.join(self.temp_dir, 'upload')
        self.allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        
        os.makedirs(self.upload_folder, exist_ok=True)
        
        self.service = ImageService(self.upload_folder, self.allowed_extensions)
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_get_image_files_empty(self):
        """Test getting image files when directory is empty"""
        files = self.service.get_image_files()
        self.assertEqual(files, [])
    
    def test_get_image_files_with_data(self):
        """Test getting image files with valid data"""
        # Create a test image file
        test_file = os.path.join(self.upload_folder, 'test.jpg')
        with open(test_file, 'w') as f:
            f.write('test image data')
        
        files = self.service.get_image_files()
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0]['filename'], 'test.jpg')
        self.assertEqual(files[0]['path'], 'test.jpg')
        self.assertIn('size', files[0])
        self.assertIn('modified', files[0])
    
    def test_save_uploaded_file_success(self):
        """Test saving uploaded file successfully"""
        mock_file = MagicMock()
        mock_file.filename = 'test.jpg'
        mock_file.save = MagicMock()
        
        result = self.service.save_uploaded_file(mock_file)
        self.assertEqual(result, 'test.jpg')
        mock_file.save.assert_called_once()
    
    def test_save_uploaded_file_invalid_extension(self):
        """Test saving uploaded file with invalid extension"""
        mock_file = MagicMock()
        mock_file.filename = 'test.txt'
        
        result = self.service.save_uploaded_file(mock_file)
        self.assertIsNone(result)
    
    def test_save_uploaded_file_no_filename(self):
        """Test saving uploaded file with no filename"""
        mock_file = MagicMock()
        mock_file.filename = ''
        
        result = self.service.save_uploaded_file(mock_file)
        self.assertIsNone(result)
    
    def test_save_uploaded_file_none(self):
        """Test saving uploaded file when file is None"""
        result = self.service.save_uploaded_file(None)
        self.assertIsNone(result)
    
    def test_get_image_stats_empty(self):
        """Test getting image stats when no images"""
        stats = self.service.get_image_stats()
        self.assertEqual(stats['total_images'], 0)
        self.assertEqual(stats['total_size'], 0)
        self.assertEqual(stats['average_size'], 0)
    
    def test_get_image_stats_with_data(self):
        """Test getting image stats with images"""
        # Create test image files
        for i in range(2):
            test_file = os.path.join(self.upload_folder, f'test{i}.jpg')
            with open(test_file, 'w') as f:
                f.write('test image data' * 10)  # Make it larger
        
        stats = self.service.get_image_stats()
        self.assertEqual(stats['total_images'], 2)
        self.assertGreater(stats['total_size'], 0)
        self.assertGreater(stats['average_size'], 0)
    
    def test_allowed_file_valid(self):
        """Test allowed file with valid extension"""
        self.assertTrue(self.service._allowed_file('test.jpg'))
        self.assertTrue(self.service._allowed_file('test.PNG'))
        self.assertTrue(self.service._allowed_file('test.jpeg'))
        self.assertTrue(self.service._allowed_file('test.gif'))
    
    def test_allowed_file_invalid(self):
        """Test allowed file with invalid extension"""
        self.assertFalse(self.service._allowed_file('test.txt'))
        self.assertFalse(self.service._allowed_file('test.pdf'))
        self.assertFalse(self.service._allowed_file('test'))
        self.assertFalse(self.service._allowed_file(''))
    
    @patch('src.services.image_service.Image.open')
    @patch('os.path.exists', return_value=True)
    @patch('os.path.getsize', return_value=1024)
    def test_create_thumbnail_success(self, mock_getsize, mock_exists, mock_image):
        """Test creating thumbnail successfully"""
        # Create a proper mock image with context manager support
        mock_img = MagicMock()
        mock_img.mode = 'RGB'
        mock_img.verify = MagicMock()
        mock_img.convert = MagicMock(return_value=mock_img)
        mock_img.thumbnail = MagicMock()
        mock_img.save = MagicMock()
        
        # Mock the context manager behavior
        mock_context = MagicMock()
        mock_context.__enter__ = MagicMock(return_value=mock_img)
        mock_context.__exit__ = MagicMock(return_value=False)
        mock_image.return_value = mock_context
        
        # Mock BytesIO for base64 encoding
        with patch('io.BytesIO') as mock_bytesio:
            mock_buffer = MagicMock()
            mock_buffer.getvalue.return_value = b'fake_image_data'
            mock_buffer.seek = MagicMock()
            mock_bytesio.return_value = mock_buffer
            
            result = self.service._create_thumbnail('test.jpg')
            self.assertIsNotNone(result)
            self.assertIsInstance(result, str)  # Should be base64 string
    
    @patch('src.services.image_service.Image.open')
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