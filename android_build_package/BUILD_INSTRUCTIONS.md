# WiFi File Server - Android Build Instructions

## Quick Start

1. **Install Dependencies**:
   ```bash
   sudo apt update
   sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
   pip install buildozer
   ```

2. **Build APK**:
   ```bash
   buildozer android debug
   ```

3. **Install on Device**:
   ```bash
   # Enable USB Debugging on your Android device
   # Connect via USB
   buildozer android deploy
   
   # Or install manually
   adb install bin/wififileserver-*-debug.apk
   ```

## Project Structure

```
android_build_package/
├── main.py              # App entry point
├── kivy_app.py          # Main application code
├── buildozer.spec       # Build configuration
├── requirements.txt     # Python dependencies
├── BUILD_INSTRUCTIONS.md # This file
├── icon.png            # App icon (optional)
├── presplash.png       # Splash screen (optional)
└── assets/             # Additional assets (optional)
```

## Build Configuration

### buildozer.spec Settings
- **App Name**: WiFi File Server
- **Package**: org.example.wififileserver
- **Version**: 1.0
- **Target API**: 33 (Android 13)
- **Min API**: 21 (Android 5.0)
- **Permissions**: Storage, Camera, Internet

### Customization

1. **Change App Details**:
   ```ini
   # Edit buildozer.spec
   title = Your App Name
   package.name = yourappname
   package.domain = com.yourcompany
   ```

2. **Add Custom Icon** (192x192 PNG):
   ```ini
   icon.filename = %(source.dir)s/icon.png
   ```

3. **Add Splash Screen** (1280x720 PNG):
   ```ini
   presplash.filename = %(source.dir)s/presplash.png
   ```

## Build Commands

### Development Build
```bash
# Debug APK (unsigned)
buildozer android debug

# Install on connected device
buildozer android deploy

# Build and install in one step
buildozer android debug deploy
```

### Release Build
```bash
# Release APK (requires signing)
buildozer android release

# Clean build cache
buildozer android clean
```

### Troubleshooting
```bash
# Verbose output for debugging
buildozer android debug -v

# Update Android SDK/NDK
buildozer android update

# Check requirements
buildozer requirements
```

## First Build Setup

The first build takes 20-40 minutes as it downloads:
- Android SDK
- Android NDK
- Python-for-Android toolchain
- All dependencies

Subsequent builds are much faster (2-5 minutes).

## System Requirements

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
```

### Fedora/CentOS
```bash
sudo dnf install -y git zip unzip java-17-openjdk-devel python3-pip autoconf libtool pkgconfig zlib-devel ncurses-devel cmake libffi-devel openssl-devel
```

### macOS
```bash
brew install git zip unzip openjdk@17 python3 autoconf libtool pkg-config cmake
pip install buildozer
```

## App Features

### Core Functionality
- ✅ Password-protected file management
- ✅ File upload via native picker
- ✅ File download/open with system apps
- ✅ Delete files with confirmation
- ✅ Local storage in app directory
- ✅ Cross-platform compatibility

### Mobile Integration
- ✅ Android permissions (storage, camera)
- ✅ Native file associations
- ✅ System notifications
- ✅ Touch-optimized interface
- ✅ Responsive design

## Development

### Test on Desktop
```bash
# Install Kivy for desktop testing
pip install kivy kivymd plyer

# Run app
python main.py
```

### Debug on Device
```bash
# View device logs
adb logcat | grep python

# Install APK manually
adb install -r bin/*.apk

# Check app permissions
# Settings → Apps → WiFi File Server → Permissions
```

## Distribution

### Direct Distribution
1. Share the APK file directly
2. Enable "Install from Unknown Sources" on target devices
3. Install via file manager or ADB

### Play Store (Future)
1. Create release build: `buildozer android release`
2. Sign APK with your keystore
3. Upload to Google Play Console
4. Complete store listing and compliance

## Security Notes

- App stores files in private app directory
- Password is hashed with SHA-256
- No network access (purely local storage)
- Android sandbox provides additional isolation
- Regular app updates recommended

## Support

- **Buildozer Issues**: [github.com/kivy/buildozer](https://github.com/kivy/buildozer)
- **Kivy Documentation**: [kivy.org/doc](https://kivy.org/doc/)
- **Android Development**: [developer.android.com](https://developer.android.com)

## Version History

- **v1.0**: Initial mobile conversion from Flask web app
- Features: File management, password auth, local storage
- Platforms: Android (iOS support planned)