import os
import socket
import secrets
import string
import mimetypes
from datetime import datetime
from urllib.parse import quote
import logging

logger = logging.getLogger(__name__)

def generate_secure_password(length=12):
    """Generate a cryptographically secure password"""
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(characters) for _ in range(length))

def get_network_interfaces():
    """Get all available network interfaces and their IP addresses"""
    interfaces = {}
    
    try:
        # Get all network interfaces
        import netifaces
        for interface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addrs:
                for addr_info in addrs[netifaces.AF_INET]:
                    ip = addr_info.get('addr')
                    if ip and not ip.startswith('127.'):
                        interfaces[interface] = ip
    except ImportError:
        # Fallback method if netifaces is not available
        hostname = socket.gethostname()
        try:
            interfaces['default'] = socket.gethostbyname(hostname)
        except socket.gaierror:
            interfaces['fallback'] = get_local_ip_fallback()
    
    return interfaces

def get_local_ip_fallback():
    """Fallback method to get local IP address"""
    try:
        # Connect to a remote address to determine local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception as e:
        logger.warning(f"Could not determine local IP: {e}")
        return "127.0.0.1"

def get_mime_type(filename):
    """Get MIME type for a file"""
    mime_type, _ = mimetypes.guess_type(filename)
    if mime_type:
        return mime_type
    
    # Fallback for common file types
    ext = filename.lower().split('.')[-1] if '.' in filename else ''
    mime_map = {
        'mp4': 'video/mp4',
        'webm': 'video/webm',
        'ogg': 'video/ogg',
        'avi': 'video/x-msvideo',
        'mov': 'video/quicktime',
        'wmv': 'video/x-ms-wmv',
        'flv': 'video/x-flv',
        'mkv': 'video/x-matroska',
        'mp3': 'audio/mpeg',
        'wav': 'audio/wav',
        'flac': 'audio/flac',
        'aac': 'audio/aac',
        'wma': 'audio/x-ms-wma',
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'gif': 'image/gif',
        'svg': 'image/svg+xml',
        'webp': 'image/webp',
        'pdf': 'application/pdf',
        'txt': 'text/plain',
        'html': 'text/html',
        'css': 'text/css',
        'js': 'application/javascript',
        'json': 'application/json',
        'xml': 'application/xml',
        'zip': 'application/zip',
        'rar': 'application/x-rar-compressed',
        '7z': 'application/x-7z-compressed',
        'tar': 'application/x-tar',
        'gz': 'application/gzip'
    }
    
    return mime_map.get(ext, 'application/octet-stream')

def sanitize_filename(filename):
    """Sanitize filename to prevent path traversal and other security issues"""
    # Remove any path separators
    filename = os.path.basename(filename)
    
    # Remove or replace dangerous characters
    dangerous_chars = '<>:"/\\|?*'
    for char in dangerous_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing whitespace and dots
    filename = filename.strip('. ')
    
    # Ensure filename is not empty
    if not filename:
        filename = f"unnamed_file_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Limit filename length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        max_name_length = 255 - len(ext)
        filename = name[:max_name_length] + ext
    
    return filename

