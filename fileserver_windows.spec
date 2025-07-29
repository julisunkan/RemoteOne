# -*- mode: python ; coding: utf-8 -*-
# Enhanced Windows-compatible PyInstaller spec file

import sys
import os

block_cipher = None

# Ensure we're building for Windows
TARGET_PLATFORM = 'win32'

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
        # Core application modules
        'netifaces', 'qrcode', 'PIL', 'PIL.Image', 'PIL.ImageDraw',
        
        # Email modules (fix for the original error)
        'email', 'email.mime', 'email.mime.text', 'email.mime.multipart',
        'email.mime.base', 'email.mime.application', 'email.utils',
        'email.header', 'email.charset', 'email.encoders', 'email.errors',
        'email.generator', 'email.iterators', 'email.message', 'email.parser',
        'email.policy',
        
        # Package resources
        'pkg_resources', 'pkg_resources.py31compat', 'pkg_resources._vendor',
        
        # Flask and related
        'werkzeug', 'werkzeug.security', 'werkzeug.utils', 'werkzeug.exceptions',
        'flask', 'flask.templating', 'flask.json', 'jinja2', 'jinja2.ext',
        'markupsafe',
        
        # Standard library modules that might be missing
        'urllib', 'urllib.parse', 'socket', 'threading', 'logging',
        'datetime', 'io', 'secrets', 'string', 'os', 'sys', 'json',
        'base64', 'hashlib', 'hmac', 'mimetypes', 'tempfile', 'shutil',
        'pathlib', 'collections', 'functools', 'itertools', 're',
        
        # Windows-specific (when building on Windows)
        'msvcrt',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules to reduce size
        'tkinter', 'matplotlib', 'numpy', 'scipy', 'pandas',
        'IPython', 'jupyter', 'notebook', 'sphinx', 'pytest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Remove any problematic modules
problematic_modules = ['_tkinter', 'tkinter']
a.pure = [x for x in a.pure if not any(x[0].startswith(mod) for mod in problematic_modules)]
a.binaries = [x for x in a.binaries if not any(x[0].startswith(mod) for mod in problematic_modules)]

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
    console=True,  # Show console for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='x86_64',
    codesign_identity=None,
    entitlements_file=None,
    icon='app.ico' if os.path.exists('app.ico') else None,
)