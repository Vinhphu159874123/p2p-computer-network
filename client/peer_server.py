"""
Peer Server for Client
Handles P2P file transfer requests from other peers
"""

import socket
import threading
from protocol import Protocol, MessageType
from config import BUFFER_SIZE, ENCODING, CHUNK_SIZE
from utils import setup_logger


class PeerServer:
    """
    P2P Server component running on each client
    Handles incoming file requests from other peers
    
    This implements the receive_request() function from requirements
    """
    
    def __init__(self, host, port, file_manager):
        self.host = host
        self.port = port
        self.file_manager = file_manager
        self.logger = setup_logger('PeerServer')
        
        # Server socket
        self.server_socket = None
        self.running = False
    
    def start(self):
        """Start the peer server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            
            self.running = True
            self.logger.info(f"Peer server started on {self.host}:{self.port}")
            
            # Accept connections in background thread
            accept_thread = threading.Thread(target=self._accept_connections, daemon=True)
            accept_thread.start()
            
        except Exception as e:
            self.logger.error(f"Error starting peer server: {e}")
            raise
    
    def stop(self):
        """Stop the peer server"""
        self.running = False
        
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        self.logger.info("Peer server stopped")
    
    def _accept_connections(self):
        """Accept incoming connections from peers"""
        while self.running:
            try:
                peer_socket, peer_address = self.server_socket.accept()
                self.logger.info(f"Peer connected: {peer_address}")
                
                # Handle peer request in new thread
                handler_thread = threading.Thread(
                    target=self._handle_peer_request,
                    args=(peer_socket, peer_address),
                    daemon=True
                )
                handler_thread.start()
                
            except Exception as e:
                if self.running:
                    self.logger.error(f"Error accepting peer connection: {e}")
    
    def _handle_peer_request(self, peer_socket, peer_address):
        """
        Handle file request from peer
        
        This implements the receive_request() function:
        - Listen for incoming GET requests
        - Validate file existence
        - Send file using TCP data stream
        
        Args:
            peer_socket: Peer socket
            peer_address: Peer address
        """
        try:
            # Receive GET request
            data = peer_socket.recv(BUFFER_SIZE)
            if not data:
                return
            
            message = data.decode(ENCODING).strip()
            self.logger.info(f"Received request from {peer_address}: {message}")
            
            # Parse message
            msg_type, msg_data = Protocol.parse_message(message)
            
            if msg_type == MessageType.GET:
                fname = msg_data['fname']
                requesting_hostname = msg_data.get('hostname', 'unknown')
                
                self.logger.info(f"Peer {requesting_hostname} requesting file: {fname}")
                
                # Check if file exists
                if not self.file_manager.file_exists(fname):
                    # Send error
                    error_msg = Protocol.build_message(MessageType.ERROR, "NOT_FOUND", "File not found")
                    peer_socket.send(error_msg.encode(ENCODING))
                    self.logger.warning(f"File not found: {fname}")
                    return
                
                # Get file size
                file_size = self.file_manager.get_file_size(fname)
                
                # Send DATA header
                data_header = Protocol.build_message(MessageType.DATA, fname, file_size)
                peer_socket.send(data_header.encode(ENCODING))
                
                # Small delay to ensure header is processed
                import time
                time.sleep(0.1)
                
                # Send file content in chunks
                file_content = self.file_manager.read_file(fname)
                if file_content:
                    total_sent = 0
                    while total_sent < len(file_content):
                        chunk = file_content[total_sent:total_sent + CHUNK_SIZE]
                        sent = peer_socket.send(chunk)
                        total_sent += sent
                    
                    self.logger.info(f"File sent to {requesting_hostname}: {fname} ({file_size} bytes)")
                else:
                    self.logger.error(f"Error reading file: {fname}")
            
            else:
                # Unknown request
                error_msg = Protocol.build_message(MessageType.ERROR, "INVALID", "Invalid request")
                peer_socket.send(error_msg.encode(ENCODING))
        
        except Exception as e:
            self.logger.error(f"Error handling peer request: {e}")
        
        finally:
            try:
                peer_socket.close()
            except:
                pass
