"""
Stream processing utilities
"""

import io
from typing import BinaryIO, Optional, List
import logging

logger = logging.getLogger(__name__)


def make_stream_seekable(stream: BinaryIO, max_size: int = 100 * 1024 * 1024) -> BinaryIO:
    """
    Make a stream seekable by copying to memory buffer if necessary.
    
    Args:
        stream: Input stream
        max_size: Maximum size to copy (default 100MB)
        
    Returns:
        Seekable stream
    """
    if stream.seekable():
        return stream
    
    # Copy to memory buffer
    buffer = io.BytesIO()
    
    try:
        copied = 0
        while copied < max_size:
            chunk = stream.read(min(8192, max_size - copied))
            if not chunk:
                break
            buffer.write(chunk)
            copied += len(chunk)
        
        if copied >= max_size:
            logger.warning(f"Stream truncated at {max_size} bytes")
        
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        logger.error(f"Failed to make stream seekable: {e}")
        raise


def read_stream_with_encoding(stream: BinaryIO, 
                            encoding: Optional[str] = None,
                            fallback_encodings: Optional[List[str]] = None) -> str:
    """
    Read stream content as text with automatic encoding detection.
    
    Args:
        stream: Input stream
        encoding: Preferred encoding
        fallback_encodings: List of fallback encodings to try
        
    Returns:
        Decoded text content
    """
    if fallback_encodings is None:
        fallback_encodings = ['utf-8', 'cp949', 'euc-kr', 'latin-1']
    
    # Read stream content
    current_pos = stream.tell()
    stream.seek(0)
    content = stream.read()
    stream.seek(current_pos)
    
    # Try specified encoding first
    if encoding:
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            logger.warning(f"Specified encoding {encoding} failed")
    
    # Try automatic detection
    try:
        import chardet
        detected = chardet.detect(content)
        if detected['encoding'] and detected['confidence'] > 0.8:
            return content.decode(detected['encoding'])
    except ImportError:
        pass
    
    # Try fallback encodings
    for enc in fallback_encodings:
        try:
            return content.decode(enc)
        except UnicodeDecodeError:
            continue
    
    # Last resort: decode with error handling
    return content.decode('utf-8', errors='ignore')


def get_stream_info(stream: BinaryIO) -> dict:
    """
    Get information about a stream.
    
    Args:
        stream: Input stream
        
    Returns:
        Dictionary with stream information
    """
    info = {
        'readable': stream.readable(),
        'writable': stream.writable(),
        'seekable': stream.seekable(),
        'closed': stream.closed,
        'size': None,
        'position': None
    }
    
    try:
        if stream.seekable():
            current_pos = stream.tell()
            stream.seek(0, 2)  # Seek to end
            info['size'] = stream.tell()
            stream.seek(current_pos)  # Restore position
            info['position'] = current_pos
    except Exception as e:
        logger.debug(f"Failed to get stream info: {e}")
    
    return info


def copy_stream(source: BinaryIO, target: BinaryIO, chunk_size: int = 8192) -> int:
    """
    Copy data from source stream to target stream.
    
    Args:
        source: Source stream
        target: Target stream
        chunk_size: Size of chunks to copy
        
    Returns:
        Number of bytes copied
    """
    copied = 0
    
    while True:
        chunk = source.read(chunk_size)
        if not chunk:
            break
        target.write(chunk)
        copied += len(chunk)
    
    return copied