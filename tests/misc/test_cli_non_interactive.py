#!/usr/bin/env python3
"""
Test CLI Non-Interactive Mode

This script tests that the CLI can run completely non-interactively
with all options provided via command-line arguments.
"""

import sys
import os
import subprocess
import tempfile
import shutil
from pathlib import Path

def run_cli_command(cmd_args, description, expect_success=True):
    """Run a CLI command and check the result"""
    print(f"🧪 Testing: {description}")
    print(f"   Command: python main.py {' '.join(cmd_args)}")
    
    try:
        result = subprocess.run(
            [sys.executable, 'main.py'] + cmd_args,
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
        )
        
        if expect_success:
            if result.returncode == 0:
                print("   ✅ SUCCESS")
                return True
            else:
                print(f"   ❌ FAILED (exit code: {result.returncode})")
                if result.stderr:
                    print(f"   Error: {result.stderr}")
                return False
        else:
            if result.returncode != 0:
                print("   ✅ EXPECTED FAILURE")
                return True
            else:
                print("   ❌ UNEXPECTED SUCCESS")
                return False
                
    except subprocess.TimeoutExpired:
        print("   ❌ TIMEOUT")
        return False
    except Exception as e:
        print(f"   ❌ EXCEPTION: {e}")
        return False

def test_process_command():
    """Test process command with all options"""
    print("\n📋 Testing Process Command")
    print("=" * 50)
    
    tests = [
        # Basic process with minimal options
        (['process', '--no-interactive'], "Basic process with no-interactive flag", True),
        
        # Process with all options specified
        (['process', '--no-interactive', 
          '--input', 'Images', 
          '--output', 'Output',
          '--api-url', 'http://localhost:7860',
          '--clip-model', 'ViT-L-14/openai',
          '--clip-modes', 'best', 'fast',
          '--prompt-choices', 'P1', 'P2',
          '--enable-clip',
          '--enable-llm',
          '--enable-metadata',
          '--enable-parallel',
          '--enable-summaries',
          '--timeout', '120',
          '--retry-limit', '3',
          '--max-file-size', '50MB',
          '--allowed-extensions', '.jpg', '.png'], 
         "Process with all options specified", True),
        
        # Process with disabled features
        (['process', '--no-interactive',
          '--disable-clip',
          '--disable-llm',
          '--disable-metadata',
          '--disable-parallel',
          '--disable-summaries'], 
         "Process with all features disabled", True),
        
        # Process with custom settings
        (['process', '--no-interactive',
          '--input', 'test_images',
          '--output', 'test_output',
          '--clip-modes', 'best',
          '--prompt-choices', 'P1',
          '--timeout', '60',
          '--retry-limit', '5'], 
         "Process with custom settings", True),
        
        # Test missing required directory (should fail gracefully)
        (['process', '--no-interactive',
          '--input', 'nonexistent_directory'], 
         "Process with non-existent input directory", False),
    ]
    
    passed = 0
    failed = 0
    
    for cmd_args, description, expect_success in tests:
        if run_cli_command(cmd_args, description, expect_success):
            passed += 1
        else:
            failed += 1
    
    return passed, failed

def test_web_command():
    """Test web command with all options"""
    print("\n🌐 Testing Web Command")
    print("=" * 50)
    
    tests = [
        # Basic web interface
        (['web', '--no-interactive'], "Basic web interface", True),
        
        # Web with custom port and host
        (['web', '--no-interactive', '--port', '8080', '--host', '127.0.0.1'], 
         "Web with custom port and host", True),
        
        # Web with debug mode
        (['web', '--no-interactive', '--debug'], "Web with debug mode", True),
        
        # Web with all options
        (['web', '--no-interactive', '--port', '9000', '--host', '0.0.0.0', '--debug'], 
         "Web with all options", True),
    ]
    
    passed = 0
    failed = 0
    
    for cmd_args, description, expect_success in tests:
        if run_cli_command(cmd_args, description, expect_success):
            passed += 1
        else:
            failed += 1
    
    return passed, failed

def test_config_command():
    """Test config command with all options"""
    print("\n⚙️  Testing Config Command")
    print("=" * 50)
    
    tests = [
        # Show configuration
        (['config', '--no-interactive', '--show'], "Show configuration", True),
        
        # Setup configuration
        (['config', '--no-interactive', '--setup'], "Setup configuration", True),
        
        # Validate configuration
        (['config', '--no-interactive', '--validate'], "Validate configuration", True),
        
        # Reset configuration
        (['config', '--no-interactive', '--reset'], "Reset configuration", True),
    ]
    
    passed = 0
    failed = 0
    
    for cmd_args, description, expect_success in tests:
        if run_cli_command(cmd_args, description, expect_success):
            passed += 1
        else:
            failed += 1
    
    return passed, failed

def test_llm_config_command():
    """Test LLM config command with all options"""
    print("\n🤖 Testing LLM Config Command")
    print("=" * 50)
    
    tests = [
        # List available models
        (['llm-config', '--no-interactive', '--list'], "List available models", True),
        
        # List configured models
        (['llm-config', '--no-interactive', '--list-configured'], "List configured models", True),
        
        # Test connections
        (['llm-config', '--no-interactive', '--test-ollama'], "Test Ollama connection", True),
        (['llm-config', '--no-interactive', '--test-openai'], "Test OpenAI connection", True),
        (['llm-config', '--no-interactive', '--test-all'], "Test all connections", True),
        
        # Add models (these will fail without API keys, but should not hang)
        (['llm-config', '--no-interactive', '--add-ollama', 'llama2'], "Add Ollama model", True),
        (['llm-config', '--no-interactive', '--add-openai', 'gpt-4', '--openai-key', 'test_key'], 
         "Add OpenAI model with key", True),
    ]
    
    passed = 0
    failed = 0
    
    for cmd_args, description, expect_success in tests:
        if run_cli_command(cmd_args, description, expect_success):
            passed += 1
        else:
            failed += 1
    
    return passed, failed

