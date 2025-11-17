"""
Audio tag reader - read metadata tags
"""
import os
from typing import Dict, Optional, Any
try:
    from mutagen import File as MutagenFile
    from mutagen.id3 import ID3NoHeaderError
    from mutagen.mp3 import MP3
    from mutagen.flac import FLAC
    from mutagen.mp4 import MP4
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False


class AudioTagger:
    """Read audio file metadata tags"""
    
    def __init__(self):
        """Initialize tagger"""
        if not MUTAGEN_AVAILABLE:
            raise ImportError("mutagen library is required. Install with: pip install mutagen")
    
    def read_tags(self, file_path: str) -> Dict[str, Any]:
        """
        Read tags from audio file
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Dictionary with tag information
        """
        if not os.path.exists(file_path):
            return {}
        
        try:
            audio_file = MutagenFile(file_path)
            if audio_file is None:
                return {}
            
            tags = {
                'file': os.path.basename(file_path),
                'path': file_path,
                'title': self._get_tag(audio_file, 'title'),
                'artist': self._get_tag(audio_file, 'artist'),
                'album': self._get_tag(audio_file, 'album'),
                'year': self._get_tag(audio_file, 'date'),
                'track': self._get_tag(audio_file, 'tracknumber'),
                'genre': self._get_tag(audio_file, 'genre'),
                'albumartist': self._get_tag(audio_file, 'albumartist'),
            }
            
            # Get file info
            if hasattr(audio_file, 'info'):
                info = audio_file.info
                if hasattr(info, 'length'):
                    tags['duration'] = int(info.length)
                if hasattr(info, 'bitrate'):
                    tags['bitrate'] = info.bitrate
            
            return tags
        except (ID3NoHeaderError, Exception) as e:
            return {
                'file': os.path.basename(file_path),
                'path': file_path,
                'error': str(e)
            }
    
    def _get_tag(self, audio_file: Any, tag_name: str) -> Optional[str]:
        """Get tag value from audio file"""
        try:
            # MP3 files
            if isinstance(audio_file, MP3):
                if tag_name == 'title':
                    return self._get_first_value(audio_file.get('TIT2', []))
                elif tag_name == 'artist':
                    return self._get_first_value(audio_file.get('TPE1', []))
                elif tag_name == 'album':
                    return self._get_first_value(audio_file.get('TALB', []))
                elif tag_name == 'date':
                    return self._get_first_value(audio_file.get('TDRC', []))
                elif tag_name == 'tracknumber':
                    return self._get_first_value(audio_file.get('TRCK', []))
                elif tag_name == 'genre':
                    return self._get_first_value(audio_file.get('TCON', []))
                elif tag_name == 'albumartist':
                    return self._get_first_value(audio_file.get('TPE2', []))
            
            # FLAC files
            elif isinstance(audio_file, FLAC):
                tag_map = {
                    'title': 'TITLE',
                    'artist': 'ARTIST',
                    'album': 'ALBUM',
                    'date': 'DATE',
                    'tracknumber': 'TRACKNUMBER',
                    'genre': 'GENRE',
                    'albumartist': 'ALBUMARTIST'
                }
                if tag_name in tag_map:
                    return self._get_first_value(audio_file.get(tag_map[tag_name], []))
            
            # MP4/M4A files
            elif isinstance(audio_file, MP4):
                tag_map = {
                    'title': '\xa9nam',
                    'artist': '\xa9ART',
                    'album': '\xa9alb',
                    'date': '\xa9day',
                    'tracknumber': 'trkn',
                    'genre': '\xa9gen',
                    'albumartist': 'aART'
                }
                if tag_name in tag_map:
                    value = audio_file.get(tag_map[tag_name], [])
                    if value:
                        if tag_name == 'tracknumber':
                            # MP4 tracknumber is a tuple
                            if isinstance(value[0], tuple):
                                return str(value[0][0])
                            return str(value[0])
                        return str(value[0])
            
            # Generic fallback
            if tag_name in audio_file:
                return self._get_first_value(audio_file[tag_name])
            
        except Exception:
            pass
        
        return None
    
    def _get_first_value(self, value_list: Any) -> Optional[str]:
        """Get first value from list or return as string"""
        if not value_list:
            return None
        
        if isinstance(value_list, list) and len(value_list) > 0:
            return str(value_list[0])
        
        return str(value_list) if value_list else None
    
    def has_tags(self, file_path: str) -> bool:
        """Check if file has tags"""
        try:
            audio_file = MutagenFile(file_path)
            return audio_file is not None and len(audio_file) > 0
        except Exception:
            return False


