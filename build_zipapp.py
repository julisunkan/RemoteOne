"""
Create a self-contained Python executable using zipapp
This creates a .pyz file that works on any system with Python
"""
import os
import shutil
import zipfile
import tempfile
from pathlib import Path

def create_zipapp_executable():
    """Create a Python zipapp executable"""
    print("Creating Python zipapp executable...")
    
    # Create temporary directory for the app
    with tempfile.TemporaryDirectory() as temp_dir:
        app_dir = Path(temp_dir) / "fileserver_app"
        app_dir.mkdir()
        
        # Copy application files
        files_to_copy = [
            'app.py', 'main.py', 'utils.py'
        ]
        
        dirs_to_copy = [
            'templates', 'static', 'uploads'
        ]
        
        # Copy files
        for file in files_to_copy:
            if Path(file).exists():
                shutil.copy2(file, app_dir / file)
                print(f"Copied {file}")
        
        # Copy directories
        for directory in dirs_to_copy:
            if Path(directory).exists():
                shutil.copytree(directory, app_dir / directory)
                print(f"Copied {directory}/")
        
        # Create __main__.py for zipapp entry point
        main_content = '''#!/usr/bin/env python3
"""
Entry point for the FileServer zipapp
"""
import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def main():
    """Main entry point"""
    try:
        print("Starting WiFi File Server...")
        print("Loading application...")
        
        # Import the app
        from app import app
        
        print("Server starting on http://0.0.0.0:5000")
        print("Press Ctrl+C to stop")
        
        # Run the app
        app.run(host='0.0.0.0', port=5000, debug=False)
        
    except KeyboardInterrupt:
        print("\\nServer stopped by user")
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install flask werkzeug pillow qrcode netifaces")
        input("Press Enter to exit...")
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
'''
        
        (app_dir / '__main__.py').write_text(main_content)
        print("Created __main__.py")
        
        # Create the zipapp
        output_file = 'FileServer.pyz'
        
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(app_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(app_dir)
                    zipf.write(file_path, arcname)
        
        # Make it executable on Unix systems
        if os.name != 'nt':
            os.chmod(output_file, 0o755)
        
        print(f"✓ Created {output_file}")
        
        # Get file size
        size_kb = Path(output_file).stat().st_size / 1024
        print(f"✓ Size: {size_kb:.1f} KB")
        
        return True

def create_windows_batch_launcher():
    """Create a Windows batch file to run the zipapp"""
    batch_content = '''@echo off
title WiFi File Server
echo Starting WiFi File Server...
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

REM Install dependencies if needed
echo Installing/checking dependencies...
python -m pip install flask werkzeug pillow qrcode netifaces --quiet

REM Run the application
echo.
echo Starting server...
python FileServer.pyz

pause
'''
    
    with open('start_server.bat', 'w') as f:
        f.write(batch_content)
    
    print("✓ Created start_server.bat")

def create_linux_shell_launcher():
    """Create a Linux/Mac shell script to run the zipapp"""
    shell_content = '''#!/bin/bash
echo "Starting WiFi File Server..."
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3"
    exit 1
fi

# Install dependencies if needed
echo "Installing/checking dependencies..."
python3 -m pip install flask werkzeug pillow qrcode netifaces --quiet

# Run the application
echo
echo "Starting server..."
python3 FileServer.pyz
'''
    
    with open('start_server.sh', 'w') as f:
        f.write(shell_content)
    
    os.chmod('start_server.sh', 0o755)
    print("✓ Created start_server.sh")

def create_readme():
    """Create README for the zipapp distribution"""
    readme_content = '''WiFi File Server - Python Executable (.pyz)
==========================================

This is a Python zipapp executable that works on any system with Python installed.

REQUIREMENTS:
- Python 3.7 or newer
- Internet connection (for first-time dependency installation)

HOW TO RUN:

Method 1 - Use the launcher scripts:
  Windows: Double-click "start_server.bat"
  Linux/Mac: Run "./start_server.sh" in terminal

Method 2 - Direct execution:
  Windows: python FileServer.pyz
  Linux/Mac: python3 FileServer.pyz

Method 3 - Direct execution (if Python is in PATH):
  Linux/Mac: ./FileServer.pyz

FIRST TIME SETUP:
The launcher scripts will automatically install required Python packages:
- Flask (web framework)
- Werkzeug (WSGI utilities)
- Pillow (image processing)
- qrcode (QR code generation)
- netifaces (network interface detection)

USAGE:
1. Run the server using one of the methods above
2. The server will show you the local network URL and password
3. Open the URL in any web browser on your network
4. Use the password to log in
5. Upload, download, and manage files through the web interface

FEATURES:
- Secure password-protected access
- File upload and download
- Works on local network (WiFi sharing)
- QR code for easy mobile access
- Support for all file types
- Progressive Web App (installable on mobile)

TROUBLESHOOTING:
- Make sure Python is installed: python --version
- If dependencies fail to install, try: pip install flask werkzeug pillow qrcode netifaces
- If port 5000 is busy, close other applications using that port
- For network access issues, check your firewall settings

The server will be accessible at: http://[your-computer-ip]:5000
Password will be displayed when the server starts.
'''
    
    with open('README_zipapp.txt', 'w') as f:
        f.write(readme_content)
    
    print("✓ Created README_zipapp.txt")

def main():
    """Main build process"""
    print("=== Python Zipapp Executable Builder ===")
    
    if create_zipapp_executable():
        create_windows_batch_launcher()
        create_linux_shell_launcher()
        create_readme()
        
        print("\n✓ BUILD SUCCESSFUL!")
        print("\nFiles created:")
        print("  FileServer.pyz - Python executable")
        print("  start_server.bat - Windows launcher")
        print("  start_server.sh - Linux/Mac launcher")
        print("  README_zipapp.txt - Instructions")
        
        print("\nHow to use:")
        print("1. Copy all files to the target computer")
        print("2. Run the appropriate launcher script")
        print("3. The server will start automatically")
        
        print("\nAdvantages of this method:")
        print("- Works on any OS with Python")
        print("- Much smaller file size than compiled executables")
        print("- No cross-compilation issues")
        print("- Easy to debug and modify")
        
        return True
    else:
        print("\n✗ BUILD FAILED")
        return False

if __name__ == "__main__":
    main()