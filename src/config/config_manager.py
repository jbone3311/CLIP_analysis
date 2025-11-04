#!/usr/bin/env python3
"""
Configuration Manager

Manages application configuration with separate handling for:
- Private data (API keys, URLs) in .env file
- Public settings in config.json file
"""

import os
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from dotenv import load_dotenv
from .config_models import AppConfig, CLIPConfig, LLMConfig, DatabaseConfig, WebConfig, AnalysisConfig, DirectoryConfig

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def get_project_root() -> str:
    """Get the project root directory"""
    return str(project_root)


def load_env_file(project_root: str = None) -> bool:
    """Load environment variables from .env file"""
    if project_root is None:
        project_root = get_project_root()
    
    env_file = os.path.join(project_root, '.env')
    if os.path.exists(env_file):
        load_dotenv(env_file)
        return True
    return False


def create_default_env_file(project_root: str = None) -> bool:
    """Create default .env file with API keys and private settings"""
    if project_root is None:
        project_root = get_project_root()
    
    env_file = os.path.join(project_root, '.env')
    
    # Private configuration (API keys, URLs, etc.)
    # This should match secure_env_example.txt exactly
    env_content = """# =============================================================================
# SECURE CONFIGURATION - API Keys and Sensitive Data Only
# =============================================================================
# Copy this file to .env and add your actual API keys
# cp secure_env_example.txt .env
# 
# WARNING: Never commit .env to version control!
# This file contains sensitive API keys and secrets.

# =============================================================================
# API Keys - Add your actual keys here
# =============================================================================

# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic API Key  
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Google API Key
GOOGLE_API_KEY=your_google_api_key_here

# Grok (xAI) API Key
GROK_API_KEY=your_grok_api_key_here

# Cohere API Key
COHERE_API_KEY=your_cohere_api_key_here

# Mistral API Key
MISTRAL_API_KEY=your_mistral_api_key_here

# Perplexity API Key
PERPLEXITY_API_KEY=your_perplexity_api_key_here

# =============================================================================
# Database Configuration (Sensitive)
# =============================================================================
# SQLite database file path
DATABASE_PATH=image_analysis.db

# =============================================================================
# Security Configuration (Sensitive)
# =============================================================================
# Secret key for Flask sessions (change this in production!)
FLASK_SECRET_KEY=your-secret-key-here-change-this-in-production

# =============================================================================
# API URLs (usually don't need to change)
# =============================================================================
OPENAI_URL=https://api.openai.com/v1
ANTHROPIC_URL=https://api.anthropic.com/v1
GOOGLE_URL=https://generativelanguage.googleapis.com/v1
GROK_URL=https://api.x.ai/v1
COHERE_URL=https://api.cohere.ai/v1
MISTRAL_URL=https://api.mistral.ai/v1
PERPLEXITY_URL=https://api.perplexity.ai

# Ollama server URL
OLLAMA_URL=http://localhost:11434

# =============================================================================
# CLIP API Configuration
# =============================================================================
# CLIP API Base URL (change to your CLIP service endpoint)
CLIP_API_URL=http://localhost:7860

# CLIP API Password (required for authenticated Forge/Pinokio APIs)
# Leave empty if your CLIP API doesn't require authentication
# Add your password here if needed
CLIP_API_PASSWORD=

# CLIP Model Configuration
CLIP_MODEL_NAME=ViT-L-14/openai

# CLIP Analysis Modes (comma-separated: best,fast,classic,negative,caption)
CLIP_MODES=best,fast,classic,negative,caption

# CLIP API Timeout (seconds)
CLIP_API_TIMEOUT=300

# =============================================================================
# Web Server Configuration (Private)
# =============================================================================
WEB_PORT=5050
SECRET_KEY=your_secret_key_here_change_this_in_production

# =============================================================================
# Directory Configuration (Optional - defaults provided)
# =============================================================================
# Image input directory (default: Images)
IMAGE_DIRECTORY=Images

# Output directory for analysis results (default: Output)
OUTPUT_DIRECTORY=Output

# =============================================================================
# Logging Configuration (Optional - defaults provided)
# =============================================================================
# Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Log file path (default: app.log)
LOG_FILE=app.log

# Error log file path (default: errors.log)
ERROR_LOG_FILE=errors.log

# Maximum log file size in bytes (default: 10MB)
LOG_MAX_SIZE=10485760

# Number of backup log files to keep (default: 5)
LOG_BACKUP_COUNT=5

# =============================================================================
# Analysis Configuration (Optional - defaults provided)
# =============================================================================
# Enable CLIP analysis (True/False)
ENABLE_CLIP_ANALYSIS=True

# Enable LLM analysis (True/False)
ENABLE_LLM_ANALYSIS=True

# Enable metadata extraction (True/False)
ENABLE_METADATA_EXTRACTION=True

# Enable parallel processing (True/False)
ENABLE_PARALLEL_PROCESSING=False

# Generate summaries (True/False)
GENERATE_SUMMARIES=True

# Force reprocessing even if cached (True/False)
FORCE_REPROCESS=False

# Enable debug mode (True/False)
DEBUG=False

# Prompt choices (comma-separated: P1,P2,P3,P4,P5)
PROMPT_CHOICES=P1,P2
"""
    
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        print(f"✅ Created .env file at {env_file}")
        print("⚠️  IMPORTANT: Edit .env file and add your actual API keys!")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False


