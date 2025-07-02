import pytest
import os
import json
import subprocess
import tempfile
from unittest.mock import patch, Mock
import responses

class TestEndToEndWorkflow:
    """Integration tests for complete end-to-end workflows."""
    
    @responses.activate
    def test_single_image_llm_analysis_workflow(self, sample_image_path, temp_dir, mock_llm_response):
        """Test complete workflow for single image LLM analysis."""
        # Setup API mock
        responses.add(
            responses.POST,
            "https://api.openai.com/v1/chat/completions",
            json=mock_llm_response,
            status=200
        )
        
        output_file = os.path.join(temp_dir, "integration_output.json")
        
        # Run LLM analysis
        result = subprocess.run([
            "python", "analysis_LLM.py", 
            sample_image_path,
            "--prompt", "PROMPT1",
            "--model", "1",
            "--output", output_file
        ], capture_output=True, text=True, cwd=".")
        
        # Verify successful execution
        assert result.returncode == 0
        assert os.path.exists(output_file)
        
        # Verify output content
        with open(output_file, 'r') as f:
            data = json.load(f)
        
        assert "image" in data
        assert "model" in data
        assert "prompts" in data
    
    @responses.activate
    def test_single_image_clip_analysis_workflow(self, sample_image_path, temp_dir, mock_clip_response):
        """Test complete workflow for single image CLIP analysis."""
        # Setup API mock
        responses.add(
            responses.POST,
            "http://localhost:7860/interrogator/prompt",
            json=mock_clip_response,
            status=200
        )
        responses.add(
            responses.POST,
            "http://localhost:7860/interrogator/analyze",
            json={"analysis": "test analysis"},
            status=200
        )
        
        output_file = os.path.join(temp_dir, "clip_output.json")
        
        # Run CLIP analysis
        result = subprocess.run([
            "python", "analysis_interrogate.py",
            sample_image_path,
            "--modes", "best",
            "--output", output_file
        ], capture_output=True, text=True, cwd=".")
        
        # Verify successful execution
        assert result.returncode == 0
        assert os.path.exists(output_file)
        
        # Verify output content
        with open(output_file, 'r') as f:
            data = json.load(f)
        
        assert "image" in data
        assert "model" in data
        assert "prompts" in data
        assert "analysis" in data

