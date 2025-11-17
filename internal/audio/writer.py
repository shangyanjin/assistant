"""
Audio tag writer - write metadata tags
"""
import os
from typing import Dict, Optional, Any
try:
    from mutagen import File as MutagenFile
    from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TRCK, TCON, TPE2, ID3NoHeaderError
    from mutagen.mp3 import MP3
    from mutagen.flac import FLAC
    from mutagen.mp4 import MP4
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False


class AudioWriter:
    """Write audio file metadata tags"""
    
    def __init__(self):
        """Initialize writer"""
        if not MUTAGEN_AVAILABLE:
            raise ImportError("mutagen library is required. Install with: pip install mutagen")
    
    def write_tags(self, file_path: str, tags: Dict[str, Any], encoding: str = 'utf-8') -> bool:
        """
        Write tags to audio file
        
        Args:
            file_path: Path to audio file
            tags: Dictionary with tag information
            encoding: Encoding for text tags (default: utf-8)
            
        Returns:
            True if successful
        """
        if not os.path.exists(file_path):
            return False
        
        try:
            audio_file = MutagenFile(file_path)
            if audio_file is None:
                return False
            
            # MP3 files
            if isinstance(audio_file, MP3) or file_path.lower().endswith('.mp3'):
                return self._write_mp3_tags(file_path, tags, encoding)
            
            # FLAC files
            elif isinstance(audio_file, FLAC) or file_path.lower().endswith('.flac'):
                return self._write_flac_tags(audio_file, tags, encoding)
            
            # MP4/M4A files
            elif isinstance(audio_file, MP4) or file_path.lower().endswith(('.m4a', '.mp4')):
                return self._write_mp4_tags(audio_file, tags, encoding)
            
            # Generic fallback
            return self._write_generic_tags(audio_file, tags, encoding)
            
        except Exception as e:
            return False
    
    def _write_mp3_tags(self, file_path: str, tags: Dict[str, Any], encoding: str) -> bool:
        """Write MP3 tags using ID3v2.4"""
        try:
            try:
                audio_file = ID3(file_path)
            except ID3NoHeaderError:
                audio_file = ID3()
            
            # Title
            if 'title' in tags and tags['title']:
                audio_file['TIT2'] = TIT2(encoding=3, text=tags['title'])
            
            # Artist
            if 'artist' in tags and tags['artist']:
                audio_file['TPE1'] = TPE1(encoding=3, text=tags['artist'])
            
            # Album
            if 'album' in tags and tags['album']:
                audio_file['TALB'] = TALB(encoding=3, text=tags['album'])
            
            # Year/Date
            if 'year' in tags and tags['year']:
                audio_file['TDRC'] = TDRC(encoding=3, text=str(tags['year']))
            
            # Track number
            if 'track' in tags and tags['track']:
                audio_file['TRCK'] = TRCK(encoding=3, text=str(tags['track']))
            
            # Genre
            if 'genre' in tags and tags['genre']:
                audio_file['TCON'] = TCON(encoding=3, text=tags['genre'])
            
            # Album Artist
            if 'albumartist' in tags and tags['albumartist']:
                audio_file['TPE2'] = TPE2(encoding=3, text=tags['albumartist'])
            
            audio_file.save(file_path, v2_version=4)
            return True
            
        except Exception:
            return False
    
    def _write_flac_tags(self, audio_file: FLAC, tags: Dict[str, Any], encoding: str) -> bool:
        """Write FLAC tags"""
        try:
            if 'title' in tags and tags['title']:
                audio_file['TITLE'] = [tags['title']]
            if 'artist' in tags and tags['artist']:
                audio_file['ARTIST'] = [tags['artist']]
            if 'album' in tags and tags['album']:
                audio_file['ALBUM'] = [tags['album']]
            if 'date' in tags and tags['date']:
                audio_file['DATE'] = [str(tags['date'])]
            elif 'year' in tags and tags['year']:
                audio_file['DATE'] = [str(tags['year'])]
            if 'track' in tags and tags['track']:
                audio_file['TRACKNUMBER'] = [str(tags['track'])]
            if 'genre' in tags and tags['genre']:
                audio_file['GENRE'] = [tags['genre']]
            if 'albumartist' in tags and tags['albumartist']:
                audio_file['ALBUMARTIST'] = [tags['albumartist']]
            
            audio_file.save()
            return True
        except Exception:
            return False
    
    def _write_mp4_tags(self, audio_file: MP4, tags: Dict[str, Any], encoding: str) -> bool:
        """Write MP4/M4A tags"""
        try:
            if 'title' in tags and tags['title']:
                audio_file['\xa9nam'] = [tags['title']]
            if 'artist' in tags and tags['artist']:
                audio_file['\xa9ART'] = [tags['artist']]
            if 'album' in tags and tags['album']:
                audio_file['\xa9alb'] = [tags['album']]
            if 'date' in tags and tags['date']:
                audio_file['\xa9day'] = [str(tags['date'])]
            elif 'year' in tags and tags['year']:
                audio_file['\xa9day'] = [str(tags['year'])]
            if 'track' in tags and tags['track']:
                track_num = int(tags['track']) if str(tags['track']).isdigit() else 0
                audio_file['trkn'] = [(track_num, 0)]
            if 'genre' in tags and tags['genre']:
                audio_file['\xa9gen'] = [tags['genre']]
            if 'albumartist' in tags and tags['albumartist']:
                audio_file['aART'] = [tags['albumartist']]
            
            audio_file.save()
            return True
        except Exception:
            return False
    
    def _write_generic_tags(self, audio_file: Any, tags: Dict[str, Any], encoding: str) -> bool:
        """Write generic tags (fallback)"""
        try:
            tag_map = {
                'title': 'title',
                'artist': 'artist',
                'album': 'album',
                'year': 'date',
                'track': 'tracknumber',
                'genre': 'genre',
                'albumartist': 'albumartist'
            }
            
            for key, value in tags.items():
                if key in tag_map and value:
                    tag_key = tag_map[key]
                    if tag_key in audio_file:
                        audio_file[tag_key] = [str(value)]
            
            audio_file.save()
            return True
        except Exception:
            return False


