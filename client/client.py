"""
Main Client Implementation
Peer component for Hybrid P2P File Sharing
"""

import socket
import threading
import time
import os
from client.file_manager import FileManager
from client.peer_server import PeerServer
from protocol import Protocol, MessageType
from config import (
    SERVER_HOST, SERVER_PORT, CLIENT_HOST, 
    DEFAULT_CLIENT_PORT_RANGE, BUFFER_SIZE, ENCODING,
    CHUNK_SIZE, PING_INTERVAL, DEFAULT_REPO_PATH
)
from utils import setup_logger


class Client:
    """
    Client (Peer) component
    
    Responsibilities:
    - Connect to centralized server
    - Publish files to server index
    - Fetch files from other peers
    - Serve file requests from other peers (P2P)
    - Maintain file list synchronization
    """
    
    def __init__(self, hostname=None, port=None, repo_path=None):
        """
        Initialize client
        
        Args:
            hostname: Client hostname (auto-generated if None)
            port: Client listening port (auto-assigned if None)
            repo_path: Repository path (default if None)
        """
        # Setup hostname and port
        if port is None:
            port = self._find_available_port()
        
        self.port = port
        
        if hostname is None:
            import platform
            hostname = f"{platform.node()}_{port}"
        
        self.hostname = hostname
        
        # Setup repository
        if repo_path is None:
            repo_path = os.path.join(DEFAULT_REPO_PATH, self.hostname)
        
        self.repo_path = repo_path
        self.file_manager = FileManager(repo_path)
        
        # Logger
        self.logger = setup_logger(f'Client-{self.hostname}')
        
        # Server connection
        self.server_socket = None
        self.server_connected = False
        
        # Peer server (for receiving requests)
        self.peer_server = PeerServer(CLIENT_HOST, self.port, self.file_manager)
        
        # Background threads
        self.running = False
        self.ping_thread = None
    
    def _find_available_port(self):
        """Find an available port in the range"""
        for port in range(*DEFAULT_CLIENT_PORT_RANGE):
            try:
                test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_socket.bind((CLIENT_HOST, port))
                test_socket.close()
                return port
            except OSError:
                continue
        raise RuntimeError("No available ports in range")
    
    def start(self):
        """Start the client"""
        try:
            # Start peer server
            self.peer_server.start()
            
            # Connect to server - must succeed to continue
            if not self.connect_to_server():
                self.peer_server.stop()  # Clean up peer server
                raise ConnectionError("Failed to connect to server - Server may be offline")
            
            self.running = True
            
            # Start background tasks
            self.ping_thread = threading.Thread(target=self._ping_worker, daemon=True)
            self.ping_thread.start()
            
            self.logger.info(f"Client started: {self.hostname} on port {self.port}")
            self.logger.info(f"Repository: {self.repo_path}")
            
        except Exception as e:
            self.logger.error(f"Error starting client: {e}")
            raise
    
    def stop(self):
        """Stop the client"""
        self.running = False
        
        # Stop peer server
        self.peer_server.stop()
        
        # Disconnect from server
        self.disconnect_from_server()
        
        self.logger.info("Client stopped")
    
    def connect_to_server(self, server_host=SERVER_HOST, server_port=SERVER_PORT):
        """
        Connect to centralized server and register
        Implements connect_to_server() function
        
        Args:
            server_host: Server hostname
            server_port: Server port
            
        Returns:
            bool: True if successful
        """
        try:
            # Create socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.connect((server_host, server_port))
            
            # Send HELLO message (server will create full hostname)
            hello_msg = Protocol.build_message(MessageType.HELLO, self.hostname, self.port)
            self.server_socket.send(hello_msg.encode(ENCODING))
            
            # Wait for OK response
            response = self.server_socket.recv(BUFFER_SIZE).decode(ENCODING)
            msg_type, msg_data = Protocol.parse_message(response)
            
            if msg_type == MessageType.OK:
                self.server_connected = True
                self.logger.info(f"Connected to server at {server_host}:{server_port}")
                
                # Sync initial file list
                self.update_file_list()
                
                return True
            else:
                self.logger.error(f"Server connection failed: {response}")
                return False
        
        except Exception as e:
            self.logger.error(f"Error connecting to server: {e}")
            self.server_connected = False
            return False
    
    def disconnect_from_server(self):
        """Disconnect from server"""
        if self.server_socket:
            try:
                # Send BYE message before disconnecting
                bye_msg = Protocol.build_message(MessageType.BYE)
                self.server_socket.send(bye_msg.encode(ENCODING))
                
                # Wait for server to process BYE
                time.sleep(0.5)
            except:
                pass
            
            try:
                self.server_socket.close()
            except:
                pass
            self.server_socket = None
        
        self.server_connected = False
        self.logger.info("Disconnected from server")
    
    def publish(self, lname, fname=None):
        """
        Publish a local file to the network
        Implements publish lname fname command
        
        Args:
            lname: Local filename (in repository)
            fname: Application name (same as lname if None)
            
        Returns:
            bool: True if successful
        """
        if fname is None:
            fname = lname
        
        # Check if file exists
        if not self.file_manager.file_exists(lname):
            self.logger.error(f"File not found in repository: {lname}")
            return False
        
        try:
            # Send PUBLISH message (server knows our full hostname from registration)
            # We need to use full hostname here for index
            full_hostname = Protocol.format_hostname(self.hostname, self.port)
            publish_msg = Protocol.build_message(MessageType.PUBLISH, fname, full_hostname)
            self.server_socket.send(publish_msg.encode(ENCODING))
            
            # Wait for response
            response = self.server_socket.recv(BUFFER_SIZE).decode(ENCODING)
            msg_type, msg_data = Protocol.parse_message(response)
            
            if msg_type == MessageType.OK:
                self.logger.info(f"File published: {fname}")
                return True
            else:
                self.logger.error(f"Publish failed: {response}")
                return False
        
        except Exception as e:
            self.logger.error(f"Error publishing file: {e}")
            return False
    
    def fetch(self, fname):
        """
        Fetch a file from the network
        Implements fetch fname command
        
        Workflow:
        1. Check if file already exists locally
        2. Send FETCH to server to get provider list
        3. Connect to a provider peer
        4. Send GET request to peer
        5. Receive file data via TCP stream
        
        Args:
            fname: Filename to fetch
            
        Returns:
            bool: True if successful
        """
        try:
            # Step 0: Check if file already exists
            if self.file_manager.file_exists(fname):
                self.logger.info(f"File already exists locally: {fname}")
                return True
            
            # Step 1: Send FETCH request to server
            fetch_msg = Protocol.build_message(MessageType.FETCH, fname)
            self.server_socket.send(fetch_msg.encode(ENCODING))
            
            # Wait for RESULT with provider list
            response = self.server_socket.recv(BUFFER_SIZE).decode(ENCODING)
            msg_type, msg_data = Protocol.parse_message(response)
            
            if msg_type == MessageType.RESULT:
                providers = msg_data['hostnames']
                
                if not providers:
                    self.logger.warning(f"No providers found for file: {fname}")
                    return False
                
                self.logger.info(f"Found {len(providers)} provider(s) for {fname}: {providers}")
                
                # Step 2: Try to download from first available provider
                full_hostname = Protocol.format_hostname(self.hostname, self.port)
                for provider_hostname in providers:
                    # Skip if provider is self
                    if provider_hostname == full_hostname:
                        self.logger.debug(f"Skipping self: {provider_hostname}")
                        continue
                    
                    success = self._download_from_peer(fname, provider_hostname)
                    if success:
                        return True
                
                self.logger.error(f"Failed to download from any provider")
                return False
            
            else:
                self.logger.error(f"Fetch failed: {response}")
                return False
        
        except Exception as e:
            self.logger.error(f"Error fetching file: {e}")
            return False
    
    def _download_from_peer(self, fname, provider_hostname):
        """
        Download file from a specific peer
        
        Args:
            fname: Filename
            provider_hostname: Provider hostname (format: "hostname:port")
            
        Returns:
            bool: True if successful
        """
        try:
            # Parse provider hostname
            if ':' in provider_hostname:
                parts = provider_hostname.rsplit(':', 1)  # Split from right
                host = parts[0]
                port = int(parts[1])
            else:
                self.logger.error(f"Invalid provider hostname format: {provider_hostname}")
                return False
            
            # If host doesn't look like an IP address, assume it's a client name on localhost
            # IP addresses have dots (e.g., 192.168.1.1), client names don't
            if '.' not in host:
                # It's a client name, use localhost
                actual_host = '127.0.0.1'
                self.logger.debug(f"Converting client name '{host}' to localhost")
            else:
                actual_host = host
            
            self.logger.info(f"Downloading {fname} from {actual_host}:{port}")
            
            # Connect to peer
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.connect((actual_host, port))
            
            # Send GET request with our full hostname
            full_hostname = Protocol.format_hostname(self.hostname, self.port)
            get_msg = Protocol.build_message(MessageType.GET, fname, full_hostname)
            peer_socket.send(get_msg.encode(ENCODING))
            
            # Receive DATA header
            header_data = peer_socket.recv(BUFFER_SIZE).decode(ENCODING)
            msg_type, msg_data = Protocol.parse_message(header_data)
            
            if msg_type == MessageType.DATA:
                file_size = msg_data['size']
                self.logger.info(f"Receiving file: {fname} ({file_size} bytes)")
                
                # Receive file content
                received_data = b''
                while len(received_data) < file_size:
                    chunk = peer_socket.recv(CHUNK_SIZE)
                    if not chunk:
                        break
                    received_data += chunk
                
                # Save file
                if len(received_data) == file_size:
                    self.file_manager.write_file(fname, received_data)
                    self.logger.info(f"File downloaded successfully: {fname}")
                    
                    # Update file list with server
                    self.update_file_list()
                    
                    peer_socket.close()
                    return True
                else:
                    self.logger.error(f"Incomplete file transfer: {len(received_data)}/{file_size} bytes")
            
            elif msg_type == MessageType.ERROR:
                self.logger.error(f"Peer error: {msg_data}")
            
            peer_socket.close()
            return False
        
        except Exception as e:
            self.logger.error(f"Error downloading from peer: {e}")
            return False
    
    def update_file_list(self):
        """
        Synchronize file list with server
        Implements update_file_list() function
        
        Returns:
            bool: True if successful
        """
        try:
            # Get current files in repository
            files = self.file_manager.list_files()
            
            # Use full hostname for update
            full_hostname = Protocol.format_hostname(self.hostname, self.port)
            
            # Send UPDATE message
            update_msg = Protocol.build_message(MessageType.UPDATE, full_hostname, files)
            self.server_socket.send(update_msg.encode(ENCODING))
            
            # Wait for response
            response = self.server_socket.recv(BUFFER_SIZE).decode(ENCODING)
            msg_type, msg_data = Protocol.parse_message(response)
            
            if msg_type == MessageType.OK:
                self.logger.info(f"File list updated: {len(files)} file(s)")
                return True
            else:
                self.logger.error(f"Update failed: {response}")
                return False
        
        except Exception as e:
            self.logger.error(f"Error updating file list: {e}")
            return False
    
    def discover(self):
        """
        Discover all files in the network
        Implements discover command
        
        Returns:
            dict: Dictionary of {filename: [providers]}
        """
        try:
            # Send DISCOVER message
            discover_msg = Protocol.build_message(MessageType.DISCOVER)
            self.server_socket.send(discover_msg.encode(ENCODING))
            
            # Receive response
            response = self.server_socket.recv(BUFFER_SIZE).decode(ENCODING)
            
            # Parse multi-line response
            lines = response.split('\n')
            if lines[0].startswith('RESULT'):
                file_dict = {}
                for line in lines[1:]:
                    if ':' in line:
                        parts = line.split(':', 1)
                        fname = parts[0].strip()
                        providers = [p.strip() for p in parts[1].split(',')]
                        file_dict[fname] = providers
                
                self.logger.info(f"Discovery: found {len(file_dict)} file(s)")
                return file_dict
            
            return {}
        
        except Exception as e:
            self.logger.error(f"Error discovering files: {e}")
            return {}
    
    def ping_server(self):
        """
        Ping server for liveness check
        Implements ping command
        
        Returns:
            bool: True if server is alive
        """
        try:
            # Use full hostname for ping
            full_hostname = Protocol.format_hostname(self.hostname, self.port)
            
            # Send PING message
            ping_msg = Protocol.build_message(MessageType.PING, full_hostname)
            self.server_socket.send(ping_msg.encode(ENCODING))
            
            # Wait for ALIVE response
            response = self.server_socket.recv(BUFFER_SIZE).decode(ENCODING)
            msg_type, msg_data = Protocol.parse_message(response)
            
            if msg_type == MessageType.ALIVE:
                self.logger.debug("Server is alive")
                return True
            
            return False
        
        except Exception as e:
            self.logger.error(f"Error pinging server: {e}")
            return False
    
    def _ping_worker(self):
        """Background worker to ping server periodically"""
        while self.running:
            try:
                time.sleep(PING_INTERVAL)
                if self.server_connected:
                    self.ping_server()
            except Exception as e:
                self.logger.error(f"Ping worker error: {e}")
    
    def add_file_to_repo(self, source_path, fname=None):
        """
        Add a file to repository from external source
        
        Args:
            source_path: Source file path
            fname: Target filename (basename of source if None)
            
        Returns:
            bool: True if successful
        """
        if fname is None:
            fname = os.path.basename(source_path)
        
        success = self.file_manager.add_file(fname, source_path)
        
        if success:
            # Update server
            self.update_file_list()
        
        return success


