import os
import socket
import secrets
import string
import logging
from datetime import datetime, timedelta
from io import BytesIO
from urllib.parse import quote

import qrcode
from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash, jsonify, abort
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestedRangeNotSatisfiable
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Configuration
UPLOAD_FOLDER = 'uploads'
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
ALLOWED_EXTENSIONS = {
    'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp',
    'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv',
    'mp3', 'wav', 'flac', 'aac', 'ogg', 'wma',
    'zip', 'rar', '7z', 'tar', 'gz',
    'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
    'html', 'css', 'js', 'json', 'xml'
}

MEDIA_EXTENSIONS = {
    'video': {'mp4', 'webm', 'ogg', 'avi', 'mov', 'wmv', 'flv', 'mkv'},
    'audio': {'mp3', 'wav', 'ogg', 'aac', 'flac', 'wma'}
}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global variables for server info
SERVER_PASSWORD = None
SERVER_URL = None
SERVER_PORT = 5000


def generate_password(length=12):
    """Generate a secure random password"""
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(characters) for _ in range(length))


def get_server_url():
    """Get the server URL - prioritize local network IP for WiFi access"""
    try:
        # First try to get local network IP using socket connection
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        
        # Don't use loopback addresses for network sharing
        if not ip.startswith('127.'):
            return f"http://{ip}:{SERVER_PORT}"
    except Exception:
        pass
    
    # Try alternative methods to get local IP
    try:
        import netifaces
        for interface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addrs:
                for addr_info in addrs[netifaces.AF_INET]:
                    ip = addr_info.get('addr')
                    if ip and not ip.startswith('127.') and not ip.startswith('169.254'):
                        return f"http://{ip}:{SERVER_PORT}"
    except ImportError:
        pass
    
    # Last resort - try hostname resolution
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        if not ip.startswith('127.'):
            return f"http://{ip}:{SERVER_PORT}"
    except:
        pass
    
    # Final fallback to localhost
    return f"http://127.0.0.1:{SERVER_PORT}"

def get_all_network_ips():
    """Get all available network IP addresses for display"""
    ips = []
    
    # Method 1: Socket connection method
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        primary_ip = s.getsockname()[0]
        s.close()
        if not primary_ip.startswith('127.'):
            ips.append({'interface': 'Primary', 'ip': primary_ip, 'url': f"http://{primary_ip}:{SERVER_PORT}"})
    except:
        pass
    
    # Method 2: netifaces library
    try:
        import netifaces
        for interface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addrs:
                for addr_info in addrs[netifaces.AF_INET]:
                    ip = addr_info.get('addr')
                    if ip and not ip.startswith('127.') and not ip.startswith('169.254'):
                        # Skip if already found via primary method
                        if not any(existing['ip'] == ip for existing in ips):
                            ips.append({'interface': interface, 'ip': ip, 'url': f"http://{ip}:{SERVER_PORT}"})
    except ImportError:
        pass
    
    # Add localhost as last option
    ips.append({'interface': 'Localhost', 'ip': '127.0.0.1', 'url': f"http://127.0.0.1:{SERVER_PORT}"})
    
    return ips


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_type(filename):
    """Determine file type for media streaming"""
    if '.' not in filename:
        return 'other'
    
    ext = filename.rsplit('.', 1)[1].lower()
    if ext in MEDIA_EXTENSIONS['video']:
        return 'video'
    elif ext in MEDIA_EXTENSIONS['audio']:
        return 'audio'
    elif ext in {'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp'}:
        return 'image'
    else:
        return 'other'


def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f}{size_names[i]}"


def generate_qr_code():
    """Generate QR code containing server URL and password"""
    global SERVER_URL, SERVER_PASSWORD
    if not SERVER_URL or not SERVER_PASSWORD:
        return None
    
    qr_data = f"URL: {SERVER_URL}\nPassword: {SERVER_PASSWORD}"
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="white", back_color="black")
    
    # Convert to bytes
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    
    return img_io


