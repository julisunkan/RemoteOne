#!/usr/bin/env python3
"""
WiFi File Server - Mobile App Entry Point
"""

import os

# Set environment variable to disable Kivy argument parsing conflicts
os.environ['KIVY_NO_ARGS'] = '1'

from kivy_app import WiFiFileServerApp

if __name__ == '__main__':
    app = WiFiFileServerApp()
    app.run()