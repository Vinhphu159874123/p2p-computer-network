"""
File Manager for Client
Manages local file repository
"""

import os
import hashlib
from utils import setup_logger


class FileManager:
    """
    Manages client's local file repository
    
    Attributes:
        repo_path: Path to local repository directory
    """
    
    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.logger = setup_logger('FileManager')
        
        # Create repository directory if not exists
        if not os.path.exists(repo_path):
            os.makedirs(repo_path)
            self.logger.info(f"Created repository directory: {repo_path}")
    
    def get_file_path(self, fname):
        """
        Get full path for a filename
        
        Args:
            fname: Filename
            
        Returns:
            str: Full file path
        """
        return os.path.join(self.repo_path, fname)
    
    def list_files(self):
        """
        List all files in the repository
        
        Returns:
            list: List of filenames
        """
        try:
            files = [f for f in os.listdir(self.repo_path) 
                    if os.path.isfile(os.path.join(self.repo_path, f))]
            return files
        except Exception as e:
            self.logger.error(f"Error listing files: {e}")
            return []
    
    def file_exists(self, fname):
        """
        Check if file exists in repository
        
        Args:
            fname: Filename
            
        Returns:
            bool: True if file exists
        """
        file_path = self.get_file_path(fname)
        return os.path.isfile(file_path)
    
    def get_file_size(self, fname):
        """
        Get file size
        
        Args:
            fname: Filename
            
        Returns:
            int: File size in bytes, or -1 if error
        """
        try:
            file_path = self.get_file_path(fname)
            if os.path.isfile(file_path):
                return os.path.getsize(file_path)
            return -1
        except Exception as e:
            self.logger.error(f"Error getting file size: {e}")
            return -1
    
    def read_file(self, fname):
        """
        Read file content
        
        Args:
            fname: Filename
            
        Returns:
            bytes: File content or None if error
        """
        try:
            file_path = self.get_file_path(fname)
            with open(file_path, 'rb') as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"Error reading file {fname}: {e}")
            return None
    
    def write_file(self, fname, content):
        """
        Write file content
        
        Args:
            fname: Filename
            content: File content (bytes)
            
        Returns:
            bool: True if successful
        """
        try:
            file_path = self.get_file_path(fname)
            with open(file_path, 'wb') as f:
                f.write(content)
            self.logger.info(f"File written: {fname} ({len(content)} bytes)")
            return True
        except Exception as e:
            self.logger.error(f"Error writing file {fname}: {e}")
            return False
    
    def delete_file(self, fname):
        """
        Delete file from repository
        
        Args:
            fname: Filename
            
        Returns:
            bool: True if successful
        """
        try:
            file_path = self.get_file_path(fname)
            if os.path.isfile(file_path):
                os.remove(file_path)
                self.logger.info(f"File deleted: {fname}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error deleting file {fname}: {e}")
            return False
    
    def calculate_checksum(self, fname):
        """
        Calculate MD5 checksum of file
        
        Args:
            fname: Filename
            
        Returns:
            str: MD5 checksum hex string or None if error
        """
        try:
            file_path = self.get_file_path(fname)
            md5 = hashlib.md5()
            
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    md5.update(chunk)
            
            return md5.hexdigest()
        except Exception as e:
            self.logger.error(f"Error calculating checksum for {fname}: {e}")
            return None
    
    def add_file(self, fname, source_path):
        """
        Add file to repository by copying from source path
        
        Args:
            fname: Target filename
            source_path: Source file path
            
        Returns:
            bool: True if successful
        """
        try:
            import shutil
            target_path = self.get_file_path(fname)
            shutil.copy2(source_path, target_path)
            self.logger.info(f"File added to repository: {fname}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding file {fname}: {e}")
            return False
