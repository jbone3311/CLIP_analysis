"""
Professional configuration manager for image analysis project.

Provides comprehensive configuration loading, validation, and management
with environment variable support and proper error handling.
"""

import os
import logging
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from dataclasses import dataclass, field
try:
    from dotenv import load_dotenv  # type: ignore
except ImportError:
    def load_dotenv(file_path):
        """Fallback function if python-dotenv is not installed."""
        pass

from input_validation import ValidationError
from exceptions import ConfigurationError, safe_error_message

logger = logging.getLogger(__name__)

@dataclass
class LLMConfig:
    """Configuration for LLM provider."""
    title: str
    api_url: str
    model_name: str
    api_key: str = ""
    timeout: int = 60
    retry_limit: int = 3
    min_request_interval: float = 0.1
    
    def __post_init__(self):
        """Validate LLM configuration after initialization."""
        if not self.api_url:
            raise ConfigurationError(f"API URL is required for LLM: {self.title}")
        if not self.model_name:
            raise ConfigurationError(f"Model name is required for LLM: {self.title}")

@dataclass
class CLIPConfig:
    """Configuration for CLIP analyzer."""
    api_base_url: str
    model_name: str = "ViT-L-14"
    timeout: int = 60
    retry_limit: int = 3
    min_request_interval: float = 0.1
    default_modes: List[str] = field(default_factory=lambda: ['best', 'fast', 'classic'])
    
    def __post_init__(self):
        """Validate CLIP configuration after initialization."""
        if not self.api_base_url:
            raise ConfigurationError("CLIP API base URL is required")

@dataclass
class ProcessingConfig:
    """Configuration for image processing."""
    image_directory: str = "Images"
    output_directory: str = "Output"
    use_json: bool = True
    use_database: bool = False
    database_path: str = "image_analysis.db"
    max_workers: int = 4
    
    def __post_init__(self):
        """Validate processing configuration after initialization."""
        if self.max_workers < 1:
            raise ConfigurationError("max_workers must be at least 1")

