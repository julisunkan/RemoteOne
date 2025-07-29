# Local Setup Instructions for Windows

## Prerequisites
- Python 3.8 or higher installed
- Command Prompt or PowerShell

## Installation Steps

1. **Navigate to the project directory:**
   ```cmd
   cd "c:\Users\Julius\Downloads\FileHost (1)\FileHost"
   ```

2. **Create a virtual environment (recommended):**
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install required packages:**
   ```cmd
   pip install Flask==3.0.0
   pip install Werkzeug==3.0.1
   pip install qrcode==7.4.2 
   pip install Pillow==10.1.0
   pip install netifaces==0.11.0
   ```

   Or install all at once:
   ```cmd
   pip install Flask Werkzeug qrcode Pillow netifaces
   ```

4. **Set environment variable (optional):**
   ```cmd
   set SESSION_SECRET=your-secret-key-here
   ```

5. **Run the server:**
   ```cmd
   python main.py
   ```

## Expected Output
The server will start and display:
- Server URL (your local network IP)
- Access password
- Server running on http://0.0.0.0:5000

## WiFi Sharing
- The server will automatically detect your local network IP
- Share the displayed URL with other devices on the same WiFi
- Use the generated password to access files from any device

## Troubleshooting
- If you get permission errors, run Command Prompt as Administrator
- If modules are still missing, try upgrading pip: `python -m pip install --upgrade pip`
- Make sure all devices are on the same WiFi network for sharing