def create_default_config_file(project_root: str = None) -> bool:
    """Create default config.json file with public settings"""
    if project_root is None:
        project_root = get_project_root()
    
    config_file = os.path.join(project_root, 'config.json')
    
    # Public configuration (safe to commit to GitHub)
    default_config = {
        "clip_config": {
            "api_base_url": "http://localhost:7860",
            "model_name": "ViT-L-14/openai",
            "enable_clip_analysis": True,
            "clip_modes": ["best", "fast", "classic"],
            "prompt_choices": ["P1", "P2", "P3", "P4", "P5"]
        },
        "analysis_features": {
            "enable_llm_analysis": True,
            "enable_metadata_extraction": True,
            "enable_parallel_processing": True,
            "generate_summaries": True,
            "retry_limit": 3,
            "timeout": 120
        },
        "logging": {
            "level": "INFO",
            "file": "app.log",
            "max_size": "10MB",
            "backup_count": 5
        },
        "ui_settings": {
            "theme": "light",
            "language": "en",
            "auto_refresh": True,
            "refresh_interval": 30
        },
        "file_handling": {
            "max_file_size": "50MB",
            "allowed_extensions": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"],
            "output_format": "json",
            "compress_output": False
        }
    }
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        print(f"✅ Created config.json file at {config_file}")
        return True
    except Exception as e:
        print(f"❌ Error creating config.json file: {e}")
        return False


def load_config_file(project_root: str = None) -> Dict[str, Any]:
    """Load public configuration from config.json"""
    if project_root is None:
        project_root = get_project_root()
    
    config_file = os.path.join(project_root, 'config.json')
    
    if not os.path.exists(config_file):
        print(f"⚠️  Config file not found: {config_file}")
        print("Creating default config file...")
        create_default_config_file(project_root)
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"❌ Error loading config file: {e}")
        return {}


def save_config_file(config: Dict[str, Any], project_root: str = None) -> bool:
    """Save public configuration to config.json"""
    if project_root is None:
        project_root = get_project_root()
    
    config_file = os.path.join(project_root, 'config.json')
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ Error saving config file: {e}")
        return False


def get_env_value(key: str, default: str = None) -> str:
    """Get environment variable value"""
    return os.getenv(key, default)


