"""
GUI for Server - Monitor and Control
Beautiful UI with real-time updates
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import Server
from utils import setup_logger


class ServerGUI:
    """GUI for Server with monitoring capabilities"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("P2P File Sharing - Server Dashboard")
        self.root.geometry("900x700")
        self.root.configure(bg='#2c3e50')
        
        # Server instance
        self.server = None
        self.server_thread = None
        self.running = False
        
        # Setup UI
        self.setup_ui()
        
        # Update thread
        self.update_thread = None
        
    def setup_ui(self):
        """Setup the user interface"""
        
        # Title
        title_frame = tk.Frame(self.root, bg='#34495e', pady=15)
        title_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            title_frame,
            text="🖥️ P2P FILE SHARING SERVER",
            font=('Arial', 20, 'bold'),
            bg='#34495e',
            fg='white'
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="Centralized Index Server - Hybrid P2P Architecture",
            font=('Arial', 10),
            bg='#34495e',
            fg='#bdc3c7'
        )
        subtitle_label.pack()
        
        # Control Panel
        control_frame = tk.Frame(self.root, bg='#2c3e50', pady=10)
        control_frame.pack(fill=tk.X, padx=20)
        
        self.start_button = tk.Button(
            control_frame,
            text="▶ START SERVER",
            command=self.start_server,
            bg='#27ae60',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor='hand2'
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = tk.Button(
            control_frame,
            text="⬛ STOP SERVER",
            command=self.stop_server,
            bg='#e74c3c',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor='hand2',
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.status_label = tk.Label(
            control_frame,
            text="● Stopped",
            font=('Arial', 12, 'bold'),
            bg='#2c3e50',
            fg='#e74c3c'
        )
        self.status_label.pack(side=tk.LEFT, padx=20)
        
        # Statistics Frame
        stats_frame = tk.Frame(self.root, bg='#2c3e50')
        stats_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Client count
        self.client_stat = self.create_stat_card(
            stats_frame, "👥 Clients", "0", "#3498db"
        )
        self.client_stat.pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)
        
        # File count
        self.file_stat = self.create_stat_card(
            stats_frame, "📁 Files", "0", "#9b59b6"
        )
        self.file_stat.pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)
        
        # Connections count
        self.conn_stat = self.create_stat_card(
            stats_frame, "🔗 Connections", "0", "#1abc9c"
        )
        self.conn_stat.pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)
        
        # Notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Clients Tab
        clients_frame = tk.Frame(notebook, bg='#ecf0f1')
        notebook.add(clients_frame, text="👥 Connected Clients")
        
        # Clients tree
        self.clients_tree = ttk.Treeview(
            clients_frame,
            columns=('hostname', 'port', 'files', 'last_seen'),
            show='headings',
            height=8
        )
        self.clients_tree.heading('hostname', text='Hostname')
        self.clients_tree.heading('port', text='Port')
        self.clients_tree.heading('files', text='Files')
        self.clients_tree.heading('last_seen', text='Last Seen')
        
        self.clients_tree.column('hostname', width=200)
        self.clients_tree.column('port', width=80)
        self.clients_tree.column('files', width=60)
        self.clients_tree.column('last_seen', width=150)
        
        self.clients_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Files Tab
        files_frame = tk.Frame(notebook, bg='#ecf0f1')
        notebook.add(files_frame, text="📁 Shared Files")
        
        # Files tree
        self.files_tree = ttk.Treeview(
            files_frame,
            columns=('filename', 'providers'),
            show='headings',
            height=8
        )
        self.files_tree.heading('filename', text='Filename')
        self.files_tree.heading('providers', text='Providers')
        
        self.files_tree.column('filename', width=250)
        self.files_tree.column('providers', width=450)
        
        self.files_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Logs Tab
        logs_frame = tk.Frame(notebook, bg='#ecf0f1')
        notebook.add(logs_frame, text="📋 Server Logs")
        
        self.log_text = scrolledtext.ScrolledText(
            logs_frame,
            wrap=tk.WORD,
            bg='#1e1e1e',
            fg='#00ff00',
            font=('Consolas', 9),
            height=15
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Footer
        footer_frame = tk.Frame(self.root, bg='#34495e', pady=8)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        footer_label = tk.Label(
            footer_frame,
            text="Computer Networks - HK251 | Hybrid P2P File Sharing System",
            font=('Arial', 9),
            bg='#34495e',
            fg='#bdc3c7'
        )
        footer_label.pack()
    
    def create_stat_card(self, parent, title, value, color):
        """Create a statistics card"""
        card = tk.Frame(parent, bg=color, relief=tk.RAISED, bd=2)
        
        title_label = tk.Label(
            card,
            text=title,
            font=('Arial', 10),
            bg=color,
            fg='white'
        )
        title_label.pack(pady=(10, 5))
        
        value_label = tk.Label(
            card,
            text=value,
            font=('Arial', 24, 'bold'),
            bg=color,
            fg='white'
        )
        value_label.pack(pady=(0, 10))
        
        # Store value label for updates
        card.value_label = value_label
        
        return card
    
    def start_server(self):
        """Start the server"""
        if not self.running:
            self.running = True
            
            # Create server
            self.server = Server()
            
            # Start server in thread
            self.server_thread = threading.Thread(target=self.server.start, daemon=True)
            self.server_thread.start()
            
            # Update UI
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.status_label.config(text="● Running", fg='#27ae60')
            
            self.log("Server started on 127.0.0.1:5000")
            
            # Start update thread
            self.update_thread = threading.Thread(target=self.update_stats, daemon=True)
            self.update_thread.start()
    
    def stop_server(self):
        """Stop the server"""
        if self.running:
            self.running = False
            
            if self.server:
                self.server.stop()
            
            # Update UI
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.status_label.config(text="● Stopped", fg='#e74c3c')
            
            self.log("Server stopped")
    
    def update_stats(self):
        """Update statistics periodically"""
        while self.running:
            try:
                if self.server and self.server.index_manager:
                    # Get stats
                    clients = self.server.index_manager.get_all_clients()
                    files = self.server.index_manager.get_all_files()
                    
                    # Update stat cards
                    self.client_stat.value_label.config(text=str(len(clients)))
                    self.file_stat.value_label.config(text=str(len(files)))
                    self.conn_stat.value_label.config(text=str(len(self.server.client_connections)))
                    
                    # Update clients tree
                    self.clients_tree.delete(*self.clients_tree.get_children())
                    for hostname, info in clients.items():
                        last_seen = time.strftime('%H:%M:%S', time.localtime(info['last_seen']))
                        self.clients_tree.insert('', tk.END, values=(
                            hostname,
                            info['port'],
                            len(info['files']),
                            last_seen
                        ))
                    
                    # Update files tree
                    self.files_tree.delete(*self.files_tree.get_children())
                    for fname, providers in files.items():
                        providers_str = ', '.join(providers)
                        self.files_tree.insert('', tk.END, values=(
                            fname,
                            providers_str
                        ))
                
                time.sleep(1)  # Update every second
                
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
        if self.running:
            self.stop_server()
        self.root.destroy()


def main():
    """Main entry point"""
    app = ServerGUI()
    app.run()


if __name__ == "__main__":
    main()
