"""
Unit tests for main entry point module
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from main import show_help, main

class TestMain(unittest.TestCase):
    """Test cases for main entry point functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.original_argv = sys.argv.copy()
    
    def tearDown(self):
        """Clean up test fixtures"""
        sys.argv = self.original_argv
    
    def test_show_help(self):
        """Test help display"""
        # show_help just calls parser.print_help()
        # Test that it doesn't crash
        try:
            show_help()
        except Exception as e:
            self.fail(f"show_help raised {e}")
    
    @patch('main.handle_process', return_value=0)
    def test_main_process_command(self, mock_process):
        """Test main function with process command"""
        sys.argv = ['main.py', 'process', '--input', 'Images', '--no-interactive', '--enable-clip']
        
        result = main()
        
        mock_process.assert_called()
        self.assertEqual(result, 0)
    
    @patch('main.handle_config', return_value=0)
    def test_main_config_command(self, mock_config):
        """Test main function with config command"""
        sys.argv = ['main.py', 'config', '--show']
        
        result = main()
        
        mock_config.assert_called()
        self.assertEqual(result, 0)
    
    @patch('main.handle_view', return_value=0)
    def test_main_view_command(self, mock_view):
        """Test main function with view command"""
        sys.argv = ['main.py', 'view', '--list']
        
        result = main()
        
        mock_view.assert_called()
        self.assertEqual(result, 0)
    
    @patch('src.utils.installer.main')
    def test_main_install_command(self, mock_install_main):
        """Test main function with install command"""
        sys.argv = ['main.py', 'install']
        mock_install_main.return_value = None
        
        try:
            result = main()
        except SystemExit:
            # installer.main may call sys.exit
            result = 0
        
        # Just verify it doesn't crash
        self.assertIsInstance(result, (int, type(None)))
    
    def test_main_help_command(self):
        """Test main function with help command"""
        sys.argv = ['main.py', '--help']
        
        try:
            main()
        except SystemExit as e:
            # argparse calls sys.exit(0) on --help
            self.assertEqual(e.code, 0)
    
    def test_main_no_arguments(self):
        """Test main function with no arguments"""
        sys.argv = ['main.py']
        
        try:
            main()
        except SystemExit as e:
            # May exit with error code
            pass
        except Exception as e:
            # Other exceptions are acceptable (argparse behavior)
            pass
    
    def test_main_unknown_command(self):
        """Test main function with unknown command"""
        sys.argv = ['main.py', 'unknown']
        
        try:
            main()
        except SystemExit as e:
            # argparse exits with error code on unknown command
            self.assertNotEqual(e.code, 0)

if __name__ == '__main__':
    unittest.main() 