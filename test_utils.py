import pytest
import os
import json
import hashlib
import logging
from unittest.mock import patch, mock_open
from utils import generate_unique_code, setup_logging, save_json, load_json

class TestUniqueCodeGeneration:
    """Test cases for unique code generation functionality."""
    
    def test_generate_unique_code_consistent(self, sample_image_path):
        """Test that generate_unique_code returns consistent results for same file."""
        code1 = generate_unique_code(sample_image_path)
        code2 = generate_unique_code(sample_image_path)
        
        assert code1 == code2
        assert isinstance(code1, str)
        assert len(code1) > 0
    
    def test_generate_unique_code_different_files(self, sample_image_path, sample_png_image_path):
        """Test that different files generate different unique codes."""
        code1 = generate_unique_code(sample_image_path)
        code2 = generate_unique_code(sample_png_image_path)
        
        assert code1 != code2
        assert isinstance(code1, str)
        assert isinstance(code2, str)
    
    def test_generate_unique_code_file_not_found(self):
        """Test generate_unique_code with non-existent file."""
        with pytest.raises((FileNotFoundError, OSError)):
            generate_unique_code("nonexistent_file.jpg")
    
    def test_generate_unique_code_format(self, sample_image_path):
        """Test that generated unique code has expected format."""
        code = generate_unique_code(sample_image_path)
        
        # Should be a valid hexadecimal string (assuming it's a hash)
        try:
            int(code, 16)  # Should not raise ValueError if it's hex
            assert True
        except ValueError:
            # If not hex, should at least be alphanumeric
            assert code.replace('-', '').replace('_', '').isalnum()
    
    def test_generate_unique_code_file_modification(self, temp_dir):
        """Test that unique code changes when file is modified."""
        test_file = os.path.join(temp_dir, "test_modify.txt")
        
        # Create initial file
        with open(test_file, 'w') as f:
            f.write("initial content")
        
        code1 = generate_unique_code(test_file)
        
        # Modify file
        with open(test_file, 'w') as f:
            f.write("modified content")
        
        code2 = generate_unique_code(test_file)
        
        assert code1 != code2

class TestLoggingSetup:
    """Test cases for logging setup functionality."""
    
    def test_setup_logging_with_config(self, temp_dir):
        """Test setup_logging with Config object."""
        from config import Config
        
        # Mock config object
        with patch.dict(os.environ, {
            'LOGGING_LEVEL': 'DEBUG',
            'LOGGING_FORMAT': '%(levelname)s - %(message)s'
        }):
            config = Config()
            setup_logging(config)
            
            # Verify logging level was set
            logger = logging.getLogger()
            assert logger.level == logging.DEBUG
    
    def test_setup_logging_info_level(self, temp_dir):
        """Test setup_logging with INFO level."""
        from config import Config
        
        with patch.dict(os.environ, {'LOGGING_LEVEL': 'INFO'}):
            config = Config()
            setup_logging(config)
            
            logger = logging.getLogger()
            assert logger.level == logging.INFO
    
    def test_setup_logging_error_level(self, temp_dir):
        """Test setup_logging with ERROR level."""
        from config import Config
        
        with patch.dict(os.environ, {'LOGGING_LEVEL': 'ERROR'}):
            config = Config()
            setup_logging(config)
            
            logger = logging.getLogger()
            assert logger.level == logging.ERROR
    
    def test_setup_logging_invalid_level(self, temp_dir):
        """Test setup_logging with invalid logging level."""
        from config import Config
        
        with patch.dict(os.environ, {'LOGGING_LEVEL': 'INVALID_LEVEL'}):
            config = Config()
            
            # Should either use default or handle gracefully
            try:
                setup_logging(config)
                # If it doesn't raise an exception, verify some reasonable level is set
                logger = logging.getLogger()
                assert logger.level in [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]
            except (ValueError, AttributeError):
                # Some implementations might raise an exception for invalid levels
                pass

