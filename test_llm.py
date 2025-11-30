#!/usr/bin/env python3
"""
Test script for LLM functionality
Tests OpenAI API integration with image analysis
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.analyzers.llm_manager import LLMManager
from src.database.db_manager import DatabaseManager
from src.config.config_manager import get_config_value
from dotenv import load_dotenv

load_dotenv()

def test_llm_setup():
    """Test LLM setup and configuration"""
    print("=" * 60)
    print("Testing LLM Setup")
    print("=" * 60)
    
    # Check OpenAI API key
    openai_key = get_config_value('OPENAI_API_KEY') or os.getenv('OPENAI_API_KEY')
    if openai_key and not openai_key.startswith('your_'):
        print(f"✅ OpenAI API Key found: {openai_key[:10]}...{openai_key[-4:]}")
    else:
        print("❌ OpenAI API Key not found or not configured")
        print("   Please set OPENAI_API_KEY in your .env file")
        return False
    
    # Check database for configured models
    db_manager = DatabaseManager()
    models = db_manager.get_llm_models()
    
    if models:
        print(f"\n✅ Found {len(models)} configured LLM model(s):")
        for model in models:
            print(f"   - {model['name']} ({model['type']})")
    
    # Check if OpenAI model exists
    openai_models = [m for m in models if m.get('type') == 'openai']
    if not openai_models:
        print("\n⚠️  No OpenAI model configured in database")
        print("   Attempting to auto-configure OpenAI...")
        
        # Auto-configure OpenAI
        try:
            db_manager.insert_llm_model(
                name='GPT-4 Vision',
                type='openai',
                url='https://api.openai.com/v1',
                api_key=openai_key,
                model_name='gpt-4o',
                prompts=None
            )
            print("   ✅ OpenAI GPT-4 Vision auto-configured")
            models = db_manager.get_llm_models()
            openai_models = [m for m in models if m.get('type') == 'openai']
            if openai_models:
                print(f"   ✅ Found OpenAI model: {openai_models[0]['name']}")
        except Exception as e:
            print(f"   ❌ Failed to auto-configure: {e}")
            import traceback
            traceback.print_exc()
            return False
    else:
        print(f"\n✅ OpenAI model already configured: {openai_models[0]['name']}")
    
    return True, models

def test_llm_analysis(image_path: str):
    """Test LLM analysis on an image"""
    print("\n" + "=" * 60)
    print("Testing LLM Image Analysis")
    print("=" * 60)
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return False
    
    print(f"📷 Image: {image_path}")
    print(f"   Size: {os.path.getsize(image_path) / 1024:.2f} KB")
    
    # Setup
    db_manager = DatabaseManager()
    llm_manager = LLMManager()
    
    # Get configured models
    models = db_manager.get_llm_models()
    if not models:
        print("❌ No LLM models configured")
        return False
    
    # Test with first OpenAI model found
    openai_model = next((m for m in models if m.get('type') == 'openai'), None)
    if not openai_model:
        print("❌ No OpenAI model found in configured models")
        return False
    
    print(f"\n🤖 Using model: {openai_model['name']}")
    print(f"   Type: {openai_model['type']}")
    print(f"   Model: {openai_model.get('model_name', 'N/A')}")
    
    # Test prompt
    test_prompt = "Describe this image in detail, including visual elements, style, composition, and any notable features."
    print(f"\n💬 Prompt: {test_prompt}")
    
    print("\n⏳ Analyzing image with LLM...")
    try:
        result = llm_manager.analyze_image(
            image_path=image_path,
            prompt=test_prompt,
            model_config=openai_model
        )
        
        print("\n" + "=" * 60)
        print("✅ Analysis Complete!")
        print("=" * 60)
        
        if result.get('status') == 'success':
            print(f"\n📝 Response:")
            print("-" * 60)
            response_text = result.get('response', {}).get('content', result.get('content', 'No content'))
            if isinstance(response_text, str):
                print(response_text)
            elif isinstance(response_text, list):
                for item in response_text:
                    if isinstance(item, dict):
                        print(item.get('text', item.get('content', str(item))))
                    else:
                        print(item)
            else:
                print(str(response_text))
            print("-" * 60)
            
            print(f"\n📊 Metadata:")
            print(f"   Model: {result.get('model', 'N/A')}")
            print(f"   Provider: {result.get('provider', 'N/A')}")
            if 'tokens' in result:
                print(f"   Tokens: {result.get('tokens', 'N/A')}")
            if 'cost' in result:
                print(f"   Cost: ${result.get('cost', 'N/A')}")
            
            return True
        else:
            print(f"\n❌ Analysis failed:")
            print(f"   Error: {result.get('message', 'Unknown error')}")
            if 'error' in result:
                print(f"   Details: {result['error']}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error during analysis:")
        print(f"   {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("\n🚀 Starting LLM Test")
    print("=" * 60)
    
    # Test setup
    setup_result = test_llm_setup()
    if isinstance(setup_result, tuple):
        success, models = setup_result
        if not success:
            print("\n❌ Setup failed. Please check your configuration.")
            sys.exit(1)
    else:
        print("\n❌ Setup failed. Please check your configuration.")
        sys.exit(1)
    
    # Find test image
    images_dir = Path(__file__).parent / "Images"
    test_image = None
    
    # Look for test images
    for ext in ['.jpg', '.jpeg', '.png', '.webp']:
        test_images = list(images_dir.glob(f"*{ext}"))
        if test_images:
            test_image = str(test_images[0])
            break
    
    # Also check Group subdirectory
    if not test_image:
        group_dir = images_dir / "Group"
        if group_dir.exists():
            for ext in ['.jpg', '.jpeg', '.png', '.webp']:
                test_images = list(group_dir.glob(f"*{ext}"))
                if test_images:
                    test_image = str(test_images[0])
                    break
    
    if not test_image:
        print("\n❌ No test images found in Images directory")
        print("   Please add a test image to the Images folder")
        sys.exit(1)
    
    # Test analysis
    success = test_llm_analysis(test_image)
    
    print("\n" + "=" * 60)
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Tests failed")
    print("=" * 60)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

