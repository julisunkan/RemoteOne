#!/usr/bin/env python3
"""
Run the Kivy mobile app
Separate entry point to avoid conflicts with Flask/Gunicorn
"""

import os
import sys

# Set environment variable to disable Kivy argument parsing conflicts
os.environ['KIVY_NO_ARGS'] = '1'

# Import and run the Kivy app
from kivy_app import WiFiFileServerApp

if __name__ == '__main__':
    print("Starting WiFi File Server mobile app...")
    app = WiFiFileServerApp()
    app.run()