def test_view_command():
    """Test view command with all options"""
    print("\n📋 Testing View Command")
    print("=" * 50)
    
    tests = [
        # List results
        (['view', '--no-interactive', '--list'], "List results", True),
        
        # Generate summary
        (['view', '--no-interactive', '--summary'], "Generate summary", True),
        
        # Export to CSV
        (['view', '--no-interactive', '--export', 'csv', '--output', 'test_export.csv'], 
         "Export to CSV", True),
        
        # Export to JSON
        (['view', '--no-interactive', '--export', 'json', '--output', 'test_export.json'], 
         "Export to JSON", True),
    ]
    
    passed = 0
    failed = 0
    
    for cmd_args, description, expect_success in tests:
        if run_cli_command(cmd_args, description, expect_success):
            passed += 1
        else:
            failed += 1
    
    return passed, failed

def test_database_command():
    """Test database command with all options"""
    print("\n🗄️  Testing Database Command")
    print("=" * 50)
    
    tests = [
        # Show database stats
        (['database', '--no-interactive', '--stats'], "Show database stats", True),
        
        # Backup database
        (['database', '--no-interactive', '--backup', 'test_backup.db'], "Backup database", True),
        
        # Clear database (should fail without confirmation in non-interactive mode)
        (['database', '--no-interactive', '--clear'], "Clear database", False),
    ]
    
    passed = 0
    failed = 0
    
    for cmd_args, description, expect_success in tests:
        if run_cli_command(cmd_args, description, expect_success):
            passed += 1
        else:
            failed += 1
    
    return passed, failed

def test_wildcard_command():
    """Test wildcard command with all options"""
    print("\n🎯 Testing Wildcard Command")
    print("=" * 50)
    
    tests = [
        # Generate all wildcards
        (['wildcard', '--no-interactive', '--all'], "Generate all wildcards", True),
        
        # Generate individual groups
        (['wildcard', '--no-interactive', '--groups'], "Generate individual groups", True),
        
        # Generate combined wildcard
        (['wildcard', '--no-interactive', '--combined'], "Generate combined wildcard", True),
        
        # Generate combinations
        (['wildcard', '--no-interactive', '--combinations'], "Generate combinations", True),
        
        # Generate with custom output directory
        (['wildcard', '--no-interactive', '--output', 'test_wildcards', '--all'], 
         "Generate with custom output", True),
    ]
    
    passed = 0
    failed = 0
    
    for cmd_args, description, expect_success in tests:
        if run_cli_command(cmd_args, description, expect_success):
            passed += 1
        else:
            failed += 1
    
    return passed, failed

def test_global_flags():
    """Test global flags"""
    print("\n🌍 Testing Global Flags")
    print("=" * 50)
    
    tests = [
        # Test --help
        (['--help'], "Global help", True),
        
        # Test --verbose
        (['process', '--no-interactive', '--verbose'], "Process with verbose output", True),
        
        # Test --quiet
        (['process', '--no-interactive', '--quiet'], "Process with quiet output", True),
        
        # Test --yes
        (['config', '--no-interactive', '--yes', '--show'], "Config with yes flag", True),
        
        # Test no command with --no-interactive (should fail)
        (['--no-interactive'], "No command with no-interactive", False),
    ]
    
    passed = 0
    failed = 0
    
    for cmd_args, description, expect_success in tests:
        if run_cli_command(cmd_args, description, expect_success):
            passed += 1
        else:
            failed += 1
    
    return passed, failed

def main():
    """Run all CLI tests"""
    print("🧪 CLI Non-Interactive Mode Tests")
    print("=" * 60)
    print("Testing that CLI can run completely non-interactively")
    print("with all options provided via command-line arguments.")
    print()
    
    # Create test directories
    os.makedirs('Images', exist_ok=True)
    os.makedirs('Output', exist_ok=True)
    
    # Run all test suites
    test_suites = [
        ("Global Flags", test_global_flags),
        ("Process Command", test_process_command),
        ("Web Command", test_web_command),
        ("Config Command", test_config_command),
        ("LLM Config Command", test_llm_config_command),
        ("View Command", test_view_command),
        ("Database Command", test_database_command),
        ("Wildcard Command", test_wildcard_command),
    ]
    
    total_passed = 0
    total_failed = 0
    
    for suite_name, test_func in test_suites:
        print(f"\n📊 Running {suite_name} Tests")
        print("-" * 40)
        
        passed, failed = test_func()
        total_passed += passed
        total_failed += failed
        
        print(f"   {suite_name}: {passed} passed, {failed} failed")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Final Test Results")
    print("=" * 60)
    print(f"✅ Total Passed: {total_passed}")
    print(f"❌ Total Failed: {total_failed}")
    print(f"🎯 Total Tests: {total_passed + total_failed}")
    
    if total_failed == 0:
        print("\n🎉 All CLI tests passed!")
        print("\nThe CLI is working correctly in non-interactive mode:")
        print("• ✅ All commands support --no-interactive flag")
        print("• ✅ All options can be set via command-line arguments")
        print("• ✅ No user input required when all options are provided")
        print("• ✅ Proper error handling for missing required arguments")
        return 0
    else:
        print(f"\n⚠️  {total_failed} test(s) failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 