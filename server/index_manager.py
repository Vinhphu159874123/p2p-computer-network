"""
Index Manager for Server
Manages file metadata and client registry
"""

import threading
import time
from utils import setup_logger


class IndexManager:
    """
    Manages the centralized index of files and clients
    
    Attributes:
        file_index: Dict mapping filename -> list of (hostname, last_update_time)
        client_registry: Dict mapping hostname -> {port, last_seen, files}
    """
    
    def __init__(self):
        self.logger = setup_logger('IndexManager')
        
        # File index: {filename: [(hostname, timestamp), ...]}
        self.file_index = {}
        
        # Client registry: {hostname: {'port': port, 'last_seen': timestamp, 'files': [...]}}
        self.client_registry = {}
        
        # Thread lock for thread-safe operations
        self.lock = threading.RLock()
    
    def register_client(self, hostname, port):
        """
        Register a new client or update existing client
        
        Args:
            hostname: Client hostname (format: "host:port")
            port: Client listening port
            
        Returns:
            bool: True if successful
        """
        with self.lock:
            if hostname not in self.client_registry:
                self.client_registry[hostname] = {
                    'port': port,
                    'last_seen': time.time(),
                    'files': []
                }
                self.logger.info(f"New client registered: {hostname} (port: {port})")
            else:
                self.client_registry[hostname]['last_seen'] = time.time()
                self.client_registry[hostname]['port'] = port
                self.logger.info(f"Client updated: {hostname}")
            
            return True
    
    def deregister_client(self, hostname):
        """
        Deregister a client and remove all its files from index
        
        Args:
            hostname: Client hostname
            
        Returns:
            bool: True if successful
        """
        with self.lock:
            if hostname in self.client_registry:
                # Remove all files published by this client
                files_to_remove = self.client_registry[hostname]['files'].copy()
                for fname in files_to_remove:
                    self.remove_file_provider(fname, hostname)
                
                del self.client_registry[hostname]
                self.logger.info(f"Client deregistered: {hostname}")
                return True
            
            return False
    
    def register_file(self, fname, hostname):
        """
        Register a file in the index
        
        Args:
            fname: Filename
            hostname: Client hostname that owns the file
            
        Returns:
            bool: True if successful
        """
        with self.lock:
            if fname not in self.file_index:
                self.file_index[fname] = []
            
            # Check if this hostname already has this file
            for i, (h, _) in enumerate(self.file_index[fname]):
                if h == hostname:
                    # Update timestamp
                    self.file_index[fname][i] = (hostname, time.time())
                    self.logger.info(f"File updated: {fname} by {hostname}")
                    return True
            
            # Add new provider
            self.file_index[fname].append((hostname, time.time()))
            
            # Update client's file list
            if hostname in self.client_registry:
                if fname not in self.client_registry[hostname]['files']:
                    self.client_registry[hostname]['files'].append(fname)
            
            self.logger.info(f"File registered: {fname} by {hostname}")
            return True
    
    def sync_client_files(self, hostname, files):
        """
        Synchronize client's file list with server index
        
        Args:
            hostname: Client hostname
            files: List of filenames
            
        Returns:
            bool: True if successful
        """
        with self.lock:
            if hostname not in self.client_registry:
                self.logger.warning(f"Cannot sync: client {hostname} not registered")
                return False
            
            # Get current files
            current_files = set(self.client_registry[hostname]['files'])
            new_files = set(files)
            
            # Files to add
            to_add = new_files - current_files
            for fname in to_add:
                self.register_file(fname, hostname)
            
            # Files to remove
            to_remove = current_files - new_files
            for fname in to_remove:
                self.remove_file_provider(fname, hostname)
            
            # Update client's file list
            self.client_registry[hostname]['files'] = list(new_files)
            self.client_registry[hostname]['last_seen'] = time.time()
            
            self.logger.info(f"Synced files for {hostname}: +{len(to_add)} -{len(to_remove)}")
            return True
    
    def lookup_providers(self, fname):
        """
        Lookup providers (hostnames) that have the requested file
        
        Args:
            fname: Filename to lookup
            
        Returns:
            list: List of hostnames that have the file
        """
        with self.lock:
            if fname in self.file_index:
                # Return only hostnames (not timestamps)
                providers = [hostname for hostname, _ in self.file_index[fname]]
                self.logger.info(f"Lookup {fname}: found {len(providers)} provider(s)")
                return providers
            
            self.logger.info(f"Lookup {fname}: no providers found")
            return []
    
    def remove_file_provider(self, fname, hostname):
        """
        Remove a specific provider from a file's provider list
        
        Args:
            fname: Filename
            hostname: Client hostname to remove
            
        Returns:
            bool: True if successful
        """
        with self.lock:
            if fname in self.file_index:
                # Remove the provider
                self.file_index[fname] = [(h, t) for h, t in self.file_index[fname] if h != hostname]
                
                # If no providers left, remove the file entry
                if not self.file_index[fname]:
                    del self.file_index[fname]
                    self.logger.info(f"File removed from index: {fname}")
                
                # Update client's file list
                if hostname in self.client_registry:
                    if fname in self.client_registry[hostname]['files']:
                        self.client_registry[hostname]['files'].remove(fname)
                
                return True
            
            return False
    
    def get_all_files(self, hostname=None):
        """
        Get all files in the index
        
        Args:
            hostname: Optional - get files for specific client
            
        Returns:
            list or dict: List of filenames or dict of {filename: [providers]}
        """
        with self.lock:
            if hostname:
                # Return files for specific client
                if hostname in self.client_registry:
                    return self.client_registry[hostname]['files'].copy()
                return []
            else:
                # Return all files with providers
                result = {}
                for fname, providers in self.file_index.items():
                    result[fname] = [h for h, _ in providers]
                return result
    
    def update_client_liveness(self, hostname):
        """
        Update client's last seen timestamp
        
        Args:
            hostname: Client hostname
            
        Returns:
            bool: True if client exists
        """
        with self.lock:
            if hostname in self.client_registry:
                self.client_registry[hostname]['last_seen'] = time.time()
                return True
            return False
    
    def get_client_info(self, hostname):
        """
        Get client information
        
        Args:
            hostname: Client hostname
            
        Returns:
            dict: Client info or None
        """
        with self.lock:
            return self.client_registry.get(hostname, None)
    
    def get_all_clients(self):
        """
        Get all registered clients
        
        Returns:
            dict: Copy of client registry
        """
        with self.lock:
            return self.client_registry.copy()
    
    def cleanup_inactive_clients(self, timeout=300):
        """
        Remove clients that haven't been seen for timeout seconds
        
        Args:
            timeout: Timeout in seconds (default: 5 minutes)
            
        Returns:
            int: Number of clients removed
        """
        with self.lock:
            current_time = time.time()
            inactive_clients = []
            
            for hostname, info in self.client_registry.items():
                if current_time - info['last_seen'] > timeout:
                    inactive_clients.append(hostname)
            
            for hostname in inactive_clients:
                self.deregister_client(hostname)
            
            if inactive_clients:
                self.logger.info(f"Cleaned up {len(inactive_clients)} inactive client(s)")
            
            return len(inactive_clients)
