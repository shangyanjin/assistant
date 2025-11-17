"""
Audio processor - batch processing coordinator
"""
import os
import re
import threading
from typing import List, Dict, Callable, Optional
from queue import Queue
from internal.audio.scanner import AudioScanner
from internal.audio.tagger import AudioTagger
from internal.audio.writer import AudioWriter
from internal.audio.encoder import EncodingDetector


class AudioProcessor:
    """Batch audio file processor"""
    
    def __init__(self, num_workers: int = 4):
        """
        Initialize processor
        
        Args:
            num_workers: Number of worker threads
        """
        self.num_workers = num_workers
        self.scanner = AudioScanner()
        self.tagger = AudioTagger()
        self.writer = AudioWriter()
        self.encoder = EncodingDetector()
        self.progress_callback: Optional[Callable] = None
        self.is_running = False
    
    def set_progress_callback(self, callback: Callable):
        """Set progress callback function"""
        self.progress_callback = callback
    
    def process_directory(self, root_path: str, options: Dict) -> Dict:
        """
        Process all audio files in directory
        
        Args:
            root_path: Root directory path
            options: Processing options:
                - fix_encoding: Fix encoding issues
                - auto_album: Auto-detect album from directory name
                - auto_title: Auto-generate title with zero-padding
                - update_tags: Update tags
                
        Returns:
            Processing statistics
        """
        self.is_running = True
        
        # Scan files
        files = self.scanner.scan_directory(root_path, recursive=True)
        stats = self.scanner.get_statistics()
        
        if not files:
            return {'total': 0, 'processed': 0, 'errors': 0, 'fixed': 0}
        
        # Process files
        results = {
            'total': len(files),
            'processed': 0,
            'errors': 0,
            'fixed': 0,
            'updated': 0,
            'renamed': 0
        }
        
        if self.num_workers > 1:
            results = self._process_multithreaded(files, root_path, options)
        else:
            results = self._process_singlethreaded(files, root_path, options)
        
        self.is_running = False
        return results
    
    def _process_singlethreaded(self, files: List[str], root_path: str, options: Dict) -> Dict:
        """Process files in single thread"""
        results = {
            'total': len(files),
            'processed': 0,
            'errors': 0,
            'fixed': 0,
            'updated': 0,
            'renamed': 0
        }
        
        for file_path in files:
            if not self.is_running:
                break
            
            try:
                result = self._process_file(file_path, root_path, options)
                results['processed'] += 1
                if result.get('fixed'):
                    results['fixed'] += 1
                if result.get('updated'):
                    results['updated'] += 1
                if result.get('renamed'):
                    results['renamed'] += 1
                
                if self.progress_callback:
                    self.progress_callback(file_path, results['processed'], results['total'], result)
                    
            except Exception as e:
                results['errors'] += 1
                if self.progress_callback:
                    self.progress_callback(file_path, results['processed'], results['total'], {'error': str(e)})
        
        return results
    
    def _process_multithreaded(self, files: List[str], root_path: str, options: Dict) -> Dict:
        """Process files using multiple threads"""
        queue = Queue()
        for file_path in files:
            queue.put(file_path)
        
        results = {
            'total': len(files),
            'processed': 0,
            'errors': 0,
            'fixed': 0,
            'updated': 0,
            'renamed': 0
        }
        results_lock = threading.Lock()
        
        def worker():
            while self.is_running:
                try:
                    file_path = queue.get(timeout=1)
                except:
                    break
                
                try:
                    result = self._process_file(file_path, root_path, options)
                    
                    with results_lock:
                        results['processed'] += 1
                        if result.get('fixed'):
                            results['fixed'] += 1
                        if result.get('updated'):
                            results['updated'] += 1
                        if result.get('renamed'):
                            results['renamed'] += 1
                    
                    if self.progress_callback:
                        self.progress_callback(file_path, results['processed'], results['total'], result)
                        
                except Exception as e:
                    with results_lock:
                        results['errors'] += 1
                    if self.progress_callback:
                        self.progress_callback(file_path, results['processed'], results['total'], {'error': str(e)})
                
                queue.task_done()
        
        threads = []
        for _ in range(min(self.num_workers, len(files))):
            t = threading.Thread(target=worker, daemon=True)
            t.start()
            threads.append(t)
        
        queue.join()
        
        return results
    
    def _process_file(self, file_path: str, root_path: str, options: Dict) -> Dict:
        """Process single file"""
        result = {'fixed': False, 'updated': False, 'renamed': False}
        
        # Read current tags
        tags = self.tagger.read_tags(file_path)
        if 'error' in tags:
            return result
        
        # Fix encoding if needed
        if options.get('fix_encoding', False):
            fixed = self._fix_encoding(tags)
            if fixed:
                result['fixed'] = True
        
        # Auto-detect album from directory
        if options.get('auto_album', False):
            album = self._detect_album(file_path, root_path)
            if album and (not tags.get('album') or options.get('overwrite_album', False)):
                tags['album'] = album
        
        # Auto-generate title with zero-padding
        if options.get('auto_title', False):
            title = self._generate_title(file_path, root_path)
            if title and (not tags.get('title') or options.get('overwrite_title', False)):
                tags['title'] = title
        
        # Update tags
        if options.get('update_tags', False):
            if self.writer.write_tags(file_path, tags):
                result['updated'] = True
        
        # Format filename
        if options.get('format_filename', False):
            new_name = self._format_filename(file_path, tags, root_path)
            if new_name:
                renamed = self._rename_file(file_path, new_name)
                if renamed:
                    result['renamed'] = True
                    # Update file_path for subsequent operations
                    file_path = os.path.join(os.path.dirname(file_path), new_name)
        
        return result
    
    def _fix_encoding(self, tags: Dict) -> bool:
        """Fix encoding issues in tags"""
        fixed = False
        
        text_fields = ['title', 'artist', 'album', 'genre', 'albumartist']
        for field in text_fields:
            if field in tags and tags[field]:
                text = tags[field]
                if self.encoder.has_encoding_issue(text):
                    fixed_text, detected = self.encoder.convert_to_utf8(text)
                    if fixed_text != text:
                        tags[field] = fixed_text
                        fixed = True
        
        return fixed
    
    def _detect_album(self, file_path: str, root_path: str) -> Optional[str]:
        """Detect album name from directory structure"""
        try:
            # Get relative path from root
            rel_path = os.path.relpath(file_path, root_path)
            dir_path = os.path.dirname(rel_path)
            
            if dir_path and dir_path != '.':
                # Use directory name as album
                album = os.path.basename(dir_path)
                return album.strip()
            
            # If in root, use root directory name
            album = os.path.basename(root_path)
            return album.strip() if album else None
            
        except Exception:
            return None
    
    def _generate_title(self, file_path: str, root_path: str) -> Optional[str]:
        """Generate title from filename with zero-padding"""
        try:
            filename = os.path.basename(file_path)
            name, ext = os.path.splitext(filename)
            
            # Try to extract track number from filename
            # Patterns: "01 Title", "1. Title", "1-Title", etc.
            # Pattern: number at start
            match = re.match(r'^(\d+)', name)
            if match:
                track_num = int(match.group(1))
                # Zero-pad to 2 digits
                track_str = f"{track_num:02d}"
                # Get rest of name as title
                title_part = name[match.end():].strip(' .-')
                if title_part:
                    return f"{track_str} {title_part}"
                else:
                    return f"{track_str}"
            
            return name.strip()
            
        except Exception:
            return None
    
    def _clean_filename(self, filename: str) -> str:
        """
        Clean filename by removing ads and decorations
        
        Args:
            filename: Original filename
            
        Returns:
            Cleaned filename
        """
        # Common ad patterns and decorations
        ad_patterns = [
            r'[-]{2,}',  # Multiple dashes (----)
            r'[_]{2,}',  # Multiple underscores (____)
            r'[=]{2,}',  # Multiple equals (====)
            r'[~]{2,}',  # Multiple tildes (~~~~)
            r'[\.]{2,}',  # Multiple dots (....)
            r'^\s+',     # Leading spaces
            r'\s+$',     # Trailing spaces
            r'\s{2,}',   # Multiple spaces
        ]
        
        # Remove common ad keywords (case insensitive)
        ad_keywords = [
            r'www\.\w+\.(com|net|org|cn)',
            r'@\w+',
            r'\[.*?广告.*?\]',
            r'\(.*?广告.*?\)',
            r'\[.*?推广.*?\]',
            r'\(.*?推广.*?\)',
        ]
        
        cleaned = filename
        
        # Remove ad patterns
        for pattern in ad_patterns + ad_keywords:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Remove common separators at start/end
        cleaned = cleaned.strip(' -_=~.()[]【】（）')
        
        # Clean up multiple separators
        cleaned = re.sub(r'[-_\s]+', ' ', cleaned)
        cleaned = cleaned.strip()
        
        return cleaned
    
    def _format_filename(self, file_path: str, tags: Dict, root_path: str) -> Optional[str]:
        """
        Format filename as: Number + Album Style
        
        Args:
            file_path: Current file path
            tags: Audio tags
            root_path: Root directory path
            
        Returns:
            New filename or None
        """
        try:
            filename = os.path.basename(file_path)
            name, ext = os.path.splitext(filename)
            
            # Get track number from tags or filename
            track_num = None
            if tags.get('track'):
                track_str = str(tags['track']).split('/')[0].strip()
                if track_str.isdigit():
                    track_num = int(track_str)
            
            # If no track number in tags, try to extract from filename
            if track_num is None:
                match = re.match(r'^(\d+)', name)
                if match:
                    track_num = int(match.group(1))
            
            # Get album style from tags or directory
            album_style = None
            if tags.get('album'):
                album_style = tags['album']
            else:
                # Try to get from directory name
                album_style = self._detect_album(file_path, root_path)
            
            # If no album, try to extract from filename (after cleaning)
            if not album_style:
                cleaned_name = self._clean_filename(name)
                # Try to find album style pattern in filename
                # Common patterns: "Album - Title", "Album_Title", etc.
                parts = re.split(r'[-_\s]{2,}', cleaned_name)
                if len(parts) > 1:
                    # Assume first part might be album style
                    album_style = parts[0].strip()
            
            # Build new filename
            new_name_parts = []
            
            # Add track number (zero-padded)
            if track_num is not None:
                new_name_parts.append(f"{track_num:02d}")
            
            # Add album style
            if album_style:
                # Clean album style
                album_style = self._clean_filename(album_style)
                if album_style:
                    new_name_parts.append(album_style)
            
            # If we have parts, build new name
            if new_name_parts:
                new_name = ' '.join(new_name_parts)
                new_name = self._clean_filename(new_name)
                new_filename = new_name + ext
                
                # Only rename if different
                if new_filename != filename:
                    return new_filename
            
            return None
            
        except Exception:
            return None
    
    def _rename_file(self, old_path: str, new_filename: str) -> bool:
        """
        Rename file
        
        Args:
            old_path: Old file path
            new_filename: New filename (without path)
            
        Returns:
            True if successful
        """
        try:
            dir_path = os.path.dirname(old_path)
            new_path = os.path.join(dir_path, new_filename)
            
            # Check if new file already exists
            if os.path.exists(new_path) and new_path != old_path:
                return False
            
            os.rename(old_path, new_path)
            return True
        except Exception:
            return False
    
    def stop(self):
        """Stop processing"""
        self.is_running = False

