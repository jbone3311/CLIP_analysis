#!/usr/bin/env python3
"""
Test runner for Image Analysis with CLIP and LLM

This script runs all unit and integration tests.
"""

import unittest
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def run_unit_tests():
    """Run all unit tests"""
    print("🧪 Running Unit Tests...")
    print("=" * 50)
    
    # Discover and run unit tests
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent / "unit"
    suite = loader.discover(start_dir, pattern="test_*.py")
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def run_integration_tests():
    """Run all integration tests"""
    print("\n🔗 Running Integration Tests...")
    print("=" * 50)
    
    # Discover and run integration tests
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent / "integration"
    suite = loader.discover(start_dir, pattern="test_*.py")
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def run_all_tests():
    """Run all tests"""
    print("🚀 Image Analysis Test Suite")
    print("=" * 50)
    
    unit_success = run_unit_tests()
    integration_success = run_integration_tests()
    
    print("\n📊 Test Results Summary")
    print("=" * 50)
    print(f"Unit Tests: {'✅ PASSED' if unit_success else '❌ FAILED'}")
    print(f"Integration Tests: {'✅ PASSED' if integration_success else '❌ FAILED'}")
    
    overall_success = unit_success and integration_success
    print(f"\nOverall Result: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    return overall_success

def run_specific_test(test_name):
    """Run a specific test by name"""
    print(f"🎯 Running Specific Test: {test_name}")
    print("=" * 50)
    
    # Try to find the test
    test_path = None
    for root, dirs, files in os.walk(Path(__file__).parent):
        for file in files:
            if file.startswith(f"test_{test_name}") and file.endswith(".py"):
                test_path = Path(root) / file
                break
        if test_path:
            break
    
    if not test_path:
        print(f"❌ Test file not found: test_{test_name}.py")
        return False
    
    # Run the specific test
    loader = unittest.TestLoader()
    suite = loader.discover(test_path.parent, pattern=test_path.name)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "unit":
            success = run_unit_tests()
        elif command == "integration":
            success = run_integration_tests()
        elif command == "specific" and len(sys.argv) > 2:
            test_name = sys.argv[2]
            success = run_specific_test(test_name)
        else:
            print("Usage:")
            print("  python run_tests.py                    # Run all tests")
            print("  python run_tests.py unit              # Run unit tests only")
            print("  python run_tests.py integration       # Run integration tests only")
            print("  python run_tests.py specific <name>   # Run specific test")
            return
    else:
        success = run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 