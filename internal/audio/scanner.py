"""
Audio file scanner - recursive directory scanning
"""
import os
from typing import List, Dict, Tuple


class AudioScanner:
    """Recursive audio file scanner"""
    
    # Supported audio formats
    AUDIO_EXTENSIONS = {'.mp3', '.flac', '.m4a', '.aac', '.ogg', '.wma', '.wav', '.ape', '.mp4'}
    
    def __init__(self):
        """Initialize scanner"""
        self.files: List[str] = []
        self.stats: Dict[str, int] = {
            'total': 0,
            'mp3': 0,
            'flac': 0,
            'm4a': 0,
            'other': 0
        }
    
    def scan_directory(self, root_path: str, recursive: bool = True) -> List[str]:
        """
        Scan directory for audio files
        
        Args:
            root_path: Root directory path
            recursive: Whether to scan subdirectories
            
        Returns:
            List of audio file paths
        """
        self.files = []
        self.stats = {'total': 0, 'mp3': 0, 'flac': 0, 'm4a': 0, 'other': 0}
        
        if recursive:
            self._scan_recursive(root_path)
        else:
            self._scan_directory(root_path)
        
        return self.files
    
    def _scan_recursive(self, path: str):
        """Recursively scan directory"""
        try:
            for root, dirs, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if self._is_audio_file(file_path):
                        self.files.append(file_path)
                        self._update_stats(file_path)
        except (PermissionError, OSError):
            pass
    
    def _scan_directory(self, path: str):
        """Scan single directory (non-recursive)"""
        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isfile(item_path) and self._is_audio_file(item_path):
                    self.files.append(item_path)
                    self._update_stats(item_path)
        except (PermissionError, OSError):
            pass
    
    def _is_audio_file(self, file_path: str) -> bool:
        """Check if file is an audio file"""
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.AUDIO_EXTENSIONS
    
    def _update_stats(self, file_path: str):
        """Update statistics"""
        ext = os.path.splitext(file_path)[1].lower()
        self.stats['total'] += 1
        
        if ext == '.mp3':
            self.stats['mp3'] += 1
        elif ext == '.flac':
            self.stats['flac'] += 1
        elif ext == '.m4a':
            self.stats['m4a'] += 1
        else:
            self.stats['other'] += 1
    
    def get_statistics(self) -> Dict[str, int]:
        """Get scan statistics"""
        return self.stats.copy()


