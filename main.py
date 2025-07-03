#!/usr/bin/env python3
"""
Main entry point for Image Analysis with CLIP and LLM

This script provides a unified interface to all the analysis tools.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from directory_processor import main as process_directory
from src.config.config_manager import main as setup_config
from src.viewers.results_viewer import main as view_results
from src.utils.installer import main as install_system

def show_help():
    """Display help information"""
    print("🖼️  Image Analysis with CLIP and LLM")
    print("=" * 50)
    print()
    print("Usage: python main.py [command] [options]")
    print()
    print("Commands:")
    print("  process     Process all images in the Images directory")
    print("  config      Interactive configuration setup")
    print("  view        View and explore analysis results")
    print("  install     Install dependencies and setup system")
    print("  help        Show this help message")
    print()
    print("Examples:")
    print("  python main.py process")
    print("  python main.py config")
    print("  python main.py view --list")
    print("  python main.py view --file Output/image_analysis.json")
    print("  python main.py install")

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "process":
        process_directory()
    elif command == "config":
        setup_config()
    elif command == "view":
        # Pass remaining arguments to results viewer
        sys.argv = sys.argv[2:]  # Remove 'view' command
        view_results()
    elif command == "install":
        install_system()
    elif command in ["help", "--help", "-h"]:
        show_help()
    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'python main.py help' for usage information")
        sys.exit(1)

if __name__ == "__main__":
    main() 