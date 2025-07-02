import pytest
import json
import os
from unittest.mock import patch, Mock, mock_open
import responses
from analysis_LLM import LLMAnalyzer, load_llm_models, list_models, list_prompts, parse_arguments
import sys
from io import StringIO

class TestLLMAnalyzer:
    """Test cases for LLMAnalyzer class."""
    
    def test_init(self):
        """Test LLMAnalyzer initialization."""
        analyzer = LLMAnalyzer(
            api_url="https://api.test.com",
            api_key="test_key",
            model_name="test_model",
            title="Test Model",
            debug=True
        )
        
        assert analyzer.api_url == "https://api.test.com"
        assert analyzer.api_key == "test_key"
        assert analyzer.model_name == "test_model"
        assert analyzer.title == "Test Model"
        assert analyzer.debug is True
    
    def test_save_json(self, temp_dir):
        """Test JSON saving functionality."""
        test_data = {"test": "data", "number": 123}
        file_path = os.path.join(temp_dir, "test_save.json")
        
        LLMAnalyzer.save_json(test_data, file_path)
        
        # Verify file was created and content is correct
        assert os.path.exists(file_path)
        with open(file_path, 'r') as f:
            loaded_data = json.load(f)
        assert loaded_data == test_data
    
    @responses.activate
    def test_process_image_success(self, sample_image_path, sample_llm_prompts, mock_llm_response):
        """Test successful image processing with LLM."""
        # Mock the API response
        responses.add(
            responses.POST,
            "https://api.test.com/chat/completions",
            json=mock_llm_response,
            status=200
        )
        
        # Set up test environment
        with patch('analysis_LLM.PROMPTS_FILE', sample_llm_prompts):
            with patch('analysis_LLM.PROMPTS', {
                "TEST_PROMPT1": {
                    "TITLE": "Test Description",
                    "PROMPT_TEXT": "Describe this test image.",
                    "TEMPERATURE": 0.7,
                    "MAX_TOKENS": 500
                }
            }):
                analyzer = LLMAnalyzer(
                    api_url="https://api.test.com/chat/completions",
                    api_key="test_key",
                    model_name="test_model"
                )
                
                # Capture stdout to test output
                captured_output = StringIO()
                with patch('sys.stdout', captured_output):
                    analyzer.process_image(sample_image_path, ["TEST_PROMPT1"])
                
                # Verify the output contains expected structure
                output = captured_output.getvalue()
                output_data = json.loads(output)
                
                assert "image" in output_data
                assert "model" in output_data
                assert "prompts" in output_data
                assert output_data["model"] == "test_model"
    
    @responses.activate
    def test_process_image_api_error(self, sample_image_path):
        """Test image processing with API error."""
        # Mock API error response
        responses.add(
            responses.POST,
            "https://api.test.com/chat/completions",
            json={"error": "API Error"},
            status=500
        )
        
        with patch('analysis_LLM.PROMPTS', {"TEST_PROMPT1": {"PROMPT_TEXT": "test", "TEMPERATURE": 0.7, "MAX_TOKENS": 500}}):
            analyzer = LLMAnalyzer(
                api_url="https://api.test.com/chat/completions",
                api_key="test_key",
                model_name="test_model"
            )
            
            # Should handle error gracefully
            captured_output = StringIO()
            with patch('sys.stdout', captured_output):
                analyzer.process_image(sample_image_path, ["TEST_PROMPT1"])
            
            output = captured_output.getvalue()
            output_data = json.loads(output)
            
            # Should contain error information
            assert "prompts" in output_data
            assert "results" in output_data["prompts"]
            assert "error" in output_data["prompts"]["results"][0]
    
    def test_process_image_file_not_found(self):
        """Test processing non-existent image file."""
        analyzer = LLMAnalyzer(
            api_url="https://api.test.com",
            api_key="test_key",
            model_name="test_model"
        )
        
        with pytest.raises(SystemExit):
            analyzer.process_image("nonexistent.jpg", ["TEST_PROMPT1"])

