#!/usr/bin/env python3
"""
Simple test runner for Image Analysis with CLIP and LLM

This script runs basic functionality tests without complex imports.
"""

import unittest
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

class TestBasicFunctionality(unittest.TestCase):
    """Basic functionality tests"""
    
    def test_project_structure(self):
        """Test that project structure is correct"""
        # Check that src directory exists
        self.assertTrue(os.path.exists("src"))
        self.assertTrue(os.path.exists("src/analyzers"))
        self.assertTrue(os.path.exists("src/config"))
        self.assertTrue(os.path.exists("src/viewers"))
        self.assertTrue(os.path.exists("src/utils"))
        
        # Check that test directory exists
        self.assertTrue(os.path.exists("tests"))
        self.assertTrue(os.path.exists("tests/unit"))
        self.assertTrue(os.path.exists("tests/integration"))
    
    def test_config_files_exist(self):
        """Test that configuration files exist"""
        self.assertTrue(os.path.exists("config/prompts.json"))
        self.assertTrue(os.path.exists("requirements.txt"))
        self.assertTrue(os.path.exists("setup.py"))
        self.assertTrue(os.path.exists("pytest.ini"))
        self.assertTrue(os.path.exists("Makefile"))
    
    def test_main_files_exist(self):
        """Test that main files exist"""
        self.assertTrue(os.path.exists("main.py"))
        self.assertTrue(os.path.exists("directory_processor.py"))
        self.assertTrue(os.path.exists("README.md"))
    
    def test_package_init_files(self):
        """Test that package __init__.py files exist"""
        init_files = [
            "src/__init__.py",
            "src/analyzers/__init__.py",
            "src/config/__init__.py",
            "src/viewers/__init__.py",
            "src/utils/__init__.py",
            "tests/__init__.py",
            "tests/unit/__init__.py",
            "tests/integration/__init__.py"
        ]
        
        for init_file in init_files:
            self.assertTrue(os.path.exists(init_file), f"Missing {init_file}")
    
    def test_analyzer_modules_exist(self):
        """Test that analyzer modules exist"""
        analyzer_files = [
            "src/analyzers/clip_analyzer.py",
            "src/analyzers/llm_analyzer.py",
            "src/analyzers/metadata_extractor.py"
        ]
        
        for analyzer_file in analyzer_files:
            self.assertTrue(os.path.exists(analyzer_file), f"Missing {analyzer_file}")
    
    def test_utility_modules_exist(self):
        """Test that utility modules exist"""
        utility_files = [
            "src/config/config_manager.py",
            "src/viewers/results_viewer.py",
            "src/utils/installer.py"
        ]
        
        for utility_file in utility_files:
            self.assertTrue(os.path.exists(utility_file), f"Missing {utility_file}")
    
    def test_test_files_exist(self):
        """Test that test files exist"""
        test_files = [
            "tests/unit/test_clip_analyzer.py",
            "tests/unit/test_llm_analyzer.py",
            "tests/unit/test_metadata_extractor.py",
            "tests/unit/test_config_manager.py",
            "tests/unit/test_results_viewer.py",
            "tests/unit/test_installer.py",
            "tests/unit/test_directory_processor.py",
            "tests/unit/test_main.py",
            "tests/integration/test_system.py",
            "tests/run_tests.py"
        ]
        
        for test_file in test_files:
            self.assertTrue(os.path.exists(test_file), f"Missing {test_file}")

class TestImportFunctionality(unittest.TestCase):
    """Test basic import functionality"""
    
    def test_src_import(self):
        """Test that src package can be imported"""
        try:
            import src
            self.assertTrue(True, "src package imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import src package: {e}")
    
    def test_analyzers_import(self):
        """Test that analyzers package can be imported"""
        try:
            import src.analyzers
            self.assertTrue(True, "analyzers package imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import analyzers package: {e}")
    
    def test_config_import(self):
        """Test that config package can be imported"""
        try:
            import src.config
            self.assertTrue(True, "config package imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import config package: {e}")
    
    def test_viewers_import(self):
        """Test that viewers package can be imported"""
        try:
            import src.viewers
            self.assertTrue(True, "viewers package imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import viewers package: {e}")
    
    def test_utils_import(self):
        """Test that utils package can be imported"""
        try:
            import src.utils
            self.assertTrue(True, "utils package imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import utils package: {e}")

def run_basic_tests():
    """Run basic functionality tests"""
    print("🧪 Running Basic Functionality Tests...")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestBasicFunctionality))
    suite.addTests(loader.loadTestsFromTestCase(TestImportFunctionality))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_basic_tests()
    
    print("\n📊 Basic Test Results Summary")
    print("=" * 50)
    print(f"Basic Tests: {'✅ PASSED' if success else '❌ FAILED'}")
    
    if success:
        print("\n✅ All basic tests passed! The project structure is correct.")
    else:
        print("\n❌ Some basic tests failed. Please check the project structure.")
    
    sys.exit(0 if success else 1) 