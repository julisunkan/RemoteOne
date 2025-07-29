"""
Kivy Mobile File Server App
Native mobile client that connects to Flask web server
Replicates web app UI with media playback capabilities
"""

import os
import requests
import threading
import time
from datetime import datetime
from urllib.parse import urljoin, quote
import webbrowser

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.uix.video import Video
from kivy.uix.slider import Slider
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import platform
from kivy.network.urlrequest import UrlRequest
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.dropdown import DropDown

# Try to import platform-specific modules
try:
    from plyer import filechooser, notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False
    filechooser = None
    notification = None

class ServerConnectionScreen(BoxLayout):
    """Server connection and authentication screen - matches web app styling"""
    
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app_instance = app_instance
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 15
        
        # Title with web app styling
        title = Label(
            text='WiFi File Server',
            font_size='28sp',
            bold=True,
            color=(0.2, 0.6, 1.0, 1),  # Bootstrap blue
            size_hint_y=None,
            height='60dp'
        )
        self.add_widget(title)
        
        # Server URL input section
        url_section = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height='120dp',
            spacing=5
        )
        
        url_label = Label(
            text='Server URL:',
            font_size='16sp',
            size_hint_y=None,
            height='30dp',
            text_size=(None, None),
            halign='left'
        )
        url_section.add_widget(url_label)
        
        self.url_input = TextInput(
            hint_text='http://192.168.1.100:5000',
            text='http://localhost:5000',
            multiline=False,
            size_hint_y=None,
            height='48dp'
        )
        url_section.add_widget(self.url_input)
        
        # Quick connect buttons
        quick_buttons = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height='40dp',
            spacing=10
        )
        
        localhost_btn = Button(
            text='Localhost',
            size_hint_x=0.33
        )
        localhost_btn.bind(on_press=lambda x: setattr(self.url_input, 'text', 'http://localhost:5000'))
        
        wifi_btn = Button(
            text='WiFi (Auto)',
            size_hint_x=0.33
        )
        wifi_btn.bind(on_press=self.detect_wifi_server)
        
        scan_btn = Button(
            text='Scan QR',
            size_hint_x=0.33
        )
        scan_btn.bind(on_press=self.scan_qr_code)
        
        quick_buttons.add_widget(localhost_btn)
        quick_buttons.add_widget(wifi_btn)
        quick_buttons.add_widget(scan_btn)
        url_section.add_widget(quick_buttons)
        
        self.add_widget(url_section)
        
        # Password section
        password_section = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height='100dp',
            spacing=5
        )
        
        password_label = Label(
            text='Password:',
            font_size='16sp',
            size_hint_y=None,
            height='30dp',
            text_size=(None, None),
            halign='left'
        )
        password_section.add_widget(password_label)
        
        self.password_input = TextInput(
            hint_text='Enter server password',
            password=True,
            multiline=False,
            size_hint_y=None,
            height='48dp'
        )
        self.password_input.bind(on_text_validate=self.connect)
        password_section.add_widget(self.password_input)
        
        self.add_widget(password_section)
        
        # Connect button
        connect_btn = Button(
            text='Connect to Server',
            size_hint_y=None,
            height='48dp',
            background_color=(0.2, 0.6, 1.0, 1)  # Bootstrap blue
        )
        connect_btn.bind(on_press=self.connect)
        self.add_widget(connect_btn)
        
        # Connection status
        self.status_label = Label(
            text='Enter server URL and password to connect',
            font_size='14sp',
            color=(0.6, 0.6, 0.6, 1),
            size_hint_y=None,
            height='60dp',
            text_size=(None, None),
            halign='center'
        )
        self.add_widget(self.status_label)
        
        # Server info section
        self.server_info = Label(
            text='Connect to your WiFi File Server to access files remotely',
            font_size='12sp',
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height='40dp',
            text_size=(None, None),
            halign='center'
        )
        self.add_widget(self.server_info)
    
    def detect_wifi_server(self, instance):
        """Auto-detect WiFi server"""
        self.status_label.text = 'Scanning for WiFi servers...'
        # TODO: Implement network scanning
        self.status_label.text = 'Enter server IP manually'
    
    def scan_qr_code(self, instance):
        """Scan QR code for server URL"""
        self.status_label.text = 'QR code scanning not implemented yet'
    
    def connect(self, instance=None):
        """Connect to server with authentication"""
        url = self.url_input.text.strip()
        password = self.password_input.text.strip()
        
        if not url:
            self.status_label.text = 'Please enter server URL'
            return
            
        if not password:
            self.status_label.text = 'Please enter password'
            return
        
        self.status_label.text = 'Connecting...'
        self.app_instance.connect_to_server(url, password)

