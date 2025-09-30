#!/usr/bin/env python3
"""
Fix logging calls in the codebase

This script replaces all 'logging.' calls with 'logger.' calls
to use the new centralized logging system.
"""

import os
import re

def fix_file(file_path):
    """Fix logging calls in a file"""
    print(f"Fixing {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace logging calls with logger calls
    content = re.sub(r'logging\.(debug|info|warning|error|critical)\(', r'logger.\1(', content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Fixed {file_path}")

def main():
    """Fix all Python files in the project"""
    files_to_fix = [
        'src/analyzers/clip_analyzer.py',
        'directory_processor.py'
    ]
    
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            fix_file(file_path)
        else:
            print(f"⚠️  File not found: {file_path}")
    
    print("🎉 Logging calls fixed!")

if __name__ == "__main__":
    main() 