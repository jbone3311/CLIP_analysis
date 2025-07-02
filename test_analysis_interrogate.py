import pytest
import json
import os
from unittest.mock import patch, Mock
import responses
from analysis_interrogate import (
    encode_image_to_base64, save_json, analyze_image, 
    prompt_image, parse_arguments, main
)
import requests

class TestImageEncoding:
    """Test cases for image encoding functionality."""
    
    def test_encode_image_to_base64(self, sample_image_path):
        """Test encoding image to base64."""
        encoded = encode_image_to_base64(sample_image_path)
        
        # Should return a string
        assert isinstance(encoded, str)
        # Should be valid base64 (no whitespace, valid characters)
        assert encoded.replace('+', '').replace('/', '').replace('=', '').isalnum()
        # Should not be empty
        assert len(encoded) > 0
    
    def test_encode_image_file_not_found(self):
        """Test encoding non-existent image file."""
        with pytest.raises(FileNotFoundError, match="Unable to encode image"):
            encode_image_to_base64("nonexistent.jpg")

class TestJSONSaving:
    """Test cases for JSON saving functionality."""
    
    def test_save_json_success(self, temp_dir, capsys):
        """Test successful JSON saving."""
        test_data = {"test": "data", "numbers": [1, 2, 3]}
        filename = os.path.join(temp_dir, "test_output.json")
        
        save_json(test_data, filename)
        
        # Verify file was created
        assert os.path.exists(filename)
        
        # Verify content is correct
        with open(filename, 'r') as f:
            loaded_data = json.load(f)
        assert loaded_data == test_data
        
        # Verify success message was printed
        captured = capsys.readouterr()
        assert f"Saved output to {filename}" in captured.out
    
    def test_save_json_invalid_path(self):
        """Test JSON saving with invalid path."""
        test_data = {"test": "data"}
        invalid_path = "/invalid/path/test.json"
        
        with pytest.raises(IOError, match="Failed to save JSON"):
            save_json(test_data, invalid_path)

class TestAnalyzeImage:
    """Test cases for CLIP image analysis functionality."""
    
    @responses.activate
    def test_analyze_image_success(self, sample_image_path, mock_clip_response):
        """Test successful image analysis."""
        api_url = "http://localhost:7860"
        
        # Mock the API response
        responses.add(
            responses.POST,
            f"{api_url}/interrogator/analyze",
            json=mock_clip_response,
            status=200
        )
        
        result = analyze_image(sample_image_path, api_url, "ViT-L-14")
        
        assert result == mock_clip_response
        
        # Verify the request was made correctly
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        assert request.headers["Content-Type"] == "application/json"
        
        # Verify payload structure
        payload = json.loads(request.body)
        assert "image" in payload
        assert "model" in payload
        assert payload["model"] == "ViT-L-14"
    
    @responses.activate
    def test_analyze_image_api_error(self, sample_image_path):
        """Test image analysis with API error."""
        api_url = "http://localhost:7860"
        
        # Mock API error response
        responses.add(
            responses.POST,
            f"{api_url}/interrogator/analyze",
            json={"error": "Internal server error"},
            status=500
        )
        
        with pytest.raises(ConnectionError, match="API request failed during analysis"):
            analyze_image(sample_image_path, api_url, "ViT-L-14")
    
    @responses.activate
    def test_analyze_image_timeout(self, sample_image_path):
        """Test image analysis with timeout."""
        api_url = "http://localhost:7860"
        
        # Mock timeout
        def timeout_callback(request):
            raise requests.Timeout("Connection timeout")
        
        responses.add_callback(
            responses.POST,
            f"{api_url}/interrogator/analyze",
            callback=timeout_callback
        )
        
        with pytest.raises(ConnectionError, match="API request failed during analysis"):
            analyze_image(sample_image_path, api_url, "ViT-L-14", timeout=1)

class TestPromptImage:
    """Test cases for CLIP prompt generation functionality."""
    
    @responses.activate
    def test_prompt_image_single_mode(self, sample_image_path):
        """Test prompt generation for a single mode."""
        api_url = "http://localhost:7860"
        mock_response = {"prompt": "test prompt", "confidence": 0.9}
        
        responses.add(
            responses.POST,
            f"{api_url}/interrogator/prompt",
            json=mock_response,
            status=200
        )
        
        result = prompt_image(sample_image_path, api_url, "ViT-L-14", ["fast"])
        
        assert "fast" in result
        assert result["fast"] == mock_response
    
    @responses.activate
    def test_prompt_image_multiple_modes(self, sample_image_path):
        """Test prompt generation for multiple modes."""
        api_url = "http://localhost:7860"
        
        # Different responses for different modes
        responses.add(
            responses.POST,
            f"{api_url}/interrogator/prompt",
            json={"prompt": "fast prompt", "mode": "fast"},
            status=200
        )
        responses.add(
            responses.POST,
            f"{api_url}/interrogator/prompt",
            json={"prompt": "best prompt", "mode": "best"},
            status=200
        )
        
        result = prompt_image(sample_image_path, api_url, "ViT-L-14", ["fast", "best"])
        
        assert "fast" in result
        assert "best" in result
        assert len(result) == 2
    
    @responses.activate
    def test_prompt_image_with_error(self, sample_image_path, capsys):
        """Test prompt generation with API error for one mode."""
        api_url = "http://localhost:7860"
        
        # Success for first mode, error for second
        responses.add(
            responses.POST,
            f"{api_url}/interrogator/prompt",
            json={"prompt": "fast prompt"},
            status=200
        )
        responses.add(
            responses.POST,
            f"{api_url}/interrogator/prompt",
            json={"error": "Server error"},
            status=500
        )
        
        result = prompt_image(sample_image_path, api_url, "ViT-L-14", ["fast", "best"])
        
        # Should have results for both modes, but one with error
        assert "fast" in result
        assert "best" in result
        assert "error" in result["best"]
        
        # Should print error message
        captured = capsys.readouterr()
        assert "Failed to get prompt for mode 'best'" in captured.out