class FileListItem(BoxLayout):
    """File list item matching web app design with media support"""
    
    def __init__(self, file_info, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.file_info = file_info
        self.app_instance = app_instance
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = '80dp'
        self.padding = 8
        self.spacing = 4
        
        # Main file row
        main_row = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height='48dp'
        )
        
        # File icon (based on type)
        icon_text = self.get_file_icon(file_info['name'])
        icon = Label(
            text=icon_text,
            font_size='20sp',
            size_hint_x=None,
            width='40dp',
            color=self.get_file_color(file_info['name'])
        )
        main_row.add_widget(icon)
        
        # File info section
        info_section = BoxLayout(
            orientation='vertical',
            size_hint_x=0.6
        )
        
        # File name
        name_label = Label(
            text=file_info['name'],
            font_size='14sp',
            text_size=(None, None),
            halign='left',
            valign='center',
            size_hint_y=0.7
        )
        
        # File size and date
        size_date = f"{file_info.get('size', 'Unknown')} • {file_info.get('modified', '')}"
        details_label = Label(
            text=size_date,
            font_size='10sp',
            color=(0.6, 0.6, 0.6, 1),
            text_size=(None, None),
            halign='left',
            valign='center',
            size_hint_y=0.3
        )
        
        info_section.add_widget(name_label)
        info_section.add_widget(details_label)
        main_row.add_widget(info_section)
        
        # Action buttons
        action_buttons = BoxLayout(
            orientation='horizontal',
            size_hint_x=0.4,
            spacing=5
        )
        
        # View/Play button
        if self.is_media_file(file_info['name']):
            view_btn = Button(
                text='Play',
                size_hint_x=0.5,
                background_color=(0.2, 0.8, 0.2, 1)  # Green for media
            )
            view_btn.bind(on_press=self.play_media)
        else:
            view_btn = Button(
                text='View',
                size_hint_x=0.5,
                background_color=(0.2, 0.6, 1.0, 1)  # Blue for documents
            )
            view_btn.bind(on_press=self.view_file)
        
        # Download button
        download_btn = Button(
            text='↓',
            size_hint_x=0.25,
            background_color=(0.6, 0.6, 0.6, 1)
        )
        download_btn.bind(on_press=self.download_file)
        
        # Delete button
        delete_btn = Button(
            text='×',
            size_hint_x=0.25,
            background_color=(1, 0.4, 0.4, 1)
        )
        delete_btn.bind(on_press=self.delete_file)
        
        action_buttons.add_widget(view_btn)
        action_buttons.add_widget(download_btn)
        action_buttons.add_widget(delete_btn)
        main_row.add_widget(action_buttons)
        
        self.add_widget(main_row)
        
        # Media controls (hidden by default)
        self.media_controls = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height='0dp',
            spacing=5
        )
        self.add_widget(self.media_controls)
    
    def get_file_icon(self, filename):
        """Get icon based on file type"""
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        
        icons = {
            'mp4': '▶', 'avi': '▶', 'mov': '▶', 'wmv': '▶', 'mkv': '▶', 'webm': '▶',
            'mp3': '♪', 'wav': '♪', 'flac': '♪', 'aac': '♪', 'ogg': '♪',
            'jpg': '🖼', 'jpeg': '🖼', 'png': '🖼', 'gif': '🖼', 'svg': '🖼',
            'pdf': '📄', 'doc': '📄', 'docx': '📄', 'txt': '📄',
            'zip': '📦', 'rar': '📦', '7z': '📦', 'tar': '📦',
            'html': '🌐', 'css': '🎨', 'js': '⚡', 'json': '{ }',
        }
        return icons.get(ext, '📄')
    
    def get_file_color(self, filename):
        """Get color based on file type"""
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        
        if ext in ['mp4', 'avi', 'mov', 'wmv', 'mkv', 'webm']:
            return (1, 0.3, 0.3, 1)  # Red for video
        elif ext in ['mp3', 'wav', 'flac', 'aac', 'ogg']:
            return (0.3, 1, 0.3, 1)  # Green for audio
        elif ext in ['jpg', 'jpeg', 'png', 'gif', 'svg']:
            return (1, 0.8, 0.3, 1)  # Orange for images
        else:
            return (0.4, 0.4, 0.4, 1)  # Gray for documents
    
    def is_media_file(self, filename):
        """Check if file is playable media"""
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        return ext in ['mp4', 'avi', 'mov', 'wmv', 'mkv', 'webm', 'mp3', 'wav', 'flac', 'aac', 'ogg']
    
    def play_media(self, instance):
        """Play media file with built-in player"""
        self.app_instance.play_media_file(self.file_info)
    
    def view_file(self, instance):
        """View file content"""
        self.app_instance.view_file(self.file_info)
    
    def download_file(self, instance):
        """Download file to device"""
        self.app_instance.download_file(self.file_info)
    
    def delete_file(self, instance):
        """Delete file with confirmation"""
        self.app_instance.confirm_delete(self.file_info)