class TestUtilityFunctions:
    """Test cases for utility functions."""
    
    @patch.dict(os.environ, {
        'LLM_1_TITLE': 'Test Model 1',
        'LLM_1_API_URL': 'https://api1.test.com',
        'LLM_1_API_KEY': 'key1',
        'LLM_1_MODEL': 'model1',
        'LLM_2_TITLE': 'Test Model 2',
        'LLM_2_API_URL': 'https://api2.test.com',
        'LLM_2_MODEL': 'model2'
    })
    def test_load_llm_models(self):
        """Test loading LLM models from environment variables."""
        models = load_llm_models()
        
        assert len(models) == 2
        assert models[0]["title"] == "Test Model 1"
        assert models[0]["api_url"] == "https://api1.test.com"
        assert models[0]["model_name"] == "model1"
        assert models[1]["title"] == "Test Model 2"
    
    def test_list_models(self, capsys):
        """Test listing available models."""
        test_models = [
            {
                "number": 1,
                "title": "Test Model 1",
                "api_url": "https://api1.test.com",
                "model_name": "model1"
            },
            {
                "number": 2,
                "title": "Test Model 2", 
                "api_url": "https://api2.test.com",
                "model_name": "model2"
            }
        ]
        
        list_models(test_models)
        captured = capsys.readouterr()
        
        assert "Test Model 1" in captured.out
        assert "Test Model 2" in captured.out
        assert "https://api1.test.com" in captured.out
    
    def test_list_prompts(self, capsys):
        """Test listing available prompts."""
        test_prompts = {
            "PROMPT1": {
                "TITLE": "Test Prompt 1",
                "PROMPT_TEXT": "This is a test prompt for testing purposes.",
                "TEMPERATURE": 0.7,
                "MAX_TOKENS": 500
            },
            "PROMPT2": {
                "TITLE": "Test Prompt 2",
                "PROMPT_TEXT": "Another test prompt for verification.",
                "TEMPERATURE": 0.8,
                "MAX_TOKENS": 750
            }
        }
        
        list_prompts(test_prompts)
        captured = capsys.readouterr()
        
        assert "PROMPT1" in captured.out
        assert "Test Prompt 1" in captured.out
        assert "Temperature: 0.7" in captured.out

class TestArgumentParsing:
    """Test cases for argument parsing."""
    
    def test_parse_arguments_basic(self):
        """Test basic argument parsing."""
        test_args = [
            "test_image.jpg",
            "--prompt", "PROMPT1,PROMPT2",
            "--model", "1",
            "--output", "output.json"
        ]
        
        with patch('sys.argv', ['analysis_LLM.py'] + test_args):
            args = parse_arguments()
            
            assert args.image_path == "test_image.jpg"
            assert args.prompt == "PROMPT1,PROMPT2"
            assert args.model == "1"
            assert args.output == "output.json"
    
    def test_parse_arguments_debug(self):
        """Test debug flag parsing."""
        test_args = [
            "test_image.jpg",
            "--prompt", "PROMPT1",
            "--model", "1",
            "--debug"
        ]
        
        with patch('sys.argv', ['analysis_LLM.py'] + test_args):
            args = parse_arguments()
            
            assert args.debug is True

class TestMainFunction:
    """Test cases for main function and CLI interface."""
    
    @patch('analysis_LLM.MODELS', [
        {"number": 1, "title": "Test Model", "api_url": "https://api.test.com", 
         "api_key": "test_key", "model_name": "test_model"}
    ])
    def test_main_list_models(self, capsys):
        """Test main function with --model list."""
        test_args = ['--model', 'list']
        
        with patch('sys.argv', ['analysis_LLM.py'] + test_args):
            with pytest.raises(SystemExit) as exc_info:
                from analysis_LLM import main
                main()
            
            assert exc_info.value.code == 0
            captured = capsys.readouterr()
            assert "Test Model" in captured.out
    
    @patch('analysis_LLM.PROMPTS', {
        "TEST_PROMPT": {
            "TITLE": "Test Prompt",
            "PROMPT_TEXT": "Test prompt text",
            "TEMPERATURE": 0.7,
            "MAX_TOKENS": 500
        }
    })
    def test_main_list_prompts(self, capsys):
        """Test main function with --prompt list."""
        test_args = ['--prompt', 'list']
        
        with patch('sys.argv', ['analysis_LLM.py'] + test_args):
            with pytest.raises(SystemExit) as exc_info:
                from analysis_LLM import main
                main()
            
            assert exc_info.value.code == 0
            captured = capsys.readouterr()
            assert "TEST_PROMPT" in captured.out
    
    def test_main_missing_args(self, capsys):
        """Test main function with missing required arguments."""
        test_args = ['--model', '1']  # Missing image_path and prompt
        
        with patch('sys.argv', ['analysis_LLM.py'] + test_args):
            with pytest.raises(SystemExit) as exc_info:
                from analysis_LLM import main
                main()
            
            assert exc_info.value.code == 1

class TestRetryDecorator:
    """Test cases for retry decorator functionality."""
    
    @patch('analysis_LLM.Config.RETRY_LIMIT', 3)
    @patch('time.sleep')  # Mock sleep to speed up tests
    def test_retry_decorator_success_after_failures(self, mock_sleep):
        """Test retry decorator with eventual success."""
        from analysis_LLM import retry_request
        
        call_count = 0
        
        @retry_request
        def test_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Test error")
            return "success"
        
        result = test_function()
        assert result == "success"
        assert call_count == 3
        assert mock_sleep.call_count == 2  # Should sleep 2 times before success
    
    @patch('analysis_LLM.Config.RETRY_LIMIT', 2)
    @patch('time.sleep')
    def test_retry_decorator_max_retries_exceeded(self, mock_sleep):
        """Test retry decorator when max retries are exceeded."""
        from analysis_LLM import retry_request
        
        @retry_request
        def test_function():
            raise Exception("Persistent error")
        
        with pytest.raises(Exception, match="Persistent error"):
            test_function()
        
        assert mock_sleep.call_count == 1  # Should sleep once before final failure