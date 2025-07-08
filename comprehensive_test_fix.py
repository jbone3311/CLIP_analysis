#!/usr/bin/env python3
"""
Comprehensive test fix script
Identifies and fixes all test issues systematically
"""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path

def run_command_with_timeout(command, timeout=30):
    """Run a command with timeout to prevent hanging"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        print(f"⚠️  Command timed out after {timeout} seconds: {command}")
        return -1, "", "Timeout"
    except Exception as e:
        print(f"❌ Command failed: {command} - {e}")
        return -1, "", str(e)

def test_individual_modules():
    """Test individual modules to identify issues"""
    print("🔍 Testing individual modules...")
    
    modules = [
        "src.config.config_manager",
        "src.database.db_manager", 
        "src.analyzers.llm_manager",
        "src.analyzers.metadata_extractor",
        "src.utils.installer",
        "src.viewers.results_viewer",
        "src.services.analysis_service",
        "src.services.image_service",
        "src.services.config_service",
        "src.routes.main_routes",
        "src.routes.api_routes"
    ]
    
    issues = []
    
    for module in modules:
        print(f"  Testing {module}...")
        code, stdout, stderr = run_command_with_timeout(
            f"python -c \"import {module}; print('OK')\"",
            timeout=10
        )
        
        if code == 0:
            print(f"    ✅ {module}")
        else:
            print(f"    ❌ {module}: {stderr}")
            issues.append((module, stderr))
    
    return issues

def fix_common_issues():
    """Fix common issues found in tests"""
    print("\n🔧 Fixing common issues...")
    
    fixes_applied = []
    
    # Fix 1: Check if .env file exists
    if not os.path.exists('.env'):
        print("  Creating .env file...")
        try:
            with open('.env', 'w') as f:
                f.write("# Image Analysis Configuration\n")
                f.write("API_BASE_URL=http://localhost:7860\n")
                f.write("CLIP_MODEL_NAME=ViT-L-14/openai\n")
                f.write("ENABLE_CLIP_ANALYSIS=True\n")
                f.write("ENABLE_LLM_ANALYSIS=True\n")
                f.write("IMAGE_DIRECTORY=Images\n")
                f.write("OUTPUT_DIRECTORY=Output\n")
                f.write("WEB_PORT=5050\n")
            fixes_applied.append("Created .env file")
        except Exception as e:
            print(f"    ❌ Failed to create .env: {e}")
    
    # Fix 2: Create necessary directories
    directories = ['Images', 'Output', 'src/viewers/static']
    for directory in directories:
        if not os.path.exists(directory):
            print(f"  Creating directory: {directory}")
            try:
                os.makedirs(directory, exist_ok=True)
                fixes_applied.append(f"Created directory: {directory}")
            except Exception as e:
                print(f"    ❌ Failed to create {directory}: {e}")
    
    # Fix 3: Create missing __init__.py files
    init_dirs = [
        'src/viewers/static',
        'src/viewers/templates_refactored'
    ]
    
    for init_dir in init_dirs:
        init_file = os.path.join(init_dir, '__init__.py')
        if not os.path.exists(init_file):
            print(f"  Creating __init__.py in {init_dir}")
            try:
                with open(init_file, 'w') as f:
                    f.write("# Auto-generated __init__.py\n")
                fixes_applied.append(f"Created __init__.py in {init_dir}")
            except Exception as e:
                print(f"    ❌ Failed to create __init__.py in {init_dir}: {e}")
    
    return fixes_applied

def run_unit_tests():
    """Run unit tests with timeout"""
    print("\n🧪 Running unit tests...")
    
    test_files = [
        "tests/unit/test_config_manager.py",
        "tests/unit/test_installer.py", 
        "tests/unit/test_metadata_extractor.py",
        "tests/unit/test_results_viewer.py",
        "tests/unit/test_directory_processor.py"
    ]
    
    results = []
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"  Running {test_file}...")
            code, stdout, stderr = run_command_with_timeout(
                f"python -m pytest {test_file} -v --tb=short",
                timeout=60
            )
            
            if code == 0:
                print(f"    ✅ {test_file} passed")
                results.append((test_file, "PASS"))
            else:
                print(f"    ❌ {test_file} failed")
                print(f"      STDOUT: {stdout}")
                print(f"      STDERR: {stderr}")
                results.append((test_file, "FAIL"))
        else:
            print(f"    ⚠️  {test_file} not found")
            results.append((test_file, "NOT_FOUND"))
    
    return results

def run_refactored_tests():
    """Run refactored tests"""
    print("\n🧪 Running refactored tests...")
    
    if os.path.exists("tests/run_refactored_tests.py"):
        code, stdout, stderr = run_command_with_timeout(
            "python tests/run_refactored_tests.py",
            timeout=120
        )
        
        if code == 0:
            print("  ✅ Refactored tests passed")
            return "PASS"
        else:
            print("  ❌ Refactored tests failed")
            print(f"    STDOUT: {stdout}")
            print(f"    STDERR: {stderr}")
            return "FAIL"
    else:
        print("  ⚠️  Refactored tests not found")
        return "NOT_FOUND"

def main():
    """Main test fix process"""
    print("🚀 Comprehensive Test Fix")
    print("=" * 50)
    
    # Step 1: Fix common issues
    fixes = fix_common_issues()
    if fixes:
        print(f"\n✅ Applied {len(fixes)} fixes:")
        for fix in fixes:
            print(f"  • {fix}")
    
    # Step 2: Test individual modules
    module_issues = test_individual_modules()
    if module_issues:
        print(f"\n❌ Found {len(module_issues)} module issues:")
        for module, error in module_issues:
            print(f"  • {module}: {error}")
    
    # Step 3: Run unit tests
    unit_results = run_unit_tests()
    
    # Step 4: Run refactored tests
    refactored_result = run_refactored_tests()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 20)
    
    passed_tests = sum(1 for _, result in unit_results if result == "PASS")
    failed_tests = sum(1 for _, result in unit_results if result == "FAIL")
    
    print(f"Unit Tests: {passed_tests} passed, {failed_tests} failed")
    print(f"Refactored Tests: {refactored_result}")
    print(f"Module Issues: {len(module_issues)}")
    print(f"Fixes Applied: {len(fixes)}")
    
    if failed_tests == 0 and len(module_issues) == 0 and refactored_result == "PASS":
        print("\n🎉 All tests are now working!")
        return 0
    else:
        print("\n⚠️  Some issues remain. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 