def main():
    """Main entry point for client with interactive shell"""
    import sys
    
    # Parse command line arguments
    port = None
    hostname = None
    repo_path = None
    
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    if len(sys.argv) > 2:
        hostname = sys.argv[2]
    if len(sys.argv) > 3:
        repo_path = sys.argv[3]
    
    # Create and start client
    client = Client(hostname=hostname, port=port, repo_path=repo_path)
    
    try:
        client.start()
        
        # Interactive shell
        print(f"\n{'='*60}")
        print(f"File Sharing Client - {client.hostname}")
        print(f"Repository: {client.repo_path}")
        print(f"Listening on port: {client.port}")
        print(f"{'='*60}\n")
        print("Commands:")
        print("  publish <lname> [fname]  - Publish a file")
        print("  fetch <fname>            - Fetch a file from network")
        print("  discover                 - List all files in network")
        print("  list                     - List local files")
        print("  ping                     - Ping server")
        print("  add <path> [fname]       - Add file to repository")
        print("  quit                     - Exit")
        print()
        
        while True:
            try:
                cmd = input(f"{client.hostname}> ").strip()
                
                if not cmd:
                    continue
                
                parts = cmd.split()
                command = parts[0].lower()
                
                if command == 'quit' or command == 'exit':
                    break
                
                elif command == 'publish':
                    if len(parts) < 2:
                        print("Usage: publish <lname> [fname]")
                    else:
                        lname = parts[1]
                        fname = parts[2] if len(parts) > 2 else lname
                        client.publish(lname, fname)
                
                elif command == 'fetch':
                    if len(parts) < 2:
                        print("Usage: fetch <fname>")
                    else:
                        fname = parts[1]
                        client.fetch(fname)
                
                elif command == 'discover':
                    files = client.discover()
                    if files:
                        print("\nFiles in network:")
                        for fname, providers in files.items():
                            print(f"  {fname}: {', '.join(providers)}")
                    else:
                        print("No files found in network")
                
                elif command == 'list':
                    files = client.file_manager.list_files()
                    if files:
                        print("\nLocal files:")
                        for f in files:
                            size = client.file_manager.get_file_size(f)
                            print(f"  {f} ({size} bytes)")
                    else:
                        print("No files in repository")
                
                elif command == 'ping':
                    if client.ping_server():
                        print("Server is alive")
                    else:
                        print("Server is not responding")
                
                elif command == 'add':
                    if len(parts) < 2:
                        print("Usage: add <path> [fname]")
                    else:
                        source_path = parts[1]
                        fname = parts[2] if len(parts) > 2 else None
                        if client.add_file_to_repo(source_path, fname):
                            print(f"File added: {fname or os.path.basename(source_path)}")
                        else:
                            print("Failed to add file")
                
                else:
                    print(f"Unknown command: {command}")
            
            except KeyboardInterrupt:
                print()
                break
            except Exception as e:
                print(f"Error: {e}")
        
        print("\nShutting down client...")
        client.stop()
    
    except Exception as e:
        print(f"Client error: {e}")
        client.stop()


if __name__ == "__main__":
    main()