def get_config_value(key: str, default: Any = None, project_root: str = None) -> Any:
    """
    Get a configuration value from either .env or config.json.
    This is the recommended way to access configuration values.
    
    Args:
        key: Configuration key (e.g., 'CLIP_API_URL', 'WEB_PORT')
        default: Default value if not found
        project_root: Optional project root directory
    
    Returns:
        Configuration value (string, int, bool, or list as appropriate)
    
    Examples:
        >>> api_url = get_config_value('CLIP_API_URL', 'http://localhost:7860')
        >>> password = get_config_value('CLIP_API_PASSWORD')
        >>> port = get_config_value('WEB_PORT', 5050)
    """
    # Load environment variables first
    load_env_file(project_root)
    
    # Try to get from environment variables first
    env_value = os.getenv(key)
    if env_value is not None:
        # Convert to appropriate type based on key
        if key in ['WEB_PORT', 'CLIP_API_TIMEOUT']:
            try:
                return int(env_value)
            except ValueError:
                return default if default is not None else env_value
        elif key in ['ENABLE_CLIP_ANALYSIS', 'ENABLE_LLM_ANALYSIS', 'ENABLE_PARALLEL_PROCESSING', 
                     'ENABLE_METADATA_EXTRACTION', 'DEBUG', 'FORCE_REPROCESS', 'GENERATE_SUMMARIES']:
            return env_value.lower() in ('true', '1', 'yes', 'on')
        elif key in ['CLIP_MODES', 'PROMPT_CHOICES']:
            return [m.strip() for m in env_value.split(',')]
        else:
            return env_value
    
    # Try to get from combined config structure
    try:
        combined = get_combined_config(project_root)
        
        # Map common keys to config structure
        key_mapping = {
            'CLIP_API_URL': ('private', 'clip_api_url'),
            'CLIP_API_PASSWORD': ('private', 'clip_api_password'),
            'CLIP_MODEL_NAME': ('private', 'clip_model_name'),
            'CLIP_MODES': ('private', 'clip_modes'),
            'CLIP_API_TIMEOUT': ('private', 'clip_api_timeout'),
            'API_BASE_URL': ('private', 'clip_api_url'),  # Legacy support
            'WEB_PORT': ('private', 'web_port'),
            'DATABASE_PATH': ('private', 'database_path'),
            'DATABASE_URL': ('private', 'database_url'),
            'OPENAI_API_KEY': ('private', 'openai_api_key'),
            'ANTHROPIC_API_KEY': ('private', 'anthropic_api_key'),
            'OLLAMA_URL': ('private', 'ollama_url'),
        }
        
        if key in key_mapping:
            section, subkey = key_mapping[key]
            value = combined.get(section, {}).get(subkey)
            if value is not None:
                return value
        
        # Check public config for feature flags
        public = combined.get('public', {})
        clip_config = public.get('clip_config', {})
        analysis_features = public.get('analysis_features', {})
        
        if key == 'ENABLE_CLIP_ANALYSIS':
            return clip_config.get('enable_clip_analysis', default if default is not None else True)
        elif key == 'ENABLE_LLM_ANALYSIS':
            return analysis_features.get('enable_llm_analysis', default if default is not None else True)
        elif key == 'ENABLE_PARALLEL_PROCESSING':
            return analysis_features.get('enable_parallel_processing', default if default is not None else False)
        elif key == 'ENABLE_METADATA_EXTRACTION':
            return analysis_features.get('enable_metadata_extraction', default if default is not None else True)
        elif key == 'CLIP_MODEL_NAME' and not env_value:
            return clip_config.get('model_name', default if default is not None else 'ViT-L-14/openai')
        elif key == 'CLIP_MODES' and not env_value:
            modes = clip_config.get('clip_modes', [])
            if modes:
                return modes
    except Exception:
        pass
    
    return default


