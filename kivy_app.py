"""
Kivy Mobile File Server App
Converts the Flask web app to a native mobile application
"""

import os
import hashlib
import threading
import time
from datetime import datetime
from pathlib import Path

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
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import platform

# Try to import platform-specific modules
try:
    from plyer import filechooser, notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False
    filechooser = None
    notification = None

class LoginScreen(BoxLayout):
    """Login screen for password authentication"""
    
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app_instance = app_instance
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 20
        
        # Title
        title = Label(
            text='WiFi File Server',
            font_size='24sp',
            size_hint_y=None,
            height='80dp'
        )
        self.add_widget(title)
        
        # Server info
        self.server_info = Label(
            text='Enter password to access files',
            font_size='16sp',
            size_hint_y=None,
            height='40dp'
        )
        self.add_widget(self.server_info)
        
        # Password input
        self.password_input = TextInput(
            hint_text='Enter password',
            password=True,
            multiline=False,
            size_hint_y=None,
            height='48dp'
        )
        self.password_input.bind(on_text_validate=self.login)
        self.add_widget(self.password_input)
        
        # Login button
        login_btn = Button(
            text='Login',
            size_hint_y=None,
            height='48dp'
        )
        login_btn.bind(on_press=self.login)
        self.add_widget(login_btn)
        
        # Status label
        self.status_label = Label(
            text='',
            color=(1, 0, 0, 1),
            size_hint_y=None,
            height='40dp'
        )
        self.add_widget(self.status_label)
    
    def login(self, instance=None):
        """Handle login attempt"""
        password = self.password_input.text.strip()
        if self.app_instance.authenticate(password):
            self.app_instance.show_file_manager()
        else:
            self.status_label.text = 'Invalid password'
            self.password_input.text = ''

