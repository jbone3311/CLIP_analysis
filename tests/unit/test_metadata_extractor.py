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
        self.test_image_path = "test_image.jpg"
    
    @patch('src.analyzers.metadata_extractor.Image.open')
    def test_extract_metadata_success(self, mock_image_open):
        """Test successful metadata extraction"""
        # Mock PIL Image object
        mock_image = MagicMock()
        mock_image.size = (1920, 1080)
        mock_image.format = "JPEG"
        mock_image.mode = "RGB"
        mock_image.info = {"dpi": (72, 72)}
        mock_image_open.return_value = mock_image
        
        # Mock os.path.getsize
        with patch('os.path.getsize', return_value=1024000):
            result = extract_metadata(self.test_image_path)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["width"], 1920)
        self.assertEqual(result["height"], 1080)
        self.assertEqual(result["format"], "JPEG")
        self.assertEqual(result["color_mode"], "RGB")
        self.assertEqual(result["file_size"], 1024000)
        mock_image_open.assert_called_once_with(self.test_image_path)
    
    @patch('src.analyzers.metadata_extractor.Image.open')
    def test_extract_metadata_image_error(self, mock_image_open):
        """Test metadata extraction with image opening error"""
        # Mock image opening error
        mock_image_open.side_effect = Exception("Cannot open image")
        
        result = extract_metadata(self.test_image_path)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["error"], "Cannot open image")
        self.assertNotIn("width", result)
        self.assertNotIn("height", result)
    
    def test_extract_metadata_file_not_found(self):
        """Test metadata extraction with non-existent file"""
        result = extract_metadata("nonexistent_image.jpg")
        
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("not found", result["error"])
    
    @patch('src.analyzers.metadata_extractor.extract_metadata')
    def test_process_image_file_success(self, mock_extract):
        """Test process_image_file function with success"""
        # Mock successful metadata extraction
        mock_extract.return_value = {
            "width": 1920,
            "height": 1080,
            "format": "JPEG",
            "color_mode": "RGB",
            "file_size": 1024000
        }
        
        result = process_image_file(self.test_image_path)
        
        self.assertEqual(result["status"], "success")
        self.assertIn("metadata", result)
        self.assertEqual(result["metadata"]["width"], 1920)
        mock_extract.assert_called_once_with(self.test_image_path)
    
    @patch('src.analyzers.metadata_extractor.extract_metadata')
    def test_process_image_file_error(self, mock_extract):
        """Test process_image_file function with error"""
        # Mock metadata extraction error
        mock_extract.return_value = {"error": "Test error"}
        
        result = process_image_file(self.test_image_path)
        
        self.assertEqual(result["status"], "error")
        self.assertIn("Test error", result["message"])
        mock_extract.assert_called_once_with(self.test_image_path)
    
    @patch('src.analyzers.metadata_extractor.Image.open')
    def test_extract_metadata_with_different_formats(self, mock_image_open):
        """Test metadata extraction with different image formats"""
        test_cases = [
            ({"size": (800, 600), "format": "PNG", "mode": "RGBA"}, "PNG"),
            ({"size": (1200, 800), "format": "GIF", "mode": "P"}, "GIF"),
            ({"size": (1600, 900), "format": "BMP", "mode": "RGB"}, "BMP"),
        ]
        
        for image_props, expected_format in test_cases:
            with self.subTest(format=expected_format):
                # Mock PIL Image object
                mock_image = MagicMock()
                mock_image.size = image_props["size"]
                mock_image.format = image_props["format"]
                mock_image.mode = image_props["mode"]
                mock_image.info = {}
                mock_image_open.return_value = mock_image
                
                with patch('os.path.getsize', return_value=500000):
                    result = extract_metadata(self.test_image_path)
                
                self.assertEqual(result["format"], expected_format)
                self.assertEqual(result["width"], image_props["size"][0])
                self.assertEqual(result["height"], image_props["size"][1])
                self.assertEqual(result["color_mode"], image_props["mode"])

if __name__ == '__main__':
    unittest.main() 