"""
Unit tests for installer module
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.utils.installer import (
    check_python_version,
    install_dependencies,
    create_directories,
    main
)

class TestInstaller(unittest.TestCase):
    """Test cases for installer functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_check_python_version_success(self):
        """Test successful Python version check"""
        result = check_python_version()
        self.assertTrue(result)
    
    @patch('sys.version_info', (3, 6, 0))
    def test_check_python_version_too_old(self):
        """Test Python version check with old version"""
        result = check_python_version()
        self.assertFalse(result)
    
    @patch('src.utils.installer.subprocess.run')
    def test_install_dependencies_success(self, mock_run):
        """Test successful dependency installation"""
        mock_run.return_value = MagicMock(returncode=0)
        
        result = install_dependencies()
        self.assertTrue(result)
        mock_run.assert_called_once()
    
    @patch('src.utils.installer.subprocess.run')
    def test_install_dependencies_failure(self, mock_run):
        """Test failed dependency installation"""
        mock_run.return_value = MagicMock(returncode=1)
        
        result = install_dependencies()
        self.assertFalse(result)
    
    def test_create_directories(self):
        """Test directory creation"""
        test_dirs = [
            os.path.join(self.temp_dir, "Images"),
            os.path.join(self.temp_dir, "Output"),
            os.path.join(self.temp_dir, "config")
        ]
        
        result = create_directories(test_dirs)
        self.assertTrue(result)
        
        # Check that directories were created
        for dir_path in test_dirs:
            self.assertTrue(os.path.exists(dir_path))
            self.assertTrue(os.path.isdir(dir_path))
    
    def test_create_directories_existing(self):
        """Test directory creation with existing directories"""
        # Create one directory beforehand
        existing_dir = os.path.join(self.temp_dir, "Images")
        os.makedirs(existing_dir)
        
        test_dirs = [
            existing_dir,
            os.path.join(self.temp_dir, "Output")
        ]
        
        result = create_directories(test_dirs)
        self.assertTrue(result)
        
        # Check that both directories exist
        for dir_path in test_dirs:
            self.assertTrue(os.path.exists(dir_path))
    
    def test_main_success(self, mock_setup):
        """Test successful main function"""
        with patch('builtins.print') as mock_print:
            main()
        
        mock_print.assert_called()
    
    def test_main_success(self, mock_setup):
        """Test successful main function"""
        with patch('builtins.print') as mock_print:
            main()
        
        mock_print.assert_called()
    
    def test_main_failure(self, mock_setup):
        """Test main function with setup failure"""
        with patch('builtins.print') as mock_print:
            main()
        
        mock_print.assert_called()

if __name__ == '__main__':
    unittest.main() 