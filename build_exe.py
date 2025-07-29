"""
Build script to convert Flask app to Windows executable
Uses PyInstaller to create standalone EXE
"""
import os
import sys
import subprocess
import shutil

def build_exe():
    """Build the Flask app as a Windows executable"""
    
    # Check if spec file exists, use it for more reliable builds
    spec_file = 'fileserver.spec'
    if os.path.exists(spec_file):
        print(f"Using spec file: {spec_file}")
        build_command = ['pyinstaller', spec_file]
    else:
        # Fallback to command-line arguments
        build_command = [
            'pyinstaller',
            '--onefile',                    # Single executable file
            '--windowed',                   # No console window (GUI mode)
            '--name=FileServer',           # Output name
            '--icon=app.ico',              # App icon (if exists)
            '--add-data=templates;templates',      # Include templates folder
            '--add-data=static;static',            # Include static files
            '--add-data=uploads;uploads',          # Include uploads folder
            '--hidden-import=netifaces',           # Ensure netifaces is included
            '--hidden-import=qrcode',              # Ensure qrcode is included
            '--hidden-import=PIL',                 # Ensure Pillow is included
            '--hidden-import=email',               # Fix email module import
            '--hidden-import=email.mime',          # Email MIME types
            '--hidden-import=email.mime.text',     # Email text handling
            '--hidden-import=email.utils',         # Email utilities
            '--hidden-import=pkg_resources',       # Package resources
            '--collect-all=email',                 # Collect all email submodules
            'main.py'                              # Entry point
        ]
    
    print("Building Windows executable...")
    print("Command:", ' '.join(build_command))
    
    try:
        result = subprocess.run(build_command, check=True, capture_output=True, text=True)
        print("Build successful!")
        print("Executable created in 'dist' folder")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except FileNotFoundError:
        print("PyInstaller not found. Installing...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)
        # Retry build
        return build_exe()

def create_app_icon():
    """Create a simple app icon"""
    try:
        from PIL import Image, ImageDraw
        
        # Create a simple icon
        size = 256
        img = Image.new('RGBA', (size, size), (13, 110, 253, 255))  # Blue background
        draw = ImageDraw.Draw(img)
        
        # Draw a simple folder icon
        folder_color = (255, 255, 255, 255)  # White
        
        # Folder base
        draw.rectangle([50, 100, 206, 200], fill=folder_color)
        # Folder tab
        draw.rectangle([50, 80, 120, 100], fill=folder_color)
        
        # Save as ICO
        img.save('app.ico', format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
        print("App icon created: app.ico")
        return True
    except ImportError:
        print("Pillow not available for icon creation")
        return False

def cleanup_build():
    """Clean up build artifacts"""
    folders_to_remove = ['build', '__pycache__']
    files_to_remove = ['*.spec']
    
    for folder in folders_to_remove:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"Removed {folder}")
    
    import glob
    for pattern in files_to_remove:
        for file in glob.glob(pattern):
            os.remove(file)
            print(f"Removed {file}")

if __name__ == "__main__":
    print("=== File Server EXE Builder ===")
    
    # Create app icon
    create_app_icon()
    
    # Build executable
    success = build_exe()
    
    if success:
        print("\n✓ Build completed successfully!")
        print("✓ Executable: dist/FileServer.exe")
        print("\nTo run the server:")
        print("1. Double-click FileServer.exe")
        print("2. The server will start automatically")
        print("3. A browser window will open with the server URL")
        
        # Clean up
        cleanup_build()
    else:
        print("\n✗ Build failed. Check error messages above.")