def initialize_server():
    """Initialize server settings"""
    global SERVER_PASSWORD, SERVER_URL
    if not SERVER_PASSWORD:
        SERVER_PASSWORD = generate_password()
    if not SERVER_URL:
        SERVER_URL = get_server_url()
    app.logger.info(f"Server initialized - URL: {SERVER_URL}, Password: {SERVER_PASSWORD}")

# Initialize server info at startup
initialize_server()


@app.route('/')
def index():
    """Main page showing server info and QR code"""
    global SERVER_URL, SERVER_PASSWORD
    if not SERVER_PASSWORD:
        SERVER_PASSWORD = generate_password()
    if not SERVER_URL:
        SERVER_URL = get_server_url()
    
    network_ips = get_all_network_ips()
    return render_template('index.html', 
                         server_url=SERVER_URL, 
                         server_password=SERVER_PASSWORD,
                         network_ips=network_ips)


@app.route('/qr')
def qr_code():
    """Generate and serve QR code"""
    qr_img = generate_qr_code()
    if qr_img:
        return send_file(qr_img, mimetype='image/png')
    else:
        abort(404)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page for password protection"""
    if request.method == 'POST':
        password = request.form.get('password')
        if password == SERVER_PASSWORD:
            session['authenticated'] = True
            session['login_time'] = datetime.now().timestamp()
            flash('Successfully authenticated!', 'success')
            return redirect(url_for('files'))
        else:
            flash('Invalid password. Please try again.', 'error')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    flash('Successfully logged out.', 'info')
    return redirect(url_for('login'))


def login_required(f):
    """Decorator to require authentication"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        
        # Check session timeout (1 hour)
        login_time = session.get('login_time')
        if login_time and datetime.now().timestamp() - login_time > 3600:  # 1 hour in seconds
            session.clear()
            flash('Session expired. Please log in again.', 'error')
            return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    
    return decorated_function


@app.route('/files')
@login_required
def files():
    """File browser page"""
    files_list = []
    
    try:
        for filename in os.listdir(UPLOAD_FOLDER):
            if filename.startswith('.'):
                continue
                
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(file_path):
                file_stats = os.stat(file_path)
                files_list.append({
                    'name': filename,
                    'size': format_file_size(file_stats.st_size),
                    'size_bytes': file_stats.st_size,
                    'modified': datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    'type': get_file_type(filename)
                })
        
        # Sort by name
        files_list.sort(key=lambda x: x['name'].lower())
        
    except Exception as e:
        app.logger.error(f"Error listing files: {e}")
        flash('Error accessing files directory.', 'error')
    
    return render_template('files.html', files=files_list)


