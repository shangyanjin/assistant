"""
Encoding detection and conversion
"""
from typing import Optional, Tuple
try:
    import chardet
    CHARDET_AVAILABLE = True
except ImportError:
    CHARDET_AVAILABLE = False


class EncodingDetector:
    """Detect and convert text encoding"""
    
    # Common encodings to try
    COMMON_ENCODINGS = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'big5', 'latin1', 'cp1252']
    
    def detect_encoding(self, data: bytes) -> Optional[str]:
        """
        Detect encoding of byte data
        
        Args:
            data: Byte data to detect
            
        Returns:
            Detected encoding name or None
        """
        if not data:
            return None
        
        if CHARDET_AVAILABLE:
            try:
                result = chardet.detect(data)
                if result and result['encoding']:
                    return result['encoding'].lower()
            except Exception:
                pass
        
        # Try common encodings
        for encoding in self.COMMON_ENCODINGS:
            try:
                data.decode(encoding)
                return encoding
            except (UnicodeDecodeError, LookupError):
                continue
        
        return None
    
    def is_valid_utf8(self, text: str) -> bool:
        """Check if text is valid UTF-8"""
        try:
            text.encode('utf-8').decode('utf-8')
            return True
        except (UnicodeEncodeError, UnicodeDecodeError):
            return False
    
    def convert_to_utf8(self, text: str, source_encoding: Optional[str] = None) -> Tuple[str, Optional[str]]:
        """
        Convert text to UTF-8
        
        Args:
            text: Text to convert (as string)
            source_encoding: Source encoding (if known)
            
        Returns:
            Tuple of (converted_text, detected_encoding)
        """
        if not text:
            return text, None
        
        # If already valid UTF-8, return as is
        if self.is_valid_utf8(text):
            return text, 'utf-8'
        
        # Try to detect encoding from bytes
        try:
            # Try to encode as latin1 first to get bytes
            data = text.encode('latin1')
            detected = self.detect_encoding(data)
            
            if detected and detected != 'utf-8':
                try:
                    decoded = data.decode(detected)
                    # Re-encode to UTF-8
                    utf8_text = decoded.encode('utf-8').decode('utf-8')
                    return utf8_text, detected
                except (UnicodeDecodeError, UnicodeEncodeError):
                    pass
        except Exception:
            pass
        
        # Try common encodings
        if source_encoding:
            encodings_to_try = [source_encoding] + [e for e in self.COMMON_ENCODINGS if e != source_encoding]
        else:
            encodings_to_try = self.COMMON_ENCODINGS
        
        for encoding in encodings_to_try:
            try:
                # Encode as latin1 to get bytes, then decode with target encoding
                data = text.encode('latin1')
                decoded = data.decode(encoding)
                utf8_text = decoded.encode('utf-8').decode('utf-8')
                return utf8_text, encoding
            except (UnicodeDecodeError, UnicodeEncodeError, LookupError):
                continue
        
        # If all fails, return original
        return text, None
    
    def has_encoding_issue(self, text: str) -> bool:
        """Check if text has encoding issues (garbled characters)"""
        if not text:
            return False
        
        # Check for common garbled patterns
        garbled_patterns = [
            '\ufffd',  # Replacement character
            '\x00',    # Null bytes
        ]
        
        for pattern in garbled_patterns:
            if pattern in text:
                return True
        
        # Check if contains non-printable characters (except common ones)
        try:
            for char in text:
                if ord(char) > 127 and not char.isprintable():
                    return True
        except Exception:
            pass
        
        return False

