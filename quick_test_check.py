#!/usr/bin/env python3
"""
Quick test to identify issues without running full test suites
"""

import os
import sys
import importlib
import traceback

def test_imports():
    """Test that all modules can be imported"""
    print("🔍 Testing imports...")
    
    modules_to_test = [
        'src.analyzers.clip_analyzer',
        'src.analyzers.llm_analyzer', 
        'src.analyzers.llm_manager',
        'src.analyzers.metadata_extractor',
        'src.config.config_manager',
        'src.database.db_manager',
        'src.utils.installer',
        'src.viewers.results_viewer',
        'src.viewers.web_interface',
        'src.viewers.web_interface_refactored',
        'src.services.analysis_service',
        'src.services.image_service', 
        'src.services.config_service',
        'src.routes.main_routes',
        'src.routes.api_routes',
        'directory_processor',
        'main'
    ]
    
    failed_imports = []
    
    for module in modules_to_test:
        try:
            importlib.import_module(module)
            print(f"  ✅ {module}")
        except Exception as e:
            print(f"  ❌ {module}: {e}")
            failed_imports.append((module, str(e)))
    
    return failed_imports

def test_basic_functionality():
    """Test basic functionality without starting servers"""
    print("\n🔍 Testing basic functionality...")
    
    issues = []
    
    # Test config manager
    try:
        from src.config.config_manager import ConfigManager
        config = ConfigManager()
        print("  ✅ ConfigManager")
    except Exception as e:
        print(f"  ❌ ConfigManager: {e}")
        issues.append(f"ConfigManager: {e}")
    
    # Test database manager
    try:
        from src.database.db_manager import DatabaseManager
        db = DatabaseManager()
        print("  ✅ DatabaseManager")
    except Exception as e:
        print(f"  ❌ DatabaseManager: {e}")
        issues.append(f"DatabaseManager: {e}")
    
    # Test LLM manager
    try:
        from src.analyzers.llm_manager import LLMManager
        llm = LLMManager()
        print("  ✅ LLMManager")
    except Exception as e:
        print(f"  ❌ LLMManager: {e}")
        issues.append(f"LLMManager: {e}")
    
    return issues

def test_service_modules():
    """Test service modules"""
    print("\n🔍 Testing service modules...")
    
    issues = []
    
    try:
        from src.services.analysis_service import AnalysisService
        service = AnalysisService()
        print("  ✅ AnalysisService")
    except Exception as e:
        print(f"  ❌ AnalysisService: {e}")
        issues.append(f"AnalysisService: {e}")
    
    try:
        from src.services.image_service import ImageService
        service = ImageService()
        print("  ✅ ImageService")
    except Exception as e:
        print(f"  ❌ ImageService: {e}")
        issues.append(f"ImageService: {e}")
    
    try:
        from src.services.config_service import ConfigService
        service = ConfigService()
        print("  ✅ ConfigService")
    except Exception as e:
        print(f"  ❌ ConfigService: {e}")
        issues.append(f"ConfigService: {e}")
    
    return issues

def main():
    """Run quick tests"""
    print("🚀 Quick Test Check")
    print("=" * 50)
    
    # Test imports
    import_issues = test_imports()
    
    # Test basic functionality
    basic_issues = test_basic_functionality()
    
    # Test service modules
    service_issues = test_service_modules()
    
    # Summary
    print("\n📊 Summary")
    print("=" * 20)
    
    total_issues = len(import_issues) + len(basic_issues) + len(service_issues)
    
    if total_issues == 0:
        print("✅ All tests passed! No issues found.")
    else:
        print(f"❌ Found {total_issues} issues:")
        
        if import_issues:
            print("\nImport Issues:")
            for module, error in import_issues:
                print(f"  • {module}: {error}")
        
        if basic_issues:
            print("\nBasic Functionality Issues:")
            for issue in basic_issues:
                print(f"  • {issue}")
        
        if service_issues:
            print("\nService Module Issues:")
            for issue in service_issues:
                print(f"  • {issue}")
    
    return total_issues

if __name__ == "__main__":
    sys.exit(main()) 