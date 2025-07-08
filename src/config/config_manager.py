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
from typing import Dict, Any, Optional
from dotenv import load_dotenv

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
    env_content = """# Private Configuration - DO NOT COMMIT TO GITHUB
# Copy this file to .env and fill in your actual API keys

# API Keys (Private - Keep Secret)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
OLLAMA_API_KEY=your_ollama_api_key_here

# API URLs (Private - Keep Secret)
OPENAI_URL=https://api.openai.com/v1
ANTHROPIC_URL=https://api.anthropic.com
GOOGLE_URL=https://generativelanguage.googleapis.com
OLLAMA_URL=http://localhost:11434

# Database Configuration (Private)
DATABASE_URL=sqlite:///image_analysis.db

# Web Server Configuration (Private)
WEB_PORT=5050
SECRET_KEY=your_secret_key_here_change_this_in_production
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
            "ollama_api_key": get_env_value("OLLAMA_API_KEY"),
            "openai_url": get_env_value("OPENAI_URL", "https://api.openai.com/v1"),
            "anthropic_url": get_env_value("ANTHROPIC_URL", "https://api.anthropic.com"),
            "google_url": get_env_value("GOOGLE_URL", "https://generativelanguage.googleapis.com"),
            "ollama_url": get_env_value("OLLAMA_URL", "http://localhost:11434"),
            "database_url": get_env_value("DATABASE_URL", "sqlite:///image_analysis.db"),
            "web_port": int(get_env_value("WEB_PORT", "5050")),
            "secret_key": get_env_value("SECRET_KEY", "change_this_in_production")
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