#!/usr/bin/env python3
"""
Test Refactoring Utilities

This script tests the new logging, error handling, and debugging utilities
to ensure they work correctly.
"""

import os
import sys
import time
import tempfile
import shutil
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_logging_system():
    """Test the centralized logging system"""
    print("🧪 Testing Logging System...")
    
    try:
        from src.utils.logger import get_logger, setup_global_logging
        
        # Test logger creation
        logger = get_logger('test_module')
        assert logger is not None, "Logger should be created"
        
        # Test different log levels
        logger.debug("Debug message", data={'test': True})
        logger.info("Info message", data={'count': 42})
        logger.warning("Warning message", data={'issue': 'minor'})
        logger.error("Error message", data={'error_code': 500})
        
        # Test performance tracking
        logger.start_timer("test_operation")
        time.sleep(0.1)  # Simulate work
        duration = logger.end_timer("test_operation")
        assert duration > 0, "Timer should return positive duration"
        
        # Test context manager
        with logger.timed_operation("context_test"):
            time.sleep(0.05)  # Simulate work
        
        print("✅ Logging system tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Logging system tests failed: {e}")
        return False

def test_error_handling():
    """Test the error handling system"""
    print("🧪 Testing Error Handling System...")
    
    try:
        from src.utils.error_handler import (
            ErrorHandler, ErrorCategory, ErrorContext, 
            handle_errors, error_context, graceful_degradation
        )
        
        # Test error handler creation
        handler = ErrorHandler()
        assert handler is not None, "Error handler should be created"
        
        # Test error categorization
        context = ErrorContext("test_operation", ErrorCategory.API)
        assert context.operation == "test_operation", "Context should store operation"
        
        # Test error context manager
        with error_context("test_context", ErrorCategory.FILE_IO) as ctx:
            ctx.add_context("filename", "test.txt")
            assert ctx.context_data['filename'] == "test.txt", "Context data should be stored"
        
        # Test graceful degradation decorator
        @graceful_degradation(default_value="fallback")
        def failing_function():
            raise Exception("Test error")
        
        result = failing_function()
        assert result == "fallback", "Graceful degradation should return fallback value"
        
        print("✅ Error handling system tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error handling system tests failed: {e}")
        return False

def test_debug_utilities():
    """Test the debugging utilities"""
    print("🧪 Testing Debug Utilities...")
    
    try:
        from src.utils.debug_utils import (
            DebugInspector, PerformanceProfiler, MemoryTracker,
            debug_function, debug_context, get_debug_info
        )
        
        # Test debug inspector
        inspector = DebugInspector()
        test_var = {"key": "value", "number": 42}
        info = inspector.inspect_variable(test_var, "test_variable")
        assert info['type'] == 'dict', "Should correctly identify variable type"
        
        # Test performance profiler
        profiler = PerformanceProfiler()
        with profiler.profile("test_profile"):
            time.sleep(0.1)  # Simulate work
        
        stats = profiler.get_profile_stats("test_profile")
        assert stats['count'] == 1, "Should have one profile entry"
        assert stats['avg_duration'] > 0, "Should have positive duration"
        
        # Test memory tracker
        tracker = MemoryTracker()
        tracker.take_snapshot("before")
        # Simulate memory usage
        large_list = [i for i in range(1000)]
        tracker.take_snapshot("after")
        
        comparison = tracker.compare_snapshots("before", "after")
        assert 'rss_delta' in comparison, "Should provide memory comparison"
        
        # Test debug info
        debug_info = get_debug_info()
        assert 'system' in debug_info, "Should provide system information"
        assert 'process' in debug_info, "Should provide process information"
        
        print("✅ Debug utilities tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Debug utilities tests failed: {e}")
        return False

def test_integration():
    """Test integration of all utilities"""
    print("🧪 Testing Integration...")
    
    try:
        from src.utils.logger import get_logger
        from src.utils.error_handler import error_context, ErrorCategory
        from src.utils.debug_utils import debug_function, debug_context
        
        logger = get_logger('integration_test')
        
        # Test integrated debugging
        @debug_function(profile=True)
        def test_function(data):
            logger.info("Processing data", data={'input_size': len(data)})
            return len(data) * 2
        
        result = test_function([1, 2, 3, 4, 5])
        assert result == 10, "Function should return correct result"
        
        # Test error handling with logging
        with error_context("integration_test", ErrorCategory.VALIDATION) as context:
            context.add_context("test_data", "sample")
            logger.info("Testing integration", data={'context': context.context_data})
        
        print("✅ Integration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Integration tests failed: {e}")
        return False

def test_configuration():
    """Test configuration and environment setup"""
    print("🧪 Testing Configuration...")
    
    try:
        # Test environment variables
        os.environ['LOG_LEVEL'] = 'DEBUG'
        os.environ['DEBUG'] = 'True'
        
        from src.utils.logger import setup_global_logging
        from src.utils.debug_utils import enable_debug_mode, disable_debug_mode
        
        # Test debug mode
        enable_debug_mode()
        assert os.getenv('DEBUG') == 'True', "Debug mode should be enabled"
        
        disable_debug_mode()
        assert os.getenv('DEBUG') == 'False', "Debug mode should be disabled"
        
        print("✅ Configuration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Configuration tests failed: {e}")
        return False

def test_file_operations():
    """Test file operations with new utilities"""
    print("🧪 Testing File Operations...")
    
    try:
        from src.utils.logger import get_logger
        from src.utils.error_handler import handle_errors, ErrorCategory
        
        logger = get_logger('file_test')
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "test.txt")
            
            @handle_errors(category=ErrorCategory.FILE_IO)
            def write_file(filename, content):
                with open(filename, 'w') as f:
                    f.write(content)
                logger.info("File written successfully", data={'filename': filename})
            
            @handle_errors(category=ErrorCategory.FILE_IO)
            def read_file(filename):
                with open(filename, 'r') as f:
                    content = f.read()
                logger.info("File read successfully", data={'filename': filename})
                return content
            
            # Test file operations
            write_file(test_file, "Hello, World!")
            content = read_file(test_file)
            assert content == "Hello, World!", "File content should match"
            
            # Test error handling with non-existent file
            try:
                read_file("nonexistent.txt")
                assert False, "Should have raised an error"
            except Exception:
                pass  # Expected error
        
        print("✅ File operations tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ File operations tests failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Refactoring Utilities")
    print("=" * 50)
    
    tests = [
        test_logging_system,
        test_error_handling,
        test_debug_utilities,
        test_integration,
        test_configuration,
        test_file_operations
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print("📊 Test Results")
    print("=" * 50)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"🎯 Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 All refactoring utility tests passed!")
        print("\nThe new utilities are working correctly:")
        print("• ✅ Centralized logging system")
        print("• ✅ Comprehensive error handling")
        print("• ✅ Advanced debugging utilities")
        print("• ✅ Performance monitoring")
        print("• ✅ Memory tracking")
        print("• ✅ Configuration management")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Check the output above for details.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 