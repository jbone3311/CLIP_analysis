#!/usr/bin/env python3
"""
Test script to verify configuration saving works
"""

import os
import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_config_saving():
    """Test that configuration saving works"""
    print("🧪 Testing Configuration Saving...")
    
    try:
        from src.config.config_manager import create_env_file, create_default_env_file
        
        # Test creating default config
        print("📝 Creating default configuration...")
        if create_default_env_file():
            print("✅ Default configuration created successfully")
        else:
            print("❌ Failed to create default configuration")
            return False
        
        # Check if .env file exists
        if os.path.exists('.env'):
            print("✅ .env file exists")
            
            # Read and display the content
            with open('.env', 'r') as f:
                content = f.read()
                print(f"📄 .env file content ({len(content)} characters):")
                print("-" * 40)
                print(content[:500] + "..." if len(content) > 500 else content)
                print("-" * 40)
        else:
            print("❌ .env file not found")
            return False
        
        # Test custom configuration
        print("\n📝 Creating custom configuration...")
        custom_config = {
            'API_BASE_URL': 'http://localhost:8080',
            'CLIP_MODEL_NAME': 'ViT-B-32/openai',
            'ENABLE_CLIP_ANALYSIS': True,
            'ENABLE_LLM_ANALYSIS': False,
            'CLIP_MODES': ['best', 'fast', 'classic'],
            'PROMPT_CHOICES': ['P1'],
            'IMAGE_DIRECTORY': 'MyImages',
            'OUTPUT_DIRECTORY': 'MyOutput',
            'LLM_MODELS': [],
            'OLLAMA_URL': 'http://localhost:11434',
            'OPENAI_API_KEY': 'test_key_123',
            'OPENAI_URL': 'https://api.openai.com/v1'
        }
        
        if create_env_file(custom_config):
            print("✅ Custom configuration created successfully")
            
            # Verify the changes
            with open('.env', 'r') as f:
                content = f.read()
                if 'http://localhost:8080' in content:
                    print("✅ Custom API URL saved correctly")
                else:
                    print("❌ Custom API URL not found in .env")
                    return False
                
                if 'ViT-B-32/openai' in content:
                    print("✅ Custom CLIP model saved correctly")
                else:
                    print("❌ Custom CLIP model not found in .env")
                    return False
        else:
            print("❌ Failed to create custom configuration")
            return False
        
        print("\n🎉 Configuration saving test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Configuration saving test failed: {e}")
        return False

def test_config_loading():
    """Test that configuration loading works"""
    print("\n🧪 Testing Configuration Loading...")
    
    try:
        from main import get_default_config
        
        # Load configuration
        config = get_default_config()
        
        # Check that key values are loaded
        required_keys = [
            'API_BASE_URL', 'CLIP_MODEL_NAME', 'ENABLE_CLIP_ANALYSIS',
            'ENABLE_LLM_ANALYSIS', 'IMAGE_DIRECTORY', 'OUTPUT_DIRECTORY'
        ]
        
        for key in required_keys:
            if key in config:
                print(f"✅ {key}: {config[key]}")
            else:
                print(f"❌ {key} not found in configuration")
                return False
        
        # Check that custom values are loaded (if we set them)
        if config.get('API_BASE_URL') == 'http://localhost:8080':
            print("✅ Custom API URL loaded correctly")
        else:
            print(f"⚠️  API URL is: {config.get('API_BASE_URL')} (may be default)")
        
        print("\n🎉 Configuration loading test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Configuration loading test failed: {e}")
        return False

def main():
    """Run configuration tests"""
    print("🚀 Testing Configuration System...")
    print("=" * 50)
    
    # Test saving
    if not test_config_saving():
        print("\n❌ Configuration saving test failed")
        return 1
    
    # Test loading
    if not test_config_loading():
        print("\n❌ Configuration loading test failed")
        return 1
    
    print("\n" + "=" * 50)
    print("🎉 All configuration tests passed!")
    print("\nThe configuration system is working correctly.")
    print("You can now use:")
    print("  python main.py config --interactive")
    print("  python main.py config --show")
    print("  python main.py config --reset")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 