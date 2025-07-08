#!/usr/bin/env python3
"""
Test core modules without web interface imports
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_core_imports():
    """Test core module imports"""
    print("Testing core module imports...")
    
    try:
        # Test basic modules that don't start servers
        import src.config.config_manager
        print("✅ config_manager imported")
        
        import src.analyzers.metadata_extractor
        print("✅ metadata_extractor imported")
        
        import src.utils.installer
        print("✅ installer imported")
        
        import src.viewers.results_viewer
        print("✅ results_viewer imported")
        
        print("✅ All core imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Core import error: {e}")
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

def test_manager_imports():
    """Test manager imports (these might hang)"""
    print("\nTesting manager imports...")
    
    try:
        import src.database.db_manager
        print("✅ db_manager imported")
        
        import src.analyzers.llm_manager
        print("✅ llm_manager imported")
        
        print("✅ All manager imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Manager import error: {e}")
        return False

def test_analyzer_imports():
    """Test analyzer imports"""
    print("\nTesting analyzer imports...")
    
    try:
        import src.analyzers.clip_analyzer
        print("✅ clip_analyzer imported")
        
        import src.analyzers.llm_analyzer
        print("✅ llm_analyzer imported")
        
        print("✅ All analyzer imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Analyzer import error: {e}")
        return False

def main():
    """Run core tests"""
    print("🚀 Core Module Test")
    print("=" * 30)
    
    success = True
    
    if not test_core_imports():
        success = False
    
    if not test_service_imports():
        success = False
    
    if not test_route_imports():
        success = False
    
    if not test_analyzer_imports():
        success = False
    
    # Test managers last as they might hang
    print("\n⚠️  Testing managers (this might take a moment)...")
    if not test_manager_imports():
        success = False
    
    print("\n" + "=" * 30)
    if success:
        print("✅ All core tests passed!")
        return 0
    else:
        print("❌ Some core tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 