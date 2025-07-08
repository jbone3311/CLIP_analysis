#!/usr/bin/env python3
"""
Comprehensive Test for All Refactoring Improvements

This script tests all the new utilities and updated modules to ensure
the refactoring improvements work correctly.
"""

import os
import sys
import time
import tempfile
import shutil
import json
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

def test_database_manager():
    """Test the updated database manager"""
    print("🧪 Testing Database Manager...")
    
    try:
        from src.database.db_manager import DatabaseManager
        
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
            db_path = tmp_db.name
        
        try:
            # Test database initialization
            db_manager = DatabaseManager(db_path)
            assert db_manager is not None, "Database manager should be created"
            
            # Test result insertion
            db_manager.insert_result(
                filename="test.jpg",
                directory="/test",
                md5="test_md5",
                model="test_model",
                modes="best,fast",
                prompts="P1,P2",
                analysis_results='{"test": "data"}',
                settings='{"setting": "value"}'
            )
            
            # Test result retrieval
            result = db_manager.get_result_by_md5("test_md5")
            assert result is not None, "Should retrieve inserted result"
            assert result['filename'] == "test.jpg", "Should have correct filename"
            
            print("✅ Database manager tests passed!")
            return True
            
        finally:
            # Clean up
            if os.path.exists(db_path):
                os.unlink(db_path)
        
    except Exception as e:
        print(f"❌ Database manager tests failed: {e}")
        return False

def test_metadata_extractor():
    """Test the updated metadata extractor"""
    print("🧪 Testing Metadata Extractor...")
    
    try:
        from src.analyzers.metadata_extractor import extract_metadata
        
        # Create a simple test image (1x1 pixel PNG)
        from PIL import Image
        import io
        
        # Create a simple test image
        img = Image.new('RGB', (100, 100), color='red')
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_img:
            img.save(tmp_img.name, 'PNG')
            img_path = tmp_img.name
        
        try:
            # Test metadata extraction
            metadata = extract_metadata(img_path)
            assert metadata is not None, "Should extract metadata"
            assert 'filename' in metadata, "Should have filename"
            assert 'width' in metadata, "Should have width"
            assert 'height' in metadata, "Should have height"
            assert 'md5' in metadata, "Should have MD5 hash"
            
            print("✅ Metadata extractor tests passed!")
            return True
            
        finally:
            # Clean up
            if os.path.exists(img_path):
                os.unlink(img_path)
        
    except Exception as e:
        print(f"❌ Metadata extractor tests failed: {e}")
        return False

def test_llm_manager():
    """Test the updated LLM manager"""
    print("🧪 Testing LLM Manager...")
    
    try:
        from src.analyzers.llm_manager import LLMManager
        
        # Test LLM manager initialization
        llm_manager = LLMManager()
        assert llm_manager is not None, "LLM manager should be created"
        
        # Test model retrieval (these should work without API keys)
        openai_models = llm_manager.get_openai_models()
        assert len(openai_models) > 0, "Should return OpenAI models"
        
        anthropic_models = llm_manager.get_anthropic_models()
        assert len(anthropic_models) > 0, "Should return Anthropic models"
        
        google_models = llm_manager.get_google_models()
        assert len(google_models) > 0, "Should return Google models"
        
        # Test all available models
        all_models = llm_manager.get_all_available_models()
        assert len(all_models) > 0, "Should return all available models"
        
        print("✅ LLM manager tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ LLM manager tests failed: {e}")
        return False

