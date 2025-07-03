#!/usr/bin/env python3
"""
System Test for Image Analysis with CLIP and LLM

This script tests all components of the system to ensure everything is working correctly.
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def print_banner():
    """Print the test banner"""
    print("🧪 Image Analysis System Test")
    print("=" * 35)
    print()

def test_imports():
    """Test that all required modules can be imported"""
    print("📦 Testing Imports")
    print("-" * 20)
    
    modules = [
        ("requests", "requests"),
        ("dotenv", "python-dotenv"),
        ("PIL", "Pillow"),
        ("imagehash", "imagehash")
    ]
    
    all_good = True
    for module_name, package_name in modules:
        try:
            __import__(module_name)
            print(f"✅ {package_name}")
        except ImportError as e:
            print(f"❌ {package_name}: {e}")
            all_good = False
    
    return all_good

def test_local_modules():
    """Test that local modules can be imported"""
    print("\n🔧 Testing Local Modules")
    print("-" * 25)
    
    modules = [
        "directory_processor",
        "analysis_interrogate", 
        "analysis_LLM",
        "image_metadata",
        "config_helper",
        "results_viewer"
    ]
    
    all_good = True
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            all_good = False
    
    return all_good

def test_directories():
    """Test that required directories exist"""
    print("\n📁 Testing Directories")
    print("-" * 20)
    
    directories = ["Images", "Output"]
    all_good = True
    
    for directory in directories:
        if os.path.exists(directory):
            print(f"✅ {directory}")
        else:
            print(f"❌ {directory} (missing)")
            all_good = False
    
    return all_good

def test_configuration():
    """Test configuration file"""
    print("\n⚙️  Testing Configuration")
    print("-" * 25)
    
    if not os.path.exists(".env"):
        print("❌ .env file not found")
        print("   Run 'python config_helper.py' to create configuration")
        return False
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        # Check some key variables
        required_vars = [
            "IMAGE_DIRECTORY",
            "OUTPUT_DIRECTORY"
        ]
        
        all_good = True
        for var in required_vars:
            value = os.getenv(var)
            if value:
                print(f"✅ {var}: {value}")
            else:
                print(f"❌ {var}: not set")
                all_good = False
        
        return all_good
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_sample_image():
    """Test if sample image exists"""
    print("\n🖼️  Testing Sample Image")
    print("-" * 25)
    
    sample_path = "Images/sample_image.png"
    if os.path.exists(sample_path):
        print(f"✅ Sample image found: {sample_path}")
        return True
    else:
        print(f"⚠️  Sample image not found: {sample_path}")
        print("   You can add your own images to test with")
        return False

def test_clip_validation():
    """Test CLIP configuration validation"""
    print("\n🔍 Testing CLIP Configuration")
    print("-" * 30)
    
    try:
        result = subprocess.run([
            sys.executable, "analysis_interrogate.py", "--validate"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ CLIP configuration is valid")
            return True
        else:
            print(f"❌ CLIP configuration error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️  CLIP validation timed out")
        return False
    except Exception as e:
        print(f"❌ CLIP validation failed: {e}")
        return False

def test_llm_validation():
    """Test LLM configuration validation"""
    print("\n🤖 Testing LLM Configuration")
    print("-" * 30)
    
    try:
        result = subprocess.run([
            sys.executable, "analysis_LLM.py", "--list-models"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ LLM models listed successfully")
            return True
        else:
            print(f"❌ LLM configuration error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️  LLM validation timed out")
        return False
    except Exception as e:
        print(f"❌ LLM validation failed: {e}")
        return False

def test_results_viewer():
    """Test results viewer functionality"""
    print("\n📊 Testing Results Viewer")
    print("-" * 25)
    
    try:
        result = subprocess.run([
            sys.executable, "results_viewer.py", "--list"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Results viewer working")
            return True
        else:
            print(f"❌ Results viewer error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️  Results viewer timed out")
        return False
    except Exception as e:
        print(f"❌ Results viewer failed: {e}")
        return False

def run_quick_test():
    """Run a quick test with sample image if available"""
    print("\n🚀 Running Quick Test")
    print("-" * 20)
    
    sample_path = "Images/sample_image.png"
    if not os.path.exists(sample_path):
        print("⚠️  No sample image found, skipping quick test")
        return True
    
    try:
        print("Testing metadata extraction...")
        result = subprocess.run([
            sys.executable, "image_metadata.py", sample_path
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Metadata extraction successful")
            return True
        else:
            print(f"❌ Metadata extraction failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️  Quick test timed out")
        return False
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        return False

def print_summary(results):
    """Print test summary"""
    print("\n📋 Test Summary")
    print("=" * 15)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! The system is ready to use.")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
    
    print("\nNext steps:")
    if results.get("configuration", False):
        print("✅ Configuration is ready")
    else:
        print("❌ Run 'python config_helper.py' to configure the system")
    
    if results.get("sample_image", False):
        print("✅ Sample image available for testing")
    else:
        print("📁 Add images to the Images directory")
    
    print("🚀 Run 'python directory_processor.py' to start analysis")

def main():
    """Main test function"""
    print_banner()
    
    results = {}
    
    # Run all tests
    results["imports"] = test_imports()
    results["local_modules"] = test_local_modules()
    results["directories"] = test_directories()
    results["configuration"] = test_configuration()
    results["sample_image"] = test_sample_image()
    results["clip_validation"] = test_clip_validation()
    results["llm_validation"] = test_llm_validation()
    results["results_viewer"] = test_results_viewer()
    results["quick_test"] = run_quick_test()
    
    # Print summary
    print_summary(results)
    
    # Return appropriate exit code
    if all(results.values()):
        return 0
    else:
        return 1

if __name__ == "__main__":
    exit(main()) 