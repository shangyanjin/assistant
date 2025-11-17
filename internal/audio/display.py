"""
Progress display - wget/axel style output
"""
import os
import sys
import time
from typing import Dict, Optional


class ProgressDisplay:
    """Display progress in wget/axel style"""
    
    def __init__(self, output_stream=None):
        """
        Initialize display
        
        Args:
            output_stream: Output stream (default: sys.stdout)
        """
        self.output_stream = output_stream or sys.stdout
        self.start_time = None
        self.last_update_time = None
        self.last_file = None
    
    def start(self, total: int):
        """Start progress display"""
        self.start_time = time.time()
        self.last_update_time = self.start_time
        self.last_file = None
    
    def update(self, file_path: str, current: int, total: int, result: Optional[Dict] = None):
        """
        Update progress display
        
        Args:
            file_path: Current file path
            current: Current file number
            total: Total files
            result: Processing result
        """
        now = time.time()
        elapsed = now - self.start_time if self.start_time else 0
        
        # Calculate speed
        if elapsed > 0:
            speed = current / elapsed
        else:
            speed = 0
        
        # Calculate ETA
        if speed > 0:
            remaining = total - current
            eta = remaining / speed
            eta_str = self._format_time(eta)
        else:
            eta_str = "--:--"
        
        # Progress percentage
        if total > 0:
            percent = (current / total) * 100
        else:
            percent = 0
        
        # File name (truncate if too long)
        filename = os.path.basename(file_path)
        if len(filename) > 40:
            filename = filename[:37] + "..."
        
        # Status
        status = "OK"
        if result:
            if 'error' in result:
                status = "ERROR"
            elif result.get('fixed'):
                status = "FIXED"
            elif result.get('updated'):
                status = "UPDATED"
        
        # Format: [progress%] filename [status] [speed] [eta]
        line = f"[{percent:5.1f}%] {filename:40s} [{status:7s}] [{speed:.1f} files/s] [ETA: {eta_str}]"
        
        # Clear previous line and write new one
        if self.last_file:
            # Move cursor up and clear line
            self.output_stream.write('\r' + ' ' * 80 + '\r')
        
        self.output_stream.write(line)
        self.output_stream.flush()
        
        self.last_file = file_path
        self.last_update_time = now
    
    def finish(self, stats: Dict):
        """Finish and display summary"""
        self.output_stream.write('\n')
        
        elapsed = time.time() - self.start_time if self.start_time else 0
        
        summary = f"""
Processing complete:
  Total files:    {stats.get('total', 0)}
  Processed:      {stats.get('processed', 0)}
  Fixed encoding: {stats.get('fixed', 0)}
  Updated tags:   {stats.get('updated', 0)}
  Errors:         {stats.get('errors', 0)}
  Time elapsed:   {self._format_time(elapsed)}
"""
        self.output_stream.write(summary)
        self.output_stream.flush()
    
    def _format_time(self, seconds: float) -> str:
        """Format time in MM:SS format"""
        if seconds < 0:
            return "--:--"
        
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

