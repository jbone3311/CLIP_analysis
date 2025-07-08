#!/usr/bin/env python3
"""
Test script for the prompts implementation
"""

import os
import sys
import json
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_prompts_file():
    """Test that the prompts.json file exists and is valid"""
    print("🔍 Testing prompts.json file...")
    
    prompts_file = os.path.join('src', 'config', 'prompts.json')
    
    if not os.path.exists(prompts_file):
        print(f"❌ Prompts file not found: {prompts_file}")
        return False
    
    try:
        with open(prompts_file, 'r', encoding='utf-8') as f:
            prompts = json.load(f)
        
        print(f"✅ Prompts file loaded successfully with {len(prompts)} prompts")
        
        # Check structure
        for prompt_id, prompt_data in prompts.items():
            required_fields = ['TITLE', 'PROMPT_TEXT', 'CATEGORY', 'TEMPERATURE', 'MAX_TOKENS']
            for field in required_fields:
                if field not in prompt_data:
                    print(f"❌ Prompt {prompt_id} missing required field: {field}")
                    return False
            
            # Validate temperature
            if not (0 <= prompt_data['TEMPERATURE'] <= 1):
                print(f"❌ Prompt {prompt_id} has invalid temperature: {prompt_data['TEMPERATURE']}")
                return False
            
            # Validate max tokens
            if not (100 <= prompt_data['MAX_TOKENS'] <= 8000):
                print(f"❌ Prompt {prompt_id} has invalid max tokens: {prompt_data['MAX_TOKENS']}")
                return False
        
        print("✅ All prompts have valid structure")
        return True
        
    except Exception as e:
        print(f"❌ Error loading prompts file: {e}")
        return False

def test_llm_manager_prompts():
    """Test LLM manager prompt methods"""
    print("\n🔍 Testing LLM Manager prompt methods...")
    
    try:
        from src.analyzers.llm_manager import LLMManager
        
        llm_manager = LLMManager()
        
        # Test loading prompts
        prompts = llm_manager.load_prompts()
        print(f"✅ Loaded {len(prompts)} prompts via LLM manager")
        
        # Test getting prompts by category
        comprehensive_prompts = llm_manager.get_prompts_by_category('comprehensive')
        print(f"✅ Found {len(comprehensive_prompts)} comprehensive prompts")
        
        # Test getting all available prompts
        all_prompts = llm_manager.get_available_prompts()
        print(f"✅ Found {len(all_prompts)} total available prompts")
        
        # Test getting specific prompt
        if all_prompts:
            first_prompt_id = all_prompts[0]['id']
            specific_prompt = llm_manager.get_prompt_by_id(first_prompt_id)
            if specific_prompt:
                print(f"✅ Successfully retrieved prompt: {specific_prompt['TITLE']}")
            else:
                print(f"❌ Failed to retrieve prompt: {first_prompt_id}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing LLM manager: {e}")
        return False

def test_api_functions():
    """Test the API functions from prompts.py"""
    print("\n🔍 Testing API functions...")
    
    try:
        from src.api.prompts import load_prompts, validate_prompt, generate_simulated_response
        
        # Test loading prompts
        prompts = load_prompts()
        print(f"✅ API load_prompts() returned {len(prompts)} prompts")
        
        # Test validation
        if prompts:
            first_prompt = list(prompts.values())[0]
            is_valid, error_msg = validate_prompt(first_prompt)
            if is_valid:
                print("✅ Prompt validation works correctly")
            else:
                print(f"❌ Prompt validation failed: {error_msg}")
                return False
        
        # Test simulated response generation
        test_prompt = {
            'TITLE': 'Test Prompt',
            'PROMPT_TEXT': 'Test prompt text',
            'CATEGORY': 'comprehensive',
            'TEMPERATURE': 0.7,
            'MAX_TOKENS': 2000
        }
        
        response = generate_simulated_response(test_prompt)
        print(f"✅ Generated simulated response: {len(response)} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing API functions: {e}")
        return False

def test_web_interface_integration():
    """Test web interface integration"""
    print("\n🔍 Testing web interface integration...")
    
    try:
        # Test that the prompts template exists
        prompts_template = os.path.join('src', 'viewers', 'templates_refactored', 'prompts.html')
        if os.path.exists(prompts_template):
            print("✅ Prompts template exists")
        else:
            print(f"❌ Prompts template not found: {prompts_template}")
            return False
        
        # Test that the API routes are properly defined
        api_routes_file = os.path.join('src', 'routes', 'api_routes.py')
        if os.path.exists(api_routes_file):
            with open(api_routes_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if '/api/prompts' in content:
                    print("✅ API routes for prompts are defined")
                else:
                    print("❌ API routes for prompts not found")
                    return False
        else:
            print(f"❌ API routes file not found: {api_routes_file}")
            return False
        
        # Test that the main routes include prompts
        main_routes_file = os.path.join('src', 'routes', 'main_routes.py')
        if os.path.exists(main_routes_file):
            with open(main_routes_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if '/prompts' in content:
                    print("✅ Main routes include prompts page")
                else:
                    print("❌ Main routes don't include prompts page")
                    return False
        else:
            print(f"❌ Main routes file not found: {main_routes_file}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing web interface integration: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Prompts Implementation")
    print("=" * 50)
    
    tests = [
        ("Prompts File", test_prompts_file),
        ("LLM Manager Prompts", test_llm_manager_prompts),
        ("API Functions", test_api_functions),
        ("Web Interface Integration", test_web_interface_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        try:
            if test_func():
                print(f"✅ {test_name} test PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} test FAILED")
        except Exception as e:
            print(f"❌ {test_name} test ERROR: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Prompts implementation is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    exit(main()) 