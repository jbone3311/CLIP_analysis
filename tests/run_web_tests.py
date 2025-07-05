#!/usr/bin/env python3
"""
Web Interface Test Runner

This script runs tests specifically for the web interface functionality.
"""

import unittest
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def run_web_interface_tests():
    """Run web interface unit tests"""
    print("🌐 Running Web Interface Unit Tests...")
    print("=" * 50)
    
    # Run web interface unit tests
    loader = unittest.TestLoader()
    test_file = Path(__file__).parent / "unit" / "test_web_interface.py"
    
    if test_file.exists():
        suite = loader.discover(test_file.parent, pattern=test_file.name)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return result.wasSuccessful()
    else:
        print("❌ Web interface unit tests not found")
        return False

def run_web_integration_tests():
    """Run web interface integration tests"""
    print("\n🔗 Running Web Interface Integration Tests...")
    print("=" * 50)
    
    # Run web interface integration tests
    loader = unittest.TestLoader()
    test_file = Path(__file__).parent / "integration" / "test_web_interface_integration.py"
    
    if test_file.exists():
        suite = loader.discover(test_file.parent, pattern=test_file.name)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return result.wasSuccessful()
    else:
        print("❌ Web interface integration tests not found")
        return False

def run_web_tests():
    """Run all web interface tests"""
    print("🚀 Web Interface Test Suite")
    print("=" * 50)
    
    unit_success = run_web_interface_tests()
    integration_success = run_web_integration_tests()
    
    print("\n📊 Web Interface Test Results")
    print("=" * 50)
    print(f"Unit Tests: {'✅ PASSED' if unit_success else '❌ FAILED'}")
    print(f"Integration Tests: {'✅ PASSED' if integration_success else '❌ FAILED'}")
    
    overall_success = unit_success and integration_success
    print(f"\nOverall Result: {'✅ ALL WEB TESTS PASSED' if overall_success else '❌ SOME WEB TESTS FAILED'}")
    
    return overall_success

def main():
    """Main entry point"""
    success = run_web_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 