@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    """Handle file uploads"""
    if 'file' not in request.files:
        flash('No file selected.', 'error')
        return redirect(url_for('files'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected.', 'error')
        return redirect(url_for('files'))
    
    if file and file.filename and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        
        # Check if file already exists
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            # Add timestamp to filename to avoid conflicts
            name, ext = os.path.splitext(filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{name}_{timestamp}{ext}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        try:
            file.save(file_path)
            flash(f'File "{filename}" uploaded successfully!', 'success')
        except Exception as e:
            app.logger.error(f"Error saving file: {e}")
            flash('Error uploading file. Please try again.', 'error')
    else:
        flash('File type not allowed.', 'error')
    
    return redirect(url_for('files'))


@app.route('/download/<filename>')
@login_required
def download_file(filename):
    """Download a file"""
    try:
        file_path = os.path.join(UPLOAD_FOLDER, secure_filename(filename))
        if not os.path.exists(file_path):
            abort(404)
        
        return send_file(file_path, as_attachment=True, download_name=filename)
    except Exception as e:
        app.logger.error(f"Error downloading file: {e}")
        abort(500)


@app.route('/stream/<filename>')
@login_required
def stream_file(filename):
    """Stream media files with range support"""
    try:
        file_path = os.path.join(UPLOAD_FOLDER, secure_filename(filename))
        if not os.path.exists(file_path):
            abort(404)
        
        file_type = get_file_type(filename)
        if file_type not in ['video', 'audio']:
            return download_file(filename)
        
        # Handle range requests for media streaming
        range_header = request.headers.get('Range', None)
        byte_start = 0
        byte_end = None
        
        file_size = os.path.getsize(file_path)
        
        if range_header:
            match = range_header.replace('bytes=', '').split('-')
            byte_start = int(match[0])
            if match[1]:
                byte_end = int(match[1])
        
        if byte_end is None:
            byte_end = file_size - 1
        
        content_length = byte_end - byte_start + 1
        
        def generate():
            with open(file_path, 'rb') as f:
                f.seek(byte_start)
                remaining = content_length
                while remaining:
                    chunk_size = min(1024 * 1024, remaining)  # 1MB chunks
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    remaining -= len(chunk)
                    yield chunk
        
        # Determine MIME type
        mime_type = 'application/octet-stream'
        if file_type == 'video':
            ext = filename.rsplit('.', 1)[1].lower()
            if ext == 'mp4':
                mime_type = 'video/mp4'
            elif ext == 'webm':
                mime_type = 'video/webm'
            elif ext == 'ogg':
                mime_type = 'video/ogg'
        elif file_type == 'audio':
            ext = filename.rsplit('.', 1)[1].lower()
            if ext == 'mp3':
                mime_type = 'audio/mpeg'
            elif ext == 'wav':
                mime_type = 'audio/wav'
            elif ext == 'ogg':
                mime_type = 'audio/ogg'
        
        response = app.response_class(
            generate(),
            206 if range_header else 200,
            mimetype=mime_type,
            direct_passthrough=True
        )
        
        response.headers.add('Accept-Ranges', 'bytes')
        response.headers.add('Content-Length', str(content_length))
        
        if range_header:
            response.headers.add('Content-Range', f'bytes {byte_start}-{byte_end}/{file_size}')
        
        return response
        
    except Exception as e:
        app.logger.error(f"Error streaming file: {e}")
        abort(500)


@app.route('/delete/<filename>', methods=['POST'])
@login_required
def delete_file(filename):
    """Delete a file"""
    try:
        file_path = os.path.join(UPLOAD_FOLDER, secure_filename(filename))
        if os.path.exists(file_path):
            os.remove(file_path)
            flash(f'File "{filename}" deleted successfully!', 'success')
        else:
            flash('File not found.', 'error')
    except Exception as e:
        app.logger.error(f"Error deleting file: {e}")
        flash('Error deleting file.', 'error')
    
    return redirect(url_for('files'))


@app.route('/api/server-info')
def api_server_info():
    """API endpoint to get server information"""
    global SERVER_URL, SERVER_PASSWORD
    return jsonify({
        'url': SERVER_URL,
        'password': SERVER_PASSWORD,
        'network_ips': get_all_network_ips()
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('login.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return render_template('login.html'), 500


@app.errorhandler(413)
def file_too_large(error):
    """Handle file too large errors"""
    flash('File too large. Maximum size is 500MB.', 'error')
    return redirect(url_for('files'))


if __name__ == '__main__':
    # Initialize server info
    if not SERVER_PASSWORD:
        SERVER_PASSWORD = generate_password()
    if not SERVER_URL:
        SERVER_URL = get_server_url()
    
    print(f"\n🚀 File Server Starting...")
    print(f"📍 Server URL: {SERVER_URL}")
    print(f"🔐 Password: {SERVER_PASSWORD}")
    print(f"📁 Upload Directory: {os.path.abspath(UPLOAD_FOLDER)}")
    print(f"🌐 Access from other devices: {SERVER_URL}")
    print(f"📱 QR Code available at: {SERVER_URL}/qr")
    
    app.run(host='0.0.0.0', port=SERVER_PORT, debug=True)
