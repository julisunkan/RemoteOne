#!/usr/bin/env python3
import sys
import os

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import and run the app
try:
    from app import app
    if __name__ == '__main__':
        print("Starting WiFi File Server...")
        print("Press Ctrl+C to stop the server")
        app.run(host='0.0.0.0', port=5000, debug=False)
except KeyboardInterrupt:
    print("\nServer stopped by user")
except Exception as e:
    print(f"Error starting server: {e}")
    input("Press Enter to exit...")
