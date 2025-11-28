"""
Unit tests for directory processor module
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os
import json
import tempfile
import shutil
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.processors.directory_processor import (
    DirectoryProcessor,
    UnifiedAnalysisResult,
    ProgressTracker
)

class TestProgressTracker(unittest.TestCase):
    """Test cases for ProgressTracker class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tracker = ProgressTracker(10)
    
    def test_initialization(self):
        """Test ProgressTracker initialization"""
        self.assertEqual(self.tracker.total_items, 10)
        self.assertEqual(self.tracker.completed, 0)
        self.assertEqual(self.tracker.failed, 0)
        self.assertIsNotNone(self.tracker.start_time)
    
    def test_update_success(self):
        """Test progress update with success"""
        self.tracker.update(success=True)
        self.assertEqual(self.tracker.completed, 1)
        self.assertEqual(self.tracker.failed, 0)
    
    def test_update_failure(self):
        """Test progress update with failure"""
        self.tracker.update(success=False)
        self.assertEqual(self.tracker.completed, 1)
        self.assertEqual(self.tracker.failed, 1)
    
    def test_progress_bar_creation(self):
        """Test progress bar creation"""
        self.tracker.completed = 5
        progress_bar = self.tracker._create_progress_bar(width=10)
        self.assertEqual(len(progress_bar), 12)  # [████████░░] format
        self.assertIn("█", progress_bar)
        self.assertIn("░", progress_bar)

class TestUnifiedAnalysisResult(unittest.TestCase):
    """Test cases for UnifiedAnalysisResult class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_image_path = os.path.join(self.temp_dir, "test_image.jpg")
        
        # Create a test image file
        with open(self.test_image_path, 'w') as f:
            f.write("test image content")
        
        self.config = {
            'ENABLE_CLIP_ANALYSIS': True,
            'ENABLE_LLM_ANALYSIS': True,
            'CLIP_MODES': ['best', 'fast'],
            'llm_models': [{'number': 1, 'title': 'Test Model'}],
            'PROMPT_CHOICES': ['P1', 'P2']
        }
        
        self.result = UnifiedAnalysisResult(self.test_image_path, self.config)
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test UnifiedAnalysisResult initialization"""
        self.assertEqual(self.result.filename, "test_image.jpg")
        self.assertIsNotNone(self.result.md5)
        self.assertIsNotNone(self.result.date_added)
        self.assertIn("file_info", self.result.result)
        self.assertIn("analysis", self.result.result)
        self.assertIn("processing_info", self.result.result)
    
    def test_add_clip_result_success(self):
        """Test adding successful CLIP result"""
        clip_result = {
            "status": "success",
            "prompt": {
                "best": {"prompt": "A beautiful landscape"},
                "fast": {"prompt": "Nature scene"}
            }
        }
        
        self.result.add_clip_result(clip_result)
        
        self.assertIn("best", self.result.result["analysis"]["clip"])
        self.assertIn("fast", self.result.result["analysis"]["clip"])
        self.assertEqual(len(self.result.result["processing_info"]["errors"]), 0)
    
    def test_add_clip_result_error(self):
        """Test adding failed CLIP result"""
        clip_result = {
            "status": "error",
            "message": "CLIP analysis failed"
        }
        
        self.result.add_clip_result(clip_result)
        
        self.assertEqual(len(self.result.result["processing_info"]["errors"]), 1)
        self.assertEqual(self.result.result["processing_info"]["errors"][0]["type"], "clip")
    
    def test_add_llm_result_success(self):
        """Test adding successful LLM result"""
        llm_result = {
            "status": "success",
            "api_responses": {
                "P1": {"content": "Detailed description"},
                "P2": {"content": "Art critique"}
            }
        }
        
        self.result.add_llm_results(llm_result)
        
        self.assertIn("P1", self.result.result["analysis"]["llm"])
        self.assertIn("P2", self.result.result["analysis"]["llm"])
        self.assertEqual(len(self.result.result["processing_info"]["errors"]), 0)
    
    def test_add_llm_result_error(self):
        """Test adding failed LLM result"""
        llm_result = {
            "status": "error",
            "message": "LLM analysis failed"
        }
        
        self.result.add_llm_results(llm_result)
        
        self.assertEqual(len(self.result.result["processing_info"]["errors"]), 1)
        self.assertEqual(self.result.result["processing_info"]["errors"][0]["type"], "llm")
    
    def test_add_metadata(self):
        """Test adding metadata"""
        metadata = {
            "width": 1920,
            "height": 1080,
            "format": "JPEG",
            "color_mode": "RGB"
        }
        
        self.result.add_metadata(metadata)
        
        self.assertEqual(self.result.result["analysis"]["metadata"]["width"], 1920)
        self.assertEqual(self.result.result["analysis"]["metadata"]["height"], 1080)
        self.assertEqual(self.result.result["analysis"]["metadata"]["format"], "JPEG")
    
    def test_mark_complete(self):
        """Test marking analysis as complete"""
        processing_time = 45.2
        self.result.mark_complete(processing_time)
        
        self.assertEqual(self.result.result["processing_info"]["processing_time"], processing_time)
        self.assertEqual(self.result.result["processing_info"]["status"], "complete")
        self.assertIsNotNone(self.result.result["file_info"]["date_processed"])
    
    def test_mark_failed(self):
        """Test marking analysis as failed"""
        error_message = "Processing failed"
        self.result.mark_failed(error_message)
        
        self.assertEqual(self.result.result["processing_info"]["status"], "failed")
        self.assertEqual(len(self.result.result["processing_info"]["errors"]), 1)
        self.assertEqual(self.result.result["processing_info"]["errors"][0]["type"], "general")
    
    def test_save(self):
        """Test saving result to file"""
        output_dir = os.path.join(self.temp_dir, "output")
        os.makedirs(output_dir)
        
        output_path = self.result.save(output_dir)
        
        self.assertTrue(os.path.exists(output_path))
        self.assertTrue(output_path.endswith("test_image_analysis.json"))
        
        # Check saved content
        with open(output_path, 'r') as f:
            saved_data = json.load(f)
            self.assertEqual(saved_data["file_info"]["filename"], "test_image.jpg")