def load_typed_config(project_root: str = None) -> AppConfig:
    """
    Load configuration as a typed AppConfig dataclass.
    This is the recommended way to access configuration with type safety.
    
    Args:
        project_root: Optional project root directory
    
    Returns:
        AppConfig: Typed configuration object
    
    Example:
        >>> config = load_typed_config()
        >>> api_url = config.clip.api_url
        >>> password = config.clip.api_password
        >>> port = config.web.port
    """
    # Load environment variables first
    load_env_file(project_root)
    
    # Load combined config
    combined = get_combined_config(project_root)
    private = combined.get('private', {})
    public = combined.get('public', {})
    
    # Build CLIP config
    clip_modes = private.get('clip_modes', 'best,fast,classic,negative,caption')
    if isinstance(clip_modes, str):
        clip_modes = [m.strip() for m in clip_modes.split(',')]
    
    clip_config = CLIPConfig(
        api_url=private.get('clip_api_url', 'http://localhost:7860'),
        api_password=private.get('clip_api_password'),
        model_name=private.get('clip_model_name', 'ViT-L-14/openai'),
        modes=clip_modes,
        timeout=int(private.get('clip_api_timeout', 300)),
    )
    
    # Build LLM config
    llm_config = LLMConfig(
        openai_api_key=private.get('openai_api_key'),
        openai_url=private.get('openai_url', 'https://api.openai.com/v1'),
        anthropic_api_key=private.get('anthropic_api_key'),
        anthropic_url=private.get('anthropic_url', 'https://api.anthropic.com/v1'),
        google_api_key=private.get('google_api_key'),
        google_url=private.get('google_url', 'https://generativelanguage.googleapis.com/v1'),
        grok_api_key=private.get('grok_api_key'),
        grok_url=private.get('grok_url', 'https://api.x.ai/v1'),
        cohere_api_key=private.get('cohere_api_key'),
        cohere_url=private.get('cohere_url', 'https://api.cohere.ai/v1'),
        mistral_api_key=private.get('mistral_api_key'),
        mistral_url=private.get('mistral_url', 'https://api.mistral.ai/v1'),
        perplexity_api_key=private.get('perplexity_api_key'),
        perplexity_url=private.get('perplexity_url', 'https://api.perplexity.ai'),
        ollama_url=private.get('ollama_url', 'http://localhost:11434'),
    )
    
    # Build Database config
    db_config = DatabaseConfig(
        path=private.get('database_path', 'image_analysis.db'),
        url=private.get('database_url', 'sqlite:///image_analysis.db'),
    )
    
    # Build Web config
    web_config = WebConfig(
        port=int(private.get('web_port', 5050)),
        secret_key=private.get('secret_key', 'change_this_in_production'),
        flask_secret_key=private.get('flask_secret_key', 'change_this_in_production'),
        host='0.0.0.0',
        debug=os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes', 'on'),
    )
    
    # Build Analysis config
    analysis_features = public.get('analysis_features', {})
    clip_cfg = public.get('clip_config', {})
    analysis_config = AnalysisConfig(
        enable_clip_analysis=clip_cfg.get('enable_clip_analysis', True),
        enable_llm_analysis=analysis_features.get('enable_llm_analysis', True),
        enable_metadata_extraction=analysis_features.get('enable_metadata_extraction', True),
        enable_parallel_processing=analysis_features.get('enable_parallel_processing', False),
        generate_summaries=analysis_features.get('generate_summaries', True),
        force_reprocess=os.getenv('FORCE_REPROCESS', 'False').lower() in ('true', '1', 'yes', 'on'),
    )
    
    # Build Directory config
    dir_config = DirectoryConfig(
        image_directory=os.getenv('IMAGE_DIRECTORY', 'Images'),
        output_directory=os.getenv('OUTPUT_DIRECTORY', 'Output'),
        log_directory='logs',
    )
    
    # Build main config
    app_config = AppConfig(
        clip=clip_config,
        llm=llm_config,
        database=db_config,
        web=web_config,
        analysis=analysis_config,
        directories=dir_config,
        debug=os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes', 'on'),
    )
    
    return app_config


