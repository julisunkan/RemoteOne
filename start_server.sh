#!/bin/bash
echo "Starting WiFi File Server..."
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3"
    exit 1
fi

# Install dependencies if needed
echo "Installing/checking dependencies..."
python3 -m pip install flask werkzeug pillow qrcode netifaces --quiet

# Run the application
echo
echo "Starting server..."
python3 FileServer.pyz
