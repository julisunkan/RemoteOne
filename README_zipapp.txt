WiFi File Server - Python Executable (.pyz)
==========================================

This is a Python zipapp executable that works on any system with Python installed.

REQUIREMENTS:
- Python 3.7 or newer
- Internet connection (for first-time dependency installation)

HOW TO RUN:

Method 1 - Use the launcher scripts:
  Windows: Double-click "start_server.bat"
  Linux/Mac: Run "./start_server.sh" in terminal

Method 2 - Direct execution:
  Windows: python FileServer.pyz
  Linux/Mac: python3 FileServer.pyz

Method 3 - Direct execution (if Python is in PATH):
  Linux/Mac: ./FileServer.pyz

FIRST TIME SETUP:
The launcher scripts will automatically install required Python packages:
- Flask (web framework)
- Werkzeug (WSGI utilities)
- Pillow (image processing)
- qrcode (QR code generation)
- netifaces (network interface detection)

USAGE:
1. Run the server using one of the methods above
2. The server will show you the local network URL and password
3. Open the URL in any web browser on your network
4. Use the password to log in
5. Upload, download, and manage files through the web interface

FEATURES:
- Secure password-protected access
- File upload and download
- Works on local network (WiFi sharing)
- QR code for easy mobile access
- Support for all file types
- Progressive Web App (installable on mobile)

TROUBLESHOOTING:
- Make sure Python is installed: python --version
- If dependencies fail to install, try: pip install flask werkzeug pillow qrcode netifaces
- If port 5000 is busy, close other applications using that port
- For network access issues, check your firewall settings

The server will be accessible at: http://[your-computer-ip]:5000
Password will be displayed when the server starts.
