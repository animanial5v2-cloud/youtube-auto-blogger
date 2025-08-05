#!/usr/bin/env python3
"""
Build script for AI Blogging Studio Desktop Application
"""
import subprocess
import sys
import os
from pathlib import Path

def install_dependencies():
    """Install Node.js dependencies"""
    print("Installing Node.js dependencies...")
    subprocess.run([
        "npm", "install", "electron", "electron-builder", "--save-dev"
    ], check=True)
    
def install_python_dependencies():
    """Install Python dependencies"""
    print("Installing Python dependencies...")
    subprocess.run([
        sys.executable, "-m", "pip", "install", "-r", "server/requirements.txt"
    ], check=True)

def build_app():
    """Build the desktop application"""
    print("Building desktop application...")
    subprocess.run(["npm", "run", "dist"], check=True)
    print("Build complete! Check the 'dist' folder for the installer.")

def main():
    """Main build process"""
    os.chdir(Path(__file__).parent)
    
    try:
        install_dependencies()
        install_python_dependencies()
        build_app()
        
        print("\n✅ Desktop application build successful!")
        print("📁 Installer files are available in the 'dist' folder")
        print("🚀 You can now distribute the installer to users")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()