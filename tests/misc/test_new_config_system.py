#!/usr/bin/env python3
"""
Test the new two-file configuration system

Tests:
- Private settings (.env) - API keys, URLs, secrets
- Public settings (config.json) - Application features, UI preferences
- Combined configuration loading
- Configuration updates
"""

import sys
import os
import json
import tempfile
import shutil
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config.config_manager import (
    create_default_env_file, create_default_config_file,
    load_config_file, get_combined_config,
    update_public_config, update_private_config
)
from src.services.config_service import ConfigService


def test_config_file_creation():
    """Test creating configuration files"""
    print("🧪 Testing configuration file creation...")
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    try:
        # Test creating .env file
        success = create_default_env_file(temp_dir)
        assert success, "Failed to create .env file"
        
        # Check .env file exists and has content
        env_file = os.path.join(temp_dir, '.env')
        assert os.path.exists(env_file), ".env file not created"
        
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'OPENAI_API_KEY' in content, "OpenAI API key not in .env"
            assert 'your_openai_api_key_here' in content, "Placeholder not in .env"
        
        # Test creating config.json file
        success = create_default_config_file(temp_dir)
        assert success, "Failed to create config.json file"
        
        # Check config.json file exists and has content
        config_file = os.path.join(temp_dir, 'config.json')
        assert os.path.exists(config_file), "config.json file not created"
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            assert 'clip_config' in config, "clip_config not in config.json"
            assert 'analysis_features' in config, "analysis_features not in config.json"
            assert config['clip_config']['model_name'] == 'ViT-L-14/openai'
        
        print("✅ Configuration file creation test passed!")
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_config_loading():
    """Test loading configuration files"""
    print("🧪 Testing configuration loading...")
    
    # Create temporary directory with config files
    temp_dir = tempfile.mkdtemp()
    try:
        # Create config files
        create_default_env_file(temp_dir)
        create_default_config_file(temp_dir)
        
        # Test loading config.json
        config = load_config_file(temp_dir)
        assert 'clip_config' in config, "clip_config not loaded"
        assert 'analysis_features' in config, "analysis_features not loaded"
        assert config['clip_config']['model_name'] == 'ViT-L-14/openai'
        
        # Test combined configuration
        combined = get_combined_config(temp_dir)
        assert 'public' in combined, "public config not in combined"
        assert 'private' in combined, "private config not in combined"
        assert combined['public']['clip_config']['model_name'] == 'ViT-L-14/openai'
        assert combined['private']['web_port'] == 5050
        
        print("✅ Configuration loading test passed!")
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_config_updates():
    """Test updating configuration"""
    print("🧪 Testing configuration updates...")
    
    # Create temporary directory with config files
    temp_dir = tempfile.mkdtemp()
    try:
        # Create config files
        create_default_env_file(temp_dir)
        create_default_config_file(temp_dir)
        
        # Test updating public config
        public_updates = {
            'clip_config': {
                'model_name': 'ViT-B-32/openai',
                'enable_clip_analysis': False
            },
            'analysis_features': {
                'enable_llm_analysis': False,
                'timeout': 60
            }
        }
        
        success = update_public_config(public_updates, temp_dir)
        assert success, "Failed to update public config"
        
        # Verify updates
        config = load_config_file(temp_dir)
        assert config['clip_config']['model_name'] == 'ViT-B-32/openai'
        assert config['clip_config']['enable_clip_analysis'] == False
        assert config['analysis_features']['enable_llm_analysis'] == False
        assert config['analysis_features']['timeout'] == 60
        
        # Test updating private config
        private_updates = {
            'OPENAI_API_KEY': 'test_openai_key_123',
            'WEB_PORT': '8080'
        }
        
        success = update_private_config(private_updates, temp_dir)
        assert success, "Failed to update private config"
        
        # Verify updates
        combined = get_combined_config(temp_dir)
        assert combined['private']['openai_api_key'] == 'test_openai_key_123'
        assert combined['private']['web_port'] == 8080
        
        print("✅ Configuration updates test passed!")
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_config_service():
    """Test ConfigService with new configuration system"""
    print("🧪 Testing ConfigService...")
    
    # Create temporary directory with config files
    temp_dir = tempfile.mkdtemp()
    try:
        # Create config files
        create_default_env_file(temp_dir)
        create_default_config_file(temp_dir)
        
        # Test ConfigService
        config_service = ConfigService(temp_dir)
        
        # Test get_config
        config = config_service.get_config()
        assert 'API_BASE_URL' in config, "API_BASE_URL not in config"
        assert 'CLIP_MODEL_NAME' in config, "CLIP_MODEL_NAME not in config"
        assert 'ENABLE_CLIP_ANALYSIS' in config, "ENABLE_CLIP_ANALYSIS not in config"
        assert config['API_BASE_URL'] == 'http://localhost:7860'
        assert config['CLIP_MODEL_NAME'] == 'ViT-L-14/openai'
        assert config['ENABLE_CLIP_ANALYSIS'] == True
        
        # Test update_config
        updates = {
            'API_BASE_URL': 'http://test:7860',
            'CLIP_MODEL_NAME': 'ViT-B-32/openai',
            'ENABLE_CLIP_ANALYSIS': False,
            'OPENAI_API_KEY': 'test_key_456'
        }
        
        success = config_service.update_config(updates)
        assert success, "Failed to update config via ConfigService"
        
        # Verify updates
        config = config_service.get_config()
        assert config['API_BASE_URL'] == 'http://test:7860'
        assert config['CLIP_MODEL_NAME'] == 'ViT-B-32/openai'
        assert config['ENABLE_CLIP_ANALYSIS'] == False
        
        print("✅ ConfigService test passed!")
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_security_separation():
    """Test that private and public settings are properly separated"""
    print("🧪 Testing security separation...")
    
    # Create temporary directory with config files
    temp_dir = tempfile.mkdtemp()
    try:
        # Create config files
        create_default_env_file(temp_dir)
        create_default_config_file(temp_dir)
        
        # Check that API keys are in .env (private)
        env_file = os.path.join(temp_dir, '.env')
        with open(env_file, 'r', encoding='utf-8') as f:
            env_content = f.read()
            assert 'OPENAI_API_KEY' in env_content, "API key should be in .env"
            assert 'your_openai_api_key_here' in env_content, "API key placeholder should be in .env"
        
        # Check that API keys are NOT in config.json (public)
        config_file = os.path.join(temp_dir, 'config.json')
        with open(config_file, 'r', encoding='utf-8') as f:
            config_content = f.read()
            assert 'OPENAI_API_KEY' not in config_content, "API key should NOT be in config.json"
            assert 'your_openai_api_key_here' not in config_content, "API key placeholder should NOT be in config.json"
        
        # Check that application settings are in config.json (public)
        assert 'clip_config' in config_content, "clip_config should be in config.json"
        assert 'analysis_features' in config_content, "analysis_features should be in config.json"
        
        print("✅ Security separation test passed!")
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def main():
    """Run all configuration tests"""
    print("🔧 Testing New Configuration System")
    print("=" * 50)
    
    tests = [
        test_config_file_creation,
        test_config_loading,
        test_config_updates,
        test_config_service,
        test_security_separation
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} failed: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print("📊 Test Results")
    print("=" * 50)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"🎯 Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 All configuration tests passed!")
        print("\nThe new two-file configuration system is working correctly:")
        print("• ✅ Private settings (.env) - API keys, URLs, secrets")
        print("• ✅ Public settings (config.json) - Application features, UI preferences")
        print("• ✅ Proper separation of sensitive and non-sensitive data")
        print("• ✅ Backward compatibility with existing code")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 