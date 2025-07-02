#!/usr/bin/env python3
"""
Test Runner for Image Analysis Project

This script runs all tests for the image analysis project with proper
configuration and reporting.

Usage:
    python run_tests.py [options]

Options:
    --verbose, -v    : Verbose output
    --coverage, -c   : Run with coverage reporting
    --unit          : Run only unit tests
    --integration   : Run only integration tests
    --module MODULE : Run tests for specific module
    --help, -h      : Show this help message
"""

import argparse
import sys
import subprocess
import os
from pathlib import Path

def setup_environment():
    """Set up test environment and dependencies."""
    print("🔧 Setting up test environment...")
    
    # Check if pytest is available
    try:
        import pytest
        print("✅ pytest is available")
    except ImportError:
        print("❌ pytest not found. Installing test dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements-test.txt"], check=True)
    
    # Set environment variables for testing
    test_env = {
        'PYTHONPATH': os.getcwd(),
        'TESTING': 'true',
        'LOG_LEVEL': 'WARNING'  # Reduce log noise during testing
    }
    
    for key, value in test_env.items():
        os.environ[key] = value
    
    print("✅ Test environment configured")

def run_unit_tests(verbose=False, coverage=False, module=None):
    """Run unit tests."""
    print("\n🧪 Running Unit Tests...")
    
    cmd = [sys.executable, "-m", "pytest"]
    
    # Test files to run
    if module:
        test_files = [f"test_{module}.py"]
    else:
        test_files = [
            "test_analysis_llm.py",
            "test_analysis_interrogate.py", 
            "test_config.py",
            "test_db_utils.py",
            "test_utils.py",
            "test_directory_processor.py"
        ]
    
    # Add existing test files only
    existing_files = [f for f in test_files if os.path.exists(f)]
    cmd.extend(existing_files)
    
    # Add options
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")
    
    if coverage:
        cmd.extend(["--cov=.", "--cov-report=html", "--cov-report=term"])
    
    # Add markers for unit tests
    cmd.extend(["-m", "not integration"])
    
    try:
        result = subprocess.run(cmd, check=False)
        if result.returncode == 0:
            print("✅ Unit tests passed")
        else:
            print("❌ Some unit tests failed")
        return result.returncode
    except FileNotFoundError:
        print("❌ pytest not found. Run with --setup to install dependencies.")
        return 1

def run_integration_tests(verbose=False, coverage=False):
    """Run integration tests."""
    print("\n🔗 Running Integration Tests...")
    
    cmd = [sys.executable, "-m", "pytest", "test_integration.py"]
    
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")
    
    if coverage:
        cmd.extend(["--cov=.", "--cov-report=html", "--cov-report=term"])
    
    try:
        result = subprocess.run(cmd, check=False)
        if result.returncode == 0:
            print("✅ Integration tests passed")
        else:
            print("❌ Some integration tests failed")
        return result.returncode
    except FileNotFoundError:
        print("❌ pytest not found. Run with --setup to install dependencies.")
        return 1

def run_all_tests(verbose=False, coverage=False):
    """Run all tests."""
    print("\n🎯 Running All Tests...")
    
    cmd = [sys.executable, "-m", "pytest"]
    
    # Include all test files
    test_files = []
    for file in os.listdir('.'):
        if file.startswith('test_') and file.endswith('.py'):
            test_files.append(file)
    
    cmd.extend(test_files)
    
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")
    
    if coverage:
        cmd.extend([
            "--cov=.",
            "--cov-report=html",
            "--cov-report=term",
            "--cov-exclude=test_*",
            "--cov-exclude=run_tests.py"
        ])
    
    try:
        result = subprocess.run(cmd, check=False)
        if result.returncode == 0:
            print("✅ All tests passed")
        else:
            print("❌ Some tests failed")
        return result.returncode
    except FileNotFoundError:
        print("❌ pytest not found. Run with --setup to install dependencies.")
        return 1

def check_test_files():
    """Check which test files exist and show test structure."""
    print("\n📋 Test Structure:")
    
    test_files = [
        ("test_analysis_llm.py", "LLM Analysis Module Tests"),
        ("test_analysis_interrogate.py", "CLIP Interrogator Tests"),
        ("test_config.py", "Configuration Management Tests"),
        ("test_db_utils.py", "Database Utilities Tests"),
        ("test_utils.py", "Utility Functions Tests"),
        ("test_directory_processor.py", "Batch Processing Tests"),
        ("test_integration.py", "Integration Tests"),
        ("conftest.py", "Test Configuration & Fixtures")
    ]
    
    for filename, description in test_files:
        if os.path.exists(filename):
            print(f"  ✅ {filename:<30} - {description}")
        else:
            print(f"  ❌ {filename:<30} - {description} (Missing)")
    
    print(f"\nTest Dependencies:")
    req_file = "requirements-test.txt"
    if os.path.exists(req_file):
        print(f"  ✅ {req_file} - Test dependencies defined")
    else:
        print(f"  ❌ {req_file} - Test dependencies file missing")

def create_test_report():
    """Generate a test coverage report."""
    print("\n📊 Generating Test Report...")
    
    if os.path.exists("htmlcov"):
        print("✅ HTML coverage report available in htmlcov/index.html")
    else:
        print("ℹ️  No coverage report found. Run tests with --coverage to generate.")

def main():
    parser = argparse.ArgumentParser(
        description="Test runner for Image Analysis Project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument("-v", "--verbose", action="store_true",
                      help="Verbose test output")
    parser.add_argument("-c", "--coverage", action="store_true",
                      help="Run with coverage reporting")
    parser.add_argument("--unit", action="store_true",
                      help="Run only unit tests")
    parser.add_argument("--integration", action="store_true",
                      help="Run only integration tests")
    parser.add_argument("--module", type=str,
                      help="Run tests for specific module (e.g., 'config', 'utils')")
    parser.add_argument("--setup", action="store_true",
                      help="Set up test environment and install dependencies")
    parser.add_argument("--check", action="store_true",
                      help="Check test structure and dependencies")
    parser.add_argument("--report", action="store_true",
                      help="Show test coverage report")
    
    args = parser.parse_args()
    
    # Print header
    print("=" * 60)
    print("🔬 Image Analysis Project Test Runner")
    print("=" * 60)
    
    # Handle special commands
    if args.check:
        check_test_files()
        return 0
    
    if args.report:
        create_test_report()
        return 0
    
    if args.setup:
        setup_environment()
        return 0
    
    # Set up environment
    setup_environment()
    
    # Run tests based on options
    return_code = 0
    
    try:
        if args.unit:
            return_code = run_unit_tests(args.verbose, args.coverage, args.module)
        elif args.integration:
            return_code = run_integration_tests(args.verbose, args.coverage)
        else:
            return_code = run_all_tests(args.verbose, args.coverage)
        
        # Show summary
        print("\n" + "=" * 60)
        if return_code == 0:
            print("🎉 All tests completed successfully!")
        else:
            print("⚠️  Some tests failed. Check output above for details.")
        
        if args.coverage:
            create_test_report()
        
        print("=" * 60)
        
        return return_code
        
    except KeyboardInterrupt:
        print("\n\n❌ Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())