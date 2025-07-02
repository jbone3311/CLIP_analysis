import pytest
import os
from unittest.mock import patch
from config import Config

class TestConfigDefaults:
    """Test cases for Config class default values."""
    
    def test_config_defaults(self):
        """Test that Config initializes with expected default values."""
        with patch.dict(os.environ, {}, clear=True):
            config = Config()
            
            # API Configuration defaults
            assert config.api_base_url == 'http://localhost:7860'
            assert config.timeout == 30
            
            # CLIP Settings defaults
            assert config.clip_model_name == 'ViT-L-14/openai'
            assert config.enable_clip_analysis is False
            assert config.enable_caption is False
            assert config.enable_best is False
            assert config.enable_fast is False
            assert config.enable_classic is False
            assert config.enable_negative is False
            
            # Processing Settings defaults
            assert config.process_json_to_txt is False
            assert config.enable_llm_analysis is False
            assert config.enable_json_processing is False
            assert config.image_directory == 'Images'
            assert config.output_directory == 'Output'
            assert config.logging_level == 'INFO'
            assert config.log_api_conversation is False
            assert config.retry_limit == 5
            
            # Database defaults
            assert config.use_database is False
            assert config.use_json is True
            assert config.database_path == 'image_analysis.db'
            
            # Emoji defaults
            assert config.EMOJI_SUCCESS == "✅"
            assert config.EMOJI_WARNING == "⚠️"
            assert config.EMOJI_ERROR == "❌"
            assert config.EMOJI_INFO == "ℹ️"
            assert config.EMOJI_PROCESSING == "🔄"
            assert config.EMOJI_START == "🚀"
            assert config.EMOJI_COMPLETE == "🎉"

class TestConfigEnvironmentVariables:
    """Test cases for Config loading from environment variables."""
    
    @patch.dict(os.environ, {
        'API_BASE_URL': 'http://custom:8080',
        'TIMEOUT': '60',
        'CLIP_MODEL_NAME': 'ViT-B-32',
        'ENABLE_CLIP_ANALYSIS': 'true',
        'ENABLE_CAPTION': 'True',
        'ENABLE_BEST': '1',
        'ENABLE_FAST': 't',
        'ENABLE_CLASSIC': 'false',
        'ENABLE_NEGATIVE': 'False',
        'IMAGE_DIRECTORY': '/custom/images',
        'OUTPUT_DIRECTORY': '/custom/output',
        'LOGGING_LEVEL': 'DEBUG',
        'RETRY_LIMIT': '10',
        'USE_DATABASE': 'true',
        'USE_JSON': 'false',
        'DATABASE_PATH': '/custom/db.sqlite'
    })
    def test_config_from_environment(self):
        """Test Config loading values from environment variables."""
        config = Config()
        
        # Verify environment values are loaded
        assert config.api_base_url == 'http://custom:8080'
        assert config.timeout == 60
        assert config.clip_model_name == 'ViT-B-32'
        assert config.enable_clip_analysis is True
        assert config.enable_caption is True
        assert config.enable_best is True
        assert config.enable_fast is True
        assert config.enable_classic is False
        assert config.enable_negative is False
        assert config.image_directory == '/custom/images'
        assert config.output_directory == '/custom/output'
        assert config.logging_level == 'DEBUG'
        assert config.retry_limit == 10
        assert config.use_database is True
        assert config.use_json is False
        assert config.database_path == '/custom/db.sqlite'
    
    @patch.dict(os.environ, {
        'EMOJI_SUCCESS': '✓',
        'EMOJI_WARNING': '!',
        'EMOJI_ERROR': 'X',
        'EMOJI_INFO': 'i',
        'EMOJI_PROCESSING': '~',
        'EMOJI_START': '>',
        'EMOJI_COMPLETE': '*'
    })
    def test_config_custom_emojis(self):
        """Test Config with custom emoji settings."""
        config = Config()
        
        assert config.EMOJI_SUCCESS == '✓'
        assert config.EMOJI_WARNING == '!'
        assert config.EMOJI_ERROR == 'X'
        assert config.EMOJI_INFO == 'i'
        assert config.EMOJI_PROCESSING == '~'
        assert config.EMOJI_START == '>'
        assert config.EMOJI_COMPLETE == '*'

