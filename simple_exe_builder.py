"""
Simple executable builder that creates a Windows-compatible bundle
Uses basic PyInstaller with minimal dependencies
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def create_minimal_main():
    """Create a minimal main.py for executable building"""
    minimal_content = """#!/usr/bin/env python3
import sys
import os

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import and run the app
try:
    from app import app
    if __name__ == '__main__':
        print("Starting WiFi File Server...")
        print("Press Ctrl+C to stop the server")
        app.run(host='0.0.0.0', port=5000, debug=False)
except KeyboardInterrupt:
    print("\\nServer stopped by user")
except Exception as e:
    print(f"Error starting server: {e}")
    input("Press Enter to exit...")
"""
    
    with open('main_exe.py', 'w') as f:
        f.write(minimal_content)
    print("✓ Created minimal main_exe.py")

def build_simple_exe():
    """Build executable with minimal configuration"""
    
    create_minimal_main()
    
    # Simple PyInstaller command
    cmd = [
        'pyinstaller',
        '--onefile',
        '--name=FileServer',
        '--add-data=templates:templates',
        '--add-data=static:static', 
        '--add-data=uploads:uploads',
        '--hidden-import=email',
        '--hidden-import=pkg_resources',
        '--hidden-import=netifaces',
        '--hidden-import=qrcode',
        '--hidden-import=PIL',
        '--distpath=./dist_simple',
        '--workpath=./build_simple',
        '--specpath=./build_simple',
        'main_exe.py'
    ]
    
    print(f"Building with command: {' '.join(cmd)}")
    
    try:
        # Set environment variables for better compatibility
        env = os.environ.copy()
        env['PYTHONOPTIMIZE'] = '1'
        
        result = subprocess.run(cmd, 
                              capture_output=True, 
                              text=True, 
                              timeout=180,
                              env=env)
        
        if result.returncode == 0:
            print("✓ Build completed successfully!")
            
            # Check if executable was created
            exe_path = Path('dist_simple/FileServer')
            exe_path_win = Path('dist_simple/FileServer.exe')
            
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"✓ Executable: {exe_path}")
                print(f"✓ Size: {size_mb:.1f} MB")
                return True
            elif exe_path_win.exists():
                size_mb = exe_path_win.stat().st_size / (1024 * 1024) 
                print(f"✓ Executable: {exe_path_win}")
                print(f"✓ Size: {size_mb:.1f} MB")
                return True
            else:
                print("✗ No executable found in dist_simple/")
                return False
        else:
            print(f"✗ Build failed with exit code {result.returncode}")
            print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ Build timeout after 3 minutes")
        return False
    except Exception as e:
        print(f"✗ Build error: {e}")
        return False

def cleanup_build_files():
    """Clean up build artifacts"""
    cleanup_dirs = ['build_simple', '__pycache__']
    cleanup_files = ['main_exe.py']
    
    for dir_name in cleanup_dirs:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"Cleaned up {dir_name}")
    
    for file_name in cleanup_files:
        if Path(file_name).exists():
            Path(file_name).unlink()
            print(f"Cleaned up {file_name}")

def main():
    print("=== Simple Windows EXE Builder ===")
    
    if build_simple_exe():
        print("\n✓ BUILD SUCCESSFUL!")
        print("\nCreated Files:")
        
        dist_dir = Path('dist_simple')
        if dist_dir.exists():
            for item in dist_dir.iterdir():
                if item.is_file():
                    size_mb = item.stat().st_size / (1024 * 1024)
                    print(f"  {item.name} ({size_mb:.1f} MB)")
        
        print("\nTo use the executable:")
        print("1. Copy the file from dist_simple/ to a Windows computer")
        print("2. Run the executable file")
        print("3. The server will start and show connection details")
        
        cleanup_build_files()
        return True
    else:
        print("\n✗ BUILD FAILED")
        print("\nFallback options:")
        print("1. Use the portable version (FileServer_Portable.zip)")
        print("2. Try building on a Windows machine directly")
        return False

if __name__ == "__main__":
    main()