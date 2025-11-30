"""
Unit tests for metadata extractor module
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.analyzers.metadata_extractor import extract_metadata, process_image_file

class TestMetadataExtractor(unittest.TestCase):
    """Test cases for metadata extractor functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        import tempfile
        import shutil
        
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp()
        self.test_image_path = os.path.join(self.temp_dir, "test_image.jpg")
        
        # Create a dummy image file
        with open(self.test_image_path, 'wb') as f:
            f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9')
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @patch('src.analyzers.metadata_extractor.Image.open')
    @patch('src.analyzers.metadata_extractor.resize_image')
    @patch('src.analyzers.metadata_extractor.generate_thumbnail')
    @patch('src.analyzers.metadata_extractor.encode_image')
    @patch('src.analyzers.metadata_extractor.compute_hashes')
    def test_extract_metadata_success(self, mock_hashes, mock_encode, mock_thumb, mock_resize, mock_image_open):
        """Test successful metadata extraction"""
        # Mock PIL Image object with context manager support
        mock_image = MagicMock()
        mock_image.size = (1920, 1080)
        mock_image.format = "JPEG"
        mock_image.mode = "RGB"
        mock_image.info = {"dpi": (72, 72)}
        mock_image.__enter__ = MagicMock(return_value=mock_image)
        mock_image.__exit__ = MagicMock(return_value=False)
        mock_image_open.return_value = mock_image
        
        # Mock resize to return same image
        mock_resize.return_value = mock_image
        mock_thumb.return_value = mock_image
        mock_encode.return_value = "base64_encoded_thumbnail"
        mock_hashes.return_value = {"average_hash": "test", "perceptual_hash": "test", "difference_hash": "test"}
        
        # Mock os.path.getsize and other functions
        with patch('os.path.getsize', return_value=1024000), \
             patch('os.path.getmtime', return_value=1000000), \
             patch('os.path.getctime', return_value=1000000), \
             patch('os.path.basename', return_value='test_image.jpg'):
            result = extract_metadata(self.test_image_path)
        
        self.assertIsInstance(result, dict)
        # Check that metadata was extracted (may have additional fields)
        self.assertIn("width", result)
        self.assertIn("height", result)
        self.assertEqual(result["width"], 1920)
        self.assertEqual(result["height"], 1080)
        self.assertIn("format", result)
        self.assertEqual(result["format"], "JPEG")
        self.assertIn("color_mode", result)
        self.assertEqual(result["color_mode"], "RGB")
        self.assertIn("file_size", result)
        self.assertEqual(result["file_size"], 1024000)
        mock_image_open.assert_called_once_with(self.test_image_path)
    
    @patch('src.analyzers.metadata_extractor.Image.open')
    def test_extract_metadata_image_error(self, mock_image_open):
        """Test metadata extraction with image opening error"""
        # Mock image opening error
        mock_image_open.side_effect = Exception("Cannot open image")
        
        result = extract_metadata(self.test_image_path)
        
        # Function returns empty dict on error (error is logged, not returned)
        self.assertIsInstance(result, dict)
        self.assertNotIn("width", result)
        self.assertNotIn("height", result)
        # May have filename and dates from before the error
        if result:
            self.assertIn("filename", result)
    
    def test_extract_metadata_file_not_found(self):
        """Test metadata extraction with non-existent file"""
        # The function calls os.path.getmtime() before the try block
        # The @handle_errors decorator will retry and then raise FileNotFoundError
        # after max retries, so we expect the exception to be raised
        with self.assertRaises(FileNotFoundError):
            extract_metadata("nonexistent_image.jpg")
    
    @patch('src.analyzers.metadata_extractor.extract_metadata')
    @patch('src.analyzers.metadata_extractor.save_metadata_to_json')
    def test_process_image_file_success(self, mock_save, mock_extract):
        """Test process_image_file function with success"""
        # Mock successful metadata extraction
        mock_extract.return_value = {
            "width": 1920,
            "height": 1080,
            "format": "JPEG",
            "color_mode": "RGB",
            "file_size": 1024000
        }
        
        # Create output directory
        output_dir = os.path.join(self.temp_dir, "test_output")
        os.makedirs(output_dir, exist_ok=True)
        
        process_image_file(self.test_image_path, output_dir)
        
        mock_extract.assert_called_once_with(self.test_image_path)
        mock_save.assert_called_once()
    
    @patch('src.analyzers.metadata_extractor.extract_metadata')
    @patch('src.analyzers.metadata_extractor.save_metadata_to_json')
    def test_process_image_file_error(self, mock_save, mock_extract):
        """Test process_image_file function with error"""
        # Mock metadata extraction error
        mock_extract.return_value = {"error": "Test error"}
        
        # Create output directory
        output_dir = os.path.join(self.temp_dir, "test_output")
        os.makedirs(output_dir, exist_ok=True)
        
        process_image_file(self.test_image_path, output_dir)
        
        mock_extract.assert_called_once_with(self.test_image_path)
        # Should still try to save even with error
        mock_save.assert_called_once()
    
    @patch('src.analyzers.metadata_extractor.Image.open')
    @patch('src.analyzers.metadata_extractor.resize_image')
    @patch('src.analyzers.metadata_extractor.generate_thumbnail')
    @patch('src.analyzers.metadata_extractor.encode_image')
    @patch('src.analyzers.metadata_extractor.compute_hashes')
    def test_extract_metadata_with_different_formats(self, mock_hashes, mock_encode, mock_thumb, mock_resize, mock_image_open):
        """Test metadata extraction with different image formats"""
        test_cases = [
            ({"size": (800, 600), "format": "PNG", "mode": "RGBA"}, "PNG"),
            ({"size": (1200, 800), "format": "GIF", "mode": "P"}, "GIF"),
            ({"size": (1600, 900), "format": "BMP", "mode": "RGB"}, "BMP"),
        ]
        
        mock_hashes.return_value = {"average_hash": "test", "perceptual_hash": "test", "difference_hash": "test"}
        mock_encode.return_value = "base64_encoded_thumbnail"
        
        for image_props, expected_format in test_cases:
            with self.subTest(format=expected_format):
                # Mock PIL Image object with context manager
                mock_image = MagicMock()
                mock_image.size = image_props["size"]
                mock_image.format = image_props["format"]
                mock_image.mode = image_props["mode"]
                mock_image.info = {}
                mock_image.__enter__ = MagicMock(return_value=mock_image)
                mock_image.__exit__ = MagicMock(return_value=False)
                mock_image_open.return_value = mock_image
                mock_resize.return_value = mock_image
                mock_thumb.return_value = mock_image
                
                with patch('os.path.getsize', return_value=500000), \
                     patch('os.path.getmtime', return_value=1000000), \
                     patch('os.path.getctime', return_value=1000000), \
                     patch('os.path.basename', return_value='test_image.jpg'):
                    result = extract_metadata(self.test_image_path)
                
                self.assertIn("format", result)
                self.assertEqual(result["format"], expected_format)
                self.assertEqual(result["width"], image_props["size"][0])
                self.assertEqual(result["height"], image_props["size"][1])
                self.assertEqual(result["color_mode"], image_props["mode"])

if __name__ == '__main__':
    unittest.main() 