class TestConfigLLMSettings:
    """Test cases for LLM configuration loading."""
    
    @patch.dict(os.environ, {
        'ENABLE_LLM_ANALYSIS': 'true',
        'LLM_1_TITLE': 'OpenAI GPT-4',
        'LLM_1_API_URL': 'https://api.openai.com/v1/chat/completions',
        'LLM_1_API_KEY': 'sk-test123',
        'LLM_1_MODEL': 'gpt-4-vision-preview',
        'LLM_2_TITLE': 'Anthropic Claude',
        'LLM_2_API_URL': 'https://api.anthropic.com/v1/messages',
        'LLM_2_API_KEY': 'sk-ant-test456',
        'LLM_2_MODEL': 'claude-3-opus-20240229'
    })
    def test_config_llm_multiple_models(self):
        """Test Config loading multiple LLM models."""
        config = Config()
        
        assert config.enable_llm_analysis is True
        assert len(config.llms) == 2
        
        # Check first LLM
        llm1 = config.llms[0]
        assert llm1['title'] == 'OpenAI GPT-4'
        assert llm1['api_url'] == 'https://api.openai.com/v1/chat/completions'
        assert llm1['api_key'] == 'sk-test123'
        assert llm1['model'] == 'gpt-4-vision-preview'
        
        # Check second LLM
        llm2 = config.llms[1]
        assert llm2['title'] == 'Anthropic Claude'
        assert llm2['api_url'] == 'https://api.anthropic.com/v1/messages'
        assert llm2['api_key'] == 'sk-ant-test456'
        assert llm2['model'] == 'claude-3-opus-20240229'
    
    @patch.dict(os.environ, {
        'LLM_1_TITLE': 'Test Model',
        'LLM_1_API_URL': 'https://api.test.com',
        # Missing LLM_1_API_KEY
        'LLM_2_TITLE': 'Another Model',
        # Missing LLM_2_API_URL
    })
    def test_config_llm_incomplete_config(self):
        """Test Config handling incomplete LLM configurations."""
        config = Config()
        
        # Only complete configurations should be loaded
        assert len(config.llms) == 0
    
    @patch.dict(os.environ, {
        'LLM_1_TITLE': 'Model 1',
        'LLM_1_API_URL': 'https://api1.test.com',
        'LLM_3_TITLE': 'Model 3',
        'LLM_3_API_URL': 'https://api3.test.com',
        'LLM_5_TITLE': 'Model 5',
        'LLM_5_API_URL': 'https://api5.test.com',
    })
    def test_config_llm_non_sequential(self):
        """Test Config loading non-sequential LLM configurations."""
        config = Config()
        
        # Should load all valid configurations regardless of gaps
        assert len(config.llms) == 3
        assert config.llms[0]['title'] == 'Model 1'
        assert config.llms[1]['title'] == 'Model 3'
        assert config.llms[2]['title'] == 'Model 5'

class TestConfigBooleanParsing:
    """Test cases for boolean value parsing from environment variables."""
    
    @patch.dict(os.environ, {
        'ENABLE_CLIP_ANALYSIS': 'true',
        'ENABLE_CAPTION': 'True',
        'ENABLE_BEST': 'TRUE',
        'ENABLE_FAST': '1',
        'ENABLE_CLASSIC': 't',
        'ENABLE_NEGATIVE': 'false',
        'PROCESS_JSON_TO_TXT': 'False',
        'ENABLE_LLM_ANALYSIS': 'FALSE',
        'USE_DATABASE': '0',
        'USE_JSON': 'f'
    })
    def test_boolean_parsing_variations(self):
        """Test Config parsing various boolean string representations."""
        config = Config()
        
        # Should parse as True
        assert config.enable_clip_analysis is True
        assert config.enable_caption is True
        assert config.enable_best is True
        assert config.enable_fast is True
        assert config.enable_classic is True  # Note: 't' is parsed as True in the implementation
        
        # Should parse as False
        assert config.enable_negative is False
        assert config.process_json_to_txt is False
        assert config.enable_llm_analysis is False
        assert config.use_database is False
        assert config.use_json is False

class TestConfigIntegerParsing:
    """Test cases for integer value parsing from environment variables."""
    
    @patch.dict(os.environ, {
        'TIMEOUT': '120',
        'RETRY_LIMIT': '3'
    })
    def test_integer_parsing(self):
        """Test Config parsing integer values."""
        config = Config()
        
        assert config.timeout == 120
        assert config.retry_limit == 3
        assert isinstance(config.timeout, int)
        assert isinstance(config.retry_limit, int)
    
    @patch.dict(os.environ, {
        'TIMEOUT': 'invalid_int',
        'RETRY_LIMIT': '3.14'
    })
    def test_invalid_integer_parsing(self):
        """Test Config handling invalid integer values."""
        # Should fall back to defaults or raise ValueError
        with pytest.raises(ValueError):
            Config()

class TestConfigValidation:
    """Test cases for Config validation logic."""
    
    def test_config_consistency(self):
        """Test that Config maintains internal consistency."""
        config = Config()
        
        # Verify that boolean settings are actually boolean
        assert isinstance(config.enable_clip_analysis, bool)
        assert isinstance(config.enable_llm_analysis, bool)
        assert isinstance(config.use_database, bool)
        assert isinstance(config.use_json, bool)
        
        # Verify that string settings are strings
        assert isinstance(config.api_base_url, str)
        assert isinstance(config.image_directory, str)
        assert isinstance(config.database_path, str)
        
        # Verify that numeric settings are numeric
        assert isinstance(config.timeout, int)
        assert isinstance(config.retry_limit, int)
    
    @patch.dict(os.environ, {
        'ENABLE_LLM_ANALYSIS': 'true',
        'LLM_1_TITLE': 'Test Model',
        'LLM_1_API_URL': 'https://api.test.com',
        'LLM_1_API_KEY': 'test_key',
        'LLM_1_MODEL': 'test_model'
    })
    def test_config_llm_enabled_with_models(self):
        """Test Config when LLM is enabled and models are configured."""
        config = Config()
        
        assert config.enable_llm_analysis is True
        assert len(config.llms) > 0
        assert all('title' in llm for llm in config.llms)
        assert all('api_url' in llm for llm in config.llms)

class TestConfigFileFormats:
    """Test cases for Config format specifications."""
    
    def test_logging_format_default(self):
        """Test that logging format has a reasonable default."""
        config = Config()
        
        assert config.logging_format == '%(asctime)s - %(levelname)s - %(message)s'
        assert isinstance(config.logging_format, str)
        assert 'levelname' in config.logging_format
        assert 'asctime' in config.logging_format
    
    @patch.dict(os.environ, {
        'LOGGING_FORMAT': '%(name)s - %(levelname)s - %(message)s'
    })
    def test_custom_logging_format(self):
        """Test Config with custom logging format."""
        config = Config()
        
        assert config.logging_format == '%(name)s - %(levelname)s - %(message)s'