class FileListItem(BoxLayout):
    """Custom widget for file list items"""
    
    def __init__(self, filename, file_path, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.filename = filename
        self.file_path = file_path
        self.app_instance = app_instance
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = '48dp'
        self.padding = 5
        
        # File name label
        name_label = Label(
            text=filename,
            text_size=(None, None),
            halign='left',
            size_hint_x=0.7
        )
        self.add_widget(name_label)
        
        # Download button
        download_btn = Button(
            text='Download',
            size_hint_x=0.15,
            size_hint_y=1
        )
        download_btn.bind(on_press=self.download_file)
        self.add_widget(download_btn)
        
        # Delete button
        delete_btn = Button(
            text='Delete',
            size_hint_x=0.15,
            size_hint_y=1,
            background_color=(1, 0.5, 0.5, 1)
        )
        delete_btn.bind(on_press=self.delete_file)
        self.add_widget(delete_btn)
    
    def download_file(self, instance):
        """Download/open file"""
        self.app_instance.download_file(self.file_path)
    
    def delete_file(self, instance):
        """Delete file with confirmation"""
        self.app_instance.confirm_delete(self.file_path, self.filename)

class FileManagerScreen(BoxLayout):
    """Main file management screen"""
    
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app_instance = app_instance
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        
        # Header
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height='48dp',
            spacing=10
        )
        
        # Title
        title = Label(
            text='File Manager',
            font_size='20sp',
            size_hint_x=0.6
        )
        header.add_widget(title)
        
        # Upload button
        upload_btn = Button(
            text='Upload',
            size_hint_x=0.2
        )
        upload_btn.bind(on_press=self.upload_file)
        header.add_widget(upload_btn)
        
        # Refresh button
        refresh_btn = Button(
            text='Refresh',
            size_hint_x=0.2
        )
        refresh_btn.bind(on_press=self.refresh_files)
        header.add_widget(refresh_btn)
        
        self.add_widget(header)
        
        # File list
        self.file_scroll = ScrollView()
        self.file_list = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=2
        )
        self.file_list.bind(minimum_height=self.file_list.setter('height'))
        self.file_scroll.add_widget(self.file_list)
        self.add_widget(self.file_scroll)
        
        # Status bar
        self.status_bar = Label(
            text='Ready',
            size_hint_y=None,
            height='30dp',
            color=(0.7, 0.7, 0.7, 1)
        )
        self.add_widget(self.status_bar)
        
        # Load files
        self.refresh_files()
    
    def upload_file(self, instance):
        """Open file chooser for upload"""
        if PLYER_AVAILABLE and filechooser:
            try:
                filechooser.open_file(
                    on_selection=self.handle_file_selection,
                    title="Select file to upload"
                )
            except Exception as e:
                self.show_popup("Error", f"File chooser error: {str(e)}")
        else:
            # Fallback file chooser
            self.show_file_chooser()
    
    def show_file_chooser(self):
        """Show Kivy's built-in file chooser"""
        content = BoxLayout(orientation='vertical')
        
        # File chooser
        filechooser = FileChooserListView()
        content.add_widget(filechooser)
        
        # Buttons
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
        
        # Create popup
        popup = Popup(
            title='Choose File',
            content=content,
            size_hint=(0.9, 0.9)
        )
        
        def select_file(instance):
            if filechooser.selection:
                self.handle_file_selection([filechooser.selection[0]])
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
            self.app_instance.upload_file(file_path)
    
    def refresh_files(self, instance=None):
        """Refresh file list"""
        self.file_list.clear_widgets()
        
        upload_dir = self.app_instance.upload_folder
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir, exist_ok=True)
            return
        
        files = []
        for filename in os.listdir(upload_dir):
            file_path = os.path.join(upload_dir, filename)
            if os.path.isfile(file_path):
                files.append((filename, file_path))
        
        files.sort(key=lambda x: x[0].lower())
        
        if not files:
            no_files = Label(
                text='No files uploaded yet',
                size_hint_y=None,
                height='48dp',
                color=(0.7, 0.7, 0.7, 1)
            )
            self.file_list.add_widget(no_files)
        else:
            for filename, file_path in files:
                file_item = FileListItem(filename, file_path, self.app_instance)
                self.file_list.add_widget(file_item)
        
        self.status_bar.text = f'{len(files)} files'
    
    def show_popup(self, title, message):
        """Show popup message"""
        popup = Popup(
            title=title,
            content=Label(text=message),
            size_hint=(0.8, 0.4)
        )
        popup.open()

