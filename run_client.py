"""
Script to run a client
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from client import Client


def main():
    """
    Main entry point
    
    Usage:
        python run_client.py [port] [hostname] [repo_path]
    """
    port = None
    hostname = None
    repo_path = None
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port: {sys.argv[1]}")
            sys.exit(1)
    
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
                        if client.publish(lname, fname):
                            print(f"✓ Published: {fname}")
                        else:
                            print(f"✗ Failed to publish: {fname}")
                
                elif command == 'fetch':
                    if len(parts) < 2:
                        print("Usage: fetch <fname>")
                    else:
                        fname = parts[1]
                        if client.fetch(fname):
                            print(f"✓ Downloaded: {fname}")
                        else:
                            print(f"✗ Failed to download: {fname}")
                
                elif command == 'discover':
                    files = client.discover()
                    if files:
                        print("\n📁 Files in network:")
                        for fname, providers in files.items():
                            print(f"  • {fname}")
                            print(f"    Providers: {', '.join(providers)}")
                        print()
                    else:
                        print("No files found in network")
                
                elif command == 'list':
                    files = client.file_manager.list_files()
                    if files:
                        print("\n📂 Local files:")
                        for f in files:
                            size = client.file_manager.get_file_size(f)
                            print(f"  • {f} ({size:,} bytes)")
                        print()
                    else:
                        print("No files in repository")
                
                elif command == 'ping':
                    if client.ping_server():
                        print("✓ Server is alive")
                    else:
                        print("✗ Server is not responding")
                
                elif command == 'add':
                    if len(parts) < 2:
                        print("Usage: add <path> [fname]")
                    else:
                        source_path = parts[1]
                        fname = parts[2] if len(parts) > 2 else None
                        if client.add_file_to_repo(source_path, fname):
                            final_name = fname or os.path.basename(source_path)
                            print(f"✓ File added: {final_name}")
                        else:
                            print("✗ Failed to add file")
                
                elif command == 'help':
                    print("\nAvailable commands:")
                    print("  publish <lname> [fname]  - Publish a file to the network")
                    print("  fetch <fname>            - Download a file from network")
                    print("  discover                 - List all files in network")
                    print("  list                     - List files in local repository")
                    print("  ping                     - Check server connectivity")
                    print("  add <path> [fname]       - Add external file to repository")
                    print("  quit/exit                - Exit the application")
                    print()
                
                else:
                    print(f"Unknown command: {command}. Type 'help' for available commands.")
            
            except KeyboardInterrupt:
                print()
                break
            except EOFError:
                break
            except Exception as e:
                print(f"Error: {e}")
        
        print("\n👋 Shutting down client...")
        client.stop()
    
    except Exception as e:
        print(f"Client error: {e}")
        import traceback
        traceback.print_exc()
        client.stop()


if __name__ == "__main__":
    main()