@dataclass
class SecurityConfig:
    """Configuration for security settings."""
    max_file_size: int = 52428800  # 50MB
    max_path_length: int = 260
    allowed_extensions: List[str] = field(default_factory=lambda: ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'])
    enable_path_validation: bool = True
    enable_content_validation: bool = True
    
    def __post_init__(self):
        """Validate security configuration after initialization."""
        if self.max_file_size <= 0:
            raise ConfigurationError("max_file_size must be positive")

@dataclass
class LoggingConfig:
    """Configuration for logging."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = "processing.log"
    log_api_conversations: bool = False
    
    # Status emojis/indicators
    emoji_success: str = "(SUCCESS)"
    emoji_warning: str = "(WARNING)"
    emoji_error: str = "(ERROR)"
    emoji_info: str = "(INFO)"
    emoji_processing: str = "(PROCESSING)"
    emoji_start: str = "(START)"
    emoji_complete: str = "(COMPLETE)"
    
    def __post_init__(self):
        """Validate logging configuration after initialization."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.level.upper() not in valid_levels:
            raise ConfigurationError(f"Invalid logging level: {self.level}")
        self.level = self.level.upper()

class ConfigurationManager:
    """
    Professional configuration manager.
    
    Loads configuration from environment variables with validation
    and provides typed access to configuration sections.
    """
    
    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            env_file: Optional path to .env file (defaults to .env)
        """
        self.env_file = env_file or ".env"
        self._load_environment()
        
        # Load configuration sections
        self.llm_configs = self._load_llm_configs()
        self.clip_config = self._load_clip_config()
        self.processing_config = self._load_processing_config()
        self.security_config = self._load_security_config()
        self.logging_config = self._load_logging_config()
        
        logger.info("Configuration loaded successfully")
    
    def _load_environment(self) -> None:
        """Load environment variables from .env file."""
        try:
            if Path(self.env_file).exists():
                load_dotenv(self.env_file)
                logger.debug(f"Loaded environment from {self.env_file}")
            else:
                logger.warning(f"Environment file {self.env_file} not found, using system environment")
        except Exception as e:
            raise ConfigurationError(f"Failed to load environment: {e}") from e
    
    def _get_env_var(self, key: str, default: Any = None, 
                     var_type: type = str, required: bool = False) -> Any:
        """
        Get environment variable with type conversion and validation.
        
        Args:
            key: Environment variable key
            default: Default value if not found
            var_type: Type to convert to
            required: Whether the variable is required
            
        Returns:
            Converted environment variable value
            
        Raises:
            ConfigurationError: If required variable is missing or conversion fails
        """
        value = os.getenv(key, default)
        
        if required and value is None:
            raise ConfigurationError(f"Required environment variable missing: {key}")
        
        if value is None:
            return default
        
        try:
            if var_type == bool:
                return str(value).lower() in ("true", "1", "t", "yes", "y")
            elif var_type == list:
                return [item.strip() for item in str(value).split(",") if item.strip()]
            else:
                return var_type(value)
        except (ValueError, TypeError) as e:
            raise ConfigurationError(f"Invalid type for {key}: expected {var_type.__name__}, got {value}") from e
    
    def _load_llm_configs(self) -> List[LLMConfig]:
        """Load LLM configurations from environment."""
        llm_configs = []
        
        # Support up to 10 LLM configurations
        for i in range(1, 11):
            title = self._get_env_var(f"LLM_{i}_TITLE")
            if not title:
                continue  # No more LLM configs
            
            try:
                config = LLMConfig(
                    title=title,
                    api_url=self._get_env_var(f"LLM_{i}_API_URL", required=True),
                    model_name=self._get_env_var(f"LLM_{i}_MODEL", required=True),
                    api_key=self._get_env_var(f"LLM_{i}_API_KEY", ""),
                    timeout=self._get_env_var(f"LLM_{i}_TIMEOUT", 60, int),
                    retry_limit=self._get_env_var(f"LLM_{i}_RETRY_LIMIT", 3, int),
                    min_request_interval=self._get_env_var(f"LLM_{i}_MIN_INTERVAL", 0.1, float)
                )
                llm_configs.append(config)
                logger.debug(f"Loaded LLM config {i}: {title}")
                
            except Exception as e:
                logger.error(f"Failed to load LLM config {i}: {safe_error_message(e)}")
                raise ConfigurationError(f"Invalid LLM_{i} configuration: {e}") from e
        
        if not llm_configs:
            logger.warning("No LLM configurations found")
        
        return llm_configs
    
    def _load_clip_config(self) -> CLIPConfig:
        """Load CLIP configuration from environment."""
        try:
            return CLIPConfig(
                api_base_url=self._get_env_var("API_BASE_URL", "http://localhost:7860"),
                model_name=self._get_env_var("CLIP_MODEL_NAME", "ViT-L-14"),
                timeout=self._get_env_var("TIMEOUT", 60, int),
                retry_limit=self._get_env_var("RETRY_LIMIT", 3, int),
                min_request_interval=self._get_env_var("CLIP_MIN_INTERVAL", 0.1, float),
                default_modes=self._get_env_var("CLIP_DEFAULT_MODES", ["best", "fast", "classic"], list)
            )
        except Exception as e:
            raise ConfigurationError(f"Invalid CLIP configuration: {e}") from e
    
    def _load_processing_config(self) -> ProcessingConfig:
        """Load processing configuration from environment."""
        try:
            return ProcessingConfig(
                image_directory=self._get_env_var("IMAGE_DIRECTORY", "Images"),
                output_directory=self._get_env_var("OUTPUT_DIRECTORY", "Output"),
                use_json=self._get_env_var("USE_JSON", True, bool),
                use_database=self._get_env_var("USE_DATABASE", False, bool),
                database_path=self._get_env_var("DATABASE_PATH", "image_analysis.db"),
                max_workers=self._get_env_var("MAX_WORKERS", 4, int)
            )
        except Exception as e:
            raise ConfigurationError(f"Invalid processing configuration: {e}") from e
    
    def _load_security_config(self) -> SecurityConfig:
        """Load security configuration from environment."""
        try:
            return SecurityConfig(
                max_file_size=self._get_env_var("MAX_FILE_SIZE", 52428800, int),
                max_path_length=self._get_env_var("MAX_PATH_LENGTH", 260, int),
                allowed_extensions=self._get_env_var("ALLOWED_EXTENSIONS", 
                                                   ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'], list),
                enable_path_validation=self._get_env_var("ENABLE_PATH_VALIDATION", True, bool),
                enable_content_validation=self._get_env_var("ENABLE_CONTENT_VALIDATION", True, bool)
            )
        except Exception as e:
            raise ConfigurationError(f"Invalid security configuration: {e}") from e
    
    def _load_logging_config(self) -> LoggingConfig:
        """Load logging configuration from environment."""
        try:
            return LoggingConfig(
                level=self._get_env_var("LOGGING_LEVEL", "INFO"),
                format=self._get_env_var("LOGGING_FORMAT", 
                                       "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
                file_path=self._get_env_var("LOG_FILE_PATH", "processing.log"),
                log_api_conversations=self._get_env_var("LOG_API_CONVERSATION", False, bool),
                emoji_success=self._get_env_var("EMOJI_SUCCESS", "(SUCCESS)"),
                emoji_warning=self._get_env_var("EMOJI_WARNING", "(WARNING)"),
                emoji_error=self._get_env_var("EMOJI_ERROR", "(ERROR)"),
                emoji_info=self._get_env_var("EMOJI_INFO", "(INFO)"),
                emoji_processing=self._get_env_var("EMOJI_PROCESSING", "(PROCESSING)"),
                emoji_start=self._get_env_var("EMOJI_START", "(START)"),
                emoji_complete=self._get_env_var("EMOJI_COMPLETE", "(COMPLETE)")
            )
        except Exception as e:
            raise ConfigurationError(f"Invalid logging configuration: {e}") from e
    
    def get_llm_config(self, index: int = 0) -> Optional[LLMConfig]:
        """
        Get LLM configuration by index.
        
        Args:
            index: Index of LLM configuration (0-based)
            
        Returns:
            LLM configuration or None if not found
        """
        if 0 <= index < len(self.llm_configs):
            return self.llm_configs[index]
        return None
    
    def get_llm_config_by_title(self, title: str) -> Optional[LLMConfig]:
        """
        Get LLM configuration by title.
        
        Args:
            title: Title of LLM configuration
            
        Returns:
            LLM configuration or None if not found
        """
        for config in self.llm_configs:
            if config.title == title:
                return config
        return None
    
    def validate_configuration(self) -> List[str]:
        """
        Validate all configuration sections.
        
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Validate directories exist or can be created
        try:
            for directory in [self.processing_config.image_directory, 
                            self.processing_config.output_directory]:
                dir_path = Path(directory)
                if not dir_path.exists():
                    try:
                        dir_path.mkdir(parents=True, exist_ok=True)
                    except OSError as e:
                        errors.append(f"Cannot create directory {directory}: {e}")
        except Exception as e:
            errors.append(f"Directory validation failed: {e}")
        
        # Validate at least one analyzer is configured
        if not self.llm_configs and not self.clip_config.api_base_url:
            errors.append("At least one analyzer (LLM or CLIP) must be configured")
        
        # Validate API keys for enabled LLMs
        for i, llm_config in enumerate(self.llm_configs):
            if not llm_config.api_key and "localhost" not in llm_config.api_url:
                errors.append(f"LLM {i+1} ({llm_config.title}) missing API key")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary format.
        
        Returns:
            Dictionary representation of all configurations
        """
        return {
            "llm_configs": [
                {
                    "title": config.title,
                    "api_url": config.api_url,
                    "model_name": config.model_name,
                    "has_api_key": bool(config.api_key),
                    "timeout": config.timeout,
                    "retry_limit": config.retry_limit
                }
                for config in self.llm_configs
            ],
            "clip_config": {
                "api_base_url": self.clip_config.api_base_url,
                "model_name": self.clip_config.model_name,
                "timeout": self.clip_config.timeout,
                "default_modes": self.clip_config.default_modes
            },
            "processing_config": {
                "image_directory": self.processing_config.image_directory,
                "output_directory": self.processing_config.output_directory,
                "use_json": self.processing_config.use_json,
                "use_database": self.processing_config.use_database,
                "max_workers": self.processing_config.max_workers
            },
            "security_config": {
                "max_file_size": self.security_config.max_file_size,
                "max_path_length": self.security_config.max_path_length,
                "allowed_extensions": self.security_config.allowed_extensions
            },
            "logging_config": {
                "level": self.logging_config.level,
                "log_api_conversations": self.logging_config.log_api_conversations
            }
        }
    
    def setup_logging(self) -> None:
        """Setup logging based on configuration."""
        # Clear existing handlers
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Set logging level
        root_logger.setLevel(getattr(logging, self.logging_config.level))
        
        # Create formatter
        formatter = logging.Formatter(self.logging_config.format)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, self.logging_config.level))
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # File handler (if specified)
        if self.logging_config.file_path:
            try:
                file_handler = logging.FileHandler(self.logging_config.file_path)
                file_handler.setLevel(getattr(logging, self.logging_config.level))
                file_handler.setFormatter(formatter)
                root_logger.addHandler(file_handler)
            except Exception as e:
                logger.warning(f"Failed to setup file logging: {e}")
        
        # Suppress noisy loggers
        logging.getLogger('requests').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        
        logger.info("Logging configured successfully")

# Global configuration instance
_config_manager: Optional[ConfigurationManager] = None

def get_config() -> ConfigurationManager:
    """
    Get global configuration manager instance.
    
    Returns:
        Global configuration manager
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigurationManager()
    return _config_manager

def reload_config(env_file: Optional[str] = None) -> ConfigurationManager:
    """
    Reload configuration from environment.
    
    Args:
        env_file: Optional path to .env file
        
    Returns:
        Reloaded configuration manager
    """
    global _config_manager
    _config_manager = ConfigurationManager(env_file)
    return _config_manager