"""
Path utilities
"""
import sys
import os


def get_resource_path(relative_path: str) -> str:
    """
    Get resource file path (supports packaged execution)
    
    Args:
        relative_path: Relative path from project root
        
    Returns:
        Absolute path to resource file
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    else:
        # Get the directory of the main.py file
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    return os.path.join(base_path, relative_path)

