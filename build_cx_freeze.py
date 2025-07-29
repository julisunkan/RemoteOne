"""
Build Windows EXE using cx_Freeze
Alternative to PyInstaller that might work better in this environment
"""
import sys
import os
from pathlib import Path

def create_setup_script():
    """Create cx_Freeze setup script"""
    setup_content = '''
import sys
import os
from cx_Freeze import setup, Executable

# Dependencies
build_options = {
    "packages": [
        "flask", "werkzeug", "jinja2", "markupsafe",
        "PIL", "qrcode", "netifaces", 
        "email", "email.mime", "pkg_resources",
        "urllib", "socket", "threading", "logging",
        "datetime", "io", "secrets", "string"
    ],
    "include_files": [
        ("templates", "templates"),
        ("static", "static"),
        ("uploads", "uploads")
    ],
    "excludes": ["tkinter", "matplotlib", "numpy"]
}

# Create executable
executables = [
    Executable(
        "main.py",
        base="Console",  # Use "Win32GUI" for no console
        target_name="FileServer.exe",
        icon="app.ico" if os.path.exists("app.ico") else None
    )
]

setup(
    name="WiFi File Server",
    version="1.0.0",
    description="WiFi File Server - Share files over local network",
    options={"build_exe": build_options},
    executables=executables
)
'''
    
    with open('setup_cx.py', 'w') as f:
        f.write(setup_content)
    
    print("✓ Created cx_Freeze setup script")

def build_with_cx_freeze():
    """Build using cx_Freeze"""
    create_setup_script()
    
    try:
        import subprocess
        
        # Build the executable
        cmd = [sys.executable, 'setup_cx.py', 'build']
        print(f"Running: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✓ cx_Freeze build successful!")
            
            # Find the executable
            build_dir = Path('build')
            if build_dir.exists():
                for exe_file in build_dir.rglob('*.exe'):
                    size_mb = exe_file.stat().st_size / (1024 * 1024)
                    print(f"✓ Executable: {exe_file}")
                    print(f"✓ Size: {size_mb:.1f} MB")
                    return True
            
            print("✗ No executable found after build")
            return False
        else:
            print(f"✗ cx_Freeze build failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ cx_Freeze error: {e}")
        return False

def main():
    """Main build process"""
    print("=== cx_Freeze Windows EXE Builder ===")
    
    try:
        import cx_Freeze
        print("cx_Freeze available")
    except ImportError:
        print("✗ cx_Freeze not available")
        return False
    
    return build_with_cx_freeze()

if __name__ == "__main__":
    main()