def get_all_config(project_root: str = None) -> Dict[str, Any]:
    """
    Get all configuration as a flat dictionary with uppercase keys.
    This provides backward compatibility with code expecting os.getenv() style access.
    
    Args:
        project_root: Optional project root directory
    
    Returns:
        Dictionary with all configuration values using uppercase keys
    """
    combined = get_combined_config(project_root)
    config = {}
    
    # Add private config
    private = combined.get('private', {})
    config.update({
        'CLIP_API_URL': private.get('clip_api_url', 'http://localhost:7860'),
        'CLIP_API_PASSWORD': private.get('clip_api_password'),
        'CLIP_MODEL_NAME': private.get('clip_model_name', 'ViT-L-14/openai'),
        'CLIP_MODES': private.get('clip_modes', 'best,fast,classic,negative,caption').split(',') if isinstance(private.get('clip_modes'), str) else private.get('clip_modes', ['best', 'fast', 'classic']),
        'CLIP_API_TIMEOUT': private.get('clip_api_timeout', 300),
        'API_BASE_URL': private.get('clip_api_url', 'http://localhost:7860'),  # Legacy support
        'WEB_PORT': private.get('web_port', 5050),
        'DATABASE_PATH': private.get('database_path', 'image_analysis.db'),
        'DATABASE_URL': private.get('database_url', 'sqlite:///image_analysis.db'),
        'OPENAI_API_KEY': private.get('openai_api_key', ''),
        'ANTHROPIC_API_KEY': private.get('anthropic_api_key', ''),
        'GOOGLE_API_KEY': private.get('google_api_key', ''),
        'GROK_API_KEY': private.get('grok_api_key', ''),
        'COHERE_API_KEY': private.get('cohere_api_key', ''),
        'MISTRAL_API_KEY': private.get('mistral_api_key', ''),
        'PERPLEXITY_API_KEY': private.get('perplexity_api_key', ''),
        'OPENAI_URL': private.get('openai_url', 'https://api.openai.com/v1'),
        'ANTHROPIC_URL': private.get('anthropic_url', 'https://api.anthropic.com/v1'),
        'OLLAMA_URL': private.get('ollama_url', 'http://localhost:11434'),
        'SECRET_KEY': private.get('secret_key', 'change_this_in_production'),
        'FLASK_SECRET_KEY': private.get('flask_secret_key', 'change_this_in_production'),
    })
    
    # Add public config
    public = combined.get('public', {})
    clip_config = public.get('clip_config', {})
    analysis_features = public.get('analysis_features', {})
    
    config.update({
        'ENABLE_CLIP_ANALYSIS': clip_config.get('enable_clip_analysis', True),
        'ENABLE_LLM_ANALYSIS': analysis_features.get('enable_llm_analysis', True),
        'ENABLE_PARALLEL_PROCESSING': analysis_features.get('enable_parallel_processing', False),
        'ENABLE_METADATA_EXTRACTION': analysis_features.get('enable_metadata_extraction', True),
        'GENERATE_SUMMARIES': analysis_features.get('generate_summaries', True),
        'IMAGE_DIRECTORY': 'Images',  # Default
        'OUTPUT_DIRECTORY': 'Output',  # Default
        'DEBUG': False,
        'FORCE_REPROCESS': False,
    })
    
    # Override with environment variables if they exist (env takes precedence)
    load_env_file(project_root)
    for key in config.keys():
        env_value = os.getenv(key)
        if env_value is not None:
            if key in ['WEB_PORT', 'CLIP_API_TIMEOUT']:
                try:
                    config[key] = int(env_value)
                except ValueError:
                    pass
            elif key in ['ENABLE_CLIP_ANALYSIS', 'ENABLE_LLM_ANALYSIS', 'ENABLE_PARALLEL_PROCESSING',
                        'ENABLE_METADATA_EXTRACTION', 'DEBUG', 'FORCE_REPROCESS', 'GENERATE_SUMMARIES']:
                config[key] = env_value.lower() in ('true', '1', 'yes', 'on')
            elif key in ['CLIP_MODES', 'PROMPT_CHOICES']:
                config[key] = [m.strip() for m in env_value.split(',')]
            else:
                config[key] = env_value
    
    return config


def set_env_value(key: str, value: str, project_root: str = None) -> bool:
    """Set environment variable in .env file"""
    if project_root is None:
        project_root = get_project_root()
    
    env_file = os.path.join(project_root, '.env')
    
    # Read existing .env file
    env_lines = []
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            env_lines = f.readlines()
    
    # Update or add the key-value pair
    key_found = False
    for i, line in enumerate(env_lines):
        if line.strip().startswith(f"{key}="):
            env_lines[i] = f"{key}={value}\n"
            key_found = True
            break
    
    if not key_found:
        env_lines.append(f"{key}={value}\n")
    
    # Write back to .env file
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.writelines(env_lines)
        return True
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")
        return False


