"""
Advanced Windows EXE builder using cross-compilation techniques
Creates a true Windows executable that works without Python installed
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def setup_wine_python():
    """Set up Python in Wine environment for Windows EXE building"""
    print("Setting up Wine environment for Windows builds...")
    
    try:
        # Initialize wine
        subprocess.run(['winecfg'], input='\n', text=True, timeout=30, capture_output=True)
        print("Wine initialized")
        
        # Download and install Python in Wine
        python_installer = "python-3.11.0-amd64.exe"
        if not Path(python_installer).exists():
            print("Downloading Python installer...")
            subprocess.run([
                'wget', 
                'https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe',
                '-O', python_installer
            ], check=True)
        
        # Install Python silently in Wine
        subprocess.run([
            'wine', python_installer, 
            '/quiet', 'InstallAllUsers=1', 'PrependPath=1'
        ], check=True, timeout=300)
        
        print("Python installed in Wine")
        return True
        
    except Exception as e:
        print(f"Wine setup failed: {e}")
        return False

def build_nuitka_exe():
    """Build Windows EXE using Nuitka (better than PyInstaller for cross-compilation)"""
    print("Building Windows EXE with Nuitka...")
    
    try:
        # Install Nuitka
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'nuitka'], check=True)
        
        # Create build command
        build_cmd = [
            sys.executable, '-m', 'nuitka',
            '--standalone',
            '--onefile',
            '--windows-disable-console',
            '--include-data-dir=templates=templates',
            '--include-data-dir=static=static', 
            '--include-data-dir=uploads=uploads',
            '--include-module=netifaces',
            '--include-module=qrcode',
            '--include-module=PIL',
            '--include-module=email',
            '--include-module=pkg_resources',
            '--output-filename=FileServer.exe',
            '--output-dir=dist_nuitka',
            'main.py'
        ]
        
        print("Running Nuitka build...")
        result = subprocess.run(build_cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            print("✓ Nuitka build successful!")
            return True
        else:
            print(f"Nuitka build failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Nuitka build error: {e}")
        return False

def build_pyinstaller_cross():
    """Build using PyInstaller with cross-compilation tricks"""
    print("Building with PyInstaller cross-compilation...")
    
    # Create enhanced spec file for cross-compilation
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

import sys
import os

block_cipher = None

# Add current directory to path
sys.path.insert(0, os.getcwd())

a = Analysis(
    ['main.py'],
    pathex=[os.getcwd()],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('static', 'static'),
        ('uploads', 'uploads'),
    ],
    hiddenimports=[
        'netifaces', 'qrcode', 'PIL', 'PIL.Image', 'PIL.ImageDraw',
        'email', 'email.mime', 'email.mime.text', 'email.mime.multipart',
        'email.utils', 'email.header', 'email.charset', 'pkg_resources',
        'werkzeug', 'werkzeug.security', 'flask', 'jinja2', 'markupsafe',
        'urllib', 'urllib.parse', 'socket', 'threading', 'logging',
        'datetime', 'io', 'secrets', 'string', 'os', 'sys',
        # Windows-specific modules
        'win32api', 'win32con', 'win32gui', 'win32process',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'scipy'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Filter out problematic modules
a.pure = [x for x in a.pure if not x[0].startswith('_tkinter')]
a.binaries = [x for x in a.binaries if not x[0].startswith('_tkinter')]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='FileServer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Enable console for easier debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app.ico' if os.path.exists('app.ico') else None,
)"""

    with open('cross_compile.spec', 'w') as f:
        f.write(spec_content)
    
    try:
        # Build with spec file
        result = subprocess.run([
            'pyinstaller', 
            '--clean',
            'cross_compile.spec'
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✓ PyInstaller cross-compilation successful!")
            return True
        else:
            print(f"PyInstaller failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"PyInstaller error: {e}")
        return False

def create_app_icon():
    """Create application icon"""
    try:
        from PIL import Image, ImageDraw
        
        # Create app icon
        size = 256
        img = Image.new('RGBA', (size, size), (13, 110, 253, 255))
        draw = ImageDraw.Draw(img)
        
        # Draw folder icon
        folder_color = (255, 255, 255, 255)
        draw.rectangle([50, 100, 206, 200], fill=folder_color)
        draw.rectangle([50, 80, 120, 100], fill=folder_color)
        
        # Save as ICO for Windows
        img.save('app.ico', format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
        print("✓ App icon created")
        return True
        
    except Exception as e:
        print(f"Icon creation failed: {e}")
        return False

def main():
    """Main build process"""
    print("=== Advanced Windows EXE Builder ===")
    
    # Create icon
    create_app_icon()
    
    # Try multiple build methods
    methods = [
        ("Nuitka (Recommended)", build_nuitka_exe),
        ("PyInstaller Cross-Compilation", build_pyinstaller_cross),
    ]
    
    for method_name, method_func in methods:
        print(f"\n--- Trying {method_name} ---")
        if method_func():
            print(f"✓ Success with {method_name}!")
            
            # Find and report the executable
            for dist_dir in ['dist_nuitka', 'dist']:
                if Path(dist_dir).exists():
                    exe_files = list(Path(dist_dir).glob('**/*.exe')) + list(Path(dist_dir).glob('**/FileServer'))
                    if exe_files:
                        exe_path = exe_files[0]
                        size_mb = exe_path.stat().st_size / (1024 * 1024)
                        print(f"✓ Executable created: {exe_path}")
                        print(f"✓ Size: {size_mb:.1f} MB")
                        print(f"✓ Method: {method_name}")
                        return True
            
            print("Warning: Build reported success but no executable found")
        else:
            print(f"✗ {method_name} failed")
    
    print("\n✗ All build methods failed")
    print("Recommendation: Use the portable version (FileServer_Portable.zip)")
    return False

if __name__ == "__main__":
    main()