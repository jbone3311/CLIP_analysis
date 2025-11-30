"""
Unit tests for results viewer module
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
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.viewers.results_viewer import (
    load_analysis_file,
    find_analysis_files,
    generate_summary,
    export_results,
    main
)

class TestResultsViewer(unittest.TestCase):
    """Test cases for results viewer functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_output_dir = os.path.join(self.temp_dir, "Output")
        os.makedirs(self.test_output_dir)
        
        # Create test analysis files
        self.test_analysis_data = {
            "file_info": {
                "filename": "test_image.jpg",
                "directory": "Images",
                "date_added": "2024-01-01T12:00:00",
                "date_processed": "2024-01-01T12:01:30",
                "md5": "abc123",
                "file_size": 1024000
            },
            "analysis": {
                "clip": {
                    "best": {"prompt": "A beautiful landscape"},
                    "fast": {"prompt": "Nature scene"}
                },
                "llm": [
                    {
                        "prompt": "P1",
                        "status": "success",
                        "result": {
                            "choices": [
                                {
                                    "message": {
                                        "content": "Detailed description"
                                    }
                                }
                            ],
                            "usage": {
                                "prompt_tokens": 10,
                                "completion_tokens": 20,
                                "total_tokens": 30
                            }
                        }
                    },
                    {
                        "prompt": "P2",
                        "status": "success",
                        "result": {
                            "choices": [
                                {
                                    "message": {
                                        "content": "Art critique"
                                    }
                                }
                            ],
                            "usage": {
                                "prompt_tokens": 15,
                                "completion_tokens": 25,
                                "total_tokens": 40
                            }
                        }
                    }
                ],
                "metadata": {
                    "width": 1920,
                    "height": 1080,
                    "format": "JPEG",
                    "color_mode": "RGB"
                }
            },
            "processing_info": {
                "config_used": {},
                "processing_time": 45.2,
                "status": "complete",
                "errors": []
            }
        }
        
        # Create test analysis file
        self.test_file_path = os.path.join(self.test_output_dir, "test_image_analysis.json")
        with open(self.test_file_path, 'w') as f:
            json.dump(self.test_analysis_data, f)
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_load_analysis_file_success(self):
        """Test successful loading of analysis file"""
        result = load_analysis_file(self.test_file_path)
        
        self.assertEqual(result["file_info"]["filename"], "test_image.jpg")
        self.assertIn("clip", result["analysis"])
        self.assertIn("llm", result["analysis"])
        self.assertIn("metadata", result["analysis"])
    
    def test_load_analysis_file_not_found(self):
        """Test loading non-existent analysis file"""
        result = load_analysis_file("nonexistent_file.json")
        
        self.assertIsNone(result)
    
    def test_load_analysis_file_invalid_json(self):
        """Test loading file with invalid JSON"""
        invalid_file = os.path.join(self.test_output_dir, "invalid.json")
        with open(invalid_file, 'w') as f:
            f.write("invalid json content")
        
        result = load_analysis_file(invalid_file)
        self.assertIsNone(result)
    
    def test_find_analysis_files(self):
        """Test finding analysis files"""
        # Create additional test files
        test_file2 = os.path.join(self.test_output_dir, "image2_analysis.json")
        test_file3 = os.path.join(self.test_output_dir, "not_analysis.txt")
        
        with open(test_file2, 'w') as f:
            json.dump(self.test_analysis_data, f)
        with open(test_file3, 'w') as f:
            f.write("not a json file")
        
        files = find_analysis_files(self.test_output_dir)
        
        self.assertEqual(len(files), 2)
        # Check that the files exist in the list (they will be full paths)
        file_names = [os.path.basename(f) for f in files]
        self.assertIn("test_image_analysis.json", file_names)
        self.assertIn("image2_analysis.json", file_names)
        self.assertNotIn("not_analysis.txt", files)
    
    def test_find_analysis_files_empty_directory(self):
        """Test finding files in empty directory"""
        empty_dir = os.path.join(self.temp_dir, "empty")
        os.makedirs(empty_dir)
        
        files = find_analysis_files(empty_dir)
        self.assertEqual(len(files), 0)
    
    def test_generate_summary(self):
        """Test generating summary from analysis files"""
        # Create multiple test files
        test_file2 = os.path.join(self.test_output_dir, "image2_analysis.json")
        test_data2 = self.test_analysis_data.copy()
        test_data2["file_info"]["filename"] = "image2.jpg"
        
        with open(test_file2, 'w') as f:
            json.dump(test_data2, f)
        
        # The function doesn't return anything, it just prints
        # So we just test that it doesn't raise an exception
        try:
            generate_summary(self.test_output_dir)
        except Exception as e:
            self.fail(f"generate_summary raised an exception: {e}")
    
    def test_export_results(self):
        """Test exporting results"""
        output_file = os.path.join(self.temp_dir, "export.json")
        
        # Mock the find_analysis_files function to return our test file
        with patch('src.viewers.results_viewer.find_analysis_files') as mock_find:
            mock_find.return_value = [self.test_file_path]
            
            export_results(self.test_output_dir, output_file, "json")
            
            # export_results doesn't return a value, check file was created instead
            self.assertTrue(os.path.exists(output_file))
            self.assertTrue(os.path.exists(output_file))
            
            # Check JSON content - export_results returns a list of results
            with open(output_file, 'r') as f:
                data = json.load(f)
                self.assertIsInstance(data, list)
                self.assertGreater(len(data), 0)
                # Check structure of first result
                if data:
                    self.assertIn("file_info", data[0])
                    self.assertIn("analysis", data[0])
    
    @patch('src.viewers.results_viewer.find_analysis_files')
    @patch('src.viewers.results_viewer.load_analysis_file')
    def test_main_list_command(self, mock_load, mock_list):
        """Test main function with list command"""
        mock_list.return_value = ["test1.json", "test2.json"]
        mock_load.return_value = self.test_analysis_data
        
        with patch('sys.argv', ['results_viewer.py', '--list']):
            with patch('builtins.print') as mock_print:
                main()
        
        mock_list.assert_called_once()
        mock_print.assert_called()
    
    @patch('src.viewers.results_viewer.load_analysis_file')
    def test_main_file_command(self, mock_load):
        """Test main function with file command"""
        mock_load.return_value = self.test_analysis_data
        
        with patch('sys.argv', ['results_viewer.py', '--file', self.test_file_path]):
            with patch('builtins.print') as mock_print:
                main()
        
        mock_load.assert_called_once_with(self.test_file_path)
        mock_print.assert_called()
    
    @patch('src.viewers.results_viewer.generate_summary')
    def test_main_summary_command(self, mock_summary):
        """Test main function with summary command"""
        # The function doesn't return anything, so we don't need to set return_value
        
        with patch('sys.argv', ['results_viewer.py', '--summary', '--directory', self.test_output_dir]):
            main()
        
        mock_summary.assert_called_once()

if __name__ == '__main__':
    unittest.main() 