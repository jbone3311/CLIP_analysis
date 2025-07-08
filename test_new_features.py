#!/usr/bin/env python3
"""
Quick test script for new features:
- Database tests
- CLI command tests  
- Wildcard generator functionality
"""

import sys
import os
import tempfile
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_database_manager():
    """Test database manager functionality"""
    print("🧪 Testing Database Manager...")
    
    try:
        from src.database.db_manager import DatabaseManager
        
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        db_manager = DatabaseManager(db_path)
        
        # Test basic operations
        test_result = {
            'filename': 'test_image.jpg',
            'directory': 'Images/landscapes',
            'md5': 'abc123def456',
            'model': 'ViT-L-14/openai',
            'modes': json.dumps(['best', 'fast']),
            'prompts': json.dumps({'P1': 'Describe this image'}),
            'analysis_results': json.dumps({'best': {'prompt': 'A beautiful landscape'}}),
            'settings': json.dumps({'api_url': 'http://localhost:7860'}),
            'llm_results': json.dumps({'P1': {'content': 'This is a landscape image'}})
        }
        
        # Insert result
        db_manager.insert_result(**test_result)
        
        # Retrieve result
        result = db_manager.get_result_by_md5('abc123def456')
        assert result is not None
        assert result['filename'] == 'test_image.jpg'
        
        # Test stats
        stats = db_manager.get_stats()
        assert stats['total_results'] == 1
        
        # Cleanup
        os.unlink(db_path)
        
        print("✅ Database Manager tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Database Manager tests failed: {e}")
        return False

def test_wildcard_generator():
    """Test wildcard generator functionality"""
    print("🎲 Testing Wildcard Generator...")
    
    try:
        from src.utils.wildcard_generator import WildcardGenerator
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        output_dir = os.path.join(temp_dir, "Output")
        
        generator = WildcardGenerator(output_dir)
        
        # Test sample results
        sample_results = [
            {
                'filename': 'landscape1.jpg',
                'directory': 'Images/landscapes',
                'analysis_results': json.dumps({
                    'best': {'prompt': 'A beautiful mountain landscape'},
                    'fast': {'prompt': 'Mountain landscape'}
                })
            },
            {
                'filename': 'portrait1.jpg',
                'directory': 'Images/portraits',
                'analysis_results': json.dumps({
                    'best': {'prompt': 'A professional portrait'},
                    'fast': {'prompt': 'Portrait photo'}
                })
            }
        ]
        
        # Generate wildcards
        wildcard_files = generator.generate_wildcards_from_results(sample_results, 'Images')
        
        # Check results
        assert 'landscapes' in wildcard_files
        assert 'portraits' in wildcard_files
        
        # Check files exist
        for group_name, file_path in wildcard_files.items():
            assert os.path.exists(file_path)
            
            # Check content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert f'# {group_name} Wildcard File' in content
        
        # Test combined wildcard
        combined_file = generator.generate_combined_wildcard(sample_results, 'Images')
        assert os.path.exists(combined_file)
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)
        
        print("✅ Wildcard Generator tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Wildcard Generator tests failed: {e}")
        return False

def test_cli_commands():
    """Test CLI command functionality"""
    print("🖥️  Testing CLI Commands...")
    
    try:
        from main import create_parser, get_default_config
        
        # Test parser creation
        parser = create_parser()
        subcommands = ['process', 'web', 'config', 'llm-config', 'view', 'database', 'wildcard']
        
        for cmd in subcommands:
            assert cmd in parser._subparsers._group_actions[0].choices
        
        # Test config
        config = get_default_config()
        required_keys = [
            'API_BASE_URL', 'CLIP_MODEL_NAME', 'ENABLE_CLIP_ANALYSIS',
            'ENABLE_LLM_ANALYSIS', 'IMAGE_DIRECTORY', 'OUTPUT_DIRECTORY'
        ]
        
        for key in required_keys:
            assert key in config
        
        print("✅ CLI Commands tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ CLI Commands tests failed: {e}")
        return False

def test_wildcard_cli():
    """Test wildcard CLI command"""
    print("🎲 Testing Wildcard CLI Command...")
    
    try:
        from main import handle_wildcard
        import argparse
        
        # Create test args
        args = argparse.Namespace(
            output='test_output',
            groups=True,
            combined=False,
            combinations=False,
            all=False
        )
        
        # This will fail because no database, but should handle gracefully
        result = handle_wildcard(args)
        assert result == 1  # Should fail with no database results
        
        print("✅ Wildcard CLI Command tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Wildcard CLI Command tests failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing New Features...")
    print("=" * 50)
    
    tests = [
        test_database_manager,
        test_wildcard_generator,
        test_cli_commands,
        test_wildcard_cli
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! New features are working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 