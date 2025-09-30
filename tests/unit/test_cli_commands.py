"""
Unit tests for CLI commands
"""

import unittest
import tempfile
import os
import sys
import json
import subprocess
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import argparse

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from main import (
    create_parser, 
    handle_process, 
    handle_web, 
    handle_config, 
    handle_llm_config, 
    handle_view, 
    handle_database,
    handle_wildcard,
    get_default_config
)

class TestCLICommands(unittest.TestCase):
    """Test cases for CLI command functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_images_dir = os.path.join(self.temp_dir, "Images")
        self.test_output_dir = os.path.join(self.temp_dir, "Output")
        
        # Create test directories
        os.makedirs(self.test_images_dir, exist_ok=True)
        os.makedirs(self.test_output_dir, exist_ok=True)
        
        # Create test image files
        for i in range(3):
            with open(os.path.join(self.test_images_dir, f"test_image_{i}.jpg"), 'w') as f:
                f.write(f"test image content {i}")
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_create_parser(self):
        """Test argument parser creation"""
        parser = create_parser()
        
        # Test that all subcommands exist
        subcommands = ['process', 'web', 'config', 'llm-config', 'view', 'database', 'wildcard']
        for cmd in subcommands:
            self.assertIn(cmd, parser._subparsers._group_actions[0].choices)
    
    def test_process_command_basic(self):
        """Test basic process command"""
        args = argparse.Namespace(
            input=self.test_images_dir,
            output=self.test_output_dir,
            api_url='http://localhost:7860',
            clip_model='ViT-L-14/openai',
            clip_modes=['best', 'fast'],
            enable_clip=True,
            disable_clip=False,
            enable_llm=True,
            disable_llm=False,
            enable_metadata=True,
            disable_metadata=False,
            parallel=False,
            force=False,
            debug=False
        )
        
        with patch('main.DirectoryProcessor') as mock_processor:
            mock_instance = MagicMock()
            mock_processor.return_value = mock_instance
            
            result = handle_process(args)
            
            # Should call process_directory
            mock_instance.process_directory.assert_called_once()
            self.assertEqual(result, 0)
    
    def test_process_command_with_errors(self):
        """Test process command with errors"""
        args = argparse.Namespace(
            input=self.test_images_dir,
            output=self.test_output_dir,
            api_url='http://localhost:7860',
            clip_model='ViT-L-14/openai',
            clip_modes=['best', 'fast'],
            enable_clip=True,
            disable_clip=False,
            enable_llm=True,
            disable_llm=False,
            enable_metadata=True,
            disable_metadata=False,
            parallel=False,
            force=False,
            debug=False
        )
        
        with patch('main.DirectoryProcessor') as mock_processor:
            mock_processor.side_effect = Exception("Test error")
            
            result = handle_process(args)
            self.assertEqual(result, 1)
    
    def test_web_command(self):
        """Test web command"""
        args = argparse.Namespace(
            host='127.0.0.1',
            port=8080,
            debug=True
        )
        
        with patch('main.WebInterface') as mock_web_interface:
            mock_instance = MagicMock()
            mock_web_interface.return_value = mock_instance
            
            result = handle_web(args)
            
            # Should call run with correct parameters
            mock_instance.run.assert_called_once_with(
                host='127.0.0.1', 
                port=8080, 
                debug=True
            )
            self.assertEqual(result, 0)
    
    def test_web_command_with_errors(self):
        """Test web command with errors"""
        args = argparse.Namespace(
            host='127.0.0.1',
            port=8080,
            debug=True
        )
        
        with patch('main.WebInterface') as mock_web_interface:
            mock_web_interface.side_effect = Exception("Web interface error")
            
            result = handle_web(args)
            self.assertEqual(result, 1)
    
    def test_config_command_show(self):
        """Test config command with show option"""
        args = argparse.Namespace(
            show=True,
            interactive=False,
            reset=False
        )
        
        with patch('builtins.print') as mock_print:
            result = handle_config(args)
            
            # Should print configuration
            mock_print.assert_called()
            self.assertEqual(result, 0)
    
    def test_config_command_reset(self):
        """Test config command with reset option"""
        args = argparse.Namespace(
            show=False,
            interactive=False,
            reset=True
        )
        
        with patch('builtins.print') as mock_print:
            result = handle_config(args)
            
            # Should print reset message
            mock_print.assert_called()
            self.assertEqual(result, 0)
    
    def test_config_command_interactive(self):
        """Test config command with interactive option"""
        args = argparse.Namespace(
            show=False,
            interactive=True,
            reset=False
        )
        
        with patch('main.config_manager') as mock_config_manager:
            result = handle_config(args)
            
            # Should call config manager main
            mock_config_manager.main.assert_called_once()
            self.assertEqual(result, 0)
    
    def test_llm_config_command_list(self):
        """Test LLM config command with list option"""
        args = argparse.Namespace(
            list=True,
            list_configured=False,
            add_ollama=None,
            add_openai=None,
            remove=None,
            test_ollama=False,
            test_openai=False,
            ollama_url='http://localhost:11434',
            openai_key=None
        )
        
        with patch('main.LLMManager') as mock_llm_manager, \
             patch('main.DatabaseManager') as mock_db_manager, \
             patch('builtins.print') as mock_print:
            
            mock_llm = MagicMock()
            mock_llm_manager.return_value = mock_llm
            mock_llm.get_all_available_models.return_value = [
                {'name': 'gpt-4', 'type': 'openai', 'size': '175B'},
                {'name': 'llama2', 'type': 'ollama', 'size': '7B'}
            ]
            
            result = handle_llm_config(args)
            
            # Should list available models
            mock_print.assert_called()
            self.assertEqual(result, 0)
    
    def test_llm_config_command_list_configured(self):
        """Test LLM config command with list-configured option"""
        args = argparse.Namespace(
            list=False,
            list_configured=True,
            add_ollama=None,
            add_openai=None,
            remove=None,
            test_ollama=False,
            test_openai=False,
            ollama_url='http://localhost:11434',
            openai_key=None
        )
        
        with patch('main.LLMManager') as mock_llm_manager, \
             patch('main.DatabaseManager') as mock_db_manager, \
             patch('builtins.print') as mock_print:
            
            mock_db = MagicMock()
            mock_db_manager.return_value = mock_db
            mock_db.get_llm_models.return_value = [
                {'id': 1, 'name': 'gpt-4', 'type': 'openai'},
                {'id': 2, 'name': 'llama2', 'type': 'ollama'}
            ]
            
            result = handle_llm_config(args)
            
            # Should list configured models
            mock_print.assert_called()
            self.assertEqual(result, 0)
    
    def test_llm_config_command_add_ollama(self):
        """Test LLM config command with add-ollama option"""
        args = argparse.Namespace(
            list=False,
            list_configured=False,
            add_ollama='llama2',
            add_openai=None,
            remove=None,
            test_ollama=False,
            test_openai=False,
            ollama_url='http://localhost:11434',
            openai_key=None
        )
        
        with patch('main.LLMManager') as mock_llm_manager, \
             patch('main.DatabaseManager') as mock_db_manager, \
             patch('builtins.print') as mock_print:
            
            mock_db = MagicMock()
            mock_db_manager.return_value = mock_db
            
            result = handle_llm_config(args)
            
            # Should add Ollama model
            mock_db.insert_llm_model.assert_called_once()
            mock_print.assert_called()
            self.assertEqual(result, 0)
    
    def test_llm_config_command_add_openai(self):
        """Test LLM config command with add-openai option"""
        args = argparse.Namespace(
            list=False,
            list_configured=False,
            add_ollama=None,
            add_openai='gpt-4',
            remove=None,
            test_ollama=False,
            test_openai=False,
            ollama_url='http://localhost:11434',
            openai_key='test_key'
        )
        
        with patch('main.LLMManager') as mock_llm_manager, \
             patch('main.DatabaseManager') as mock_db_manager, \
             patch('builtins.print') as mock_print:
            
            mock_db = MagicMock()
            mock_db_manager.return_value = mock_db
            
            result = handle_llm_config(args)
            
            # Should add OpenAI model
            mock_db.insert_llm_model.assert_called_once()
            mock_print.assert_called()
            self.assertEqual(result, 0)
    
    def test_llm_config_command_add_openai_no_key(self):
        """Test LLM config command with add-openai but no key"""
        args = argparse.Namespace(
            list=False,
            list_configured=False,
            add_ollama=None,
            add_openai='gpt-4',
            remove=None,
            test_ollama=False,
            test_openai=False,
            ollama_url='http://localhost:11434',
            openai_key=None
        )
        
        with patch('main.LLMManager') as mock_llm_manager, \
             patch('main.DatabaseManager') as mock_db_manager, \
             patch('builtins.print') as mock_print:
            
            result = handle_llm_config(args)
            
            # Should fail without API key
            mock_print.assert_called()
            self.assertEqual(result, 1)
    
    def test_llm_config_command_test_ollama(self):
        """Test LLM config command with test-ollama option"""
        args = argparse.Namespace(
            list=False,
            list_configured=False,
            add_ollama=None,
            add_openai=None,
            remove=None,
            test_ollama=True,
            test_openai=False,
            ollama_url='http://localhost:11434',
            openai_key=None
        )
        
        with patch('main.LLMManager') as mock_llm_manager, \
             patch('main.DatabaseManager') as mock_db_manager, \
             patch('builtins.print') as mock_print:
            
            mock_llm = MagicMock()
            mock_llm_manager.return_value = mock_llm
            mock_llm.test_ollama_connection.return_value = True
            
            result = handle_llm_config(args)
            
            # Should test Ollama connection
            mock_llm.test_ollama_connection.assert_called_once()
            mock_print.assert_called()
            self.assertEqual(result, 0)
    
    def test_llm_config_command_test_openai(self):
        """Test LLM config command with test-openai option"""
        args = argparse.Namespace(
            list=False,
            list_configured=False,
            add_ollama=None,
            add_openai=None,
            remove=None,
            test_ollama=False,
            test_openai=True,
            ollama_url='http://localhost:11434',
            openai_key=None
        )
        
        with patch('main.LLMManager') as mock_llm_manager, \
             patch('main.DatabaseManager') as mock_db_manager, \
             patch('builtins.print') as mock_print:
            
            mock_llm = MagicMock()
            mock_llm_manager.return_value = mock_llm
            mock_llm.test_openai_connection.return_value = True
            
            result = handle_llm_config(args)
            
            # Should test OpenAI connection
            mock_llm.test_openai_connection.assert_called_once()
            mock_print.assert_called()
            self.assertEqual(result, 0)
    
    def test_view_command_list(self):
        """Test view command with list option"""
        args = argparse.Namespace(
            list=True,
            file=None,
            summary=False,
            export=None,
            output=None
        )
        
        with patch('main.DatabaseManager') as mock_db_manager, \
             patch('builtins.print') as mock_print:
            
            mock_db = MagicMock()
            mock_db_manager.return_value = mock_db
            mock_db.get_all_results.return_value = [
                {'id': 1, 'filename': 'image1.jpg', 'date_added': '2024-01-01'},
                {'id': 2, 'filename': 'image2.jpg', 'date_added': '2024-01-02'}
            ]
            
            result = handle_view(args)
            
            # Should list results
            mock_print.assert_called()
            self.assertEqual(result, 0)
    
    def test_view_command_file(self):
        """Test view command with file option"""
        test_file = os.path.join(self.test_output_dir, "test_analysis.json")
        with open(test_file, 'w') as f:
            json.dump({'test': 'data'}, f)
        
        args = argparse.Namespace(
            list=False,
            file=test_file,
            summary=False,
            export=None,
            output=None
        )
        
        with patch('builtins.print') as mock_print:
            result = handle_view(args)
            
            # Should view file
            mock_print.assert_called()
            self.assertEqual(result, 0)
    
    def test_view_command_summary(self):
        """Test view command with summary option"""
        args = argparse.Namespace(
            list=False,
            file=None,
            summary=True,
            export=None,
            output=None
        )
        
        with patch('main.DatabaseManager') as mock_db_manager, \
             patch('builtins.print') as mock_print:
            
            mock_db = MagicMock()
            mock_db_manager.return_value = mock_db
            mock_db.get_stats.return_value = {
                'total_results': 10,
                'recent_results': 5,
                'llm_models': 3
            }
            
            result = handle_view(args)
            
            # Should show summary
            mock_print.assert_called()
            self.assertEqual(result, 0)
    
    def test_database_command_stats(self):
        """Test database command with stats option"""
        args = argparse.Namespace(
            stats=True,
            clear=False,
            backup=None,
            restore=None
        )
        
        with patch('main.DatabaseManager') as mock_db_manager, \
             patch('builtins.print') as mock_print:
            
            mock_db = MagicMock()
            mock_db_manager.return_value = mock_db
            mock_db.get_stats.return_value = {
                'total_results': 10,
                'recent_results': 5,
                'llm_models': 3
            }
            
            result = handle_database(args)
            
            # Should show stats
            mock_print.assert_called()
            self.assertEqual(result, 0)
    
    def test_database_command_clear(self):
        """Test database command with clear option"""
        args = argparse.Namespace(
            stats=False,
            clear=True,
            backup=None,
            restore=None
        )
        
        with patch('main.DatabaseManager') as mock_db_manager, \
             patch('builtins.print') as mock_print:
            
            mock_db = MagicMock()
            mock_db_manager.return_value = mock_db
            mock_db.clear_database.return_value = True
            
            result = handle_database(args)
            
            # Should clear database
            mock_db.clear_database.assert_called_once()
            mock_print.assert_called()
            self.assertEqual(result, 0)
    
    def test_database_command_clear_failure(self):
        """Test database command with clear option failure"""
        args = argparse.Namespace(
            stats=False,
            clear=True,
            backup=None,
            restore=None
        )
        
        with patch('main.DatabaseManager') as mock_db_manager, \
             patch('builtins.print') as mock_print:
            
            mock_db = MagicMock()
            mock_db_manager.return_value = mock_db
            mock_db.clear_database.return_value = False
            
            result = handle_database(args)
            
            # Should fail
            mock_db.clear_database.assert_called_once()
            mock_print.assert_called()
            self.assertEqual(result, 1)
    
    def test_wildcard_command_groups(self):
        """Test wildcard command with groups option"""
        args = argparse.Namespace(
            output=self.test_output_dir,
            groups=True,
            combined=False,
            combinations=False,
            all=False
        )
        
        with patch('main.WildcardGenerator') as mock_generator_class, \
             patch('main.DatabaseManager') as mock_db_manager, \
             patch('builtins.print') as mock_print:
            
            mock_generator = MagicMock()
            mock_generator_class.return_value = mock_generator
            mock_generator.generate_wildcards_from_results.return_value = {
                'landscapes': 'path/to/landscapes.txt',
                'portraits': 'path/to/portraits.txt'
            }
            
            mock_db = MagicMock()
            mock_db_manager.return_value = mock_db
            mock_db.get_all_results.return_value = [
                {'filename': 'test.jpg', 'directory': 'Images/landscapes'}
            ]
            
            result = handle_wildcard(args)
            
            # Should generate group wildcards
            mock_generator.generate_wildcards_from_results.assert_called_once()
            mock_print.assert_called()
            self.assertEqual(result, 0)
    
    def test_wildcard_command_combined(self):
        """Test wildcard command with combined option"""
        args = argparse.Namespace(
            output=self.test_output_dir,
            groups=False,
            combined=True,
            combinations=False,
            all=False
        )
        
        with patch('main.WildcardGenerator') as mock_generator_class, \
             patch('main.DatabaseManager') as mock_db_manager, \
             patch('builtins.print') as mock_print:
            
            mock_generator = MagicMock()
            mock_generator_class.return_value = mock_generator
            mock_generator.generate_combined_wildcard.return_value = 'path/to/combined.txt'
            
            mock_db = MagicMock()
            mock_db_manager.return_value = mock_db
            mock_db.get_all_results.return_value = [
                {'filename': 'test.jpg', 'directory': 'Images'}
            ]
            
            result = handle_wildcard(args)
            
            # Should generate combined wildcard
            mock_generator.generate_combined_wildcard.assert_called_once()
            mock_print.assert_called()
            self.assertEqual(result, 0)
    
    def test_wildcard_command_all(self):
        """Test wildcard command with all option"""
        args = argparse.Namespace(
            output=self.test_output_dir,
            groups=False,
            combined=False,
            combinations=False,
            all=True
        )
        
        with patch('main.WildcardGenerator') as mock_generator_class, \
             patch('main.DatabaseManager') as mock_db_manager, \
             patch('builtins.print') as mock_print:
            
            mock_generator = MagicMock()
            mock_generator_class.return_value = mock_generator
            mock_generator.generate_wildcards_from_results.return_value = {'test': 'path.txt'}
            mock_generator.generate_combined_wildcard.return_value = 'path/to/combined.txt'
            mock_generator.generate_group_combinations.return_value = {'combo': 'path.txt'}
            
            mock_db = MagicMock()
            mock_db_manager.return_value = mock_db
            mock_db.get_all_results.return_value = [
                {'filename': 'test.jpg', 'directory': 'Images'}
            ]
            
            result = handle_wildcard(args)
            
            # Should generate all types of wildcards
            mock_generator.generate_wildcards_from_results.assert_called_once()
            mock_generator.generate_combined_wildcard.assert_called_once()
            mock_generator.generate_group_combinations.assert_called_once()
            mock_print.assert_called()
            self.assertEqual(result, 0)
    
    def test_wildcard_command_no_results(self):
        """Test wildcard command with no database results"""
        args = argparse.Namespace(
            output=self.test_output_dir,
            groups=True,
            combined=False,
            combinations=False,
            all=False
        )
        
        with patch('main.WildcardGenerator') as mock_generator_class, \
             patch('main.DatabaseManager') as mock_db_manager, \
             patch('builtins.print') as mock_print:
            
            mock_db = MagicMock()
            mock_db_manager.return_value = mock_db
            mock_db.get_all_results.return_value = []
            
            result = handle_wildcard(args)
            
            # Should fail with no results
            mock_print.assert_called()
            self.assertEqual(result, 1)
    
    def test_wildcard_command_import_error(self):
        """Test wildcard command with import error"""
        args = argparse.Namespace(
            output=self.test_output_dir,
            groups=True,
            combined=False,
            combinations=False,
            all=False
        )
        
        with patch('main.WildcardGenerator', side_effect=ImportError("Test import error")), \
             patch('builtins.print') as mock_print:
            
            result = handle_wildcard(args)
            
            # Should handle import error
            mock_print.assert_called()
            self.assertEqual(result, 1)
    
    def test_get_default_config(self):
        """Test getting default configuration"""
        config = get_default_config()
        
        # Check required keys exist
        required_keys = [
            'API_BASE_URL', 'CLIP_MODEL_NAME', 'ENABLE_CLIP_ANALYSIS',
            'ENABLE_LLM_ANALYSIS', 'IMAGE_DIRECTORY', 'OUTPUT_DIRECTORY',
            'CLIP_MODES', 'PROMPT_CHOICES', 'LOGGING_LEVEL', 'RETRY_LIMIT',
            'TIMEOUT', 'WEB_PORT'
        ]
        
        for key in required_keys:
            self.assertIn(key, config)
        
        # Check data types
        self.assertIsInstance(config['ENABLE_CLIP_ANALYSIS'], bool)
        self.assertIsInstance(config['ENABLE_LLM_ANALYSIS'], bool)
        self.assertIsInstance(config['CLIP_MODES'], list)
        self.assertIsInstance(config['PROMPT_CHOICES'], list)
        self.assertIsInstance(config['RETRY_LIMIT'], int)
        self.assertIsInstance(config['TIMEOUT'], int)
        self.assertIsInstance(config['WEB_PORT'], int)

if __name__ == '__main__':
    unittest.main() 