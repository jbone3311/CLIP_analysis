"""
Unit tests for database manager
"""

import unittest
import tempfile
import os
import json
import sqlite3
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.database.db_manager import DatabaseManager

class TestDatabaseManager(unittest.TestCase):
    """Test cases for DatabaseManager functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a temporary database file
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_db.sqlite")
        self.db_manager = DatabaseManager(self.db_path)
        
        # Sample test data
        self.sample_result = {
            'filename': 'test_image.jpg',
            'directory': 'Images',
            'md5': 'abc123def456',
            'model': 'ViT-L-14/openai',
            'modes': ['best', 'fast'],
            'prompts': {'P1': 'Describe this image'},
            'analysis_results': {'best': {'prompt': 'A beautiful landscape'}},
            'settings': {'api_url': 'http://localhost:7860'},
            'llm_results': {'P1': {'content': 'This is a landscape image'}}
        }
        
        self.sample_llm_model = {
            'name': 'gpt-4',
            'type': 'openai',
            'url': 'https://api.openai.com/v1',
            'api_key': 'test_key',
            'model_name': 'gpt-4',
            'prompts': {'P1': 'Describe this image'}
        }
    
    def tearDown(self):
        """Clean up test fixtures"""
        # Remove temporary database
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_init_db(self):
        """Test database initialization"""
        # Check if tables were created
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check analysis_results table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='analysis_results'")
            self.assertIsNotNone(cursor.fetchone())
            
            # Check llm_models table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='llm_models'")
            self.assertIsNotNone(cursor.fetchone())
    
    def test_insert_and_get_result(self):
        """Test inserting and retrieving analysis results"""
        # Insert test result
        self.db_manager.insert_result(
            filename=self.sample_result['filename'],
            directory=self.sample_result['directory'],
            md5=self.sample_result['md5'],
            model=self.sample_result['model'],
            modes=json.dumps(self.sample_result['modes']),
            prompts=json.dumps(self.sample_result['prompts']),
            analysis_results=json.dumps(self.sample_result['analysis_results']),
            settings=json.dumps(self.sample_result['settings']),
            llm_results=json.dumps(self.sample_result['llm_results'])
        )
        
        # Retrieve by MD5
        result = self.db_manager.get_result_by_md5(self.sample_result['md5'])
        self.assertIsNotNone(result)
        self.assertEqual(result['filename'], self.sample_result['filename'])
        self.assertEqual(result['directory'], self.sample_result['directory'])
        self.assertEqual(result['md5'], self.sample_result['md5'])
        self.assertEqual(result['model'], self.sample_result['model'])
        
        # Check JSON fields are parsed
        self.assertEqual(result['modes'], self.sample_result['modes'])
        self.assertEqual(result['prompts'], self.sample_result['prompts'])
        self.assertEqual(result['analysis_results'], self.sample_result['analysis_results'])
        self.assertEqual(result['settings'], self.sample_result['settings'])
        self.assertEqual(result['llm_results'], self.sample_result['llm_results'])
    
    def test_get_result_by_id(self):
        """Test retrieving result by ID"""
        # Insert test result
        self.db_manager.insert_result(
            filename=self.sample_result['filename'],
            directory=self.sample_result['directory'],
            md5=self.sample_result['md5'],
            model=self.sample_result['model'],
            modes=json.dumps(self.sample_result['modes']),
            prompts=json.dumps(self.sample_result['prompts']),
            analysis_results=json.dumps(self.sample_result['analysis_results']),
            settings=json.dumps(self.sample_result['settings'])
        )
        
        # Get the ID from MD5 lookup
        result = self.db_manager.get_result_by_md5(self.sample_result['md5'])
        result_id = result['id']
        
        # Retrieve by ID
        result_by_id = self.db_manager.get_result_by_id(result_id)
        self.assertIsNotNone(result_by_id)
        self.assertEqual(result_by_id['id'], result_id)
        self.assertEqual(result_by_id['filename'], self.sample_result['filename'])
    
    def test_get_result_by_filename(self):
        """Test retrieving result by filename and directory"""
        # Insert test result
        self.db_manager.insert_result(
            filename=self.sample_result['filename'],
            directory=self.sample_result['directory'],
            md5=self.sample_result['md5'],
            model=self.sample_result['model'],
            modes=json.dumps(self.sample_result['modes']),
            prompts=json.dumps(self.sample_result['prompts']),
            analysis_results=json.dumps(self.sample_result['analysis_results']),
            settings=json.dumps(self.sample_result['settings'])
        )
        
        # Retrieve by filename and directory
        result = self.db_manager.get_result_by_filename(
            self.sample_result['filename'], 
            self.sample_result['directory']
        )
        self.assertIsNotNone(result)
        self.assertEqual(result['filename'], self.sample_result['filename'])
        self.assertEqual(result['directory'], self.sample_result['directory'])
    
    def test_get_all_results(self):
        """Test retrieving all results"""
        # Insert multiple test results
        for i in range(3):
            self.db_manager.insert_result(
                filename=f'test_image_{i}.jpg',
                directory='Images',
                md5=f'abc123def456_{i}',
                model='ViT-L-14/openai',
                modes=json.dumps(['best']),
                prompts=json.dumps({'P1': 'Describe this image'}),
                analysis_results=json.dumps({'best': {'prompt': 'Test image'}}),
                settings=json.dumps({'api_url': 'http://localhost:7860'})
            )
        
        # Get all results
        results = self.db_manager.get_all_results()
        self.assertEqual(len(results), 3)
        
        # Check they're ordered by date (newest first)
        self.assertGreaterEqual(results[0]['date_added'], results[1]['date_added'])
    
    def test_delete_result(self):
        """Test deleting a result"""
        # Insert test result
        self.db_manager.insert_result(
            filename=self.sample_result['filename'],
            directory=self.sample_result['directory'],
            md5=self.sample_result['md5'],
            model=self.sample_result['model'],
            modes=json.dumps(self.sample_result['modes']),
            prompts=json.dumps(self.sample_result['prompts']),
            analysis_results=json.dumps(self.sample_result['analysis_results']),
            settings=json.dumps(self.sample_result['settings'])
        )
        
        # Get the ID
        result = self.db_manager.get_result_by_md5(self.sample_result['md5'])
        result_id = result['id']
        
        # Delete the result
        success = self.db_manager.delete_result(result_id)
        self.assertTrue(success)
        
        # Verify it's gone
        deleted_result = self.db_manager.get_result_by_id(result_id)
        self.assertIsNone(deleted_result)
    
    def test_clear_database(self):
        """Test clearing all results"""
        # Insert multiple test results
        for i in range(3):
            self.db_manager.insert_result(
                filename=f'test_image_{i}.jpg',
                directory='Images',
                md5=f'abc123def456_{i}',
                model='ViT-L-14/openai',
                modes=json.dumps(['best']),
                prompts=json.dumps({'P1': 'Describe this image'}),
                analysis_results=json.dumps({'best': {'prompt': 'Test image'}}),
                settings=json.dumps({'api_url': 'http://localhost:7860'})
            )
        
        # Clear database
        success = self.db_manager.clear_database()
        self.assertTrue(success)
        
        # Verify all results are gone
        results = self.db_manager.get_all_results()
        self.assertEqual(len(results), 0)
    
    def test_insert_and_get_llm_model(self):
        """Test inserting and retrieving LLM models"""
        # Insert test model
        self.db_manager.insert_llm_model(
            name=self.sample_llm_model['name'],
            type=self.sample_llm_model['type'],
            url=self.sample_llm_model['url'],
            api_key=self.sample_llm_model['api_key'],
            model_name=self.sample_llm_model['model_name'],
            prompts=json.dumps(self.sample_llm_model['prompts'])
        )
        
        # Get all models
        models = self.db_manager.get_llm_models()
        self.assertEqual(len(models), 1)
        
        model = models[0]
        self.assertEqual(model['name'], self.sample_llm_model['name'])
        self.assertEqual(model['type'], self.sample_llm_model['type'])
        self.assertEqual(model['url'], self.sample_llm_model['url'])
        self.assertEqual(model['api_key'], self.sample_llm_model['api_key'])
        self.assertEqual(model['model_name'], self.sample_llm_model['model_name'])
        self.assertEqual(model['prompts'], self.sample_llm_model['prompts'])
        self.assertTrue(model['is_active'])
    
    def test_delete_llm_model(self):
        """Test deleting an LLM model"""
        # Insert test model
        self.db_manager.insert_llm_model(
            name=self.sample_llm_model['name'],
            type=self.sample_llm_model['type'],
            url=self.sample_llm_model['url'],
            api_key=self.sample_llm_model['api_key'],
            model_name=self.sample_llm_model['model_name']
        )
        
        # Get the model ID
        models = self.db_manager.get_llm_models()
        model_id = models[0]['id']
        
        # Delete the model
        success = self.db_manager.delete_llm_model(model_id)
        self.assertTrue(success)
        
        # Verify it's marked as inactive
        models_after = self.db_manager.get_llm_models()
        self.assertEqual(len(models_after), 0)
    
    def test_update_llm_model_prompts(self):
        """Test updating LLM model prompts"""
        # Insert test model
        self.db_manager.insert_llm_model(
            name=self.sample_llm_model['name'],
            type=self.sample_llm_model['type'],
            url=self.sample_llm_model['url'],
            api_key=self.sample_llm_model['api_key'],
            model_name=self.sample_llm_model['model_name']
        )
        
        # Get the model ID
        models = self.db_manager.get_llm_models()
        model_id = models[0]['id']
        
        # Update prompts
        new_prompts = {'P1': 'New prompt', 'P2': 'Another prompt'}
        success = self.db_manager.update_llm_model_prompts(model_id, json.dumps(new_prompts))
        self.assertTrue(success)
        
        # Verify prompts were updated
        models_after = self.db_manager.get_llm_models()
        self.assertEqual(models_after[0]['prompts'], new_prompts)
    
    def test_get_stats(self):
        """Test getting database statistics"""
        # Insert some test data
        for i in range(5):
            self.db_manager.insert_result(
                filename=f'test_image_{i}.jpg',
                directory='Images',
                md5=f'abc123def456_{i}',
                model='ViT-L-14/openai',
                modes=json.dumps(['best']),
                prompts=json.dumps({'P1': 'Describe this image'}),
                analysis_results=json.dumps({'best': {'prompt': 'Test image'}}),
                settings=json.dumps({'api_url': 'http://localhost:7860'})
            )
        
        # Insert some LLM models
        for i in range(2):
            self.db_manager.insert_llm_model(
                name=f'model_{i}',
                type='openai',
                url='https://api.openai.com/v1',
                api_key=f'key_{i}',
                model_name=f'gpt-{i}'
            )
        
        # Get stats
        stats = self.db_manager.get_stats()
        
        self.assertIn('total_results', stats)
        self.assertIn('recent_results', stats)
        self.assertIn('llm_models', stats)
        
        self.assertEqual(stats['total_results'], 5)
        self.assertEqual(stats['llm_models'], 2)
        self.assertGreaterEqual(stats['recent_results'], 0)
    
    def test_duplicate_md5_handling(self):
        """Test handling of duplicate MD5 hashes"""
        # Insert first result
        self.db_manager.insert_result(
            filename='image1.jpg',
            directory='Images',
            md5='duplicate_md5',
            model='ViT-L-14/openai',
            modes=json.dumps(['best']),
            prompts=json.dumps({'P1': 'Describe this image'}),
            analysis_results=json.dumps({'best': {'prompt': 'First image'}}),
            settings=json.dumps({'api_url': 'http://localhost:7860'})
        )
        
        # Insert second result with same MD5 (should replace)
        self.db_manager.insert_result(
            filename='image2.jpg',
            directory='Images',
            md5='duplicate_md5',
            model='ViT-L-14/openai',
            modes=json.dumps(['best']),
            prompts=json.dumps({'P1': 'Describe this image'}),
            analysis_results=json.dumps({'best': {'prompt': 'Second image'}}),
            settings=json.dumps({'api_url': 'http://localhost:7860'})
        )
        
        # Should only have one result
        results = self.db_manager.get_all_results()
        self.assertEqual(len(results), 1)
        
        # Should be the second result
        result = results[0]
        self.assertEqual(result['filename'], 'image2.jpg')
        self.assertEqual(result['analysis_results']['best']['prompt'], 'Second image')

if __name__ == '__main__':
    unittest.main() 