class WiFiFileServerApp(App):
    """Main Kivy application"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = 'WiFi File Server'
        self.upload_folder = 'mobile_uploads'
        self.password_hash = None
        self.authenticated = False
        
        # Create upload directory
        os.makedirs(self.upload_folder, exist_ok=True)
        
        # Generate password if not exists
        self.setup_password()
    
    def build(self):
        """Build the app interface"""
        # Set window properties for mobile
        if platform == 'android':
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([
                    Permission.READ_EXTERNAL_STORAGE,
                    Permission.WRITE_EXTERNAL_STORAGE,
                    Permission.CAMERA
                ])
            except ImportError:
                pass  # Running in desktop environment
        
        # Create main container
        self.root_widget = BoxLayout()
        
        # Show login screen
        self.show_login()
        
        return self.root_widget
    
    def setup_password(self):
        """Setup or load password"""
        password_file = os.path.join(self.upload_folder, '.password')
        
        if os.path.exists(password_file):
            # Load existing password hash
            with open(password_file, 'r') as f:
                self.password_hash = f.read().strip()
        else:
            # Generate new password
            import secrets
            import string
            password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
            self.password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            # Save password hash
            with open(password_file, 'w') as f:
                f.write(self.password_hash)
            
            # Show password to user
            if PLYER_AVAILABLE and notification:
                notification.notify(
                    title='File Server Password',
                    message=f'Your password is: {password}',
                    timeout=10
                )
            
            print(f"Generated password: {password}")
    
    def authenticate(self, password):
        """Authenticate user with password"""
        input_hash = hashlib.sha256(password.encode()).hexdigest()
        self.authenticated = input_hash == self.password_hash
        return self.authenticated
    
    def show_login(self):
        """Show login screen"""
        self.root_widget.clear_widgets()
        login_screen = LoginScreen(self)
        self.root_widget.add_widget(login_screen)
    
    def show_file_manager(self):
        """Show file manager screen"""
        if self.authenticated:
            self.root_widget.clear_widgets()
            file_manager = FileManagerScreen(self)
            self.root_widget.add_widget(file_manager)
    
    def upload_file(self, source_path):
        """Upload file to app directory"""
        try:
            filename = os.path.basename(source_path)
            dest_path = os.path.join(self.upload_folder, filename)
            
            # Copy file
            import shutil
            shutil.copy2(source_path, dest_path)
            
            # Show success
            if PLYER_AVAILABLE and notification:
                notification.notify(
                    title='Upload Complete',
                    message=f'Uploaded: {filename}',
                    timeout=3
                )
            
            # Refresh file list
            file_manager = self.root_widget.children[0]
            if hasattr(file_manager, 'refresh_files'):
                file_manager.refresh_files()
                
        except Exception as e:
            self.show_error(f"Upload failed: {str(e)}")
    
    def download_file(self, file_path):
        """Download/open file"""
        try:
            if platform == 'android':
                # On Android, try to open with system app
                try:
                    from jnius import autoclass
                    Intent = autoclass('android.content.Intent')
                    Uri = autoclass('android.net.Uri')
                    File = autoclass('java.io.File')
                    
                    intent = Intent(Intent.ACTION_VIEW)
                    file_uri = Uri.fromFile(File(file_path))
                    intent.setData(file_uri)
                    
                    from android import mActivity
                    mActivity.startActivity(intent)
                except ImportError:
                    self.show_error("Android modules not available")
            else:
                # On desktop, open file with default application
                import subprocess
                import sys
                
                if sys.platform.startswith('darwin'):  # macOS
                    subprocess.call(['open', file_path])
                elif sys.platform.startswith('linux'):  # Linux
                    subprocess.call(['xdg-open', file_path])
                elif sys.platform.startswith('win'):  # Windows
                    import os
                    os.startfile(file_path)
                    
        except Exception as e:
            self.show_error(f"Cannot open file: {str(e)}")
    
    def confirm_delete(self, file_path, filename):
        """Show delete confirmation"""
        content = BoxLayout(orientation='vertical', spacing=10)
        
        message = Label(text=f'Delete "{filename}"?')
        content.add_widget(message)
        
        buttons = BoxLayout(orientation='horizontal', size_hint_y=None, height='48dp')
        
        delete_btn = Button(text='Delete', background_color=(1, 0.5, 0.5, 1))
        cancel_btn = Button(text='Cancel')
        
        buttons.add_widget(delete_btn)
        buttons.add_widget(cancel_btn)
        content.add_widget(buttons)
        
        popup = Popup(
            title='Confirm Delete',
            content=content,
            size_hint=(0.8, 0.4)
        )
        
        def delete_file(instance):
            try:
                os.remove(file_path)
                # Refresh file list
                file_manager = self.root_widget.children[0]
                if hasattr(file_manager, 'refresh_files'):
                    file_manager.refresh_files()
                popup.dismiss()
            except Exception as e:
                self.show_error(f"Delete failed: {str(e)}")
        
        def cancel(instance):
            popup.dismiss()
        
        delete_btn.bind(on_press=delete_file)
        cancel_btn.bind(on_press=cancel)
        
        popup.open()
    
    def show_error(self, message):
        """Show error popup"""
        popup = Popup(
            title='Error',
            content=Label(text=message),
            size_hint=(0.8, 0.4)
        )
        popup.open()

if __name__ == '__main__':
    app = WiFiFileServerApp()
    app.run()