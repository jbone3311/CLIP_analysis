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
    
    @patch('builtins.print')
    def test_show_help(self, mock_print):
        """Test help display"""
        show_help()
        
        # Check that help information was printed
        mock_print.assert_called()
        calls = [call[0][0] for call in mock_print.call_args_list]
        help_text = ' '.join(calls)
        
        self.assertIn("Image Analysis with CLIP and LLM", help_text)
        self.assertIn("process", help_text)
        self.assertIn("config", help_text)
        self.assertIn("view", help_text)
        self.assertIn("install", help_text)
    
    def test_main_process_command(self, mock_process):
        """Test main function with process command"""
        sys.argv = ['main.py', 'process']
        
        with patch('builtins.print') as mock_print:
            main()
        
        mock_print.assert_called()
    
    def test_main_config_command(self, mock_config):
        """Test main function with config command"""
        sys.argv = ['main.py', 'config']
        
        with patch('builtins.print') as mock_print:
            main()
        
        mock_print.assert_called()
    
    def test_main_view_command(self, mock_view):
        """Test main function with view command"""
        sys.argv = ['main.py', 'view', '--list']
        
        with patch('builtins.print') as mock_print:
            main()
        
        mock_print.assert_called()
    
    def test_main_install_command(self, mock_install):
        """Test main function with install command"""
        sys.argv = ['main.py', 'install']
        
        with patch('builtins.print') as mock_print:
            main()
        
        mock_print.assert_called()
    
    @patch('main.show_help')
    def test_main_help_command(self, mock_help):
        """Test main function with help command"""
        sys.argv = ['main.py', 'help']
        
        main()
        
        mock_help.assert_called_once()
    
    @patch('main.show_help')
    def test_main_no_arguments(self, mock_help):
        """Test main function with no arguments"""
        sys.argv = ['main.py']
        
        main()
        
        mock_help.assert_called_once()
    
    @patch('builtins.print')
    def test_main_unknown_command(self, mock_print):
        """Test main function with unknown command"""
        sys.argv = ['main.py', 'unknown']
        
        main()
        
        mock_print.assert_called()
        calls = [call[0][0] for call in mock_print.call_args_list]
        error_text = ' '.join(calls)
        
        self.assertIn("Unknown command", error_text)
        self.assertIn("help", error_text)

if __name__ == '__main__':
    unittest.main() 