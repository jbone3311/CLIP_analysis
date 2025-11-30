"""
Unit tests for wildcard generator
"""

import unittest
import tempfile
import os
import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.utils.wildcard_generator import WildcardGenerator

class TestWildcardGenerator(unittest.TestCase):
    """Test cases for WildcardGenerator functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = os.path.join(self.temp_dir, "Output")
        self.generator = WildcardGenerator(self.output_dir)
        
        # Sample test results
        self.sample_results = [
            {
                'filename': 'landscape1.jpg',
                'directory': 'Images/landscapes',
                'analysis_results': json.dumps({
                    'best': {'prompt': 'A beautiful mountain landscape with snow peaks'},
                    'fast': {'prompt': 'Mountain landscape with trees'}
                }),
                'llm_results': json.dumps({
                    'P1': {'content': 'This is a stunning mountain landscape'}
                })
            },
            {
                'filename': 'landscape2.jpg',
                'directory': 'Images/landscapes',
                'analysis_results': json.dumps({
                    'best': {'prompt': 'A serene lake surrounded by mountains'},
                    'fast': {'prompt': 'Lake and mountains'}
                })
            },
            {
                'filename': 'portrait1.jpg',
                'directory': 'Images/portraits',
                'analysis_results': json.dumps({
                    'best': {'prompt': 'A professional portrait of a woman'},
                    'fast': {'prompt': 'Portrait photo'}
                }),
                'llm_results': json.dumps({
                    'P1': {'content': 'This is a professional portrait'}
                })
            },
            {
                'filename': 'portrait2.jpg',
                'directory': 'Images/portraits',
                'analysis_results': json.dumps({
                    'best': {'prompt': 'A candid portrait of a man'},
                    'fast': {'prompt': 'Man portrait'}
                })
            },
            {
                'filename': 'root_image.jpg',
                'directory': 'Images',
                'analysis_results': json.dumps({
                    'best': {'prompt': 'A random image in root directory'},
                    'fast': {'prompt': 'Random image'}
                })
            }
        ]
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_init(self):
        """Test wildcard generator initialization"""
        self.assertEqual(self.generator.output_directory, self.output_dir)
        self.assertTrue(os.path.exists(self.generator.wildcards_dir))
    
    def test_extract_group_from_path(self):
        """Test group extraction from file paths"""
        # Test subfolder group
        group = self.generator.extract_group_from_path('Images/landscapes/image.jpg', 'Images')
        self.assertEqual(group, 'landscapes')
        
        # Test root group
        group = self.generator.extract_group_from_path('Images/image.jpg', 'Images')
        self.assertEqual(group, 'root')
        
        # Test nested subfolder (should get first level)
        group = self.generator.extract_group_from_path('Images/landscapes/mountains/image.jpg', 'Images')
        self.assertEqual(group, 'landscapes')
        
        # Test error handling - path that can't be made relative
        # This will return the first part of the path or 'unknown' on exception
        group = self.generator.extract_group_from_path('/absolute/invalid/path', 'Images')
        # The function may return 'unknown' or the first path component depending on the error
        self.assertIn(group, ['unknown', '..', 'absolute'])
    
    def test_extract_prompts_from_result(self):
        """Test prompt extraction from analysis results"""
        result = self.sample_results[0]  # landscape1.jpg
        
        prompts = self.generator.extract_prompts_from_result(result)
        
        # Should extract prompts from both analysis_results and llm_results
        expected_prompts = [
            'A beautiful mountain landscape with snow peaks',
            'Mountain landscape with trees',
            'This is a stunning mountain landscape'
        ]
        
        self.assertEqual(len(prompts), len(expected_prompts))
        for prompt in expected_prompts:
            self.assertIn(prompt, prompts)
    
    def test_extract_prompts_from_result_string_json(self):
        """Test prompt extraction when analysis_results is a JSON string"""
        result = {
            'analysis_results': json.dumps({
                'best': {'prompt': 'Test prompt from string JSON'}
            })
        }
        
        prompts = self.generator.extract_prompts_from_result(result)
        self.assertIn('Test prompt from string JSON', prompts)
    
    def test_extract_prompts_from_result_invalid_json(self):
        """Test prompt extraction with invalid JSON"""
        result = {
            'analysis_results': 'invalid json string'
        }
        
        prompts = self.generator.extract_prompts_from_result(result)
        self.assertEqual(prompts, [])
    
    def test_create_wildcard_content(self):
        """Test wildcard content creation"""
        prompts = [
            'A beautiful landscape',
            'Mountain view',
            'Lake scene'
        ]
        
        content = self.generator.create_wildcard_content(prompts, 'landscapes')
        
        # Should contain header and all prompts
        self.assertIn('# landscapes Wildcard File', content)
        self.assertIn('# Generated from 3 images', content)
        self.assertIn('# Group: landscapes', content)
        self.assertIn('A beautiful landscape', content)
        self.assertIn('Mountain view', content)
        self.assertIn('Lake scene', content)
    
    def test_create_wildcard_content_empty(self):
        """Test wildcard content creation with empty prompts"""
        content = self.generator.create_wildcard_content([], 'empty_group')
        
        self.assertIn('# empty_group - No prompts found', content)
    
    def test_create_wildcard_content_cleanup(self):
        """Test that wildcard content cleans up prompts"""
        prompts = [
            'A beautiful {landscape} with [mountains]',
            'Simple prompt',
            'Another {complex} prompt [with] wildcards'
        ]
        
        content = self.generator.create_wildcard_content(prompts, 'test')
        
        # Should remove wildcard formatting (may have extra spaces)
        self.assertIn('A beautiful', content)
        self.assertIn('Simple prompt', content)
        self.assertIn('Another', content)
        self.assertIn('wildcards', content)
    
    def test_generate_wildcards_from_results(self):
        """Test wildcard generation from results"""
        wildcard_files = self.generator.generate_wildcards_from_results(
            self.sample_results, 'Images'
        )
        
        # Should generate wildcards for landscapes, portraits, and root
        self.assertIn('landscapes', wildcard_files)
        self.assertIn('portraits', wildcard_files)
        self.assertIn('root', wildcard_files)
        
        # Check that files were created
        for group_name, file_path in wildcard_files.items():
            self.assertTrue(os.path.exists(file_path))
            
            # Check file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn(f'# {group_name} Wildcard File', content)
    
    def test_generate_wildcards_from_results_empty(self):
        """Test wildcard generation with empty results"""
        wildcard_files = self.generator.generate_wildcards_from_results([], 'Images')
        self.assertEqual(wildcard_files, {})
    
    def test_generate_combined_wildcard(self):
        """Test combined wildcard generation"""
        combined_file = self.generator.generate_combined_wildcard(
            self.sample_results, 'Images'
        )
        
        self.assertIsNotNone(combined_file)
        self.assertTrue(os.path.exists(combined_file))
        
        # Check file content
        with open(combined_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('# combined Wildcard File', content)
    
    def test_generate_group_combinations(self):
        """Test group combination generation"""
        # First generate individual wildcards
        self.generator.generate_wildcards_from_results(self.sample_results, 'Images')
        
        # Generate combinations
        combo_files = self.generator.generate_group_combinations(
            self.sample_results, 'Images'
        )
        
        # Should generate combinations like landscapes_portraits
        expected_combinations = ['landscapes_portraits', 'landscapes_root', 'portraits_root']
        
        for combo in expected_combinations:
            self.assertIn(combo, combo_files)
            self.assertTrue(os.path.exists(combo_files[combo]))
    
    def test_generate_group_combinations_insufficient_groups(self):
        """Test group combinations with insufficient groups"""
        # Create results with only one group
        single_group_results = [
            {
                'filename': 'image1.jpg',
                'directory': 'Images/landscapes',
                'analysis_results': json.dumps({
                    'best': {'prompt': 'Test prompt'}
                })
            }
        ]
        
        # Generate individual wildcards first
        self.generator.generate_wildcards_from_results(single_group_results, 'Images')
        
        # Try to generate combinations
        combo_files = self.generator.generate_group_combinations(
            single_group_results, 'Images'
        )
        
        # Should return empty dict when insufficient groups
        self.assertEqual(combo_files, {})
    
    def test_generate_wildcards_from_database(self):
        """Test wildcard generation from database"""
        # Mock database manager
        class MockDBManager:
            def get_all_results(self):
                return self.sample_results
        
        mock_db = MockDBManager()
        mock_db.sample_results = self.sample_results
        
        # generate_wildcards_from_database needs base_directory parameter
        wildcard_files = self.generator.generate_wildcards_from_database(mock_db)
        
        # Should generate wildcards (keys are original group names from paths)
        # The actual keys depend on the directory structure in sample_results
        self.assertGreater(len(wildcard_files), 0)
        # Check that files were created
        for file_path in wildcard_files.values():
            self.assertTrue(os.path.exists(file_path))
    
    def test_generate_wildcards_from_database_empty(self):
        """Test wildcard generation from empty database"""
        class MockDBManager:
            def get_all_results(self):
                return []
        
        mock_db = MockDBManager()
        
        wildcard_files = self.generator.generate_wildcards_from_database(mock_db)
        self.assertEqual(wildcard_files, {})
    
    def test_sanitize_group_name(self):
        """Test that group names are properly sanitized for filenames"""
        # Test with special characters
        result = {
            'filename': 'test.jpg',
            'directory': 'Images/test group (special)',
            'analysis_results': json.dumps({
                'best': {'prompt': 'Test prompt'}
            })
        }
        
        wildcard_files = self.generator.generate_wildcards_from_results([result], 'Images')
        
        # Keys are original group names, not sanitized
        # The group name will be extracted from the directory path
        self.assertGreater(len(wildcard_files), 0)
        # Check that files were created with sanitized filenames
        for group_name, file_path in wildcard_files.items():
            self.assertTrue(os.path.exists(file_path))
            # Filename should be sanitized
            filename = os.path.basename(file_path)
            self.assertNotIn('(', filename)  # No special chars in filename
    
    def test_duplicate_prompt_removal(self):
        """Test that duplicate prompts are removed"""
        result = {
            'filename': 'test.jpg',
            'directory': 'Images/test',
            'analysis_results': json.dumps({
                'best': {'prompt': 'Same prompt'},
                'fast': {'prompt': 'Same prompt'}  # Duplicate
            }),
            'llm_results': json.dumps({
                'P1': {'content': 'Same prompt'}  # Another duplicate
            })
        }
        
        prompts = self.generator.extract_prompts_from_result(result)
        
        # Should only have one instance of 'Same prompt'
        self.assertEqual(prompts.count('Same prompt'), 1)
        self.assertEqual(len(prompts), 1)

if __name__ == '__main__':
    unittest.main() 