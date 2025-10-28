"""
P2P Client GUI - Clean Light Theme  
White background with blue accents
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import time
import socket
import sys
import os
import random
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from client import Client


# Light Theme
class Theme:
    WHITE = '#ffffff'
    LIGHT_BG = '#f5f7fa'
    BLUE = '#4a90e2'
    BLUE_HOVER = '#357abd'
    BLUE_LIGHT = '#e8f4fd'
    GREEN = '#52c41a'
    RED = '#ff4d4f'
    ORANGE = '#faad14'
    TEXT = '#2c3e50'
    TEXT_GRAY = '#8c8c8c'
    BORDER = '#e0e0e0'


class ClientGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("P2P Client")
        self.root.geometry("1100x800")
        self.root.configure(bg=Theme.LIGHT_BG)
        
        self.client = None
        self.connected = False
        self.client_name = f"Client_{random.randint(1000, 9999)}"
        self.port = random.randint(5001, 5100)  # Random port to avoid conflicts
        self.published_files = set()  # Track published files
        
        self._create_ui()
        self._start_connection_monitor()
    
    def _start_connection_monitor(self):
        """Monitor connection status and detect server disconnection"""
        def monitor():
            while True:
                if self.connected and self.client:
                    try:
                        # Check if server is still reachable by testing socket
                        if not self._is_socket_alive():
                            # Server disconnected
                            self.root.after(0, self._handle_server_disconnect)
                    except:
                        pass
                time.sleep(3)  # Check every 3 seconds
        
        threading.Thread(target=monitor, daemon=True).start()
    
    def _is_socket_alive(self):
        """Check if server connection is still alive"""
        try:
            if not self.client.server_socket:
                return False
            
            # Try to send a minimal ping to check if socket is alive
            # Use MSG_PEEK to check without removing data from queue
            self.client.server_socket.setblocking(False)
            try:
                # Try to receive with peek - if socket is closed, this will raise error
                self.client.server_socket.recv(1, socket.MSG_PEEK)
                return True
            except BlockingIOError:
                # No data available but socket is alive
                return True
            except:
                # Socket is dead
                return False
            finally:
                self.client.server_socket.setblocking(True)
        except:
            return False
    
    def _handle_server_disconnect(self):
        """Handle server disconnection"""
        if not self.connected:
            return
        
        self.connected = False
        self.status_dot.config(fg=Theme.RED)
        self.conn_btn.config(text="Connect", bg=Theme.GREEN,
                            activebackground='#45a017')
        
        # Clean up client connection
        if self.client:
            try:
                self.client.disconnect()
            except:
                pass
        
        self.log("⚠️ Server disconnected - Connection lost", 'ERROR')
        messagebox.showwarning("Connection Lost", 
                              "Server has gone offline!\nYou have been disconnected.\n\n"
                              "Click 'Connect' to reconnect when server is back online.")
    
    def _create_ui(self):
        # Header
        header = tk.Frame(self.root, bg=Theme.WHITE, height=110)
        header.pack(fill='x', pady=(0, 20))
        header.pack_propagate(False)
        
        # Title
        title_frame = tk.Frame(header, bg=Theme.WHITE)
        title_frame.pack(side='left', padx=40, pady=25)
        
        tk.Label(title_frame, text="📁 P2P File Sharing Client",
                font=('Segoe UI', 22, 'bold'),
                fg=Theme.TEXT, bg=Theme.WHITE).pack(anchor='w')
        
        tk.Label(title_frame, text="Share and download files from the network",
                font=('Segoe UI', 10),
                fg=Theme.TEXT_GRAY, bg=Theme.WHITE).pack(anchor='w', pady=(5, 0))
        
        # Connection panel
        conn_panel = tk.Frame(header, bg=Theme.BLUE_LIGHT, relief='flat')
        conn_panel.pack(side='right', padx=40, pady=20)
        
        inner = tk.Frame(conn_panel, bg=Theme.BLUE_LIGHT)
        inner.pack(padx=15, pady=12)
        
        tk.Label(inner, text="Name:", font=('Segoe UI', 9),
                fg=Theme.TEXT, bg=Theme.BLUE_LIGHT).grid(row=0, column=0, padx=8, pady=5)
        
        self.name_entry = tk.Entry(inner, font=('Segoe UI', 10),
                                   bg=Theme.WHITE, fg=Theme.TEXT,
                                   relief='flat', bd=5, width=14)
        self.name_entry.insert(0, self.client_name)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(inner, text="Port:", font=('Segoe UI', 9),
                fg=Theme.TEXT, bg=Theme.BLUE_LIGHT).grid(row=0, column=2, padx=8, pady=5)
        
        self.port_entry = tk.Entry(inner, font=('Segoe UI', 10),
                                   bg=Theme.WHITE, fg=Theme.TEXT,
                                   relief='flat', bd=5, width=7)
        self.port_entry.insert(0, str(self.port))
        self.port_entry.grid(row=0, column=3, padx=5, pady=5)
        
        self.conn_btn = tk.Button(inner, text="Connect",
                                 command=self.toggle_connection,
                                 bg=Theme.GREEN, fg='white',
                                 font=('Segoe UI', 10, 'bold'),
                                 relief='flat', padx=20, pady=8,
                                 cursor='hand2',
                                 activebackground='#45a017')
        self.conn_btn.grid(row=0, column=4, padx=10, pady=5)
        
        self.status_dot = tk.Label(inner, text="●", font=('Arial', 14),
                                  fg=Theme.RED, bg=Theme.BLUE_LIGHT)
        self.status_dot.grid(row=0, column=5, padx=5)
        
        # Main content
        main = tk.Frame(self.root, bg=Theme.LIGHT_BG)
        main.pack(fill='both', expand=True, padx=30, pady=(0, 20))
        
        # Notebook
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Light.TNotebook', background=Theme.LIGHT_BG, borderwidth=0)
        style.configure('Light.TNotebook.Tab',
                       background=Theme.WHITE, foreground=Theme.TEXT_GRAY,
                       padding=[30, 14], borderwidth=0, focuscolor='none')
        style.map('Light.TNotebook.Tab',
                 background=[('selected', Theme.BLUE_LIGHT)],
                 foreground=[('selected', Theme.BLUE)])
        
        notebook = ttk.Notebook(main, style='Light.TNotebook')
        notebook.pack(fill='both', expand=True)
        
        # Tab 1: My Files
        my_files = tk.Frame(notebook, bg=Theme.WHITE)
        notebook.add(my_files, text='  📂 My Files  ')
        self._create_my_files(my_files)
        
        # Tab 2: Network Files
        network = tk.Frame(notebook, bg=Theme.WHITE)
        notebook.add(network, text='  🌐 Network Files  ')
        self._create_network(network)
        
        # Tab 3: Activity
        activity = tk.Frame(notebook, bg=Theme.WHITE)
        notebook.add(activity, text='  📊 Activity  ')
        self._create_activity(activity)
    
    def _create_my_files(self, parent):
        # Buttons
        btn_bar = tk.Frame(parent, bg=Theme.WHITE)
        btn_bar.pack(fill='x', padx=25, pady=20)
        
        tk.Button(btn_bar, text="➕ Add File", command=self.add_file,
                 bg=Theme.BLUE, fg='white', font=('Segoe UI', 10, 'bold'),
                 relief='flat', padx=20, pady=10, cursor='hand2',
                 activebackground=Theme.BLUE_HOVER).pack(side='left', padx=5)
        
        tk.Button(btn_bar, text="📤 Publish", command=self.publish_file,
                 bg=Theme.GREEN, fg='white', font=('Segoe UI', 10, 'bold'),
                 relief='flat', padx=20, pady=10, cursor='hand2',
                 activebackground='#45a017').pack(side='left', padx=5)
        
        tk.Button(btn_bar, text="🔄 Refresh", command=self.refresh_my_files,
                 bg=Theme.TEXT_GRAY, fg='white', font=('Segoe UI', 10, 'bold'),
                 relief='flat', padx=20, pady=10, cursor='hand2',
                 activebackground='#6c6c6c').pack(side='left', padx=5)
        
        # Tree
        tree_frame = tk.Frame(parent, bg=Theme.WHITE)
        tree_frame.pack(fill='both', expand=True, padx=25, pady=(0, 25))
        
        style = ttk.Style()
        style.configure("Clean.Treeview",
                       background=Theme.WHITE, foreground=Theme.TEXT,
                       fieldbackground=Theme.WHITE, borderwidth=0, rowheight=32)
        style.configure("Clean.Treeview.Heading",
                       background=Theme.BLUE_LIGHT, foreground=Theme.BLUE,
                       borderwidth=0, font=('Segoe UI', 10, 'bold'))
        style.map('Clean.Treeview',
                 background=[('selected', Theme.BLUE)],
                 foreground=[('selected', 'white')])
        
        cols = ('filename', 'size', 'status')
        self.my_files_tree = ttk.Treeview(tree_frame, columns=cols,
                                         show='headings', style='Clean.Treeview')
        
        self.my_files_tree.heading('filename', text='Filename')
        self.my_files_tree.heading('size', text='Size')
        self.my_files_tree.heading('status', text='Status')
        
        self.my_files_tree.column('filename', width=450)
        self.my_files_tree.column('size', width=150)
        self.my_files_tree.column('status', width=150)
        
        scroll = ttk.Scrollbar(tree_frame, orient='vertical',
                              command=self.my_files_tree.yview)
        self.my_files_tree.configure(yscrollcommand=scroll.set)
        
        self.my_files_tree.pack(side='left', fill='both', expand=True)
        scroll.pack(side='right', fill='y')
    
    def _create_network(self, parent):
        # Top bar
        top = tk.Frame(parent, bg=Theme.WHITE)
        top.pack(fill='x', padx=25, pady=20)
        
        tk.Button(top, text="🔍 Discover", command=self.discover_files,
                 bg=Theme.BLUE, fg='white', font=('Segoe UI', 10, 'bold'),
                 relief='flat', padx=22, pady=10, cursor='hand2',
                 activebackground=Theme.BLUE_HOVER).pack(side='left', padx=5)
        
        tk.Button(top, text="⬇️ Download", command=self.download_file,
                 bg=Theme.GREEN, fg='white', font=('Segoe UI', 10, 'bold'),
                 relief='flat', padx=20, pady=10, cursor='hand2',
                 activebackground='#45a017').pack(side='left', padx=5)
        
        # Search
        search_frame = tk.Frame(top, bg=Theme.BLUE_LIGHT)
        search_frame.pack(side='left', padx=20, fill='x', expand=True)
        
        tk.Label(search_frame, text="🔎", font=('Segoe UI', 12),
                fg=Theme.BLUE, bg=Theme.BLUE_LIGHT).pack(side='left', padx=12, pady=8)
        
        self.search_entry = tk.Entry(search_frame, font=('Segoe UI', 11),
                                     bg=Theme.BLUE_LIGHT, fg=Theme.TEXT,
                                     relief='flat', bd=0)
        self.search_entry.pack(side='left', fill='x', expand=True, pady=8, padx=(0, 12))
        self.search_entry.bind('<KeyRelease>', self.filter_network)
        
        # Tree
        tree_frame = tk.Frame(parent, bg=Theme.WHITE)
        tree_frame.pack(fill='both', expand=True, padx=25, pady=(0, 25))
        
        cols = ('filename', 'providers')
        self.network_tree = ttk.Treeview(tree_frame, columns=cols,
                                        show='headings', style='Clean.Treeview')
        
        self.network_tree.heading('filename', text='Filename')
        self.network_tree.heading('providers', text='Available From')
        
        self.network_tree.column('filename', width=400)
        self.network_tree.column('providers', width=500)
        
        scroll = ttk.Scrollbar(tree_frame, orient='vertical',
                              command=self.network_tree.yview)
        self.network_tree.configure(yscrollcommand=scroll.set)
        
        self.network_tree.pack(side='left', fill='both', expand=True)
        scroll.pack(side='right', fill='y')
        
        self.all_network_files = {}
    
    def _create_activity(self, parent):
        log_frame = tk.Frame(parent, bg=Theme.WHITE)
        log_frame.pack(fill='both', expand=True, padx=25, pady=25)
        
        self.log_text = scrolledtext.ScrolledText(log_frame,
                                                  bg=Theme.WHITE, fg=Theme.TEXT,
                                                  font=('Consolas', 10),
                                                  relief='flat', borderwidth=10,
                                                  insertbackground=Theme.BLUE,
                                                  selectbackground=Theme.BLUE_LIGHT)
        self.log_text.pack(fill='both', expand=True)
        
        self.log_text.tag_config('INFO', foreground=Theme.BLUE)
        self.log_text.tag_config('SUCCESS', foreground=Theme.GREEN)
        self.log_text.tag_config('ERROR', foreground=Theme.RED)
        self.log_text.tag_config('WARNING', foreground=Theme.ORANGE)
    
    def log(self, msg, level='INFO'):
        time = datetime.now().strftime('%H:%M:%S')
        self.log_text.insert('end', f"[{time}] {msg}\n", level)
        self.log_text.see('end')
    
    def toggle_connection(self):
        if self.connected:
            self.disconnect()
        else:
            self.connect()
    
    def connect(self):
        if self.connected:
            return
        
        try:
            name = self.name_entry.get().strip()
            port = int(self.port_entry.get())
            
            if not name:
                messagebox.showwarning("Invalid", "Enter a client name")
                self.log("✗ Invalid client name", 'ERROR')
                return
            
            # Create client instance
            self.client = Client(name, port)
            
            # Try to start (which includes server connection)
            try:
                self.client.start()
                
                # If we reach here, connection was successful
                self.connected = True
                self.status_dot.config(fg=Theme.GREEN)
                self.conn_btn.config(text="Disconnect", bg=Theme.RED,
                                    activebackground='#d43f3f')
                
                self.log(f"✓ Connected as {name} on port {port}", 'SUCCESS')
                self.refresh_my_files()
                
            except Exception as start_error:
                # Connection failed - clean up client
                self.client = None
                error_msg = str(start_error)
                
                # Check if it's a connection refused error
                if "WinError 10061" in error_msg or "Connection refused" in error_msg:
                    self.log("✗ Server is offline - Cannot connect", 'ERROR')
                    messagebox.showerror("Server Offline", 
                                        "The server is not running!\n\n"
                                        "Please start the server first.")
                else:
                    self.log(f"✗ Connection failed: {start_error}", 'ERROR')
                    messagebox.showerror("Connection Failed", 
                                        f"Cannot connect to server:\n{start_error}")
            
        except ValueError:
            self.log("✗ Invalid port number", 'ERROR')
            messagebox.showwarning("Invalid Port", "Port must be a number")
        except Exception as e:
            self.log(f"✗ Error: {e}", 'ERROR')
            messagebox.showerror("Error", f"Unexpected error:\n{e}")
    
    def disconnect(self):
        if not self.connected:
            return
        
        try:
            if self.client:
                self.client.stop()
            
            self.connected = False
            self.status_dot.config(fg=Theme.RED)
            self.conn_btn.config(text="Connect", bg=Theme.GREEN,
                                activebackground='#45a017')
            
            self.log("⏹ Disconnected", 'WARNING')
            
        except Exception as e:
            self.log(f"✗ Error: {e}", 'ERROR')
    
    def add_file(self):
        if not self.connected:
            messagebox.showwarning("Not Connected", "Connect first!")
            return
        
        filepath = filedialog.askopenfilename(title="Select File")
        if not filepath:
            return
        
        try:
            filename = os.path.basename(filepath)
            with open(filepath, 'rb') as f:
                content = f.read()
            
            self.client.file_manager.write_file(filename, content)
            self.log(f"➕ Added: {filename}", 'SUCCESS')
            self.refresh_my_files()
            
        except Exception as e:
            self.log(f"✗ Error: {e}", 'ERROR')
            messagebox.showerror("Error", f"Failed:\n{e}")
    
    def publish_file(self):
        if not self.connected:
            messagebox.showwarning("Not Connected", "Connect first!")
            return
        
        selected = self.my_files_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a file")
            return
        
        filename = self.my_files_tree.item(selected[0])['values'][0]
        
        def pub():
            try:
                if self.client.publish(filename):
                    # Mark file as published (global)
                    self.published_files.add(filename)
                    self.log(f"📤 Published: {filename}", 'SUCCESS')
                    self.root.after(0, self.refresh_my_files)
                else:
                    self.log(f"✗ Failed: {filename}", 'ERROR')
            except Exception as e:
                self.log(f"✗ Error: {e}", 'ERROR')
        
        threading.Thread(target=pub, daemon=True).start()
    
    def refresh_my_files(self):
        if not self.client:
            return
        
        self.my_files_tree.delete(*self.my_files_tree.get_children())
        
        for filename in self.client.file_manager.list_files():
            size = os.path.getsize(self.client.file_manager.get_file_path(filename))
            size_str = self._format_size(size)
            
            # Check if file is published (global) or local only
            if filename in self.published_files:
                status = "🌐 Global"
            else:
                status = "🔒 Local"
            
            self.my_files_tree.insert('', 'end', values=(filename, size_str, status))
    
    def discover_files(self):
        if not self.connected:
            messagebox.showwarning("Not Connected", "Connect first!")
            return
        
        self.log("🔍 Discovering...", 'INFO')
        
        def disc():
            try:
                files = self.client.discover()
                self.all_network_files = files
                self.root.after(0, lambda: self._display_network(files))
                self.log(f"✓ Found {len(files)} file(s)", 'SUCCESS')
            except Exception as e:
                self.log(f"✗ Failed: {e}", 'ERROR')
        
        threading.Thread(target=disc, daemon=True).start()
    
    def _display_network(self, files):
        self.network_tree.delete(*self.network_tree.get_children())
        for filename, providers in files.items():
            providers_str = ', '.join(providers)
            self.network_tree.insert('', 'end', values=(filename, providers_str))
    
    def filter_network(self, event=None):
        search = self.search_entry.get().lower()
        filtered = {k: v for k, v in self.all_network_files.items()
                   if search in k.lower()}
        self._display_network(filtered)
    
    def download_file(self):
        if not self.connected:
            messagebox.showwarning("Not Connected", "Connect first!")
            return
        
        selected = self.network_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a file")
            return
        
        filename = self.network_tree.item(selected[0])['values'][0]
        self.log(f"⬇️ Downloading: {filename}...", 'INFO')
        
        def down():
            try:
                if self.client.fetch(filename):
                    self.log(f"✓ Downloaded: {filename}", 'SUCCESS')
                    self.root.after(0, self.refresh_my_files)
                    self.root.after(0, lambda: messagebox.showinfo("Success",
                                    f"Downloaded:\n{filename}"))
                else:
                    self.log(f"✗ Failed: {filename}", 'ERROR')
                    self.root.after(0, lambda: messagebox.showerror("Error",
                                    f"Failed:\n{filename}"))
            except Exception as e:
                self.log(f"✗ Error: {e}", 'ERROR')
        
        threading.Thread(target=down, daemon=True).start()
    
    def _format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    def run(self):
        self.log("🚀 P2P Client Ready", 'INFO')
        self.log("Connect to join the network", 'INFO')
        self.root.mainloop()


def main():
    app = ClientGUI()
    app.run()


if __name__ == "__main__":
    main()
