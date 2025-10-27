"""
Script to run the centralized server
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import Server


def main():
    """Main entry point"""
    print("="*60)
    print("File Sharing Application - Centralized Server")
    print("="*60)
    print()
    
    server = Server()
    
    try:
        print("Starting server...")
        server.start()
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        server.stop()
    except Exception as e:
        print(f"\nServer error: {e}")
        server.stop()


if __name__ == "__main__":
    main()