def test_clip_analyzer():
    """Test the updated CLIP analyzer"""
    print("🧪 Testing CLIP Analyzer...")
    
    try:
        from src.analyzers.clip_analyzer import encode_image_to_base64
        
        # Create a simple test image
        from PIL import Image
        import io
        
        img = Image.new('RGB', (100, 100), color='blue')
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_img:
            img.save(tmp_img.name, 'PNG')
            img_path = tmp_img.name
        
        try:
            # Test image encoding
            encoded = encode_image_to_base64(img_path)
            assert encoded is not None, "Should encode image"
            assert len(encoded) > 0, "Encoded string should not be empty"
            
            print("✅ CLIP analyzer tests passed!")
            return True
            
        finally:
            # Clean up
            if os.path.exists(img_path):
                os.unlink(img_path)
        
    except Exception as e:
        print(f"❌ CLIP analyzer tests failed: {e}")
        return False

def test_directory_processor():
    """Test the updated directory processor"""
    print("🧪 Testing Directory Processor...")
    
    try:
        from directory_processor import DirectoryProcessor
        
        # Create test configuration
        config = {
            'ENABLE_CLIP_ANALYSIS': False,  # Disable to avoid API calls
            'ENABLE_LLM_ANALYSIS': False,   # Disable to avoid API calls
            'ENABLE_METADATA_EXTRACTION': True,
            'IMAGE_DIRECTORY': 'Images',
            'OUTPUT_DIRECTORY': 'Output',
            'CLIP_MODES': ['best', 'fast'],
            'PROMPT_CHOICES': ['P1', 'P2']
        }
        
        # Test processor initialization
        processor = DirectoryProcessor(config)
        assert processor is not None, "Directory processor should be created"
        
        # Test image file finding
        image_files = processor.find_image_files('Images')
        assert isinstance(image_files, list), "Should return list of image files"
        
        print("✅ Directory processor tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Directory processor tests failed: {e}")
        return False

def test_web_interface():
    """Test the updated web interface"""
    print("🧪 Testing Web Interface...")
    
    try:
        from src.viewers.web_interface_refactored import WebInterface
        
        # Test web interface initialization
        web_interface = WebInterface()
        assert web_interface is not None, "Web interface should be created"
        assert web_interface.app is not None, "Flask app should be created"
        
        # Test configuration
        assert web_interface.allowed_extensions is not None, "Should have allowed extensions"
        assert web_interface.max_content_length > 0, "Should have max content length"
        
        print("✅ Web interface tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Web interface tests failed: {e}")
        return False

def test_main_entry_point():
    """Test the updated main entry point"""
    print("🧪 Testing Main Entry Point...")
    
    try:
        # Test that main.py can be imported without errors
        import main
        assert main is not None, "Main module should be importable"
        
        # Test that logger is available
        from src.utils.logger import get_global_logger
        logger = get_global_logger()
        assert logger is not None, "Global logger should be available"
        
        print("✅ Main entry point tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Main entry point tests failed: {e}")
        return False

def test_integration():
    """Test integration of all components"""
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

def main():
    """Run all tests"""
    print("🚀 Testing All Refactoring Improvements")
    print("=" * 60)
    
    tests = [
        test_logging_system,
        test_error_handling,
        test_debug_utilities,
        test_database_manager,
        test_metadata_extractor,
        test_llm_manager,
        test_clip_analyzer,
        test_directory_processor,
        test_web_interface,
        test_main_entry_point,
        test_integration,
        test_configuration
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
    
    print("\n" + "=" * 60)
    print("📊 Test Results")
    print("=" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"🎯 Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 All refactoring improvement tests passed!")
        print("\nThe refactoring improvements are working correctly:")
        print("• ✅ Centralized logging system")
        print("• ✅ Comprehensive error handling")
        print("• ✅ Advanced debugging utilities")
        print("• ✅ Updated database manager")
        print("• ✅ Updated metadata extractor")
        print("• ✅ Updated LLM manager")
        print("• ✅ Updated CLIP analyzer")
        print("• ✅ Updated directory processor")
        print("• ✅ Updated web interface")
        print("• ✅ Updated main entry point")
        print("• ✅ Performance monitoring")
        print("• ✅ Memory tracking")
        print("• ✅ Configuration management")
        print("• ✅ Integration testing")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Check the output above for details.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 