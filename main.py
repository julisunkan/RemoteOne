"""
Main entry point - supports both Flask web server and Kivy mobile app
"""

import sys
import os

def run_web_server():
    """Run the Flask web server"""
    from app import app
    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=5000, debug=True)

def run_kivy_app():
    """Run the Kivy mobile app"""
    from kivy_app import WiFiFileServerApp
    app = WiFiFileServerApp()
    app.run()

# Import Flask app for Gunicorn
from app import app

# Check command line arguments or environment to decide which app to run
if __name__ == '__main__':
    if '--kivy' in sys.argv or os.environ.get('RUN_KIVY'):
        run_kivy_app()
    else:
        # Default to web server for Replit workflow
        app.run(host='0.0.0.0', port=5000, debug=True)