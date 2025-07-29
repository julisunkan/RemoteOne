# WiFi File Server Android App - Quick Start

## What You Get

A native Android app that provides secure file management on your mobile device:
- Password-protected access
- Upload files from device storage
- Download/open files with system apps
- Delete files with confirmation
- Local storage in app directory
- No internet required

## Build in 3 Steps

### 1. Install Build Tools (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
pip install buildozer
```

### 2. Build APK
```bash
cd android_build_package
buildozer android debug
```
*First build takes 20-40 minutes (downloads Android SDK/NDK)*

### 3. Install on Device
```bash
# Enable USB Debugging on Android device
# Connect via USB cable
buildozer android deploy

# Or install manually
adb install bin/wififileserver-*-debug.apk
```

## Files Included

- **main.py** - App entry point
- **kivy_app.py** - Mobile UI and functionality 
- **buildozer.spec** - Build configuration
- **requirements.txt** - Dependencies
- **icon.png** - App icon (192x192)
- **presplash.png** - Splash screen (1280x720)
- **BUILD_INSTRUCTIONS.md** - Detailed guide

## First Run

1. Install APK on Android device
2. Open "WiFi File Server" app
3. App generates secure password (shown in notification)
4. Enter password to access file manager
5. Use Upload button to add files
6. Tap files to open with system apps

## Customization

Edit `buildozer.spec` to change:
- App name: `title = Your App Name`
- Package name: `package.name = yourapp`
- Company domain: `package.domain = com.yourcompany`

## Support

- Issues with build? See BUILD_INSTRUCTIONS.md
- Need help? Check Kivy documentation
- Want web version? Use original Flask app

Your file server is now mobile! 📱