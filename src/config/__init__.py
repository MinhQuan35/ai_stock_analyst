"""
Configuration module re-export for backward compatibility.
"""
from src.utils.config import Settings, get_settings, settings

__all__ = ["Settings", "get_settings", "settings"]