class FileManagerScreen(BoxLayout):
    """Main file management screen - matches web app interface"""
    
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app_instance = app_instance
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        
        # Header bar matching web app
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height='60dp',
            spacing=10
        )
        
        # Server info
        server_info = BoxLayout(
            orientation='vertical',
            size_hint_x=0.6
        )
        
        title = Label(
            text='WiFi File Server',
            font_size='18sp',
            bold=True,
            color=(0.2, 0.6, 1.0, 1),
            size_hint_y=0.6,
            text_size=(None, None),
            halign='left'
        )
        
        self.connection_status = Label(
            text=f'Connected to: {self.app_instance.server_url}',
            font_size='12sp',
            color=(0.6, 0.6, 0.6, 1),
            size_hint_y=0.4,
            text_size=(None, None),
            halign='left'
        )
        
        server_info.add_widget(title)
        server_info.add_widget(self.connection_status)
        header.add_widget(server_info)
        
        # Action buttons
        action_buttons = BoxLayout(
            orientation='horizontal',
            size_hint_x=0.4,
            spacing=5
        )
        
        upload_btn = Button(
            text='Upload',
            background_color=(0.2, 0.8, 0.2, 1)
        )
        upload_btn.bind(on_press=self.upload_file)
        
        refresh_btn = Button(
            text='Refresh',
            background_color=(0.2, 0.6, 1.0, 1)
        )
        refresh_btn.bind(on_press=self.refresh_files)
        
        disconnect_btn = Button(
            text='Disconnect',
            background_color=(1, 0.4, 0.4, 1)
        )
        disconnect_btn.bind(on_press=self.disconnect)
        
        action_buttons.add_widget(upload_btn)
        action_buttons.add_widget(refresh_btn)
        action_buttons.add_widget(disconnect_btn)
        header.add_widget(action_buttons)
        
        self.add_widget(header)
        
        # File list with scroll
        self.file_scroll = ScrollView()
        self.file_list = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=1
        )
        self.file_list.bind(minimum_height=self.file_list.setter('height'))
        self.file_scroll.add_widget(self.file_list)
        self.add_widget(self.file_scroll)
        
        # Status bar matching web app
        status_bar = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height='40dp',
            padding=10
        )
        
        self.status_label = Label(
            text='Loading files...',
            font_size='12sp',
            color=(0.6, 0.6, 0.6, 1),
            size_hint_x=0.7,
            text_size=(None, None),
            halign='left'
        )
        
        self.file_count = Label(
            text='',
            font_size='12sp',
            color=(0.6, 0.6, 0.6, 1),
            size_hint_x=0.3,
            text_size=(None, None),
            halign='right'
        )
        
        status_bar.add_widget(self.status_label)
        status_bar.add_widget(self.file_count)
        self.add_widget(status_bar)
        
        # Load files
        self.refresh_files()
    
    def upload_file(self, instance):
        """Upload file to server"""
        if PLYER_AVAILABLE and filechooser:
            try:
                filechooser.open_file(
                    on_selection=self.handle_file_selection,
                    title="Select file to upload"
                )
            except Exception as e:
                self.show_popup("Error", f"File chooser error: {str(e)}")
        else:
            self.show_file_chooser()
    
    def show_file_chooser(self):
        """Fallback file chooser"""
        content = BoxLayout(orientation='vertical')
        
        filechooser_widget = FileChooserListView()
        content.add_widget(filechooser_widget)
        
        buttons = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height='48dp'
        )
        
        select_btn = Button(text='Select')
        cancel_btn = Button(text='Cancel')
        
        buttons.add_widget(select_btn)
        buttons.add_widget(cancel_btn)
        content.add_widget(buttons)
        
        popup = Popup(
            title='Choose File',
            content=content,
            size_hint=(0.9, 0.9)
        )
        
        def select_file(instance):
            if filechooser_widget.selection:
                self.handle_file_selection([filechooser_widget.selection[0]])
            popup.dismiss()
        
        def cancel(instance):
            popup.dismiss()
        
        select_btn.bind(on_press=select_file)
        cancel_btn.bind(on_press=cancel)
        
        popup.open()
    
    def handle_file_selection(self, selection):
        """Handle selected file for upload"""
        if selection:
            file_path = selection[0]
            self.app_instance.upload_file_to_server(file_path)
    
    def refresh_files(self, instance=None):
        """Refresh file list from server"""
        self.status_label.text = 'Loading files...'
        self.app_instance.load_files_from_server()
    
    def update_file_list(self, files):
        """Update UI with file list from server"""
        self.file_list.clear_widgets()
        
        if not files:
            no_files = Label(
                text='No files on server',
                size_hint_y=None,
                height='60dp',
                color=(0.7, 0.7, 0.7, 1),
                font_size='14sp'
            )
            self.file_list.add_widget(no_files)
            self.status_label.text = 'No files found'
            self.file_count.text = ''
        else:
            for file_info in files:
                file_item = FileListItem(file_info, self.app_instance)
                self.file_list.add_widget(file_item)
            
            self.status_label.text = 'Files loaded successfully'
            self.file_count.text = f'{len(files)} files'
    
    def disconnect(self, instance):
        """Disconnect from server"""
        self.app_instance.disconnect_from_server()
    
    def show_popup(self, title, message):
        """Show popup message"""
        popup = Popup(
            title=title,
            content=Label(text=message),
            size_hint=(0.8, 0.4)
        )
        popup.open()

