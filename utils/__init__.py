"""
Logging utilities for the application
"""

import logging
import sys
from config import LOG_LEVEL, LOG_FORMAT


def setup_logger(name, level=None):
    """
    Setup logger with consistent formatting
    
    Args:
        name: Logger name
        level: Log level (default from config)
        
    Returns:
        logging.Logger: Configured logger
    """
    if level is None:
        level = LOG_LEVEL
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level))
    
    # Avoid duplicate handlers
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, level))
        
        formatter = logging.Formatter(LOG_FORMAT)
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
    
    return logger