def format_bytes(size_bytes):
    """Format bytes in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB", "PB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def is_safe_path(path, base_path):
    """Check if a path is safe (no directory traversal)"""
    try:
        # Resolve both paths to absolute paths
        abs_path = os.path.abspath(path)
        abs_base = os.path.abspath(base_path)
        
        # Check if the resolved path is within the base directory
        common_path = os.path.commonpath([abs_path, abs_base])
        return common_path == abs_base
    except (ValueError, OSError):
        return False

def get_file_info(file_path):
    """Get detailed information about a file"""
    try:
        stats = os.stat(file_path)
        filename = os.path.basename(file_path)
        
        return {
            'name': filename,
            'size': stats.st_size,
            'size_formatted': format_bytes(stats.st_size),
            'modified': datetime.fromtimestamp(stats.st_mtime),
            'modified_formatted': datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            'mime_type': get_mime_type(filename),
            'extension': filename.split('.')[-1].lower() if '.' in filename else '',
            'is_media': is_media_file(filename),
            'is_image': is_image_file(filename),
            'is_video': is_video_file(filename),
            'is_audio': is_audio_file(filename)
        }
    except OSError as e:
        logger.error(f"Error getting file info for {file_path}: {e}")
        return None

def is_media_file(filename):
    """Check if file is a media file (video or audio)"""
    return is_video_file(filename) or is_audio_file(filename)

def is_video_file(filename):
    """Check if file is a video file"""
    video_extensions = {'mp4', 'webm', 'ogg', 'avi', 'mov', 'wmv', 'flv', 'mkv', '3gp', 'm4v'}
    ext = filename.lower().split('.')[-1] if '.' in filename else ''
    return ext in video_extensions

def is_audio_file(filename):
    """Check if file is an audio file"""
    audio_extensions = {'mp3', 'wav', 'flac', 'aac', 'ogg', 'wma', 'm4a', 'opus'}
    ext = filename.lower().split('.')[-1] if '.' in filename else ''
    return ext in audio_extensions

def is_image_file(filename):
    """Check if file is an image file"""
    image_extensions = {'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp', 'bmp', 'ico'}
    ext = filename.lower().split('.')[-1] if '.' in filename else ''
    return ext in image_extensions

def validate_file_upload(file, max_size=500*1024*1024, allowed_extensions=None):
    """Validate file upload"""
    errors = []
    
    if not file or not file.filename:
        errors.append("No file selected")
        return errors
    
    # Check file size
    if hasattr(file, 'content_length') and file.content_length:
        if file.content_length > max_size:
            errors.append(f"File too large. Maximum size is {format_bytes(max_size)}")
    
    # Check file extension
    if allowed_extensions:
        filename = file.filename.lower()
        if '.' not in filename:
            errors.append("File must have an extension")
        else:
            ext = filename.rsplit('.', 1)[1]
            if ext not in allowed_extensions:
                errors.append(f"File type '{ext}' not allowed")
    
    # Check filename
    sanitized = sanitize_filename(file.filename)
    if not sanitized or sanitized != file.filename:
        errors.append("Invalid filename")
    
    return errors

def create_directory_if_not_exists(directory):
    """Create directory if it doesn't exist"""
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except OSError as e:
        logger.error(f"Error creating directory {directory}: {e}")
        return False

def get_free_disk_space(path):
    """Get free disk space for a given path"""
    try:
        statvfs = os.statvfs(path)
        # Free space = fragment size * available fragments
        free_space = statvfs.f_frsize * statvfs.f_bavail
        return free_space
    except (OSError, AttributeError):
        # Fallback for systems that don't support statvfs
        try:
            import shutil
            total, used, free = shutil.disk_usage(path)
            return free
        except:
            return None

def log_file_operation(operation, filename, user_ip=None, success=True, error=None):
    """Log file operations for audit purposes"""
    log_level = logging.INFO if success else logging.ERROR
    message = f"File {operation}: {filename}"
    
    if user_ip:
        message += f" from {user_ip}"
    
    if not success and error:
        message += f" - Error: {error}"
    
    logger.log(log_level, message)

def generate_unique_filename(directory, filename):
    """Generate a unique filename in the given directory"""
    base_name, extension = os.path.splitext(filename)
    counter = 1
    
    while os.path.exists(os.path.join(directory, filename)):
        filename = f"{base_name}_{counter}{extension}"
        counter += 1
    
    return filename

# Security utilities
def is_allowed_file_type(filename, allowed_extensions):
    """Check if file type is allowed"""
    if not filename or '.' not in filename:
        return False
    
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in allowed_extensions

def validate_password_strength(password, min_length=8):
    """Validate password strength"""
    errors = []
    
    if len(password) < min_length:
        errors.append(f"Password must be at least {min_length} characters long")
    
    if not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one digit")
    
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        errors.append("Password must contain at least one special character")
    
    return errors

# Rate limiting helpers
class RateLimiter:
    def __init__(self, max_requests=100, time_window=3600):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = {}
    
    def is_allowed(self, identifier):
        """Check if request is allowed for the given identifier"""
        now = datetime.now().timestamp()
        
        # Clean old entries
        self.requests = {
            key: timestamps for key, timestamps in self.requests.items()
            if any(now - ts < self.time_window for ts in timestamps)
        }
        
        # Get recent requests for this identifier
        recent_requests = [
            ts for ts in self.requests.get(identifier, [])
            if now - ts < self.time_window
        ]
        
        if len(recent_requests) >= self.max_requests:
            return False
        
        # Add current request
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        self.requests[identifier] = recent_requests + [now]
        return True