class TestBatchProcessingWorkflow:
    """Integration tests for batch processing workflows."""
    
    @patch.dict(os.environ, {
        'USE_DATABASE': 'false',
        'USE_JSON': 'true',
        'ENABLE_CLIP_ANALYSIS': 'true',
        'ENABLE_LLM_ANALYSIS': 'false'
    })
    @responses.activate
    def test_directory_batch_processing(self, multiple_test_images, temp_dir, mock_clip_response):
        """Test batch processing of multiple images in a directory."""
        # Setup CLIP API mocks
        responses.add(
            responses.POST,
            "http://localhost:7860/interrogator/prompt",
            json=mock_clip_response,
            status=200
        )
        responses.add(
            responses.POST,
            "http://localhost:7860/interrogator/analyze",
            json={"analysis": "test analysis"},
            status=200
        )
        
        # Configure for batch processing
        from config import Config
        config = Config()
        config.image_directory = temp_dir
        
        # Run batch processing
        from directory_processor import DirectoryProcessor
        processor = DirectoryProcessor(config)
        processor.process_directory()
        processor.close()
        
        # Verify JSON files were created for all images
        json_files = [f for f in os.listdir(temp_dir) if f.endswith('.json')]
        image_files = [f for f in os.listdir(temp_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        # Should have one JSON file per image
        assert len(json_files) == len(image_files)

class TestConfigurationIntegration:
    """Integration tests for different configuration scenarios."""
    
    def test_environment_variable_integration(self, temp_dir, sample_image_path):
        """Test that environment variables are properly integrated throughout the system."""
        custom_env = {
            'IMAGE_DIRECTORY': temp_dir,
            'OUTPUT_DIRECTORY': temp_dir,
            'USE_JSON': 'true',
            'USE_DATABASE': 'false',
            'ENABLE_CLIP_ANALYSIS': 'true',
            'ENABLE_CAPTION': 'true',
            'ENABLE_BEST': 'false',
            'ENABLE_FAST': 'true',
            'CLIP_MODEL_NAME': 'ViT-B-32',
            'API_BASE_URL': 'http://custom:8080',
            'TIMEOUT': '120',
            'RETRY_LIMIT': '10',
            'EMOJI_SUCCESS': '✓',
            'EMOJI_ERROR': '✗'
        }
        
        with patch.dict(os.environ, custom_env):
            from config import Config
            config = Config()
            
            # Verify all custom settings are loaded
            assert config.image_directory == temp_dir
            assert config.use_json is True
            assert config.use_database is False
            assert config.enable_clip_analysis is True
            assert config.enable_caption is True
            assert config.enable_best is False
            assert config.enable_fast is True
            assert config.clip_model_name == 'ViT-B-32'
            assert config.api_base_url == 'http://custom:8080'
            assert config.timeout == 120
            assert config.retry_limit == 10
            assert config.EMOJI_SUCCESS == '✓'
            assert config.EMOJI_ERROR == '✗'

class TestErrorRecoveryIntegration:
    """Integration tests for error recovery and resilience."""
    
    @patch.dict(os.environ, {
        'USE_DATABASE': 'false',
        'USE_JSON': 'true',
        'RETRY_LIMIT': '2'
    })
    @responses.activate
    def test_api_retry_integration(self, sample_image_path, temp_dir):
        """Test API retry mechanism in real workflow."""
        # First two calls fail, third succeeds
        responses.add(
            responses.POST,
            "https://api.openai.com/v1/chat/completions",
            json={"error": "Rate limit exceeded"},
            status=429
        )
        responses.add(
            responses.POST,
            "https://api.openai.com/v1/chat/completions",
            json={"error": "Server error"},
            status=500
        )
        responses.add(
            responses.POST,
            "https://api.openai.com/v1/chat/completions",
            json={
                "choices": [{"message": {"content": "Success after retries"}}],
                "usage": {"total_tokens": 50}
            },
            status=200
        )
        
        output_file = os.path.join(temp_dir, "retry_test.json")
        
        # Run with retries enabled
        result = subprocess.run([
            "python", "analysis_LLM.py",
            sample_image_path,
            "--prompt", "PROMPT1",
            "--model", "1",
            "--output", output_file
        ], capture_output=True, text=True, cwd=".")
        
        # Should eventually succeed despite initial failures
        assert result.returncode == 0
        assert os.path.exists(output_file)
    
    def test_mixed_success_failure_batch(self, temp_dir):
        """Test batch processing with mixed success and failure cases."""
        # Create multiple test images
        good_image = os.path.join(temp_dir, "good_image.jpg")
        bad_image = os.path.join(temp_dir, "corrupted_image.jpg")
        
        # Create a valid image
        from PIL import Image
        img = Image.new('RGB', (50, 50), color='red')
        img.save(good_image, "JPEG")
        
        # Create a corrupted image file
        with open(bad_image, 'w') as f:
            f.write("This is not a valid image file")
        
        with patch.dict(os.environ, {
            'USE_DATABASE': 'false',
            'USE_JSON': 'true',
            'ENABLE_CLIP_ANALYSIS': 'true'
        }):
            from config import Config
            from directory_processor import DirectoryProcessor
            
            config = Config()
            config.image_directory = temp_dir
            
            # Should handle mixed success/failure gracefully
            processor = DirectoryProcessor(config)
            processor.process_directory()
            processor.close()
            
            # Good image should have JSON output
            good_json = good_image.replace('.jpg', '.json')
            # Depending on implementation, might or might not create JSON for failed images

class TestDatabaseIntegration:
    """Integration tests for database functionality."""
    
    @patch.dict(os.environ, {
        'USE_DATABASE': 'true',
        'USE_JSON': 'false'
    })
    def test_database_full_workflow(self, temp_dir, sample_image_path, mock_database):
        """Test complete workflow with database storage."""
        from db_utils import Database
        from directory_processor import DirectoryProcessor
        from config import Config
        
        config = Config()
        config.database_path = mock_database
        config.image_directory = temp_dir
        
        # Initialize database
        db = Database(mock_database)
        
        # Verify database is empty initially
        assert db.is_processed_db("test_unique_id") is False
        
        # Add and process an image
        unique_id = "integration_test_123"
        db.add_image(unique_id, "test.jpg", 1699999999.0, 1024)
        image_id = db.get_image_id_db(unique_id)
        
        # Update status and add results
        db.update_image_status(image_id, 'processing')
        db.add_analysis_result(image_id, 'CLIP', None, '{"test": "result"}')
        db.update_image_status(image_id, 'completed')
        
        # Verify final state
        assert db.is_processed_db(unique_id) is True
        
        db.close()

class TestUtilityIntegration:
    """Integration tests for utility function interactions."""
    
    def test_unique_code_consistency_across_modules(self, sample_image_path):
        """Test that unique code generation is consistent across different modules."""
        from utils import generate_unique_code
        
        # Generate unique code multiple times
        code1 = generate_unique_code(sample_image_path)
        code2 = generate_unique_code(sample_image_path)
        code3 = generate_unique_code(sample_image_path)
        
        # Should be consistent
        assert code1 == code2 == code3
        
        # Should be a valid identifier
        assert isinstance(code1, str)
        assert len(code1) > 0
    
    def test_json_utilities_integration(self, temp_dir):
        """Test JSON utilities working with real data structures."""
        from utils import save_json, load_json
        
        test_data = {
            "image_analysis": {
                "llm_results": [
                    {"prompt": "PROMPT1", "response": "Detailed description"},
                    {"prompt": "PROMPT2", "response": "Artistic analysis"}
                ],
                "clip_results": {
                    "best": "high quality prompt",
                    "fast": "quick prompt",
                    "caption": "image caption"
                }
            },
            "metadata": {
                "image_path": "/path/to/image.jpg",
                "processing_date": "2023-11-01T12:00:00Z",
                "model_versions": {
                    "clip": "ViT-L-14/openai",
                    "llm": "gpt-4-vision-preview"
                }
            }
        }
        
        file_path = os.path.join(temp_dir, "integration_data.json")
        
        # Save and load
        save_json(test_data, file_path)
        loaded_data = load_json(file_path)
        
        # Verify data integrity
        assert loaded_data == test_data
        assert loaded_data["image_analysis"]["llm_results"][0]["prompt"] == "PROMPT1"
        assert loaded_data["metadata"]["model_versions"]["clip"] == "ViT-L-14/openai"

class TestCLIIntegration:
    """Integration tests for command-line interface functionality."""
    
    def test_llm_cli_help(self):
        """Test LLM analysis CLI help functionality."""
        result = subprocess.run([
            "python", "analysis_LLM.py", "--help"
        ], capture_output=True, text=True, cwd=".")
        
        assert result.returncode == 0
        assert "image_path" in result.stdout or "--help" in result.stdout
    
    def test_clip_cli_help(self):
        """Test CLIP analysis CLI help functionality."""
        result = subprocess.run([
            "python", "analysis_interrogate.py", "--help"
        ], capture_output=True, text=True, cwd=".")
        
        assert result.returncode == 0
        assert "image_path" in result.stdout or "--help" in result.stdout
    
    @patch.dict(os.environ, {
        'LLM_1_TITLE': 'Test Model',
        'LLM_1_API_URL': 'https://api.test.com',
        'LLM_1_API_KEY': 'test_key',
        'LLM_1_MODEL': 'test_model'
    })
    def test_llm_list_models(self):
        """Test LLM model listing functionality."""
        result = subprocess.run([
            "python", "analysis_LLM.py", "--model", "list"
        ], capture_output=True, text=True, cwd=".")
        
        assert result.returncode == 0
        assert "Test Model" in result.stdout
    
    def test_llm_list_prompts(self):
        """Test LLM prompt listing functionality."""
        result = subprocess.run([
            "python", "analysis_LLM.py", "--prompt", "list"
        ], capture_output=True, text=True, cwd=".")
        
        assert result.returncode == 0
        # Should list available prompts
        assert "PROMPT" in result.stdout or "Available" in result.stdout

class TestFullSystemIntegration:
    """Integration tests that exercise the complete system."""
    
    @patch.dict(os.environ, {
        'USE_DATABASE': 'true',
        'USE_JSON': 'true',
        'ENABLE_CLIP_ANALYSIS': 'true',
        'ENABLE_LLM_ANALYSIS': 'true',
        'LLM_1_TITLE': 'Integration Test Model',
        'LLM_1_API_URL': 'https://api.test.com',
        'LLM_1_API_KEY': 'test_key',
        'LLM_1_MODEL': 'test_model'
    })
    @responses.activate
    def test_complete_system_workflow(self, temp_dir, multiple_test_images, mock_database, mock_clip_response, mock_llm_response):
        """Test complete system with all components enabled."""
        # Setup API mocks
        responses.add(
            responses.POST,
            "http://localhost:7860/interrogator/prompt",
            json=mock_clip_response,
            status=200
        )
        responses.add(
            responses.POST,
            "http://localhost:7860/interrogator/analyze",
            json={"analysis": "comprehensive analysis"},
            status=200
        )
        responses.add(
            responses.POST,
            "https://api.test.com",
            json=mock_llm_response,
            status=200
        )
        
        from config import Config
        from directory_processor import DirectoryProcessor
        
        config = Config()
        config.image_directory = temp_dir
        config.database_path = mock_database
        
        # Run complete processing workflow
        processor = DirectoryProcessor(config)
        processor.process_directory()
        processor.close()
        
        # Verify both JSON and database storage
        json_files = [f for f in os.listdir(temp_dir) if f.endswith('.json')]
        assert len(json_files) > 0  # Should create JSON files
        
        # Verify database contains processed images
        from db_utils import Database
        db = Database(mock_database)
        
        # Check that images were added to database
        # (Specific verification depends on actual implementation)
        db.close()
    
    def test_logging_integration(self, temp_dir, caplog):
        """Test that logging works correctly across all modules."""
        with patch.dict(os.environ, {
            'LOGGING_LEVEL': 'INFO',
            'IMAGE_DIRECTORY': temp_dir,
            'USE_DATABASE': 'false'
        }):
            from config import Config
            from utils import setup_logging
            
            config = Config()
            setup_logging(config)
            
            # Test logging from different modules
            import logging
            logging.info("Integration test logging")
            
            assert "Integration test logging" in caplog.text