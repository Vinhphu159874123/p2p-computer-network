"""
P2P Server GUI - Clean Light Theme
White background with blue accents for a professional look
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import logging
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from server import Server


class GUILogHandler(logging.Handler):
    """Custom logging handler to redirect logs to GUI"""
    def __init__(self, log_callback):
        super().__init__()
        self.log_callback = log_callback
    
    def emit(self, record):
        msg = self.format(record)
        # Determine log type based on level
        if record.levelno >= logging.ERROR:
            log_type = 'ERROR'
        elif record.levelno >= logging.WARNING:
            log_type = 'WARNING'
        else:
            log_type = 'INFO'
        
        # Call GUI log function (thread-safe)
        self.log_callback(msg, log_type)


# Clean Light Theme
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


class ServerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("P2P Server Dashboard")
        self.root.geometry("1050x750")
        self.root.configure(bg=Theme.LIGHT_BG)
        
        self.server = None
        self.running = False
        
        # Setup logging handler for server logs
        self.log_handler = None
        
        self._create_ui()
        self._start_monitor()
    
    def _create_ui(self):
        # Header
        header = tk.Frame(self.root, bg=Theme.WHITE, height=100)
        header.pack(fill='x', padx=0, pady=(0, 20))
        header.pack_propagate(False)
        
        # Title section
        title_frame = tk.Frame(header, bg=Theme.WHITE)
        title_frame.pack(side='left', padx=40, pady=25)
        
        tk.Label(title_frame, text="🖥️ P2P Server Dashboard",
                font=('Segoe UI', 22, 'bold'),
                fg=Theme.TEXT, bg=Theme.WHITE).pack(anchor='w')
        
        tk.Label(title_frame, text="Manage and monitor your P2P file sharing network",
                font=('Segoe UI', 10),
                fg=Theme.TEXT_GRAY, bg=Theme.WHITE).pack(anchor='w', pady=(5, 0))
        
        # Control buttons
        btn_frame = tk.Frame(header, bg=Theme.WHITE)
        btn_frame.pack(side='right', padx=40, pady=25)
        
        self.start_btn = tk.Button(btn_frame, text="▶ Start Server",
                                   command=self.start_server,
                                   bg=Theme.GREEN, fg='white',
                                   font=('Segoe UI', 11, 'bold'),
                                   relief='flat', bd=0,
                                   padx=25, pady=12,
                                   cursor='hand2',
                                   activebackground='#45a017')
        self.start_btn.pack(side='left', padx=5)
        
        self.stop_btn = tk.Button(btn_frame, text="⏹ Stop Server",
                                  command=self.stop_server,
                                  bg=Theme.RED, fg='white',
                                  font=('Segoe UI', 11, 'bold'),
                                  relief='flat', bd=0,
                                  padx=25, pady=12,
                                  cursor='hand2',
                                  state='disabled',
                                  activebackground='#d43f3f')
        self.stop_btn.pack(side='left', padx=5)
        
        # Main content
        main = tk.Frame(self.root, bg=Theme.LIGHT_BG)
        main.pack(fill='both', expand=True, padx=30, pady=(0, 20))
        
        # Stats cards
        stats = tk.Frame(main, bg=Theme.LIGHT_BG)
        stats.pack(fill='x', pady=(0, 20))
        
        self.clients_val = self._create_stat_card(stats, "Active Clients", "0", Theme.BLUE, 0)
        self.files_val = self._create_stat_card(stats, "Shared Files", "0", Theme.GREEN, 1)
        self.conn_val = self._create_stat_card(stats, "Connections", "0", Theme.ORANGE, 2)
        
        # Status card
        status_card = tk.Frame(stats, bg=Theme.WHITE, relief='flat', bd=1,
                              highlightbackground=Theme.BORDER, highlightthickness=1)
        status_card.grid(row=0, column=3, sticky='ew', padx=8)
        stats.columnconfigure(3, weight=1)
        
        tk.Label(status_card, text="Server Status",
                font=('Segoe UI', 10), fg=Theme.TEXT_GRAY,
                bg=Theme.WHITE).pack(pady=(15, 5))
        
        self.status_lbl = tk.Label(status_card, text="● OFFLINE",
                                   font=('Segoe UI', 14, 'bold'),
                                   fg=Theme.RED, bg=Theme.WHITE)
        self.status_lbl.pack(pady=(0, 15))
        
        # Notebook for tabs
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Custom.TNotebook', background=Theme.LIGHT_BG,
                       borderwidth=0, relief='flat')
        style.configure('Custom.TNotebook.Tab',
                       background=Theme.WHITE,
                       foreground=Theme.TEXT_GRAY,
                       padding=[25, 12],
                       borderwidth=0,
                       focuscolor='none')
        style.map('Custom.TNotebook.Tab',
                 background=[('selected', Theme.BLUE_LIGHT)],
                 foreground=[('selected', Theme.BLUE)])
        
        notebook = ttk.Notebook(main, style='Custom.TNotebook')
        notebook.pack(fill='both', expand=True)
        
        # Tab 1: Clients
        clients_tab = tk.Frame(notebook, bg=Theme.WHITE)
        notebook.add(clients_tab, text='  Connected Clients  ')
        
        tree_frame = tk.Frame(clients_tab, bg=Theme.WHITE)
        tree_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        style.configure("Light.Treeview",
                       background=Theme.WHITE,
                       foreground=Theme.TEXT,
                       fieldbackground=Theme.WHITE,
                       borderwidth=0,
                       rowheight=30)
        style.configure("Light.Treeview.Heading",
                       background=Theme.BLUE_LIGHT,
                       foreground=Theme.BLUE,
                       borderwidth=0,
                       font=('Segoe UI', 10, 'bold'))
        style.map('Light.Treeview',
                 background=[('selected', Theme.BLUE)],
                 foreground=[('selected', 'white')])
        
        cols = ('hostname', 'port', 'files', 'last_seen')
        self.clients_tree = ttk.Treeview(tree_frame, columns=cols,
                                        show='headings', style='Light.Treeview')
        
        self.clients_tree.heading('hostname', text='Client Name')
        self.clients_tree.heading('port', text='Port')
        self.clients_tree.heading('files', text='Files Shared')
        self.clients_tree.heading('last_seen', text='Last Seen')
        
        self.clients_tree.column('hostname', width=250)
        self.clients_tree.column('port', width=100)
        self.clients_tree.column('files', width=120)
        self.clients_tree.column('last_seen', width=200)
        
        scroll = ttk.Scrollbar(tree_frame, orient='vertical',
                              command=self.clients_tree.yview)
        self.clients_tree.configure(yscrollcommand=scroll.set)
        
        self.clients_tree.pack(side='left', fill='both', expand=True)
        scroll.pack(side='right', fill='y')
        
        # Tab 2: Files
        files_tab = tk.Frame(notebook, bg=Theme.WHITE)
        notebook.add(files_tab, text='  Shared Files  ')
        
        files_frame = tk.Frame(files_tab, bg=Theme.WHITE)
        files_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        file_cols = ('filename', 'providers', 'count')
        self.files_tree = ttk.Treeview(files_frame, columns=file_cols,
                                      show='headings', style='Light.Treeview')
        
        self.files_tree.heading('filename', text='Filename')
        self.files_tree.heading('providers', text='Available From')
        self.files_tree.heading('count', text='Copies')
        
        self.files_tree.column('filename', width=350)
        self.files_tree.column('providers', width=400)
        self.files_tree.column('count', width=100)
        
        files_scroll = ttk.Scrollbar(files_frame, orient='vertical',
                                    command=self.files_tree.yview)
        self.files_tree.configure(yscrollcommand=files_scroll.set)
        
        self.files_tree.pack(side='left', fill='both', expand=True)
        files_scroll.pack(side='right', fill='y')
        
        # Tab 3: Logs
        logs_tab = tk.Frame(notebook, bg=Theme.WHITE)
        notebook.add(logs_tab, text='  Activity Logs  ')
        
        log_frame = tk.Frame(logs_tab, bg=Theme.WHITE)
        log_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        self.log_text = scrolledtext.ScrolledText(log_frame,
                                                  bg=Theme.WHITE,
                                                  fg=Theme.TEXT,
                                                  font=('Consolas', 10),
                                                  relief='flat',
                                                  borderwidth=10,
                                                  insertbackground=Theme.BLUE,
                                                  selectbackground=Theme.BLUE_LIGHT,
                                                  selectforeground=Theme.TEXT)
        self.log_text.pack(fill='both', expand=True)
        
        self.log_text.tag_config('INFO', foreground=Theme.BLUE)
        self.log_text.tag_config('SUCCESS', foreground=Theme.GREEN)
        self.log_text.tag_config('ERROR', foreground=Theme.RED)
        self.log_text.tag_config('WARNING', foreground=Theme.ORANGE)
    
    def _create_stat_card(self, parent, label, value, color, col):
        card = tk.Frame(parent, bg=Theme.WHITE, relief='flat', bd=1,
                       highlightbackground=Theme.BORDER, highlightthickness=1)
        card.grid(row=0, column=col, sticky='ew', padx=8)
        parent.columnconfigure(col, weight=1)
        
        tk.Label(card, text=label, font=('Segoe UI', 10),
                fg=Theme.TEXT_GRAY, bg=Theme.WHITE).pack(pady=(15, 8))
        
        val_label = tk.Label(card, text=value, font=('Segoe UI', 28, 'bold'),
                            fg=color, bg=Theme.WHITE)
        val_label.pack(pady=(0, 15))
        
        return val_label
    
    def _start_monitor(self):
        def monitor():
            prev_clients = set()
            while True:
                if self.running and self.server:
                    self.root.after(0, self._update_display)
                    
                    # Detect client disconnections
                    try:
                        current_clients = set(self.server.index_manager.client_registry.keys())
                        disconnected = prev_clients - current_clients
                        new_clients = current_clients - prev_clients
                        
                        for client in disconnected:
                            self.root.after(0, lambda c=client: 
                                self.log(f"⚠️ Client disconnected: {c}", 'WARNING'))
                        
                        for client in new_clients:
                            self.root.after(0, lambda c=client: 
                                self.log(f"✓ New client connected: {c}", 'SUCCESS'))
                        
                        prev_clients = current_clients
                    except:
                        pass
                
                time.sleep(1)
        
        threading.Thread(target=monitor, daemon=True).start()
    
    def _update_display(self):
        if not self.server:
            return
        
        idx_mgr = self.server.index_manager
        
        # Update stats
        self.clients_val.config(text=str(len(idx_mgr.client_registry)))
        self.files_val.config(text=str(len(idx_mgr.file_index)))
        self.conn_val.config(text=str(len(self.server.client_connections)))
        
        # Update clients
        self.clients_tree.delete(*self.clients_tree.get_children())
        for hostname, info in idx_mgr.client_registry.items():
            last = datetime.fromtimestamp(info['last_seen']).strftime('%Y-%m-%d %H:%M:%S')
            self.clients_tree.insert('', 'end', values=(
                hostname, info['port'], len(info['files']), last
            ))
        
        # Update files
        self.files_tree.delete(*self.files_tree.get_children())
        for filename, providers in idx_mgr.file_index.items():
            provider_names = ', '.join([p[0] for p in providers])
            self.files_tree.insert('', 'end', values=(
                filename, provider_names, len(providers)
            ))
    
    def log(self, msg, level='INFO'):
        time = datetime.now().strftime('%H:%M:%S')
        self.log_text.insert('end', f"[{time}] {msg}\n", level)
        self.log_text.see('end')
    
    def _log_from_thread(self, msg, level='INFO'):
        """Thread-safe logging from server threads"""
        self.root.after(0, lambda: self.log(msg, level))
    
    def start_server(self):
        if self.running:
            return
        
        try:
            self.server = Server()
            
            # Setup custom log handler to redirect server logs to GUI
            self.log_handler = GUILogHandler(self._log_from_thread)
            self.log_handler.setFormatter(logging.Formatter('%(message)s'))
            self.server.logger.addHandler(self.log_handler)
            
            threading.Thread(target=self.server.start, daemon=True).start()
            
            self.running = True
            self.status_lbl.config(text="● ONLINE", fg=Theme.GREEN)
            self.start_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            
            self.log("✓ Server started successfully", 'SUCCESS')
            
        except Exception as e:
            self.log(f"✗ Failed to start: {e}", 'ERROR')
            messagebox.showerror("Error", f"Failed to start server:\n{e}")
    
    def stop_server(self):
        if not self.running:
            return
        
        try:
            num_clients = len(self.server.index_manager.client_registry) if self.server else 0
            
            if self.server:
                self.server.stop()
            
            self.running = False
            self.status_lbl.config(text="● OFFLINE", fg=Theme.RED)
            self.start_btn.config(state='normal')
            self.stop_btn.config(state='disabled')
            
            if num_clients > 0:
                self.log(f"⏹ Server stopped - {num_clients} client(s) disconnected", 'WARNING')
            else:
                self.log("⏹ Server stopped", 'WARNING')
            
        except Exception as e:
            self.log(f"✗ Error stopping: {e}", 'ERROR')
    
    def run(self):
        self.log("🚀 Server Dashboard Ready", 'INFO')
        self.log("Click 'Start Server' to begin", 'INFO')
        self.root.mainloop()


def main():
    app = ServerGUI()
    app.run()


if __name__ == "__main__":
    main()
