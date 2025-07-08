#!/usr/bin/env python3
"""
Simple test to check basic functionality without any server startup
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_imports():
    """Test basic imports without any server startup"""
    print("Testing basic imports...")
    
    try:
        # Test basic modules
        import src.config.config_manager
        print("✅ config_manager imported")
        
        import src.database.db_manager
        print("✅ db_manager imported")
        
        import src.analyzers.llm_manager
        print("✅ llm_manager imported")
        
        import src.analyzers.metadata_extractor
        print("✅ metadata_extractor imported")
        
        import src.utils.installer
        print("✅ installer imported")
        
        import src.viewers.results_viewer
        print("✅ results_viewer imported")
        
        print("\n✅ All basic imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_service_imports():
    """Test service imports"""
    print("\nTesting service imports...")
    
    try:
        import src.services.analysis_service
        print("✅ analysis_service imported")
        
        import src.services.image_service
        print("✅ image_service imported")
        
        import src.services.config_service
        print("✅ config_service imported")
        
        print("✅ All service imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Service import error: {e}")
        return False

def test_route_imports():
    """Test route imports"""
    print("\nTesting route imports...")
    
    try:
        import src.routes.main_routes
        print("✅ main_routes imported")
        
        import src.routes.api_routes
        print("✅ api_routes imported")
        
        print("✅ All route imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Route import error: {e}")
        return False

def main():
    """Run simple tests"""
    print("🚀 Simple Import Test")
    print("=" * 30)
    
    success = True
    
    if not test_basic_imports():
        success = False
    
    if not test_service_imports():
        success = False
    
    if not test_route_imports():
        success = False
    
    print("\n" + "=" * 30)
    if success:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 