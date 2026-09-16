"""
Logger configuration
"""
import logging
import sys
from pathlib import Path
from src.utils.config import settings


def setup_logger(name: str = "agent") -> logging.Logger:
    """Setup logger."""
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, settings.app_log_level.upper(), logging.INFO))
    
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


logger = setup_logger()