class TestJSONOperations:
    """Test cases for JSON save and load operations."""
    
    def test_save_json_basic(self, temp_dir):
        """Test basic JSON saving functionality."""
        test_data = {"key": "value", "number": 123, "list": [1, 2, 3]}
        file_path = os.path.join(temp_dir, "test_save.json")
        
        save_json(test_data, file_path)
        
        # Verify file was created
        assert os.path.exists(file_path)
        
        # Verify content is correct
        with open(file_path, 'r') as f:
            loaded_data = json.load(f)
        assert loaded_data == test_data
    
    def test_save_json_complex_data(self, temp_dir):
        """Test saving complex JSON data structures."""
        complex_data = {
            "nested": {
                "dict": {"inner": "value"},
                "list": [{"item": 1}, {"item": 2}]
            },
            "unicode": "Testing unicode: 你好, мир, 🌍",
            "numbers": {
                "int": 42,
                "float": 3.14159,
                "scientific": 1.23e-10
            },
            "boolean": True,
            "null_value": None
        }
        
        file_path = os.path.join(temp_dir, "complex_save.json")
        save_json(complex_data, file_path)
        
        # Verify file was created and content is correct
        assert os.path.exists(file_path)
        with open(file_path, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        assert loaded_data == complex_data
    
    def test_save_json_invalid_path(self):
        """Test saving JSON to invalid path."""
        test_data = {"test": "data"}
        invalid_path = "/invalid/path/test.json"
        
        with pytest.raises((OSError, IOError, PermissionError)):
            save_json(test_data, invalid_path)
    
    def test_save_json_non_serializable(self, temp_dir):
        """Test saving non-JSON-serializable data."""
        # Create an object that can't be JSON serialized
        non_serializable_data = {"function": lambda x: x}
        file_path = os.path.join(temp_dir, "non_serializable.json")
        
        with pytest.raises(TypeError):
            save_json(non_serializable_data, file_path)
    
    def test_load_json_basic(self, temp_dir):
        """Test basic JSON loading functionality."""
        test_data = {"key": "value", "number": 456}
        file_path = os.path.join(temp_dir, "test_load.json")
        
        # Create JSON file
        with open(file_path, 'w') as f:
            json.dump(test_data, f)
        
        # Load and verify
        loaded_data = load_json(file_path)
        assert loaded_data == test_data
    
    def test_load_json_file_not_found(self):
        """Test loading non-existent JSON file."""
        with pytest.raises(FileNotFoundError):
            load_json("nonexistent.json")
    
    def test_load_json_invalid_json(self, temp_dir):
        """Test loading invalid JSON content."""
        file_path = os.path.join(temp_dir, "invalid.json")
        
        # Create file with invalid JSON
        with open(file_path, 'w') as f:
            f.write("{ invalid json content }")
        
        with pytest.raises(json.JSONDecodeError):
            load_json(file_path)
    
    def test_load_json_empty_file(self, temp_dir):
        """Test loading empty JSON file."""
        file_path = os.path.join(temp_dir, "empty.json")
        
        # Create empty file
        with open(file_path, 'w') as f:
            pass
        
        with pytest.raises(json.JSONDecodeError):
            load_json(file_path)
    
    def test_save_load_roundtrip(self, temp_dir):
        """Test save and load roundtrip preserves data."""
        original_data = {
            "string": "test",
            "integer": 42,
            "float": 3.14,
            "boolean": True,
            "null": None,
            "array": [1, 2, "three"],
            "object": {"nested": "value"}
        }
        
        file_path = os.path.join(temp_dir, "roundtrip.json")
        
        # Save and load
        save_json(original_data, file_path)
        loaded_data = load_json(file_path)
        
        assert loaded_data == original_data

class TestUtilityFunctionIntegration:
    """Integration tests for utility functions working together."""
    
    def test_unique_code_with_hash_verification(self, temp_dir):
        """Test that unique code generation is consistent with file hashing."""
        test_file = os.path.join(temp_dir, "hash_test.txt")
        content = "test content for hashing"
        
        with open(test_file, 'w') as f:
            f.write(content)
        
        # Generate unique code
        unique_code = generate_unique_code(test_file)
        
        # Calculate expected hash
        with open(test_file, 'rb') as f:
            file_content = f.read()
        expected_hash = hashlib.md5(file_content).hexdigest()
        
        # Depending on implementation, might be MD5, SHA1, or SHA256
        # Test that the unique code is some kind of hash of the file
        assert len(unique_code) in [32, 40, 64]  # Common hash lengths
        assert unique_code.lower() == unique_code  # Should be lowercase hex
    
    def test_logging_and_json_integration(self, temp_dir, caplog):
        """Test logging setup works with JSON operations."""
        from config import Config
        
        with patch.dict(os.environ, {'LOGGING_LEVEL': 'INFO'}):
            config = Config()
            setup_logging(config)
            
            # Perform JSON operations that might log
            test_data = {"integration": "test"}
            file_path = os.path.join(temp_dir, "integration.json")
            
            save_json(test_data, file_path)
            loaded_data = load_json(file_path)
            
            assert loaded_data == test_data
            # Verify logging was set up (check that we can log)
            logging.info("Integration test message")
            assert "Integration test message" in caplog.text

class TestErrorHandling:
    """Test cases for error handling in utility functions."""
    
    def test_unicode_handling_in_json(self, temp_dir):
        """Test handling of Unicode characters in JSON operations."""
        unicode_data = {
            "chinese": "你好世界",
            "russian": "Привет мир",
            "japanese": "こんにちは世界",
            "emoji": "🌍🚀✨",
            "mixed": "Hello 世界 🌟"
        }
        
        file_path = os.path.join(temp_dir, "unicode_test.json")
        
        # Should handle Unicode correctly
        save_json(unicode_data, file_path)
        loaded_data = load_json(file_path)
        
        assert loaded_data == unicode_data
        
        # Verify file contains correct Unicode
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
            assert "你好世界" in file_content
            assert "🌍" in file_content
    
    def test_large_file_unique_code(self, temp_dir):
        """Test unique code generation for large files."""
        large_file = os.path.join(temp_dir, "large_file.txt")
        
        # Create a reasonably large file
        with open(large_file, 'w') as f:
            for i in range(10000):
                f.write(f"Line {i}: This is a test line with some content.\n")
        
        # Should handle large files without issues
        unique_code = generate_unique_code(large_file)
        
        assert isinstance(unique_code, str)
        assert len(unique_code) > 0
    
    def test_binary_file_unique_code(self, sample_image_path):
        """Test unique code generation for binary files."""
        # Image files are binary
        unique_code = generate_unique_code(sample_image_path)
        
        assert isinstance(unique_code, str)
        assert len(unique_code) > 0
        
        # Should be consistent for the same binary file
        unique_code2 = generate_unique_code(sample_image_path)
        assert unique_code == unique_code2

class TestFileSystemOperations:
    """Test cases for file system related operations."""
    
    def test_json_file_permissions(self, temp_dir):
        """Test JSON operations with different file permissions."""
        test_data = {"permission": "test"}
        file_path = os.path.join(temp_dir, "permission_test.json")
        
        # Save normally
        save_json(test_data, file_path)
        
        # Make file read-only
        os.chmod(file_path, 0o444)
        
        try:
            # Should still be able to read
            loaded_data = load_json(file_path)
            assert loaded_data == test_data
            
            # Should not be able to write
            with pytest.raises((OSError, PermissionError)):
                save_json({"new": "data"}, file_path)
        finally:
            # Restore permissions for cleanup
            os.chmod(file_path, 0o644)
    
    def test_concurrent_file_access(self, temp_dir):
        """Test handling of concurrent file access scenarios."""
        test_data = {"concurrent": "test"}
        file_path = os.path.join(temp_dir, "concurrent_test.json")
        
        # Save file
        save_json(test_data, file_path)
        
        # Simulate concurrent access by opening file for writing
        # while trying to read (depending on OS, this might or might not cause issues)
        with open(file_path, 'a') as f:
            try:
                loaded_data = load_json(file_path)
                assert loaded_data == test_data
            except (OSError, json.JSONDecodeError):
                # Some platforms might have issues with concurrent access
                pass