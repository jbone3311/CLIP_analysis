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
    print("  web         Start the web interface (opens browser automatically)")
    print("  help        Show this help message")
    print()
    print("Examples:")
    print("  python main.py process")
    print("  python main.py config")
    print("  python main.py view --list")
    print("  python main.py view --file Output/image_analysis.json")
    print("  python main.py install")
    print("  python main.py web")
    print()
    print("Default behavior:")
    print("  python main.py          # Launches web interface automatically")
    print("  python main.py --help   # Shows this menu")

def show_interactive_menu():
    """Display interactive menu for user choice"""
    print("🖼️  Image Analysis with CLIP and LLM")
    print("=" * 50)
    print()
    print("What would you like to do?")
    print()
    print("1. 📁 Process Images - Analyze all images in the Images directory")
    print("2. ⚙️  Setup Configuration - Configure analysis settings")
    print("3. 📊 View Results - Explore analysis results")
    print("4. 🔧 Install System - Install dependencies and setup")
    print("5. 🌐 Start Web Interface - Launch the web application (opens browser automatically)")
    print("6. ❓ Help - Show detailed help information")
    print("7. 🚪 Exit")
    print()
    
    while True:
        try:
            choice = input("Enter your choice (1-7): ").strip()
            
            if choice == "1":
                print("\n🚀 Starting image processing...")
                process_directory()
                break
            elif choice == "2":
                print("\n⚙️  Starting configuration setup...")
                setup_config()
                break
            elif choice == "3":
                print("\n📊 Opening results viewer...")
                view_results()
                break
            elif choice == "4":
                print("\n🔧 Starting system installation...")
                install_system()
                break
            elif choice == "5":
                print("\n🌐 Starting web interface...")
                start_web_interface()
                break
            elif choice == "6":
                print("\n" + "="*50)
                show_help()
                print("\n" + "="*50)
                print("\nWhat would you like to do?")
                print("1. 📁 Process Images")
                print("2. ⚙️  Setup Configuration")
                print("3. 📊 View Results")
                print("4. 🔧 Install System")
                print("5. 🌐 Start Web Interface (opens browser automatically)")
                print("6. ❓ Help")
                print("7. 🚪 Exit")
                print()
                continue
            elif choice == "7":
                print("\n👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter a number between 1 and 7.")
                continue
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except EOFError:
            print("\n\n👋 Goodbye!")
            break

def start_web_interface():
    """Start the Flask web interface"""
    try:
        from src.viewers.web_interface import app, open_browser
        import threading
        
        print("🌐 Web interface starting at http://localhost:5000")
        print("📱 Browser will open automatically...")
        print("⏹️  Press Ctrl+C to stop the web server")
        print()
        
        # Start browser opening in background thread
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        app.run(debug=False, host='0.0.0.0', port=5000)
    except ImportError as e:
        print(f"❌ Error importing web interface: {e}")
        print("💡 Make sure Flask is installed: pip install Flask")
    except Exception as e:
        print(f"❌ Error starting web interface: {e}")

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        # No arguments provided - launch web interface by default
        print("🖼️  Image Analysis with CLIP and LLM")
        print("🌐 Launching web interface...")
        print("💡 Use 'python main.py --help' for command line options")
        print()
        start_web_interface()
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
    elif command == "web":
        start_web_interface()
    elif command in ["help", "--help", "-h"]:
        show_interactive_menu()
    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'python main.py --help' for usage information")
        sys.exit(1)

if __name__ == "__main__":
    main() 