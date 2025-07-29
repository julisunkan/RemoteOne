# File Server Application

## Overview

This is a Flask-based personal file server application that allows users to securely upload, manage, and share files across devices. The application features password-protected access, a web-based file management interface, and support for multiple file types including documents, images, videos, and audio files.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Server**: Built-in Flask development server
- **File Storage**: Local filesystem storage in `uploads/` directory
- **Authentication**: Session-based authentication with password protection
- **Security**: Werkzeug security utilities for password hashing

### Frontend Architecture
- **Template Engine**: Jinja2 (Flask's default)
- **CSS Framework**: Bootstrap 5.3.0 with dark theme
- **Icons**: Font Awesome 6.4.0
- **JavaScript**: Vanilla JavaScript for client-side functionality
- **Responsive Design**: Mobile-first responsive layout

### File Management System
- **Upload Directory**: `uploads/` folder for file storage
- **File Size Limit**: 500MB maximum per file
- **Supported Formats**: 
  - Documents: txt, pdf, doc, docx, xls, xlsx, ppt, pptx
  - Images: png, jpg, jpeg, gif, svg, webp
  - Videos: mp4, avi, mov, wmv, flv, webm, mkv
  - Audio: mp3, wav, flac, aac, ogg, wma
  - Archives: zip, rar, 7z, tar, gz
  - Web: html, css, js, json, xml

## Key Components

### Core Application Files
- `app.py`: Main Flask application with route definitions and configuration
- `main.py`: Application entry point for running the server
- `utils.py`: Utility functions for network operations and security

### Frontend Components
- `templates/`: HTML templates using Jinja2
  - `index.html`: Welcome page with server information
  - `login.html`: Authentication page
  - `files.html`: File management interface (incomplete in provided code)
- `static/`: Static assets
  - `css/style.css`: Custom dark theme styling
  - `js/script.js`: Client-side functionality

### Security Features
- Password-based authentication using session management
- Secure password generation utility
- File upload validation and security measures
- CSRF protection through Flask's built-in session handling

## Data Flow

1. **User Access**: Users access the application through web browser
2. **Authentication**: Password verification required for access
3. **File Operations**: 
   - Upload files through web interface
   - Browse and manage files via file manager
   - Download files with proper MIME type handling
4. **Session Management**: User sessions maintained server-side
5. **Network Access**: Server accessible via local network interfaces

## External Dependencies

### Python Packages
- **Flask**: Web framework
- **Werkzeug**: WSGI utilities and security functions
- **Pillow (PIL)**: Image processing
- **qrcode**: QR code generation for easy access
- **netifaces**: Network interface detection (optional fallback)

### Frontend Dependencies (CDN)
- **Bootstrap 5.3.0**: UI framework
- **Font Awesome 6.4.0**: Icon library

### System Dependencies
- **File System**: Local storage for uploaded files
- **Network**: Socket operations for IP detection

## Deployment Strategy

### Development Setup
- Flask development server with debug mode enabled
- Host: `0.0.0.0` (all interfaces)
- Port: `5000`
- Auto-reload enabled for development

### Configuration
- Environment-based secret key configuration
- Configurable upload directory and file size limits
- Network interface auto-detection for multi-device access

### Security Considerations
- Session secret should be changed in production
- File upload restrictions to prevent malicious uploads
- Directory traversal protection through secure filename handling
- Password-based access control

### Network Access
- Automatic local IP detection for network sharing
- QR code generation for easy mobile access
- Support for multiple network interfaces

### File Storage
- Local filesystem storage in dedicated upload directory
- Automatic directory creation
- File type validation and extension checking
- Secure filename sanitization

## Recent Changes

### July 29, 2025
- ✓ Fixed Flask compatibility issues (`@app.before_first_request` deprecated)
- ✓ Improved clipboard functionality with multiple fallback methods for different browsers
- ✓ Removed service worker to fix HTTPS-only clipboard API issues
- ✓ Enhanced error handling and toast notifications
- ✓ Added helpful UI hints for manual copying when clipboard fails
- ✓ **WiFi Sharing Implementation**: Modified server to prioritize local network IP detection
- ✓ **Network Interface Detection**: Added multiple network IP discovery methods using netifaces
- ✓ **Enhanced UI**: Shows all available network interfaces for optimal WiFi sharing
- ✓ **Setup Instructions**: Added step-by-step WiFi sharing guide in UI
- ✓ Server running on local network: http://172.31.84.130:5000
- ✓ QR code generation working for easy mobile access

## Notes

- The application is designed for local network use and personal file sharing
- Full file management interface implemented with drag & drop upload functionality
- Media streaming support for video and audio files with HTML5 players
- The system supports both development and production deployment scenarios
- Network utilities provide fallback methods for IP detection across different environments
- Clipboard functionality now works across different security contexts (HTTP/HTTPS)