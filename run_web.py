#!/usr/bin/env python3
"""
Simple script to run the refactored web interface
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.viewers.web_interface_refactored import WebInterface

def main():
    """Run the refactored web interface"""
    print("🌐 Starting Refactored Web Interface...")
    print("📁 Project root:", os.path.dirname(os.path.abspath(__file__)))
    
    try:
        web_interface = WebInterface()
        print("✅ Web interface initialized successfully!")
        print("🌐 Starting server on http://localhost:5050")
        print("📝 Press Ctrl+C to stop the server")
        
        web_interface.run(host='0.0.0.0', port=5050, debug=True)
        
    except Exception as e:
        print(f"❌ Failed to start web interface: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 