def get_combined_config(project_root: str = None) -> Dict[str, Any]:
    """Get combined configuration from both .env and config.json"""
    # Load environment variables
    load_env_file(project_root)
    
    # Load public config
    public_config = load_config_file(project_root)
    
    # Combine with environment variables
    combined_config = {
        "public": public_config,
        "private": {
            "openai_api_key": get_env_value("OPENAI_API_KEY"),
            "anthropic_api_key": get_env_value("ANTHROPIC_API_KEY"),
            "google_api_key": get_env_value("GOOGLE_API_KEY"),
            "grok_api_key": get_env_value("GROK_API_KEY"),
            "cohere_api_key": get_env_value("COHERE_API_KEY"),
            "mistral_api_key": get_env_value("MISTRAL_API_KEY"),
            "perplexity_api_key": get_env_value("PERPLEXITY_API_KEY"),
            "openai_url": get_env_value("OPENAI_URL", "https://api.openai.com/v1"),
            "anthropic_url": get_env_value("ANTHROPIC_URL", "https://api.anthropic.com/v1"),
            "google_url": get_env_value("GOOGLE_URL", "https://generativelanguage.googleapis.com/v1"),
            "grok_url": get_env_value("GROK_URL", "https://api.x.ai/v1"),
            "cohere_url": get_env_value("COHERE_URL", "https://api.cohere.ai/v1"),
            "mistral_url": get_env_value("MISTRAL_URL", "https://api.mistral.ai/v1"),
            "perplexity_url": get_env_value("PERPLEXITY_URL", "https://api.perplexity.ai"),
            "ollama_url": get_env_value("OLLAMA_URL", "http://localhost:11434"),
            "clip_api_url": get_env_value("CLIP_API_URL", "http://localhost:7860"),
            "clip_api_password": get_env_value("CLIP_API_PASSWORD"),
            "clip_model_name": get_env_value("CLIP_MODEL_NAME", "ViT-L-14/openai"),
            "clip_modes": get_env_value("CLIP_MODES", "best,fast,classic,negative,caption"),
            "clip_api_timeout": int(get_env_value("CLIP_API_TIMEOUT", "300")),
            "database_path": get_env_value("DATABASE_PATH", "image_analysis.db"),
            "database_url": get_env_value("DATABASE_URL", "sqlite:///image_analysis.db"),
            "web_port": int(get_env_value("WEB_PORT", "5050")),
            "secret_key": get_env_value("SECRET_KEY", "change_this_in_production"),
            "flask_secret_key": get_env_value("FLASK_SECRET_KEY", "change_this_in_production")
        }
    }
    
    return combined_config


def update_public_config(updates: Dict[str, Any], project_root: str = None) -> bool:
    """Update public configuration in config.json"""
    config = load_config_file(project_root)
    
    # Deep merge updates
    def deep_merge(target, source):
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                deep_merge(target[key], value)
            else:
                target[key] = value
    
    deep_merge(config, updates)
    
    return save_config_file(config, project_root)


def update_private_config(updates: Dict[str, str], project_root: str = None) -> bool:
    """Update private configuration in .env file"""
    success = True
    for key, value in updates.items():
        if not set_env_value(key, value, project_root):
            success = False
    return success


def setup_initial_config(project_root: str = None) -> bool:
    """Set up initial configuration files"""
    if project_root is None:
        project_root = get_project_root()
    
    print("🔧 Setting up configuration files...")
    
    # Create .env file if it doesn't exist
    env_file = os.path.join(project_root, '.env')
    if not os.path.exists(env_file):
        print("📝 Creating .env file for private configuration...")
        if not create_default_env_file(project_root):
            return False
    
    # Create config.json file if it doesn't exist
    config_file = os.path.join(project_root, 'config.json')
    if not os.path.exists(config_file):
        print("📝 Creating config.json file for public configuration...")
        if not create_default_config_file(project_root):
            return False
    
    print("✅ Configuration setup complete!")
    print(f"📁 Private config: {env_file}")
    print(f"📁 Public config: {config_file}")
    print("⚠️  Remember to add your API keys to the .env file!")
    
    return True


