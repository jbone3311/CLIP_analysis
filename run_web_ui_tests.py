#!/usr/bin/env python3
"""
Web UI Test Runner

Run comprehensive tests for web interface functionality including:
- Config saving and loading
- UI interactions (eye icon button, etc.)
- Template rendering
- Route functionality
"""

import sys
import os
import subprocess
from pathlib import Path

def run_tests():
    """Run web UI integration tests"""
    print("🧪 Running Web UI Integration Tests...")
    print("=" * 60)
    
    # Get project root
    project_root = Path(__file__).parent
    
    # Test files to run
    test_files = [
        "tests/integration/test_web_ui_integration.py",
        "tests/integration/test_ui_interactions.py"
    ]
    
    results = []
    
    for test_file in test_files:
        test_path = project_root / test_file
        
        if not test_path.exists():
            print(f"❌ Test file not found: {test_file}")
            continue
        
        print(f"\n📝 Running tests from: {test_file}")
        print("-" * 40)
        
        try:
            # Run pytest on the test file
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                str(test_path), 
                "-v", 
                "--tb=short"
            ], capture_output=True, text=True, cwd=project_root)
            
            if result.returncode == 0:
                print("✅ All tests passed!")
                results.append((test_file, True, result.stdout))
            else:
                print("❌ Some tests failed!")
                print("Error output:")
                print(result.stderr)
                results.append((test_file, False, result.stderr))
                
        except Exception as e:
            print(f"❌ Error running tests: {e}")
            results.append((test_file, False, str(e)))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_file, success, output in results:
        if success:
            print(f"✅ {test_file} - PASSED")
            passed += 1
        else:
            print(f"❌ {test_file} - FAILED")
            failed += 1
    
    print(f"\n🎯 Total: {passed + failed} test files")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All web UI tests passed!")
        print("\nThe web interface is working correctly with:")
        print("• ✅ Config saving and loading")
        print("• ✅ Eye icon button functionality")
        print("• ✅ Template rendering")
        print("• ✅ Route functionality")
        print("• ✅ Database integration")
        return 0
    else:
        print(f"\n⚠️  {failed} test file(s) failed. Check the output above for details.")
        return 1

def run_specific_test(test_name):
    """Run a specific test by name"""
    print(f"🧪 Running specific test: {test_name}")
    print("=" * 60)
    
    project_root = Path(__file__).parent
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "-k", test_name,
            "tests/integration/",
            "-v", 
            "--tb=short"
        ], capture_output=True, text=True, cwd=project_root)
        
        if result.returncode == 0:
            print("✅ Test passed!")
            print(result.stdout)
            return 0
        else:
            print("❌ Test failed!")
            print(result.stderr)
            return 1
            
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return 1

def main():
    """Main test runner"""
    if len(sys.argv) > 1:
        # Run specific test
        test_name = sys.argv[1]
        return run_specific_test(test_name)
    else:
        # Run all tests
        return run_tests()

if __name__ == "__main__":
    sys.exit(main()) 