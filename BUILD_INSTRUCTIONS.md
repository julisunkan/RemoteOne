# Building EXE and MSI Installers

This guide explains how to convert your Flask file server into Windows executables and installers.

## Quick Start

### Option 1: Automated Build (Recommended)
```cmd
python setup_build.py
```
This will:
- Install required build dependencies
- Create all necessary build files
- Guide you through build options
- Generate both EXE and MSI files

### Option 2: Manual Build Steps

#### For EXE (Standalone Executable):
```cmd
# Install dependencies
pip install pyinstaller pillow

# Build executable
python build_exe.py
```

#### For MSI (Windows Installer):
```cmd
# Install dependencies
pip install cx_Freeze pillow

# Build installer
python build_msi.py
```

## Build Files Created

### Core Build Scripts:
- `setup_build.py` - Master build script with guided setup
- `build_exe.py` - Creates standalone EXE using PyInstaller
- `build_msi.py` - Creates MSI installer using cx_Freeze
- `launcher.py` - GUI launcher with start/stop controls

### Generated Files:
- `FileServer.exe` - Standalone executable (no installation needed)
- `WiFi File Server-1.0.0-amd64.msi` - Professional Windows installer
- `app.ico` - Application icon
- `version_info.py` - Windows version information
- `FileServer.spec` - Advanced PyInstaller configuration

## Output Files Location

After building, check the `dist/` folder:
```
dist/
├── FileServer.exe                          # Standalone executable
└── WiFi File Server-1.0.0-amd64.msi      # Windows installer
```

## Distribution Options

### EXE Distribution (Portable):
- **Size**: ~15-25MB single file
- **Installation**: None required
- **Usage**: Double-click to run
- **Pros**: Portable, no installation needed
- **Cons**: Larger file size, slower startup

### MSI Distribution (Professional):
- **Size**: ~20-30MB installer
- **Installation**: Standard Windows installer
- **Usage**: Install once, run from Start Menu
- **Pros**: Professional experience, Start Menu integration, uninstaller
- **Cons**: Requires installation step

## Features Included in Both Builds

✅ **Complete Flask Application**
- All web server functionality
- File upload/download capabilities
- Media streaming support
- PWA functionality

✅ **Dependencies Bundled**
- Python runtime included
- All required libraries (Flask, Pillow, etc.)
- No external dependencies needed

✅ **User Experience**
- GUI launcher with start/stop controls
- Automatic browser opening
- System tray integration (MSI only)
- Professional Windows integration

✅ **File Management**
- Creates uploads folder automatically
- Includes documentation files
- Proper file associations

## System Requirements

### Build Requirements:
- Windows 7/8/10/11 (for building)
- Python 3.8+ with pip
- 500MB free disk space for build tools

### Runtime Requirements (for end users):
- Windows 7/8/10/11
- 100MB free disk space
- Network connection (WiFi/Ethernet)
- No Python installation needed

## Advanced Configuration

### Customizing the Build:

1. **Icon**: Replace `app.ico` with your custom icon
2. **Version**: Edit version numbers in `build_msi.py`
3. **Company Info**: Update company details in `version_info.py`
4. **Features**: Modify `FileServer.spec` for advanced PyInstaller options

### Build Optimization:

- **Size Optimization**: Use `--strip` and `--upx` flags
- **Speed Optimization**: Use `--onedir` instead of `--onefile`
- **Security**: Add code signing with `--codesign-identity`

## Troubleshooting

### Common PyInstaller Issues

#### Missing Email Module Error
If you get: `ModuleNotFoundError: No module named 'email'`

**Solution**: The project now includes a comprehensive PyInstaller spec file (`fileserver.spec`) that properly handles all Python standard library dependencies including the email module. Use this command:

```cmd
pyinstaller fileserver.spec
```

This spec file includes all necessary hidden imports and should resolve the email module issue.

## Additional Troubleshooting

### Common Build Issues:

1. **Missing Dependencies**:
   ```cmd
   pip install pyinstaller cx_Freeze pillow
   ```

2. **Import Errors**:
   - Check `hiddenimports` in build scripts
   - Add missing modules to the imports list

3. **File Not Found**:
   - Ensure all template and static files are included
   - Check `include_files` in build configuration

4. **Antivirus False Positives**:
   - Built executables may trigger antivirus warnings
   - This is normal for PyInstaller builds
   - Submit to antivirus vendors for whitelisting

### Testing Builds:

1. **EXE Testing**:
   ```cmd
   dist\FileServer.exe
   ```

2. **MSI Testing**:
   - Install MSI on clean Windows VM
   - Test all functionality
   - Verify uninstallation works

## Distribution Checklist

Before distributing your builds:

- [ ] Test on clean Windows system
- [ ] Verify all features work
- [ ] Check file permissions
- [ ] Test network connectivity
- [ ] Validate installer/uninstaller
- [ ] Include documentation
- [ ] Consider code signing for production

## Production Deployment

For production distribution:

1. **Code Signing**: Sign executables with valid certificate
2. **Testing**: Test on multiple Windows versions
3. **Documentation**: Include user manuals
4. **Support**: Provide contact information
5. **Updates**: Plan for version updates and distribution

Your file server is now ready for professional Windows distribution!