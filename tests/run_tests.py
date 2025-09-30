#!/usr/bin/env python3
"""
Unified Test Runner for CLIP Analysis Project

This consolidated test runner replaces all the individual test runners.
Run all tests or specific test suites with command-line options.

Usage:
    python tests/run_tests.py                  # Run all tests
    python tests/run_tests.py --unit          # Run unit tests only
    python tests/run_tests.py --integration   # Run integration tests only
    python tests/run_tests.py --web           # Run web interface tests only
    python tests/run_tests.py --misc          # Run misc tests
    python tests/run_tests.py --fast          # Run fast tests (skip slow integration)
    python tests/run_tests.py --verbose       # Verbose output
    python tests/run_tests.py --coverage      # Run with coverage report
"""

import argparse
import sys
import os
import subprocess
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestRunner:
    """Unified test runner with flexible options"""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.tests_dir = self.project_root / "tests"
        
    def run_pytest(self, test_paths, verbose=False, coverage=False, markers=None):
        """Run pytest with specified options"""
        cmd = [sys.executable, "-m", "pytest"]
        
        # Add test paths
        cmd.extend([str(p) for p in test_paths])
        
        # Add options
        if verbose:
            cmd.append("-vv")
        else:
            cmd.append("-v")
        
        if coverage:
            cmd.extend(["--cov=src", "--cov-report=html", "--cov-report=term"])
        
        if markers:
            cmd.extend(["-m", markers])
        
        # Add other useful options
        cmd.extend([
            "--tb=short",  # Shorter tracebacks
            "--color=yes",  # Colored output
        ])
        
        print(f"🧪 Running: {' '.join(cmd)}")
        print("=" * 70)
        
        result = subprocess.run(cmd, cwd=self.project_root)
        return result.returncode
    
    def run_unit_tests(self, verbose=False, coverage=False):
        """Run all unit tests"""
        print("🧪 Running Unit Tests")
        test_path = self.tests_dir / "unit"
        return self.run_pytest([test_path], verbose, coverage)
    
    def run_integration_tests(self, verbose=False, coverage=False):
        """Run all integration tests"""
        print("🧪 Running Integration Tests")
        test_path = self.tests_dir / "integration"
        return self.run_pytest([test_path], verbose, coverage)
    
    def run_web_tests(self, verbose=False, coverage=False):
        """Run web interface tests"""
        print("🧪 Running Web Interface Tests")
        test_paths = [
            self.tests_dir / "unit" / "test_web_interface_refactored.py",
            self.tests_dir / "integration" / "test_web_ui_integration.py",
            self.tests_dir / "integration" / "test_ui_interactions.py",
        ]
        return self.run_pytest(test_paths, verbose, coverage)
    
    def run_misc_tests(self, verbose=False):
        """Run miscellaneous tests"""
        print("🧪 Running Miscellaneous Tests")
        test_path = self.tests_dir / "misc"
        
        # These are mostly standalone test scripts, run them individually
        misc_files = [
            "simple_test.py",
            "test_refactored_system.py",
            "test_all_refactoring.py",
        ]
        
        results = []
        for test_file in misc_files:
            test_path_full = test_path / test_file
            if test_path_full.exists():
                print(f"\n📝 Running {test_file}...")
                print("-" * 50)
                result = subprocess.run(
                    [sys.executable, str(test_path_full)],
                    cwd=self.project_root
                )
                results.append(result.returncode)
            else:
                print(f"⚠️  Test file not found: {test_file}")
        
        return 0 if all(r == 0 for r in results) else 1
    
    def run_fast_tests(self, verbose=False, coverage=False):
        """Run fast tests (unit tests only, skip slow integration)"""
        print("🧪 Running Fast Tests (Unit Tests Only)")
        return self.run_unit_tests(verbose, coverage)
    
    def run_all_tests(self, verbose=False, coverage=False):
        """Run all test suites"""
        print("🧪 Running All Tests")
        print("=" * 70)
        
        results = []
        
        print("\n" + "=" * 70)
        print("1️⃣  UNIT TESTS")
        print("=" * 70)
        results.append(self.run_unit_tests(verbose, coverage))
        
        print("\n" + "=" * 70)
        print("2️⃣  INTEGRATION TESTS")
        print("=" * 70)
        results.append(self.run_integration_tests(verbose, coverage))
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        
        suite_names = ["Unit Tests", "Integration Tests"]
        for i, (name, result) in enumerate(zip(suite_names, results)):
            status = "✅ PASSED" if result == 0 else "❌ FAILED"
            print(f"{name}: {status}")
        
        all_passed = all(r == 0 for r in results)
        print("\n" + "=" * 70)
        if all_passed:
            print("🎉 ALL TESTS PASSED!")
        else:
            print("❌ SOME TESTS FAILED")
        print("=" * 70)
        
        return 0 if all_passed else 1


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Unified Test Runner for CLIP Analysis Project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tests/run_tests.py                  # Run all tests
  python tests/run_tests.py --unit          # Run unit tests only
  python tests/run_tests.py --web --verbose # Run web tests with verbose output
  python tests/run_tests.py --fast --coverage # Run fast tests with coverage
        """
    )
    
    # Test suite selection
    suite_group = parser.add_mutually_exclusive_group()
    suite_group.add_argument('--unit', action='store_true',
                           help='Run unit tests only')
    suite_group.add_argument('--integration', action='store_true',
                           help='Run integration tests only')
    suite_group.add_argument('--web', action='store_true',
                           help='Run web interface tests only')
    suite_group.add_argument('--misc', action='store_true',
                           help='Run miscellaneous tests')
    suite_group.add_argument('--fast', action='store_true',
                           help='Run fast tests (unit tests only)')
    
    # Options
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    parser.add_argument('--coverage', '-c', action='store_true',
                       help='Run with coverage report')
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    # Run selected test suite
    if args.unit:
        return runner.run_unit_tests(args.verbose, args.coverage)
    elif args.integration:
        return runner.run_integration_tests(args.verbose, args.coverage)
    elif args.web:
        return runner.run_web_tests(args.verbose, args.coverage)
    elif args.misc:
        return runner.run_misc_tests(args.verbose)
    elif args.fast:
        return runner.run_fast_tests(args.verbose, args.coverage)
    else:
        # Run all tests by default
        return runner.run_all_tests(args.verbose, args.coverage)


if __name__ == "__main__":
    sys.exit(main())