class MediaPlayerScreen(BoxLayout):
    """Built-in media player matching web app functionality"""
    
    def __init__(self, app_instance, file_info, **kwargs):
        super().__init__(**kwargs)
        self.app_instance = app_instance
        self.file_info = file_info
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        
        # Header
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height='50dp'
        )
        
        back_btn = Button(
            text='← Back',
            size_hint_x=None,
            width='100dp',
            background_color=(0.6, 0.6, 0.6, 1)
        )
        back_btn.bind(on_press=self.go_back)
        
        title = Label(
            text=file_info['name'],
            font_size='16sp',
            bold=True
        )
        
        header.add_widget(back_btn)
        header.add_widget(title)
        self.add_widget(header)
        
        # Media player area
        if self.is_video_file(file_info['name']):
            self.create_video_player()
        elif self.is_audio_file(file_info['name']):
            self.create_audio_player()
        else:
            self.create_image_viewer()
    
    def is_video_file(self, filename):
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        return ext in ['mp4', 'avi', 'mov', 'wmv', 'mkv', 'webm']
    
    def is_audio_file(self, filename):
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        return ext in ['mp3', 'wav', 'flac', 'aac', 'ogg']
    
    def create_video_player(self):
        """Create video player"""
        media_url = f"{self.app_instance.server_url}/download/{quote(self.file_info['name'])}"
        
        self.video = Video(
            source=media_url,
            state='stop',
            options={'allow_stretch': True}
        )
        self.add_widget(self.video)
        
        # Video controls
        controls = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height='60dp',
            spacing=10
        )
        
        play_btn = Button(text='Play', size_hint_x=0.2)
        play_btn.bind(on_press=self.toggle_play)
        
        self.progress = Slider(min=0, max=100, value=0, size_hint_x=0.6)
        
        volume = Slider(min=0, max=1, value=0.8, size_hint_x=0.2)
        volume.bind(value=self.set_volume)
        
        controls.add_widget(play_btn)
        controls.add_widget(self.progress)
        controls.add_widget(volume)
        self.add_widget(controls)
        
        self.play_button = play_btn
    
    def create_audio_player(self):
        """Create audio player"""
        # Audio visualization placeholder
        audio_display = BoxLayout(
            orientation='vertical',
            size_hint_y=0.7
        )
        
        audio_icon = Label(
            text='♪',
            font_size='100sp',
            color=(0.3, 1, 0.3, 1)
        )
        
        audio_title = Label(
            text=self.file_info['name'],
            font_size='18sp',
            bold=True
        )
        
        audio_display.add_widget(audio_icon)
        audio_display.add_widget(audio_title)
        self.add_widget(audio_display)
        
        # Audio controls
        controls = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height='60dp',
            spacing=10
        )
        
        play_btn = Button(text='Play', size_hint_x=0.2)
        play_btn.bind(on_press=self.play_audio)
        
        self.progress = Slider(min=0, max=100, value=0, size_hint_x=0.6)
        
        volume = Slider(min=0, max=1, value=0.8, size_hint_x=0.2)
        
        controls.add_widget(play_btn)
        controls.add_widget(self.progress)
        controls.add_widget(volume)
        self.add_widget(controls)
    
    def create_image_viewer(self):
        """Create image viewer"""
        image_url = f"{self.app_instance.server_url}/download/{quote(self.file_info['name'])}"
        
        self.image = Image(
            source=image_url,
            allow_stretch=True,
            keep_ratio=True
        )
        self.add_widget(self.image)
    
    def toggle_play(self, instance):
        """Toggle video playback"""
        if hasattr(self, 'video'):
            if self.video.state == 'play':
                self.video.state = 'pause'
                self.play_button.text = 'Play'
            else:
                self.video.state = 'play'
                self.play_button.text = 'Pause'
    
    def play_audio(self, instance):
        """Play audio file"""
        # Use system default audio player
        audio_url = f"{self.app_instance.server_url}/download/{quote(self.file_info['name'])}"
        webbrowser.open(audio_url)
    
    def set_volume(self, instance, value):
        """Set media volume"""
        if hasattr(self, 'video'):
            self.video.volume = value
    
    def go_back(self, instance):
        """Return to file manager"""
        self.app_instance.show_file_manager()

