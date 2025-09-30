#!/usr/bin/env python3
"""
Fixed CLI Non-Interactive Mode Tests
Handles Unicode encoding issues on Windows
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def run_command_with_unicode_fix(command, timeout=30):
    """Run command with proper Unicode handling"""
    try:
        # Use UTF-8 encoding and handle Unicode properly
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',  # Replace problematic characters
            timeout=timeout,
            env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)

def test_global_flags():
    """Test global flags"""
    print("📊 Running Global Flags Tests")
    print("-" * 40)
    
    tests = [
        ("Global help", "python main.py --help"),
        ("Config with yes flag", "python main.py config --no-interactive --yes --show"),
        ("No command with no-interactive", "python main.py --no-interactive")
    ]
    
    passed = 0
    failed = 0
    
    for test_name, command in tests:
        print(f"🧪 Testing: {test_name}")
        print(f"   Command: {command}")
        
        exit_code, stdout, stderr = run_command_with_unicode_fix(command)
        
        if exit_code == 0:
            print("   ✅ SUCCESS")
            passed += 1
        elif test_name == "No command with no-interactive" and exit_code != 0:
            print("   ✅ EXPECTED FAILURE")
            passed += 1
        else:
            print(f"   ❌ FAILED (exit code: {exit_code})")
            if stderr:
                print(f"   Error: {stderr[:200]}...")
            failed += 1
    
    print(f"Global Flags: {passed} passed, {failed} failed")
    return passed, failed

def test_process_command():
    """Test process command"""
    print("\n📊 Running Process Command Tests")
    print("-" * 40)
    
    tests = [
        ("Basic process with no-interactive flag", "python main.py process --no-interactive"),
        ("Process with all features disabled", "python main.py process --no-interactive --disable-clip --disable-llm --disable-metadata --disable-parallel --disable-summaries"),
        ("Process with non-existent input directory", "python main.py process --no-interactive --input nonexistent_directory")
    ]
    
    passed = 0
    failed = 0
    
    for test_name, command in tests:
        print(f"🧪 Testing: {test_name}")
        print(f"   Command: {command}")
        
        exit_code, stdout, stderr = run_command_with_unicode_fix(command, timeout=10)
        
        if exit_code == 0:
            print("   ✅ SUCCESS")
            passed += 1
        elif test_name == "Process with non-existent input directory" and exit_code != 0:
            print("   ✅ EXPECTED FAILURE")
            passed += 1
        else:
            print(f"   ❌ FAILED (exit code: {exit_code})")
            if stderr:
                print(f"   Error: {stderr[:200]}...")
            failed += 1
    
    print(f"Process Command: {passed} passed, {failed} failed")
    return passed, failed

def test_config_command():
    """Test config command"""
    print("\n📊 Running Config Command Tests")
    print("-" * 40)
    
    tests = [
        ("Show configuration", "python main.py config --no-interactive --show"),
        ("Validate configuration", "python main.py config --no-interactive --validate")
    ]
    
    passed = 0
    failed = 0
    
    for test_name, command in tests:
        print(f"🧪 Testing: {test_name}")
        print(f"   Command: {command}")
        
        exit_code, stdout, stderr = run_command_with_unicode_fix(command)
        
        if exit_code == 0:
            print("   ✅ SUCCESS")
            passed += 1
        else:
            print(f"   ❌ FAILED (exit code: {exit_code})")
            if stderr:
                print(f"   Error: {stderr[:200]}...")
            failed += 1
    
    print(f"Config Command: {passed} passed, {failed} failed")
    return passed, failed

def test_llm_config_command():
    """Test LLM config command"""
    print("\n📊 Running LLM Config Command Tests")
    print("-" * 40)
    
    tests = [
        ("List available models", "python main.py llm-config --no-interactive --list"),
        ("List configured models", "python main.py llm-config --no-interactive --list-configured"),
        ("Test Ollama connection", "python main.py llm-config --no-interactive --test-ollama"),
        ("Test all connections", "python main.py llm-config --no-interactive --test-all")
    ]
    
    passed = 0
    failed = 0
    
    for test_name, command in tests:
        print(f"🧪 Testing: {test_name}")
        print(f"   Command: {command}")
        
        exit_code, stdout, stderr = run_command_with_unicode_fix(command)
        
        if exit_code == 0:
            print("   ✅ SUCCESS")
            passed += 1
        else:
            print(f"   ❌ FAILED (exit code: {exit_code})")
            if stderr:
                print(f"   Error: {stderr[:200]}...")
            failed += 1
    
    print(f"LLM Config Command: {passed} passed, {failed} failed")
    return passed, failed

def test_view_command():
    """Test view command"""
    print("\n📊 Running View Command Tests")
    print("-" * 40)
    
    tests = [
        ("List results", "python main.py view --no-interactive --list"),
        ("Generate summary", "python main.py view --no-interactive --summary"),
        ("Export to CSV", "python main.py view --no-interactive --export csv --output test_export.csv"),
        ("Export to JSON", "python main.py view --no-interactive --export json --output test_export.json")
    ]
    
    passed = 0
    failed = 0
    
    for test_name, command in tests:
        print(f"🧪 Testing: {test_name}")
        print(f"   Command: {command}")
        
        exit_code, stdout, stderr = run_command_with_unicode_fix(command)
        
        if exit_code == 0:
            print("   ✅ SUCCESS")
            passed += 1
        else:
            print(f"   ❌ FAILED (exit code: {exit_code})")
            if stderr:
                print(f"   Error: {stderr[:200]}...")
            failed += 1
    
    print(f"View Command: {passed} passed, {failed} failed")
    return passed, failed

def test_database_command():
    """Test database command"""
    print("\n📊 Running Database Command Tests")
    print("-" * 40)
    
    tests = [
        ("Show database stats", "python main.py database --no-interactive --stats")
    ]
    
    passed = 0
    failed = 0
    
    for test_name, command in tests:
        print(f"🧪 Testing: {test_name}")
        print(f"   Command: {command}")
        
        exit_code, stdout, stderr = run_command_with_unicode_fix(command)
        
        if exit_code == 0:
            print("   ✅ SUCCESS")
            passed += 1
        else:
            print(f"   ❌ FAILED (exit code: {exit_code})")
            if stderr:
                print(f"   Error: {stderr[:200]}...")
            failed += 1
    
    print(f"Database Command: {passed} passed, {failed} failed")
    return passed, failed

def main():
    """Run all CLI tests"""
    print("🧪 Fixed CLI Non-Interactive Mode Tests")
    print("=" * 60)
    print("Testing that CLI can run completely non-interactively")
    print("with all options provided via command-line arguments.")
    print("Fixed for Unicode encoding issues on Windows.")
    print()
    
    total_passed = 0
    total_failed = 0
    
    # Run all test suites
    test_suites = [
        ("Global Flags", test_global_flags),
        ("Process Command", test_process_command),
        ("Config Command", test_config_command),
        ("LLM Config Command", test_llm_config_command),
        ("View Command", test_view_command),
        ("Database Command", test_database_command)
    ]
    
    for suite_name, test_func in test_suites:
        print(f"\n📋 Testing {suite_name}")
        print("=" * 50)
        passed, failed = test_func()
        total_passed += passed
        total_failed += failed
    
    print("\n" + "=" * 60)
    print("📊 Final Test Results")
    print("=" * 60)
    print(f"✅ Total Passed: {total_passed}")
    print(f"❌ Total Failed: {total_failed}")
    print(f"🎯 Total Tests: {total_passed + total_failed}")
    
    if total_failed == 0:
        print("\n🎉 All tests passed! CLI is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total_failed} test(s) failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    exit(main()) 