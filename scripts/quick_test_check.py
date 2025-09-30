#!/usr/bin/env python3
"""
Quick test status checker
"""

import os
import sys
import importlib
import traceback
from pathlib import Path

def check_test_files():
    """Check which test files exist and their status"""
    print("🔍 Checking Test Files")
    print("=" * 40)
    
    test_dirs = [
        "tests/unit",
        "tests/integration"
    ]
    
    test_files = []
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            for file in os.listdir(test_dir):
                if file.startswith("test_") and file.endswith(".py"):
                    test_files.append(os.path.join(test_dir, file))
    
    print(f"Found {len(test_files)} test files:")
    for test_file in sorted(test_files):
        print(f"  📄 {test_file}")
    
    return test_files

def check_module_imports():
    """Check if core modules can be imported"""
    print("\n🔍 Checking Module Imports")
    print("=" * 40)
    
    modules_to_test = [
        "src.services.analysis_service",
        "src.services.image_service", 
        "src.services.config_service",
        "src.analyzers.clip_analyzer",
        "src.analyzers.llm_analyzer",
        "src.analyzers.metadata_extractor",
        "src.config.config_manager",
        "src.utils.installer",
        "src.viewers.results_viewer"
    ]
    
    results = []
    for module in modules_to_test:
        try:
            importlib.import_module(module)
            print(f"  ✅ {module}")
            results.append((module, "PASS"))
        except Exception as e:
            print(f"  ❌ {module}: {str(e)[:100]}...")
            results.append((module, f"FAIL: {str(e)[:100]}"))
    
    return results

def check_test_runners():
    """Check test runner scripts"""
    print("\n🔍 Checking Test Runners")
    print("=" * 40)
    
    runners = [
        "tests/run_refactored_tests.py",
        "tests/run_tests.py", 
        "tests/run_simple_tests.py",
        "tests/run_web_tests.py",
        "safe_test_runner.py"
    ]
    
    for runner in runners:
        if os.path.exists(runner):
            print(f"  📄 {runner}")
        else:
            print(f"  ❌ {runner} (missing)")

def main():
    """Main function"""
    print("🚀 CLIP Analysis Test Status Check")
    print("=" * 50)
    
    # Add project root to path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Check test files
    test_files = check_test_files()
    
    # Check module imports
    import_results = check_module_imports()
    
    # Check test runners
    check_test_runners()
    
    # Summary
    print("\n📊 Summary")
    print("=" * 20)
    print(f"Test files found: {len(test_files)}")
    
    passed_imports = sum(1 for _, result in import_results if result == "PASS")
    failed_imports = sum(1 for _, result in import_results if result != "PASS")
    
    print(f"Module imports: {passed_imports} passed, {failed_imports} failed")
    
    if failed_imports == 0:
        print("\n🎉 All core modules can be imported!")
        print("✅ Ready to run tests")
    else:
        print(f"\n⚠️  {failed_imports} modules failed to import")
        print("❌ Some tests may fail due to import issues")

if __name__ == "__main__":
    main() 