class WiFiFileServerApp(App):
    """Main Kivy application - connects to Flask server"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = 'WiFi File Server'
        self.server_url = None
        self.session = requests.Session()
        self.authenticated = False
        self.files_data = []
    
    def build(self):
        """Build the app interface"""
        # Set window properties for mobile
        if platform == 'android':
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([
                    Permission.READ_EXTERNAL_STORAGE,
                    Permission.WRITE_EXTERNAL_STORAGE,
                    Permission.INTERNET
                ])
            except ImportError:
                pass  # Running in desktop environment
        
        # Create main container
        self.root_widget = BoxLayout()
        
        # Show connection screen
        self.show_connection_screen()
        
        return self.root_widget
    
    def show_connection_screen(self):
        """Show server connection screen"""
        self.root_widget.clear_widgets()
        connection_screen = ServerConnectionScreen(self)
        self.root_widget.add_widget(connection_screen)
    
    def connect_to_server(self, url, password):
        """Connect to Flask server with authentication"""
        self.server_url = url.rstrip('/')
        
        # Thread for connection attempt
        def connect_thread():
            try:
                # Test server connectivity
                response = self.session.get(f"{self.server_url}/", timeout=5)
                if response.status_code != 200:
                    Clock.schedule_once(lambda dt: self.connection_failed("Server not responding"))
                    return
                
                # Attempt login
                login_data = {'password': password}
                response = self.session.post(f"{self.server_url}/login", data=login_data, timeout=5)
                
                if response.status_code == 200 and 'files' in response.url:
                    # Login successful
                    self.authenticated = True
                    Clock.schedule_once(lambda dt: self.connection_success())
                else:
                    Clock.schedule_once(lambda dt: self.connection_failed("Invalid password"))
                    
            except requests.exceptions.RequestException as e:
                Clock.schedule_once(lambda dt: self.connection_failed(f"Connection error: {str(e)}"))
        
        threading.Thread(target=connect_thread, daemon=True).start()
    
    def connection_success(self):
        """Handle successful connection"""
        self.show_file_manager()
    
    def connection_failed(self, error_message):
        """Handle connection failure"""
        # Update connection screen status
        if len(self.root_widget.children) > 0:
            connection_screen = self.root_widget.children[0]
            if hasattr(connection_screen, 'status_label'):
                connection_screen.status_label.text = error_message
    
    def show_file_manager(self):
        """Show file manager screen"""
        self.root_widget.clear_widgets()
        file_manager = FileManagerScreen(self)
        self.root_widget.add_widget(file_manager)
        self.current_file_manager = file_manager
    
    def disconnect_from_server(self):
        """Disconnect from server"""
        self.server_url = None
        self.authenticated = False
        self.session = requests.Session()
        self.show_connection_screen()
    
    def load_files_from_server(self):
        """Load file list from server by scraping the files page"""
        def load_thread():
            try:
                response = self.session.get(f"{self.server_url}/files", timeout=10)
                if response.status_code == 200:
                    import re
                    files_data = []
                    download_pattern = r'href="/download/([^"]*)"'
                    matches = re.findall(download_pattern, response.text)
                    
                    for filename in matches:
                        from urllib.parse import unquote
                        decoded_name = unquote(filename)
                        files_data.append({'name': decoded_name, 'size': 'Unknown', 'modified': ''})
                    
                    Clock.schedule_once(lambda dt: self.files_loaded(files_data))
                else:
                    Clock.schedule_once(lambda dt: self.files_load_failed("Failed to load files"))
            except Exception as e:
                Clock.schedule_once(lambda dt: self.files_load_failed(f"Connection error: {str(e)}"))
        
        threading.Thread(target=load_thread, daemon=True).start()
    
    def files_loaded(self, files_data):
        self.files_data = files_data
        if hasattr(self, 'current_file_manager'):
            self.current_file_manager.update_file_list(files_data)
    
    def files_load_failed(self, error_message):
        if hasattr(self, 'current_file_manager'):
            self.current_file_manager.status_label.text = error_message
    
    def upload_file_to_server(self, file_path):
        def upload_thread():
            try:
                filename = os.path.basename(file_path)
                Clock.schedule_once(lambda dt: self.update_upload_status(f"Uploading {filename}..."))
                
                with open(file_path, 'rb') as f:
                    files = {'file': (filename, f)}
                    response = self.session.post(f"{self.server_url}/upload", files=files, timeout=30)
                
                if response.status_code == 200:
                    Clock.schedule_once(lambda dt: self.upload_success(filename))
                else:
                    Clock.schedule_once(lambda dt: self.upload_failed("Upload failed"))
            except Exception as e:
                Clock.schedule_once(lambda dt: self.upload_failed(f"Upload error: {str(e)}"))
        
        threading.Thread(target=upload_thread, daemon=True).start()
    
    def update_upload_status(self, message):
        if hasattr(self, 'current_file_manager'):
            self.current_file_manager.status_label.text = message
    
    def upload_success(self, filename):
        if hasattr(self, 'current_file_manager'):
            self.current_file_manager.status_label.text = f"Uploaded: {filename}"
            self.current_file_manager.refresh_files()
        if PLYER_AVAILABLE and notification:
            notification.notify(title='Upload Complete', message=f'Uploaded: {filename}', timeout=3)
    
    def upload_failed(self, error_message):
        if hasattr(self, 'current_file_manager'):
            self.current_file_manager.status_label.text = error_message
    
    def download_file(self, file_info):
        def download_thread():
            try:
                filename = file_info['name']
                Clock.schedule_once(lambda dt: self.update_download_status(f"Downloading {filename}..."))
                
                response = self.session.get(f"{self.server_url}/download/{quote(filename)}", stream=True, timeout=30)
                
                if response.status_code == 200:
                    downloads_dir = '/storage/emulated/0/Download' if platform == 'android' else os.path.expanduser('~/Downloads')
                    if not os.path.exists(downloads_dir):
                        downloads_dir = os.path.expanduser('~')
                    
                    save_path = os.path.join(downloads_dir, filename)
                    with open(save_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    Clock.schedule_once(lambda dt: self.download_success(filename))
                else:
                    Clock.schedule_once(lambda dt: self.download_failed("Download failed"))
            except Exception as e:
                Clock.schedule_once(lambda dt: self.download_failed(f"Download error: {str(e)}"))
        
        threading.Thread(target=download_thread, daemon=True).start()
    
    def update_download_status(self, message):
        if hasattr(self, 'current_file_manager'):
            self.current_file_manager.status_label.text = message
    
    def download_success(self, filename):
        if hasattr(self, 'current_file_manager'):
            self.current_file_manager.status_label.text = f"Downloaded: {filename}"
        if PLYER_AVAILABLE and notification:
            notification.notify(title='Download Complete', message=f'Saved: {filename}', timeout=3)
    
    def download_failed(self, error_message):
        if hasattr(self, 'current_file_manager'):
            self.current_file_manager.status_label.text = error_message
    
    def play_media_file(self, file_info):
        self.root_widget.clear_widgets()
        media_player = MediaPlayerScreen(self, file_info)
        self.root_widget.add_widget(media_player)
    
    def view_file(self, file_info):
        file_url = f"{self.server_url}/download/{quote(file_info['name'])}"
        try:
            webbrowser.open(file_url)
        except Exception:
            self.play_media_file(file_info)
    
    def confirm_delete(self, file_info):
        content = BoxLayout(orientation='vertical', spacing=10)
        message = Label(text=f'Delete "{file_info["name"]}" from server?')
        content.add_widget(message)
        
        buttons = BoxLayout(orientation='horizontal', size_hint_y=None, height='48dp')
        delete_btn = Button(text='Delete', background_color=(1, 0.5, 0.5, 1))
        cancel_btn = Button(text='Cancel')
        buttons.add_widget(delete_btn)
        buttons.add_widget(cancel_btn)
        content.add_widget(buttons)
        
        popup = Popup(title='Confirm Delete', content=content, size_hint=(0.8, 0.4))
        
        def delete_file(instance):
            self.delete_file_from_server(file_info)
            popup.dismiss()
        
        def cancel(instance):
            popup.dismiss()
        
        delete_btn.bind(on_press=delete_file)
        cancel_btn.bind(on_press=cancel)
        popup.open()
    
    def delete_file_from_server(self, file_info):
        def delete_thread():
            try:
                filename = file_info['name']
                response = self.session.post(f"{self.server_url}/delete/{quote(filename)}", timeout=10)
                
                if response.status_code == 200:
                    Clock.schedule_once(lambda dt: self.delete_success(filename))
                else:
                    Clock.schedule_once(lambda dt: self.delete_failed("Delete failed"))
            except Exception as e:
                Clock.schedule_once(lambda dt: self.delete_failed(f"Delete error: {str(e)}"))
        
        threading.Thread(target=delete_thread, daemon=True).start()
    
    def delete_success(self, filename):
        if hasattr(self, 'current_file_manager'):
            self.current_file_manager.status_label.text = f"Deleted: {filename}"
            self.current_file_manager.refresh_files()
    
    def delete_failed(self, error_message):
        if hasattr(self, 'current_file_manager'):
            self.current_file_manager.status_label.text = error_message
    


if __name__ == '__main__':
    app = WiFiFileServerApp()
    app.run()