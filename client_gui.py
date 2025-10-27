"""
GUI for Client - User-Friendly Interface
Beautiful UI for file sharing operations
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import time
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from client import Client
from config import DEFAULT_REPO_PATH


class ClientGUI:
    """GUI for Client with easy-to-use interface"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("P2P File Sharing - Client")
        self.root.geometry("1000x750")
        self.root.configure(bg='#ecf0f1')
        
        # Client instance
        self.client = None
        self.connected = False
        
        # Setup UI
        self.setup_ui()
        
        # Update thread
        self.update_thread = None
        self.running = False
        
    def setup_ui(self):
        """Setup the user interface"""
        
        # Header
        header_frame = tk.Frame(self.root, bg='#3498db', pady=20)
        header_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            header_frame,
            text="📁 P2P File Sharing Client",
            font=('Arial', 22, 'bold'),
            bg='#3498db',
            fg='white'
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            header_frame,
            text="Share and download files from the network",
            font=('Arial', 11),
            bg='#3498db',
            fg='#ecf0f1'
        )
        subtitle_label.pack()
        
        # Connection Panel
        conn_frame = tk.LabelFrame(
            self.root,
            text=" 🔌 Connection Settings ",
            font=('Arial', 11, 'bold'),
            bg='white',
            fg='#2c3e50',
            pady=15,
            padx=15
        )
        conn_frame.pack(fill=tk.X, padx=20, pady=15)
        
        # Hostname
        tk.Label(
            conn_frame,
            text="Client Name:",
            font=('Arial', 10),
            bg='white'
        ).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.hostname_entry = tk.Entry(conn_frame, font=('Arial', 10), width=20)
        self.hostname_entry.insert(0, f"Client_{int(time.time()) % 10000}")
        self.hostname_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Port
        tk.Label(
            conn_frame,
            text="Port:",
            font=('Arial', 10),
            bg='white'
        ).grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        
        self.port_entry = tk.Entry(conn_frame, font=('Arial', 10), width=10)
        self.port_entry.insert(0, "5001")
        self.port_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Connect button
        self.connect_btn = tk.Button(
            conn_frame,
            text="🔗 CONNECT",
            command=self.connect_to_server,
            bg='#27ae60',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=8,
            relief=tk.FLAT,
            cursor='hand2'
        )
        self.connect_btn.grid(row=0, column=4, padx=15, pady=5)
        
        # Status
        self.conn_status = tk.Label(
            conn_frame,
            text="● Disconnected",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg='#e74c3c'
        )
        self.conn_status.grid(row=0, column=5, padx=10, pady=5)
        
        # Main content - Notebook
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Tab 1: My Files
        my_files_frame = tk.Frame(notebook, bg='white')
        notebook.add(my_files_frame, text="📂 My Files")
        self.setup_my_files_tab(my_files_frame)
        
        # Tab 2: Network Files
        network_frame = tk.Frame(notebook, bg='white')
        notebook.add(network_frame, text="🌐 Network Files")
        self.setup_network_tab(network_frame)
        
        # Tab 3: Logs
        logs_frame = tk.Frame(notebook, bg='white')
        notebook.add(logs_frame, text="📋 Activity Logs")
        self.setup_logs_tab(logs_frame)
        
        # Footer
        footer_frame = tk.Frame(self.root, bg='#34495e', pady=10)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.footer_label = tk.Label(
            footer_frame,
            text="Ready to connect...",
            font=('Arial', 9),
            bg='#34495e',
            fg='white'
        )
        self.footer_label.pack()
    
    def setup_my_files_tab(self, parent):
        """Setup my files tab"""
        
        # Toolbar
        toolbar = tk.Frame(parent, bg='#ecf0f1', pady=10)
        toolbar.pack(fill=tk.X)
        
        tk.Button(
            toolbar,
            text="➕ Add File",
            command=self.add_file,
            bg='#3498db',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=15,
            pady=5,
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            toolbar,
            text="📤 Publish Selected",
            command=self.publish_file,
            bg='#9b59b6',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=15,
            pady=5,
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            toolbar,
            text="🔄 Refresh",
            command=self.refresh_my_files,
            bg='#95a5a6',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=15,
            pady=5,
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
        
        # Files list
        list_frame = tk.Frame(parent, bg='white')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.my_files_tree = ttk.Treeview(
            list_frame,
            columns=('filename', 'size', 'status'),
            show='headings',
            yscrollcommand=scrollbar.set
        )
        
        self.my_files_tree.heading('filename', text='Filename')
        self.my_files_tree.heading('size', text='Size')
        self.my_files_tree.heading('status', text='Status')
        
        self.my_files_tree.column('filename', width=400)
        self.my_files_tree.column('size', width=150)
        self.my_files_tree.column('status', width=150)
        
        self.my_files_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.my_files_tree.yview)
    
    def setup_network_tab(self, parent):
        """Setup network files tab"""
        
        # Toolbar
        toolbar = tk.Frame(parent, bg='#ecf0f1', pady=10)
        toolbar.pack(fill=tk.X)
        
        tk.Button(
            toolbar,
            text="🔍 Discover Files",
            command=self.discover_files,
            bg='#1abc9c',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=15,
            pady=5,
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            toolbar,
            text="📥 Download Selected",
            command=self.download_file,
            bg='#e67e22',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=15,
            pady=5,
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
        
        # Search
        tk.Label(
            toolbar,
            text="Search:",
            font=('Arial', 10),
            bg='#ecf0f1'
        ).pack(side=tk.LEFT, padx=(20, 5))
        
        self.search_entry = tk.Entry(toolbar, font=('Arial', 10), width=25)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<KeyRelease>', lambda e: self.filter_network_files())
        
        # Files list
        list_frame = tk.Frame(parent, bg='white')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.network_files_tree = ttk.Treeview(
            list_frame,
            columns=('filename', 'providers'),
            show='headings',
            yscrollcommand=scrollbar.set
        )
        
        self.network_files_tree.heading('filename', text='Filename')
        self.network_files_tree.heading('providers', text='Available Providers')
        
        self.network_files_tree.column('filename', width=300)
        self.network_files_tree.column('providers', width=450)
        
        self.network_files_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.network_files_tree.yview)
        
        # Store all network files for filtering
        self.all_network_files = {}
    
    def setup_logs_tab(self, parent):
        """Setup logs tab"""
        
        self.log_text = scrolledtext.ScrolledText(
            parent,
            wrap=tk.WORD,
            bg='#2c3e50',
            fg='#ecf0f1',
            font=('Consolas', 9),
            padx=10,
            pady=10
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def connect_to_server(self):
        """Connect to the server"""
        if not self.connected:
            hostname = self.hostname_entry.get().strip()
            try:
                port = int(self.port_entry.get().strip())
            except ValueError:
                messagebox.showerror("Error", "Invalid port number!")
                return
            
            if not hostname:
                messagebox.showerror("Error", "Please enter a client name!")
                return
            
            # Disable connection controls
            self.hostname_entry.config(state=tk.DISABLED)
            self.port_entry.config(state=tk.DISABLED)
            self.connect_btn.config(state=tk.DISABLED, text="Connecting...")
            
            # Connect in thread
            thread = threading.Thread(
                target=self._connect_thread,
                args=(hostname, port),
                daemon=True
            )
            thread.start()
    
    def _connect_thread(self, hostname, port):
        """Connect to server in background"""
        try:
            # Create client
            repo_path = os.path.join(DEFAULT_REPO_PATH, hostname)
            self.client = Client(hostname=hostname, port=port, repo_path=repo_path)
            
            # Start client
            self.client.start()
            
            # Update UI
            self.connected = True
            self.conn_status.config(text="● Connected", fg='#27ae60')
            self.connect_btn.config(
                text="🔌 DISCONNECT",
                bg='#e74c3c',
                command=self.disconnect_from_server,
                state=tk.NORMAL
            )
            
            self.footer_label.config(text=f"Connected as {hostname}:{port} | Repository: {repo_path}")
            
            self.log(f"✓ Connected to server as {hostname}:{port}")
            self.log(f"✓ Repository: {repo_path}")
            
            # Start update thread
            self.running = True
            self.update_thread = threading.Thread(target=self.update_ui, daemon=True)
            self.update_thread.start()
            
            # Initial refresh
            self.refresh_my_files()
            
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect:\n{str(e)}")
            self.hostname_entry.config(state=tk.NORMAL)
            self.port_entry.config(state=tk.NORMAL)
            self.connect_btn.config(state=tk.NORMAL, text="🔗 CONNECT")
            self.log(f"✗ Connection failed: {e}")
    
    def disconnect_from_server(self):
        """Disconnect from server"""
        if self.connected:
            self.running = False
            
            if self.client:
                self.client.stop()
            
            self.connected = False
            self.conn_status.config(text="● Disconnected", fg='#e74c3c')
            
            self.hostname_entry.config(state=tk.NORMAL)
            self.port_entry.config(state=tk.NORMAL)
            self.connect_btn.config(
                text="🔗 CONNECT",
                bg='#27ae60',
                command=self.connect_to_server
            )
            
            self.footer_label.config(text="Disconnected")
            self.log("✓ Disconnected from server")
    
    def add_file(self):
        """Add file to repository"""
        if not self.connected:
            messagebox.showwarning("Not Connected", "Please connect to server first!")
            return
        
        # Open file dialog
        file_path = filedialog.askopenfilename(
            title="Select file to add",
            filetypes=[("All Files", "*.*")]
        )
        
        if file_path:
            filename = os.path.basename(file_path)
            
            try:
                success = self.client.add_file_to_repo(file_path, filename)
                
                if success:
                    self.log(f"✓ File added: {filename}")
                    self.refresh_my_files()
                    messagebox.showinfo("Success", f"File added successfully:\n{filename}")
                else:
                    messagebox.showerror("Error", "Failed to add file!")
            except Exception as e:
                messagebox.showerror("Error", f"Error adding file:\n{str(e)}")
                self.log(f"✗ Error adding file: {e}")
    
    def publish_file(self):
        """Publish selected file"""
        if not self.connected:
            messagebox.showwarning("Not Connected", "Please connect to server first!")
            return
        
        selected = self.my_files_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a file to publish!")
            return
        
        item = self.my_files_tree.item(selected[0])
        filename = item['values'][0]
        
        try:
            success = self.client.publish(filename)
            
            if success:
                self.log(f"✓ Published: {filename}")
                self.refresh_my_files()
                messagebox.showinfo("Success", f"File published successfully:\n{filename}")
            else:
                messagebox.showerror("Error", "Failed to publish file!")
        except Exception as e:
            messagebox.showerror("Error", f"Error publishing file:\n{str(e)}")
            self.log(f"✗ Error publishing: {e}")
    
    def discover_files(self):
        """Discover files on network"""
        if not self.connected:
            messagebox.showwarning("Not Connected", "Please connect to server first!")
            return
        
        self.log("🔍 Discovering files on network...")
        
        # Discover in thread
        thread = threading.Thread(target=self._discover_thread, daemon=True)
        thread.start()
    
    def _discover_thread(self):
        """Discover files in background"""
        try:
            files = self.client.discover()
            
            self.all_network_files = files
            
            # Update tree
            self.network_files_tree.delete(*self.network_files_tree.get_children())
            
            for filename, providers in files.items():
                providers_str = ', '.join(providers)
                self.network_files_tree.insert('', tk.END, values=(filename, providers_str))
            
            self.log(f"✓ Found {len(files)} file(s) on network")
            
        except Exception as e:
            self.log(f"✗ Discovery error: {e}")
    
    def download_file(self):
        """Download selected file"""
        if not self.connected:
            messagebox.showwarning("Not Connected", "Please connect to server first!")
            return
        
        selected = self.network_files_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a file to download!")
            return
        
        item = self.network_files_tree.item(selected[0])
        filename = item['values'][0]
        
        self.log(f"📥 Downloading: {filename}...")
        
        # Download in thread
        thread = threading.Thread(
            target=self._download_thread,
            args=(filename,),
            daemon=True
        )
        thread.start()
    
    def _download_thread(self, filename):
        """Download file in background"""
        try:
            success = self.client.fetch(filename)
            
            if success:
                self.log(f"✓ Downloaded: {filename}")
                self.refresh_my_files()
                messagebox.showinfo("Success", f"File downloaded successfully:\n{filename}")
            else:
                self.log(f"✗ Download failed: {filename}")
                messagebox.showerror("Error", f"Failed to download:\n{filename}")
        except Exception as e:
            self.log(f"✗ Download error: {e}")
            messagebox.showerror("Error", f"Error downloading file:\n{str(e)}")
    
    def refresh_my_files(self):
        """Refresh my files list"""
        if not self.connected or not self.client:
            return
        
        try:
            files = self.client.file_manager.list_files()
            
            self.my_files_tree.delete(*self.my_files_tree.get_children())
            
            for filename in files:
                size = self.client.file_manager.get_file_size(filename)
                size_str = self.format_size(size)
                status = "Local"
                
                self.my_files_tree.insert('', tk.END, values=(filename, size_str, status))
            
        except Exception as e:
            self.log(f"✗ Error refreshing files: {e}")
    
    def filter_network_files(self):
        """Filter network files by search term"""
        search_term = self.search_entry.get().lower()
        
        self.network_files_tree.delete(*self.network_files_tree.get_children())
        
        for filename, providers in self.all_network_files.items():
            if search_term in filename.lower():
                providers_str = ', '.join(providers)
                self.network_files_tree.insert('', tk.END, values=(filename, providers_str))
    
    def format_size(self, size):
        """Format file size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def update_ui(self):
        """Update UI periodically"""
        while self.running and self.connected:
            try:
                # Auto-refresh every 5 seconds
                time.sleep(5)
                if self.connected:
                    self.refresh_my_files()
            except Exception as e:
                pass
    
    def log(self, message):
        """Add message to log"""
        timestamp = time.strftime('%H:%M:%S')
        log_msg = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_msg)
        self.log_text.see(tk.END)
    
    def run(self):
        """Run the GUI"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Handle window closing"""
        if self.connected:
            self.disconnect_from_server()
        self.root.destroy()


def main():
    """Main entry point"""
    app = ClientGUI()
    app.run()


if __name__ == "__main__":
    main()
