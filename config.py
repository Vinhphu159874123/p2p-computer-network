"""
Configuration file for File Sharing Application
"""

# Server Configuration
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5000

# Client Configuration
CLIENT_HOST = '0.0.0.0'  # Listen on all interfaces for P2P connections
DEFAULT_CLIENT_PORT_RANGE = (5001, 6000)  # Range for client listening ports

# Protocol Configuration
BUFFER_SIZE = 4096
ENCODING = 'utf-8'
CHUNK_SIZE = 10240  # 10KB chunks for file transfer

# Timeouts
CONNECTION_TIMEOUT = 30
PING_INTERVAL = 60  # Ping every 60 seconds
PING_TIMEOUT = 10

# Repository
DEFAULT_REPO_PATH = './repository'  # Default local repository path

# Logging
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
