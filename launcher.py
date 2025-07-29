"""
Enhanced launcher for the File Server application
Provides GUI startup and better user experience
"""
import os
import sys
import threading
import time
import webbrowser
from tkinter import *
from tkinter import ttk, messagebox
import subprocess

class FileServerLauncher:
    def __init__(self):
        self.root = Tk()
        self.root.title("WiFi File Server")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Center the window
        self.center_window()
        
        # Server process
        self.server_process = None
        self.server_running = False
        
        self.create_gui()
        
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (300 // 2)
        self.root.geometry(f"400x300+{x}+{y}")
    
    def create_gui(self):
        """Create the GUI interface"""
        # Title
        title_frame = Frame(self.root, bg="#0d6efd", height=60)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)
        
        title_label = Label(title_frame, text="WiFi File Server", 
                           font=("Arial", 16, "bold"), 
                           fg="white", bg="#0d6efd")
        title_label.pack(expand=True)
        
        # Main content
        main_frame = Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Status
        self.status_label = Label(main_frame, text="Server Status: Stopped", 
                                 font=("Arial", 10))
        self.status_label.pack(pady=10)
        
        # URL display
        self.url_frame = Frame(main_frame)
        self.url_frame.pack(pady=10, fill="x")
        
        Label(self.url_frame, text="Server URL:", font=("Arial", 9)).pack(anchor="w")
        self.url_var = StringVar(value="Not running")
        self.url_entry = Entry(self.url_frame, textvariable=self.url_var, 
                              state="readonly", font=("Arial", 9))
        self.url_entry.pack(fill="x", pady=2)
        
        # Password display
        Label(self.url_frame, text="Password:", font=("Arial", 9)).pack(anchor="w", pady=(10,0))
        self.password_var = StringVar(value="Not running")
        self.password_entry = Entry(self.url_frame, textvariable=self.password_var, 
                                   state="readonly", font=("Arial", 9))
        self.password_entry.pack(fill="x", pady=2)
        
        # Buttons
        button_frame = Frame(main_frame)
        button_frame.pack(pady=20)
        
        self.start_button = Button(button_frame, text="Start Server", 
                                  command=self.start_server, 
                                  bg="#28a745", fg="white", 
                                  font=("Arial", 10, "bold"),
                                  padx=20, pady=5)
        self.start_button.pack(side="left", padx=5)
        
        self.stop_button = Button(button_frame, text="Stop Server", 
                                 command=self.stop_server, 
                                 bg="#dc3545", fg="white", 
                                 font=("Arial", 10, "bold"),
                                 padx=20, pady=5, state="disabled")
        self.stop_button.pack(side="left", padx=5)
        
        self.browser_button = Button(button_frame, text="Open Browser", 
                                    command=self.open_browser, 
                                    bg="#007bff", fg="white", 
                                    font=("Arial", 10, "bold"),
                                    padx=20, pady=5, state="disabled")
        self.browser_button.pack(side="left", padx=5)
        
        # Info text
        info_text = Text(main_frame, height=4, font=("Arial", 8), 
                        wrap="word", state="disabled")
        info_text.pack(fill="x", pady=10)
        
        info_content = """Share files over WiFi with any device on your network.
Other devices can access files by visiting the URL above.
The server runs locally - no internet connection required."""
        
        info_text.config(state="normal")
        info_text.insert("1.0", info_content)
        info_text.config(state="disabled")
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def start_server(self):
        """Start the Flask server"""
        try:
            # Import and start the server
            def run_server():
                try:
                    from app import app, SERVER_URL, SERVER_PASSWORD
                    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
                except Exception as e:
                    messagebox.showerror("Server Error", f"Failed to start server: {e}")
            
            # Start server in separate thread
            server_thread = threading.Thread(target=run_server, daemon=True)
            server_thread.start()
            
            self.server_running = True
            self.update_gui_state()
            
            # Get server info after a short delay
            self.root.after(1000, self.update_server_info)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start server: {e}")
    
    def stop_server(self):
        """Stop the Flask server"""
        self.server_running = False
        self.update_gui_state()
        messagebox.showinfo("Server Stopped", "Server has been stopped")
    
    def open_browser(self):
        """Open the server in default browser"""
        if self.server_running and self.url_var.get() != "Not running":
            webbrowser.open(self.url_var.get())
    
    def update_server_info(self):
        """Update server URL and password display"""
        try:
            from app import SERVER_URL, SERVER_PASSWORD
            self.url_var.set(SERVER_URL or "Starting...")
            self.password_var.set(SERVER_PASSWORD or "Generating...")
            
            # Auto-open browser
            if SERVER_URL and self.server_running:
                self.root.after(1000, lambda: webbrowser.open(SERVER_URL))
        except:
            pass
    
    def update_gui_state(self):
        """Update GUI based on server state"""
        if self.server_running:
            self.status_label.config(text="Server Status: Running", fg="green")
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            self.browser_button.config(state="normal")
        else:
            self.status_label.config(text="Server Status: Stopped", fg="red")
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
            self.browser_button.config(state="disabled")
            self.url_var.set("Not running")
            self.password_var.set("Not running")
    
    def on_closing(self):
        """Handle window close event"""
        if self.server_running:
            if messagebox.askokcancel("Quit", "Server is running. Do you want to stop it and quit?"):
                self.stop_server()
                self.root.destroy()
        else:
            self.root.destroy()
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

if __name__ == "__main__":
    try:
        launcher = FileServerLauncher()
        launcher.run()
    except Exception as e:
        print(f"Failed to start launcher: {e}")
        # Fallback to command line
        import main