def validate_config(project_root: str = None) -> Dict[str, Any]:
    """Validate configuration and return issues"""
    issues = {
        "errors": [],
        "warnings": []
    }
    
    # Load combined config
    config = get_combined_config(project_root)
    
    # Check for missing API keys
    private_config = config["private"]
    if not private_config["openai_api_key"] or private_config["openai_api_key"] == "your_openai_api_key_here":
        issues["warnings"].append("OpenAI API key not set")
    
    if not private_config["anthropic_api_key"] or private_config["anthropic_api_key"] == "your_anthropic_api_key_here":
        issues["warnings"].append("Anthropic API key not set")
    
    # Check for default secret key
    if private_config["secret_key"] == "change_this_in_production":
        issues["warnings"].append("Using default secret key - change this in production")
    
    # Check for valid port
    if not (1024 <= private_config["web_port"] <= 65535):
        issues["errors"].append(f"Invalid web port: {private_config['web_port']}")
    
    return issues


def validate_api_key(api_key: str, api_url: str) -> bool:
    """Validate an API key by making a test request"""
    import requests
    
    if not api_key or api_key == "your_api_key_here":
        return False
    
    try:
        # Make a simple test request to validate the API key
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(f"{api_url}/models", headers=headers, timeout=10)
        return response.status_code == 200
    except Exception:
        return False


def test_clip_connection(api_url: str) -> bool:
    """Test connection to CLIP API"""
    import requests
    
    try:
        response = requests.get(f"{api_url}/", timeout=10)
        return response.status_code == 200
    except Exception:
        return False


def test_llm_connection(api_url: str, api_key: str, model_name: str) -> bool:
    """Test connection to LLM API"""
    import requests
    
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 10
        }
        response = requests.post(f"{api_url}/chat/completions", headers=headers, json=payload, timeout=10)
        return response.status_code == 200
    except Exception:
        return False


if __name__ == "__main__":
    # Interactive setup
    print("🔧 CLIP Analysis Configuration Setup")
    print("=" * 50)
    
    if setup_initial_config():
        print("\n📋 Configuration Summary:")
        config = get_combined_config()
        
        print("\n🔐 Private Configuration (.env):")
        private = config["private"]
        print(f"  • OpenAI API Key: {'✅ Set' if private['openai_api_key'] and private['openai_api_key'] != 'your_openai_api_key_here' else '❌ Not set'}")
        print(f"  • Anthropic API Key: {'✅ Set' if private['anthropic_api_key'] and private['anthropic_api_key'] != 'your_anthropic_api_key_here' else '❌ Not set'}")
        print(f"  • Web Port: {private['web_port']}")
        
        print("\n⚙️  Public Configuration (config.json):")
        public = config["public"]
        print(f"  • CLIP Model: {public.get('clip_config', {}).get('model_name', 'Not set')}")
        print(f"  • CLIP Analysis: {'✅ Enabled' if public.get('clip_config', {}).get('enable_clip_analysis') else '❌ Disabled'}")
        print(f"  • LLM Analysis: {'✅ Enabled' if public.get('analysis_features', {}).get('enable_llm_analysis') else '❌ Disabled'}")
        
        # Validate configuration
        issues = validate_config()
        if issues["errors"]:
            print("\n❌ Configuration Errors:")
            for error in issues["errors"]:
                print(f"  • {error}")
        
        if issues["warnings"]:
            print("\n⚠️  Configuration Warnings:")
            for warning in issues["warnings"]:
                print(f"  • {warning}")
        
        if not issues["errors"] and not issues["warnings"]:
            print("\n🎉 Configuration is valid and ready to use!")
    else:
        print("❌ Configuration setup failed!")
        sys.exit(1) 