class TestDirectoryProcessor(unittest.TestCase):
    """Test cases for DirectoryProcessor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.image_dir = os.path.join(self.temp_dir, "Images")
        self.output_dir = os.path.join(self.temp_dir, "Output")
        
        os.makedirs(self.image_dir)
        os.makedirs(self.output_dir)
        
        # Create test image files
        test_images = ["image1.jpg", "image2.png", "image3.gif"]
        for img in test_images:
            with open(os.path.join(self.image_dir, img), 'w') as f:
                f.write(f"test content for {img}")
        
        self.config = {
            'CLIP_API_URL': 'http://localhost:7860',
            'API_BASE_URL': 'http://localhost:7860',  # Legacy support
            'CLIP_MODEL_NAME': 'ViT-L-14/openai',
            'ENABLE_CLIP_ANALYSIS': True,
            'ENABLE_LLM_ANALYSIS': True,
            'ENABLE_PARALLEL_PROCESSING': False,
            'ENABLE_METADATA_EXTRACTION': True,
            'IMAGE_DIRECTORY': self.image_dir,
            'OUTPUT_DIRECTORY': self.output_dir,
            'CLIP_MODES': ['best', 'fast'],
            'PROMPT_CHOICES': ['P1', 'P2'],
            'DEBUG': False,
            'FORCE_REPROCESS': False,
            'GENERATE_SUMMARIES': True,
            'llm_models': [{'number': 1, 'title': 'Test Model', 'api_url': 'https://api.test.com', 'api_key': 'test_key', 'model_name': 'test-model'}]
        }
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    @patch('src.processors.directory_processor.analyze_image_with_clip')
    @patch('src.processors.directory_processor.LLMManager')
    @patch('src.processors.directory_processor.extract_metadata')
    def test_initialization(self, mock_metadata, mock_llm, mock_clip):
        """Test DirectoryProcessor initialization"""
        processor = DirectoryProcessor(self.config)
        
        self.assertEqual(processor.config['IMAGE_DIRECTORY'], self.image_dir)
        self.assertEqual(processor.config['OUTPUT_DIRECTORY'], self.output_dir)
        self.assertTrue(processor.config['ENABLE_CLIP_ANALYSIS'])
        self.assertTrue(processor.config['ENABLE_LLM_ANALYSIS'])
    
    @patch('src.processors.directory_processor.analyze_image_with_clip')
    @patch('src.processors.directory_processor.LLMManager')
    @patch('src.processors.directory_processor.extract_metadata')
    def test_find_image_files(self, mock_metadata, mock_llm, mock_clip):
        """Test finding image files"""
        processor = DirectoryProcessor(self.config)
        image_files = processor.find_image_files(self.image_dir)
        
        self.assertEqual(len(image_files), 3)
        self.assertTrue(any("image1.jpg" in f for f in image_files))
        self.assertTrue(any("image2.png" in f for f in image_files))
        self.assertTrue(any("image3.gif" in f for f in image_files))
    
    @patch('src.processors.directory_processor.analyze_image_with_clip')
    @patch('src.processors.directory_processor.LLMManager')
    @patch('src.processors.directory_processor.extract_metadata')
    def test_find_image_files_empty_directory(self, mock_metadata, mock_llm, mock_clip):
        """Test finding image files in empty directory"""
        empty_dir = os.path.join(self.temp_dir, "empty")
        os.makedirs(empty_dir)
        
        processor = DirectoryProcessor(self.config)
        image_files = processor.find_image_files(empty_dir)
        
        self.assertEqual(len(image_files), 0)
    
    @patch('src.processors.directory_processor.analyze_image_with_clip')
    @patch('src.processors.directory_processor.LLMManager')
    @patch('src.processors.directory_processor.extract_metadata')
    @patch('src.processors.directory_processor.compute_file_hash')
    def test_load_existing_analysis(self, mock_hash, mock_metadata, mock_llm, mock_clip):
        """Test loading existing analysis"""
        processor = DirectoryProcessor(self.config)
        
        # Create existing analysis file
        existing_file = os.path.join(self.output_dir, "image1_analysis.json")
        existing_data = {
            "file_info": {
                "filename": "image1.jpg",
                "md5": "test_md5"
            }
        }
        with open(existing_file, 'w') as f:
            json.dump(existing_data, f)
        
        # Mock MD5 computation
        mock_hash.return_value = "test_md5"
        
        result = processor._load_existing_analysis(os.path.join(self.image_dir, "image1.jpg"))
        
        self.assertIsNotNone(result)
        self.assertEqual(result["file_info"]["filename"], "image1.jpg")

if __name__ == '__main__':
    unittest.main() 