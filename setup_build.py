"""
Complete build setup for creating EXE and MSI installers
Handles dependency installation and build configuration
"""
import os
import sys
import subprocess
import platform

def install_build_dependencies():
    """Install required packages for building executables"""
    print("Installing build dependencies...")
    
    dependencies = [
        'pyinstaller',
        'cx_Freeze',
        'pillow',  # For icon creation
    ]
    
    for dep in dependencies:
        try:
            print(f"Installing {dep}...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', dep], 
                          check=True, capture_output=True)
            print(f"✓ {dep} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install {dep}: {e}")
            return False
    
    return True

def create_build_files():
    """Create additional files needed for building"""
    
    # Create version info for Windows
    version_info = '''
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'File Server'),
        StringStruct(u'FileDescription', u'WiFi File Sharing Server'),
        StringStruct(u'FileVersion', u'1.0.0.0'),
        StringStruct(u'InternalName', u'FileServer'),
        StringStruct(u'LegalCopyright', u'Open Source'),
        StringStruct(u'OriginalFilename', u'FileServer.exe'),
        StringStruct(u'ProductName', u'WiFi File Server'),
        StringStruct(u'ProductVersion', u'1.0.0.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
    
    with open('version_info.py', 'w') as f:
        f.write(version_info)
    
    print("✓ Created version_info.py")

def create_pyinstaller_spec():
    """Create a detailed PyInstaller spec file"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('static', 'static'),
        ('uploads', 'uploads'),
        ('*.md', '.'),
        ('*.txt', '.'),
    ],
    hiddenimports=[
        'netifaces',
        'qrcode',
        'PIL',
        'PIL.Image',
        'flask',
        'werkzeug',
        'jinja2',
        'markupsafe',
        'itsdangerous',
        'click',
        'logging',
        'datetime',
        'secrets',
        'socket',
        'string',
        'os',
        'io',
        'urllib.parse'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'unittest',
        'email',
        'xml',
        'pydoc',
        'doctest',
        'xmlrpc',
        'pdb',
        'difflib'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version_info.py',
    icon='app.ico'
)
'''
    
    with open('FileServer.spec', 'w') as f:
        f.write(spec_content)
    
    print("✓ Created FileServer.spec")

def build_exe_with_spec():
    """Build EXE using the spec file"""
    try:
        print("Building EXE with PyInstaller spec...")
        result = subprocess.run(['pyinstaller', 'FileServer.spec', '--clean'], 
                              check=True, capture_output=True, text=True)
        print("✓ EXE build completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ EXE build failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    """Main build process"""
    print("=== File Server Build Setup ===")
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.system()} {platform.architecture()[0]}")
    print()
    
    # Check if we're on Windows
    if platform.system() != "Windows":
        print("Warning: EXE and MSI builds are designed for Windows")
        print("You can still create the build files, but testing should be done on Windows")
        print()
    
    # Install dependencies
    if not install_build_dependencies():
        print("Failed to install dependencies. Exiting.")
        return
    
    print()
    
    # Create build files
    create_build_files()
    create_pyinstaller_spec()
    
    print()
    print("=== Build Options ===")
    print("1. Quick EXE build (using build_exe.py)")
    print("2. Advanced EXE build (using spec file)")
    print("3. MSI installer build (using build_msi.py)")
    print("4. All builds")
    print()
    
    choice = input("Select build option (1-4): ").strip()
    
    if choice == "1":
        print("Running quick EXE build...")
        os.system(f"{sys.executable} build_exe.py")
    
    elif choice == "2":
        print("Running advanced EXE build...")
        build_exe_with_spec()
    
    elif choice == "3":
        print("Running MSI installer build...")
        os.system(f"{sys.executable} build_msi.py")
    
    elif choice == "4":
        print("Running all builds...")
        build_exe_with_spec()
        print("\nStarting MSI build...")
        os.system(f"{sys.executable} build_msi.py")
    
    else:
        print("Invalid choice. Use 1-4")
        return
    
    print("\n=== Build Complete ===")
    print("Check the 'dist' folder for output files:")
    print("- FileServer.exe (standalone executable)")
    print("- WiFi File Server-1.0.0-amd64.msi (Windows installer)")
    print("\nDistribution files are ready for sharing!")

if __name__ == "__main__":
    main()