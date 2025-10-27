"""
Main Server Implementation
Centralized Index Server for Hybrid P2P File Sharing
"""

import socket
import threading
import time
from server.index_manager import IndexManager
from protocol import Protocol, MessageType
from config import SERVER_HOST, SERVER_PORT, BUFFER_SIZE, ENCODING
from utils import setup_logger


class Server:
    """
    Centralized Index Server
    
    Responsibilities:
    - Accept client connections
    - Maintain file index and client registry
    - Handle client requests (HELLO, PUBLISH, UPDATE, FETCH, PING, DISCOVER)
    - Monitor client liveness
    """
    
    def __init__(self, host=SERVER_HOST, port=SERVER_PORT):
        self.host = host
        self.port = port
        self.logger = setup_logger('Server')
        
        # Index manager
        self.index_manager = IndexManager()
        
        # Server socket
        self.server_socket = None
        self.running = False
        
        # Client connections: {hostname: socket}
        self.client_connections = {}
        self.connections_lock = threading.Lock()
        
    def start(self):
        """Start the server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            
            self.running = True
            self.logger.info(f"Server started on {self.host}:{self.port}")
            
            # Start cleanup thread
            cleanup_thread = threading.Thread(target=self._cleanup_worker, daemon=True)
            cleanup_thread.start()
            
            # Accept client connections
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    self.logger.info(f"New connection from {client_address}")
                    
                    # Handle client in a new thread
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, client_address),
                        daemon=True
                    )
                    client_thread.start()
                    
                except Exception as e:
                    if self.running:
                        self.logger.error(f"Error accepting connection: {e}")
        
        except Exception as e:
            self.logger.error(f"Server error: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the server"""
        self.running = False
        
        # Close all client connections
        with self.connections_lock:
            for hostname, sock in list(self.client_connections.items()):
                try:
                    sock.close()
                except:
                    pass
            self.client_connections.clear()
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        self.logger.info("Server stopped")
    
    def _handle_client(self, client_socket, client_address):
        """
        Handle client connection
        
        Args:
            client_socket: Client socket
            client_address: Client address tuple
        """
        hostname = None
        
        try:
            while self.running:
                # Receive message
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    break
                
                message = data.decode(ENCODING).strip()
                self.logger.debug(f"Received from {client_address}: {message}")
                
                # Parse message
                msg_type, msg_data = Protocol.parse_message(message)
                
                if not msg_type:
                    self._send_error(client_socket, "INVALID", "Invalid message format")
                    continue
                
                # Handle different message types
                if msg_type == MessageType.HELLO:
                    response = self._handle_hello(msg_data, client_socket)
                    hostname = msg_data['hostname']
                
                elif msg_type == MessageType.PUBLISH:
                    response = self._handle_publish(msg_data)
                
                elif msg_type == MessageType.UPDATE:
                    response = self._handle_update(msg_data)
                
                elif msg_type == MessageType.FETCH:
                    response = self._handle_fetch(msg_data)
                
                elif msg_type == MessageType.PING:
                    response = self._handle_ping(msg_data)
                
                elif msg_type == MessageType.DISCOVER:
                    response = self._handle_discover(msg_data)
                
                else:
                    response = Protocol.build_message(MessageType.ERROR, "UNKNOWN", "Unknown command")
                
                # Send response
                if response:
                    self._send_message(client_socket, response)
        
        except Exception as e:
            self.logger.error(f"Error handling client {client_address}: {e}")
        
        finally:
            # Clean up
            if hostname:
                with self.connections_lock:
                    if hostname in self.client_connections:
                        del self.client_connections[hostname]
                # Note: We don't deregister client here as they might reconnect
            
            try:
                client_socket.close()
            except:
                pass
            
            self.logger.info(f"Connection closed: {client_address}")
    
    def _handle_hello(self, data, client_socket):
        """
        Handle HELLO message - client registration
        
        Args:
            data: Parsed message data
            client_socket: Client socket
            
        Returns:
            str: Response message
        """
        hostname = data['hostname']
        port = data['port']
        
        # Create full hostname with port
        full_hostname = f"{hostname}:{port}"
        
        # Register client with full hostname
        self.index_manager.register_client(full_hostname, port)
        
        # Store connection
        with self.connections_lock:
            self.client_connections[full_hostname] = client_socket
        
        self.logger.info(f"Client registered: {full_hostname}")
        return Protocol.build_message(MessageType.OK, "registered")
    
    def _handle_publish(self, data):
        """
        Handle PUBLISH message - register file
        
        Args:
            data: Parsed message data
            
        Returns:
            str: Response message
        """
        fname = data['fname']
        hostname = data['hostname']
        
        # Register file in index
        success = self.index_manager.register_file(fname, hostname)
        
        if success:
            self.logger.info(f"File published: {fname} by {hostname}")
            return Protocol.build_message(MessageType.OK, "published")
        else:
            return Protocol.build_message(MessageType.ERROR, "PUBLISH_FAILED", "Failed to publish file")
    
    def _handle_update(self, data):
        """
        Handle UPDATE message - sync file list
        
        Args:
            data: Parsed message data
            
        Returns:
            str: Response message
        """
        hostname = data['hostname']
        files = data['files']
        
        # Sync client's file list
        success = self.index_manager.sync_client_files(hostname, files)
        
        if success:
            self.logger.info(f"File list updated for {hostname}: {len(files)} file(s)")
            return Protocol.build_message(MessageType.OK, "synchronized")
        else:
            return Protocol.build_message(MessageType.ERROR, "UPDATE_FAILED", "Client not registered")
    
    def _handle_fetch(self, data):
        """
        Handle FETCH message - lookup file providers
        
        Args:
            data: Parsed message data
            
        Returns:
            str: Response message with provider list
        """
        fname = data['fname']
        
        # Lookup providers
        providers = self.index_manager.lookup_providers(fname)
        
        self.logger.info(f"Fetch request for {fname}: {len(providers)} provider(s)")
        return Protocol.build_message(MessageType.RESULT, providers)
    
    def _handle_ping(self, data):
        """
        Handle PING message - liveness check
        
        Args:
            data: Parsed message data
            
        Returns:
            str: Response message
        """
        hostname = data.get('hostname')
        
        if hostname:
            # Update client's last seen
            self.index_manager.update_client_liveness(hostname)
            self.logger.debug(f"Ping from {hostname}")
        
        return Protocol.build_message(MessageType.ALIVE)
    
    def _handle_discover(self, data):
        """
        Handle DISCOVER message - get file list
        
        Args:
            data: Parsed message data
            
        Returns:
            str: Response message with file list
        """
        hostname = data.get('hostname')
        
        if hostname:
            # Get files for specific client
            files = self.index_manager.get_all_files(hostname)
            file_list = ' '.join(files) if files else ''
            self.logger.info(f"Discover request from {hostname}: {len(files)} file(s)")
            return f"RESULT {file_list}".strip()
        else:
            # Get all files in the system
            all_files = self.index_manager.get_all_files()
            result_lines = []
            for fname, providers in all_files.items():
                result_lines.append(f"{fname}: {', '.join(providers)}")
            
            if result_lines:
                return "RESULT\n" + "\n".join(result_lines)
            else:
                return "RESULT"
    
    def _send_message(self, client_socket, message):
        """
        Send message to client
        
        Args:
            client_socket: Client socket
            message: Message string
        """
        try:
            client_socket.send(message.encode(ENCODING))
            self.logger.debug(f"Sent: {message}")
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
    
    def _send_error(self, client_socket, code, description):
        """
        Send error message to client
        
        Args:
            client_socket: Client socket
            code: Error code
            description: Error description
        """
        error_msg = Protocol.build_message(MessageType.ERROR, code, description)
        self._send_message(client_socket, error_msg)
    
    def _cleanup_worker(self):
        """Background worker to cleanup inactive clients"""
        while self.running:
            try:
                time.sleep(60)  # Run every minute
                self.index_manager.cleanup_inactive_clients(timeout=300)
            except Exception as e:
                self.logger.error(f"Cleanup error: {e}")


def main():
    """Main entry point for server"""
    server = Server()
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.stop()


if __name__ == "__main__":
    main()
