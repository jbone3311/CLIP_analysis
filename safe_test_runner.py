#!/usr/bin/env python3
"""
Safe test runner that avoids hanging issues
"""

import os
import sys
import importlib
import traceback

def safe_import_test(module_name):
    """Safely test importing a module"""
    try:
        importlib.import_module(module_name)
        return True, None
    except Exception as e:
        return False, str(e)

def test_core_modules():
    """Test core modules that should work"""
    print("🔍 Testing core modules...")
    
    core_modules = [
        'src.config.config_manager',
        'src.analyzers.metadata_extractor',
        'src.utils.installer',
        'src.viewers.results_viewer'
    ]
    
    results = []
    for module in core_modules:
        success, error = safe_import_test(module)
        if success:
            print(f"  ✅ {module}")
            results.append((module, "PASS"))
        else:
            print(f"  ❌ {module}: {error}")
            results.append((module, f"FAIL: {error}"))
    
    return results

def test_service_modules():
    """Test service modules"""
    print("\n🔍 Testing service modules...")
    
    service_modules = [
        'src.services.analysis_service',
        'src.services.image_service',
        'src.services.config_service'
    ]
    
    results = []
    for module in service_modules:
        success, error = safe_import_test(module)
        if success:
            print(f"  ✅ {module}")
            results.append((module, "PASS"))
        else:
            print(f"  ❌ {module}: {error}")
            results.append((module, f"FAIL: {error}"))
    
    return results

def test_route_modules():
    """Test route modules"""
    print("\n🔍 Testing route modules...")
    
    route_modules = [
        'src.routes.main_routes',
        'src.routes.api_routes'
    ]
    
    results = []
    for module in route_modules:
        success, error = safe_import_test(module)
        if success:
            print(f"  ✅ {module}")
            results.append((module, "PASS"))
        else:
            print(f"  ❌ {module}: {error}")
            results.append((module, f"FAIL: {error}"))
    
    return results

def test_manager_modules():
    """Test manager modules (these might be problematic)"""
    print("\n🔍 Testing manager modules...")
    
    manager_modules = [
        'src.database.db_manager',
        'src.analyzers.llm_manager'
    ]
    
    results = []
    for module in manager_modules:
        print(f"  Testing {module}...")
        success, error = safe_import_test(module)
        if success:
            print(f"    ✅ {module}")
            results.append((module, "PASS"))
        else:
            print(f"    ❌ {module}: {error}")
            results.append((module, f"FAIL: {error}"))
    
    return results

def test_analyzer_modules():
    """Test analyzer modules"""
    print("\n🔍 Testing analyzer modules...")
    
    analyzer_modules = [
        'src.analyzers.clip_analyzer',
        'src.analyzers.llm_analyzer'
    ]
    
    results = []
    for module in analyzer_modules:
        success, error = safe_import_test(module)
        if success:
            print(f"  ✅ {module}")
            results.append((module, "PASS"))
        else:
            print(f"  ❌ {module}: {error}")
            results.append((module, f"FAIL: {error}"))
    
    return results

def main():
    """Run safe tests"""
    print("🚀 Safe Test Runner")
    print("=" * 30)
    
    # Add project root to path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    all_results = []
    
    # Test core modules
    core_results = test_core_modules()
    all_results.extend(core_results)
    
    # Test service modules
    service_results = test_service_modules()
    all_results.extend(service_results)
    
    # Test route modules
    route_results = test_route_modules()
    all_results.extend(route_results)
    
    # Test analyzer modules
    analyzer_results = test_analyzer_modules()
    all_results.extend(analyzer_results)
    
    # Test manager modules last (most likely to cause issues)
    manager_results = test_manager_modules()
    all_results.extend(manager_results)
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 20)
    
    passed = sum(1 for _, result in all_results if result == "PASS")
    failed = sum(1 for _, result in all_results if result != "PASS")
    
    print(f"Total modules tested: {len(all_results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed > 0:
        print("\n❌ Failed modules:")
        for module, result in all_results:
            if result != "PASS":
                print(f"  • {module}: {result}")
    
    if failed == 0:
        print("\n🎉 All modules imported successfully!")
        return 0
    else:
        print(f"\n⚠️  {failed} modules failed to import")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 