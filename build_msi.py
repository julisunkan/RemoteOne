"""
Build script to create MSI installer for Windows
Uses cx_Freeze to create Windows installer package
"""
import os
import sys
from cx_Freeze import setup, Executable
import shutil

# Dependencies that need to be included
packages = [
    "flask", "werkzeug", "jinja2", "markupsafe", "itsdangerous", "click",
    "qrcode", "PIL", "netifaces", "logging", "datetime", "secrets", "socket",
    "string", "os", "io", "urllib"
]

# Files to include with the application
include_files = [
    ("templates/", "templates/"),
    ("static/", "static/"),
    ("uploads/", "uploads/"),
    ("SETUP.md", "SETUP.md"),
    ("ANDROID_CONVERSION.md", "ANDROID_CONVERSION.md"),
    ("local_requirements.txt", "requirements.txt")
]

# Ensure uploads directory exists
os.makedirs("uploads", exist_ok=True)

# Build options
build_exe_options = {
    "packages": packages,
    "excludes": ["tkinter", "unittest", "email", "xml", "pydoc"],
    "include_files": include_files,
    "include_msvcrt": True,
    "optimize": 2,
}

# MSI build options
bdist_msi_options = {
    "upgrade_code": "{12345678-1234-5678-9012-123456789012}",
    "add_to_path": False,
    "initial_target_dir": r"[ProgramFilesFolder]\FileServer",
    "install_icon": "app.ico" if os.path.exists("app.ico") else None,
}

# Executable definition
executable = Executable(
    script="main.py",
    base="Win32GUI",  # Use Win32GUI for no console window
    target_name="FileServer.exe",
    icon="app.ico" if os.path.exists("app.ico") else None,
    shortcut_name="WiFi File Server",
    shortcut_dir="DesktopFolder",
)

def create_installer():
    """Create the MSI installer"""
    print("Building MSI installer...")
    
    setup(
        name="WiFi File Server",
        version="1.0.0",
        description="Personal WiFi File Sharing Server",
        author="File Server",
        options={
            "build_exe": build_exe_options,
            "bdist_msi": bdist_msi_options,
        },
        executables=[executable]
    )

def create_batch_launcher():
    """Create a batch file launcher for better user experience"""
    batch_content = '''@echo off
title WiFi File Server
echo Starting WiFi File Server...
echo.
echo The server will open in your default browser.
echo Close this window to stop the server.
echo.

start "" "FileServer.exe"
pause > nul
'''
    
    with open("Start_FileServer.bat", "w") as f:
        f.write(batch_content)
    
    print("Created Start_FileServer.bat launcher")

def create_readme():
    """Create a README file for the installer"""
    readme_content = '''# WiFi File Server

## Installation
1. Run the MSI installer
2. Follow the installation wizard
3. The application will be installed to Program Files

## Usage
1. Click "WiFi File Server" from your Start Menu or Desktop
2. The server will start and open in your default browser
3. Share the displayed URL and password with other devices on your WiFi network
4. Other devices can access your files by visiting the URL

## Features
- Secure password-protected file sharing
- Works on any device with a web browser
- Upload and download files over WiFi
- Stream videos and audio directly
- Mobile-optimized interface
- Progressive Web App support (installable on phones)

## System Requirements
- Windows 7/8/10/11
- WiFi or Ethernet network connection
- 100MB free disk space

## Uninstalling
Use "Add or Remove Programs" in Windows Settings to uninstall.

## Support
For issues or questions, refer to the documentation files included with the installation.
'''
    
    with open("README.txt", "w") as f:
        f.write(readme_content)
    
    print("Created README.txt")

if __name__ == "__main__":
    print("=== WiFi File Server MSI Builder ===")
    
    # Create additional files
    create_batch_launcher()
    create_readme()
    
    try:
        create_installer()
        print("\n✓ MSI installer created successfully!")
        print("✓ Installer file: dist/WiFi File Server-1.0.0-amd64.msi")
        print("\nInstaller features:")
        print("- Installs to Program Files")
        print("- Creates Start Menu shortcuts")
        print("- Creates Desktop shortcut")
        print("- Includes all dependencies")
        print("- Professional Windows installer experience")
        
    except Exception as e:
        print(f"\n✗ MSI build failed: {e}")
        print("\nTrying to install cx_Freeze...")
        try:
            import subprocess
            subprocess.run([sys.executable, "-m", "pip", "install", "cx_Freeze"], check=True)
            print("cx_Freeze installed. Please run this script again.")
        except:
            print("Failed to install cx_Freeze. Please install manually:")
            print("pip install cx_Freeze")