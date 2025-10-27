"""
Protocol definitions for File Sharing Application
Based on Table 5: Control and Data Plane Message Formats
"""

class MessageType:
    """Message types for the protocol"""
    # Client -> Server
    HELLO = "HELLO"
    PUBLISH = "PUBLISH"
    UPDATE = "UPDATE"
    FETCH = "FETCH"
    PING = "PING"
    DISCOVER = "DISCOVER"
    
    # Server -> Client
    OK = "OK"
    ERROR = "ERROR"
    RESULT = "RESULT"
    ALIVE = "ALIVE"
    
    # Client -> Client (P2P)
    GET = "GET"
    DATA = "DATA"


class Protocol:
    """Protocol message builder and parser"""
    
    @staticmethod
    def build_message(msg_type, *args):
        """
        Build protocol message
        
        Args:
            msg_type: Message type from MessageType
            *args: Variable arguments based on message type
            
        Returns:
            str: Formatted message
        """
        if msg_type == MessageType.HELLO:
            # HELLO <hostname> <port>
            hostname, port = args
            return f"HELLO {hostname} {port}"
        
        elif msg_type == MessageType.PUBLISH:
            # PUBLISH <fname>|||<hostname>
            # Use ||| as separator to handle filenames with spaces
            fname, hostname = args
            return f"PUBLISH {fname}|||{hostname}"
        
        elif msg_type == MessageType.UPDATE:
            # UPDATE <hostname> <file1>|||<file2>|||<file3>...
            # Use ||| as separator to handle filenames with spaces
            hostname = args[0]
            files = args[1] if len(args) > 1 else []
            files_str = '|||'.join(files) if files else ''
            return f"UPDATE {hostname} {files_str}".strip()
        
        elif msg_type == MessageType.FETCH:
            # FETCH <fname>
            fname = args[0]
            return f"FETCH {fname}"
        
        elif msg_type == MessageType.RESULT:
            # RESULT <hostname1> <hostname2> ...
            hostnames = args[0] if args else []
            hostnames_str = ' '.join(hostnames) if hostnames else ''
            return f"RESULT {hostnames_str}".strip()
        
        elif msg_type == MessageType.GET:
            # GET <fname>|||<hostname>
            # Use ||| as separator to handle filenames with spaces
            fname, hostname = args
            return f"GET {fname}|||{hostname}"
        
        elif msg_type == MessageType.DATA:
            # DATA <fname>|||<size> + [binary stream]
            # Use ||| as separator to handle filenames with spaces
            fname, size = args
            return f"DATA {fname}|||{size}"
        
        elif msg_type == MessageType.PING:
            # PING <hostname> / ALIVE
            if args:
                hostname = args[0]
                return f"PING {hostname}"
            return "PING"
        
        elif msg_type == MessageType.ALIVE:
            return "ALIVE"
        
        elif msg_type == MessageType.DISCOVER:
            # DISCOVER <hostname>
            if args:
                hostname = args[0]
                return f"DISCOVER {hostname}"
            return "DISCOVER"
        
        elif msg_type == MessageType.OK:
            # OK <message>
            message = args[0] if args else "published"
            return f"OK {message}"
        
        elif msg_type == MessageType.ERROR:
            # ERROR <code> <description>
            code, description = args
            return f"ERROR {code} {description}"
        
        else:
            raise ValueError(f"Unknown message type: {msg_type}")
    
    @staticmethod
    def parse_message(message):
        """
        Parse protocol message
        
        Args:
            message: Raw message string
            
        Returns:
            tuple: (message_type, parsed_data)
        """
        if not message:
            return None, None
        
        parts = message.strip().split(maxsplit=1)
        if not parts:
            return None, None
        
        msg_type = parts[0].upper()
        data = parts[1] if len(parts) > 1 else None
        
        if msg_type == MessageType.HELLO:
            # HELLO <hostname> <port>
            if data:
                parts = data.split()
                hostname = parts[0]
                port = int(parts[1]) if len(parts) > 1 else None
                return msg_type, {'hostname': hostname, 'port': port}
        
        elif msg_type == MessageType.PUBLISH:
            # PUBLISH <fname>|||<hostname>
            if data:
                parts = data.split('|||')
                fname = parts[0]
                hostname = parts[1] if len(parts) > 1 else None
                return msg_type, {'fname': fname, 'hostname': hostname}
        
        elif msg_type == MessageType.UPDATE:
            # UPDATE <hostname> <file1>|||<file2>|||<file3>...
            if data:
                parts = data.split(maxsplit=1)
                hostname = parts[0]
                files = parts[1].split('|||') if len(parts) > 1 and parts[1] else []
                return msg_type, {'hostname': hostname, 'files': files}
        
        elif msg_type == MessageType.FETCH:
            # FETCH <fname>
            if data:
                return msg_type, {'fname': data.strip()}
        
        elif msg_type == MessageType.RESULT:
            # RESULT <hostname1> <hostname2> ...
            hostnames = data.split() if data else []
            return msg_type, {'hostnames': hostnames}
        
        elif msg_type == MessageType.GET:
            # GET <fname>|||<hostname>
            if data:
                parts = data.split('|||')
                fname = parts[0]
                hostname = parts[1] if len(parts) > 1 else None
                return msg_type, {'fname': fname, 'hostname': hostname}
        
        elif msg_type == MessageType.DATA:
            # DATA <fname>|||<size>
            if data:
                parts = data.split('|||')
                fname = parts[0]
                size = int(parts[1]) if len(parts) > 1 else 0
                return msg_type, {'fname': fname, 'size': size}
        
        elif msg_type == MessageType.PING:
            # PING <hostname> (optional)
            hostname = data.strip() if data else None
            return msg_type, {'hostname': hostname}
        
        elif msg_type == MessageType.DISCOVER:
            # DISCOVER <hostname> (optional)
            hostname = data.strip() if data else None
            return msg_type, {'hostname': hostname}
        
        elif msg_type == MessageType.ALIVE:
            return msg_type, {}
        
        elif msg_type == MessageType.OK:
            # OK <message>
            message = data.strip() if data else "success"
            return msg_type, {'message': message}
        
        elif msg_type == MessageType.ERROR:
            # ERROR <code> <description>
            if data:
                parts = data.split(maxsplit=1)
                code = parts[0]
                description = parts[1] if len(parts) > 1 else "Unknown error"
                return msg_type, {'code': code, 'description': description}
        
        return msg_type, {}
    
    @staticmethod
    def format_hostname(hostname, port):
        """Format hostname with port"""
        return f"{hostname}:{port}"
    
    @staticmethod
    def parse_hostname(hostname_str):
        """Parse hostname string to get host and port"""
        if ':' in hostname_str:
            parts = hostname_str.split(':')
            return parts[0], int(parts[1])
        return hostname_str, None
