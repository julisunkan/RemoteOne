"""
Cross-platform portable build script
Creates a portable Python application that works on any platform
"""
import os
import shutil
import sys
import zipfile
from pathlib import Path

def create_portable_app():
    """Create a portable Python application"""
    
    print("Creating portable file server application...")
    
    # Create portable directory
    portable_dir = Path("portable_fileserver")
    if portable_dir.exists():
        shutil.rmtree(portable_dir)
    
    portable_dir.mkdir()
    
    # Copy application files
    files_to_copy = [
        "app.py",
        "main.py", 
        "utils.py",
        "requirements.txt" if Path("requirements.txt").exists() else None,
        "local_requirements.txt" if Path("local_requirements.txt").exists() else None,
    ]
    
    directories_to_copy = [
        "templates",
        "static",
        "uploads"
    ]
    
    # Copy files
    for file in files_to_copy:
        if file and Path(file).exists():
            shutil.copy2(file, portable_dir / file)
            print(f"Copied {file}")
    
    # Copy directories
    for directory in directories_to_copy:
        if Path(directory).exists():
            shutil.copytree(directory, portable_dir / directory)
            print(f"Copied {directory}/")
    
    # Create requirements.txt if it doesn't exist
    requirements_file = portable_dir / "requirements.txt"
    if not requirements_file.exists():
        requirements_content = """Flask>=2.3.0
Werkzeug>=2.3.0
Pillow>=9.0.0
qrcode>=7.0.0
netifaces>=0.11.0
gunicorn>=21.0.0
"""
        requirements_file.write_text(requirements_content)
        print("Created requirements.txt")
    
    # Create startup script for Windows
    windows_script = portable_dir / "start_fileserver.bat"
    windows_script.write_text("""@echo off
echo Starting File Server...
echo.
echo Installing Python dependencies...
python -m pip install -r requirements.txt --quiet
echo.
echo Starting server...
python main.py
pause
""")
    print("Created start_fileserver.bat")
    
    # Create startup script for Linux/Mac
    unix_script = portable_dir / "start_fileserver.sh"
    unix_script.write_text("""#!/bin/bash
echo "Starting File Server..."
echo
echo "Installing Python dependencies..."
python3 -m pip install -r requirements.txt --quiet
echo
echo "Starting server..."
python3 main.py
""")
    unix_script.chmod(0o755)
    print("Created start_fileserver.sh")
    
    # Create README
    readme = portable_dir / "README.txt"
    readme.write_text("""WiFi File Server - Portable Version
===================================

This is a portable version of the WiFi File Server that works on any computer with Python installed.

Requirements:
- Python 3.7 or newer
- Internet connection (for first-time setup to install dependencies)

How to Run:

Windows:
1. Double-click "start_fileserver.bat"
2. Wait for dependencies to install (first time only)
3. The server will start and show you the access URL and password

Linux/Mac:
1. Open terminal in this folder
2. Run: ./start_fileserver.sh
3. Wait for dependencies to install (first time only)  
4. The server will start and show you the access URL and password

Features:
- Secure password-protected access
- File upload and download
- Works on local network (WiFi sharing)
- QR code for easy mobile access
- Support for all file types
- Progressive Web App (installable on mobile)

Troubleshooting:
- Make sure Python is installed: python --version
- If script fails, try: python main.py
- For Windows: python -m pip install -r requirements.txt
- For Linux/Mac: python3 -m pip install -r requirements.txt

The server will be accessible at: http://[your-ip]:5000
Password will be shown when the server starts.
""")
    print("Created README.txt")
    
    # Create ZIP archive
    zip_path = "FileServer_Portable.zip"
    if Path(zip_path).exists():
        Path(zip_path).unlink()
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(portable_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(portable_dir)
                zipf.write(file_path, arcname)
                
    print(f"\n✓ Portable application created: {zip_path}")
    print(f"✓ Size: {Path(zip_path).stat().st_size / (1024*1024):.1f} MB")
    
    # Clean up directory
    shutil.rmtree(portable_dir)
    
    print("\nTo use:")
    print("1. Download and extract FileServer_Portable.zip")
    print("2. Run start_fileserver.bat (Windows) or start_fileserver.sh (Linux/Mac)")
    print("3. Access the server using the displayed URL and password")
    
    return True

if __name__ == "__main__":
    create_portable_app()