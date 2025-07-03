#!/usr/bin/env python3
"""
Installation script for Image Analysis with CLIP and LLM

This script helps users set up the environment and install dependencies.
"""

import os
import sys
import subprocess
import platform

def print_banner():
    """Print the installation banner"""
    print("🖼️  Image Analysis with CLIP and LLM - Installation")
    print("=" * 55)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing Dependencies")
    print("-" * 30)
    
    try:
        # Check if pip is available
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ pip is not available. Please install pip first.")
        return False
    
    # Install dependencies from requirements.txt
    try:
        print("Installing dependencies from requirements.txt...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
            return True
        else:
            print(f"❌ Failed to install dependencies: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating Directories")
    print("-" * 25)
    
    directories = ["Images", "Output"]
    
    for directory in directories:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                print(f"✅ Created directory: {directory}")
            except Exception as e:
                print(f"❌ Failed to create {directory}: {e}")
                return False
        else:
            print(f"✅ Directory exists: {directory}")
    
    return True

def check_existing_config():
    """Check if configuration already exists"""
    if os.path.exists(".env"):
        print("\n⚠️  Configuration file (.env) already exists")
        response = input("Do you want to run the configuration helper anyway? (y/N): ")
        return response.lower() in ['y', 'yes']
    return True

def run_config_helper():
    """Run the configuration helper"""
    print("\n⚙️  Running Configuration Helper")
    print("-" * 35)
    
    if not check_existing_config():
        print("Skipping configuration setup")
        return True
    
    try:
        result = subprocess.run([sys.executable, "config_helper.py"], 
                              capture_output=False)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Failed to run configuration helper: {e}")
        return False

def create_sample_image():
    """Create a sample image for testing"""
    print("\n🖼️  Creating Sample Image")
    print("-" * 25)
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a simple test image
        img = Image.new('RGB', (400, 300), color='lightblue')
        draw = ImageDraw.Draw(img)
        
        # Add some text
        try:
            # Try to use a default font
            font = ImageFont.load_default()
        except:
            font = None
        
        text = "Sample Image\nfor Testing"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (400 - text_width) // 2
        y = (300 - text_height) // 2
        
        draw.text((x, y), text, fill='black', font=font)
        
        # Save the image
        img.save("Images/sample_image.png")
        print("✅ Created sample image: Images/sample_image.png")
        return True
        
    except Exception as e:
        print(f"⚠️  Could not create sample image: {e}")
        print("   You can add your own images to the Images directory")
        return False

def print_next_steps():
    """Print next steps for the user"""
    print("\n🎉 Installation Complete!")
    print("=" * 25)
    print("\nNext steps:")
    print("1. 📁 Add your images to the 'Images' directory")
    print("2. 🚀 Run the analysis: python directory_processor.py")
    print("3. 📊 View results: python results_viewer.py --list")
    print("\nUseful commands:")
    print("   python directory_processor.py          # Process all images")
    print("   python results_viewer.py --list        # List all results")
    print("   python results_viewer.py --summary     # Generate summary")
    print("   python config_helper.py                # Reconfigure settings")

def main():
    """Main installation process"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Installation failed. Please check the errors above.")
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        print("\n❌ Failed to create directories.")
        sys.exit(1)
    
    # Run configuration helper
    if not run_config_helper():
        print("\n⚠️  Configuration setup was skipped or failed.")
        print("   You can run 'python config_helper.py' later to configure the system.")
    
    # Create sample image
    create_sample_image()
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    main() 