#!/usr/bin/env python3
"""
Test runner for refactored code
"""

import unittest
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_refactored_tests():
    """Run all tests for refactored code"""
    print("🧪 Running Refactored Code Tests")
    print("=" * 50)
    
    # Test discovery patterns
    test_patterns = [
        'tests/unit/test_analysis_service.py',
        'tests/unit/test_image_service.py', 
        'tests/unit/test_config_service.py',
        'tests/unit/test_web_interface_refactored.py'
    ]
    
    # Load test suites
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    for pattern in test_patterns:
        if os.path.exists(pattern):
            print(f"📁 Loading tests from: {pattern}")
            tests = loader.discover(os.path.dirname(pattern), 
                                  pattern=os.path.basename(pattern))
            suite.addTests(tests)
        else:
            print(f"⚠️  Test file not found: {pattern}")
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"   {test}: {traceback.split('Exception:')[-1].strip()}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\n{'✅ All tests passed!' if success else '❌ Some tests failed!'}")
    
    return success


if __name__ == '__main__':
    success = run_refactored_tests()
    sys.exit(0 if success else 1) 