class TestArgumentParsing:
    """Test cases for command line argument parsing."""
    
    def test_parse_arguments_default(self):
        """Test argument parsing with default values."""
        test_args = ["test_image.jpg"]
        
        with patch('sys.argv', ['analysis_interrogate.py'] + test_args):
            args = parse_arguments()
            
            assert args.image_path == "test_image.jpg"
            assert args.api_base_url == "http://localhost:7860"
            assert args.model == "ViT-L-14"
            assert args.modes == ['best', 'fast', 'classic', 'negative', 'caption']
            assert args.output == "analysis_results.json"
    
    def test_parse_arguments_custom(self):
        """Test argument parsing with custom values."""
        test_args = [
            "custom_image.png",
            "--api_base_url", "http://custom:8080",
            "--model", "ViT-B-32",
            "--modes", "best", "fast",
            "--output", "custom_output.json"
        ]
        
        with patch('sys.argv', ['analysis_interrogate.py'] + test_args):
            args = parse_arguments()
            
            assert args.image_path == "custom_image.png"
            assert args.api_base_url == "http://custom:8080"
            assert args.model == "ViT-B-32"
            assert args.modes == ["best", "fast"]
            assert args.output == "custom_output.json"

class TestMainFunction:
    """Test cases for main function and full workflow."""
    
    @responses.activate
    def test_main_success(self, sample_image_path, temp_dir, capsys):
        """Test successful main function execution."""
        api_url = "http://localhost:7860"
        output_file = os.path.join(temp_dir, "test_results.json")
        
        # Mock API responses
        responses.add(
            responses.POST,
            f"{api_url}/interrogator/prompt",
            json={"prompt": "test prompt", "mode": "best"},
            status=200
        )
        responses.add(
            responses.POST,
            f"{api_url}/interrogator/analyze",
            json={"analysis": "test analysis"},
            status=200
        )
        
        test_args = [
            sample_image_path,
            "--modes", "best",
            "--output", output_file
        ]
        
        with patch('sys.argv', ['analysis_interrogate.py'] + test_args):
            main()
        
        # Verify output file was created
        assert os.path.exists(output_file)
        
        # Verify file content
        with open(output_file, 'r') as f:
            result_data = json.load(f)
        
        assert "image" in result_data
        assert "model" in result_data
        assert "prompts" in result_data
        assert "analysis" in result_data
        assert result_data["image"] == os.path.abspath(sample_image_path)
    
    def test_main_image_not_found(self, capsys):
        """Test main function with non-existent image."""
        test_args = ["nonexistent.jpg"]
        
        with patch('sys.argv', ['analysis_interrogate.py'] + test_args):
            main()
        
        captured = capsys.readouterr()
        assert "Image file 'nonexistent.jpg' not found" in captured.out
    
    @responses.activate
    def test_main_api_error(self, sample_image_path, capsys):
        """Test main function with API errors."""
        api_url = "http://localhost:7860"
        
        # Mock API error responses
        responses.add(
            responses.POST,
            f"{api_url}/interrogator/prompt",
            json={"error": "Server error"},
            status=500
        )
        responses.add(
            responses.POST,
            f"{api_url}/interrogator/analyze",
            json={"error": "Server error"},
            status=500
        )
        
        test_args = [sample_image_path, "--modes", "best"]
        
        with patch('sys.argv', ['analysis_interrogate.py'] + test_args):
            main()
        
        captured = capsys.readouterr()
        assert "An error occurred during prompt generation" in captured.out
        assert "An error occurred during analysis" in captured.out

class TestIntegration:
    """Integration tests for full workflow."""
    
    @responses.activate
    def test_full_workflow_all_modes(self, sample_image_path, temp_dir):
        """Test complete workflow with all modes."""
        api_url = "http://localhost:7860"
        output_file = os.path.join(temp_dir, "full_test.json")
        
        # Mock responses for all modes
        modes = ["best", "fast", "classic", "negative", "caption"]
        for mode in modes:
            responses.add(
                responses.POST,
                f"{api_url}/interrogator/prompt",
                json={"prompt": f"{mode} prompt", "mode": mode},
                status=200
            )
        
        # Mock analysis response
        responses.add(
            responses.POST,
            f"{api_url}/interrogator/analyze",
            json={"analysis": "comprehensive analysis", "confidence": 0.95},
            status=200
        )
        
        test_args = [
            sample_image_path,
            "--modes"] + modes + [
            "--output", output_file
        ]
        
        with patch('sys.argv', ['analysis_interrogate.py'] + test_args):
            main()
        
        # Verify all modes were processed
        with open(output_file, 'r') as f:
            result_data = json.load(f)
        
        assert len(result_data["prompts"]) == len(modes)
        for mode in modes:
            assert mode in result_data["prompts"]
            assert result_data["prompts"][mode]["prompt"] == f"{mode} prompt"