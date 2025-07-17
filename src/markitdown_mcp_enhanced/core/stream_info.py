"""
Stream information management for MarkItDown MCP Enhanced
"""

from dataclasses import dataclass
from typing import Optional, List
from pathlib import Path


@dataclass
class StreamInfo:
    """Information about a file stream"""
    
    mimetype: Optional[str] = None
    extension: Optional[str] = None
    charset: Optional[str] = None
    filename: Optional[str] = None
    local_path: Optional[str] = None
    url: Optional[str] = None
    
    def __post_init__(self):
        """Post-initialization processing"""
        # Normalize extension
        if self.extension and not self.extension.startswith('.'):
            self.extension = '.' + self.extension
        
        # Extract extension from filename if not provided
        if self.filename and not self.extension:
            self.extension = Path(self.filename).suffix.lower()
    
    def __str__(self) -> str:
        """String representation"""
        parts = []
        if self.mimetype:
            parts.append(f"mimetype={self.mimetype}")
        if self.extension:
            parts.append(f"ext={self.extension}")
        if self.filename:
            parts.append(f"filename={self.filename}")
        return f"StreamInfo({', '.join(parts)})"
    
    def __eq__(self, other) -> bool:
        """Equality comparison"""
        if not isinstance(other, StreamInfo):
            return False
        return (
            self.mimetype == other.mimetype and 
            self.extension == other.extension and
            self.filename == other.filename
        )
    
    def matches_extension(self, extensions: List[str]) -> bool:
        """Check if extension matches any in the list"""
        if not self.extension:
            return False
        return self.extension.lower() in [ext.lower() for ext in extensions]
    
    def matches_mimetype(self, mimetypes: List[str]) -> bool:
        """Check if mimetype matches any in the list"""
        if not self.mimetype:
            return False
        return any(self.mimetype.startswith(mt) for mt in mimetypes)
    
    def is_empty(self) -> bool:
        """Check if stream info is empty"""
        return not any([
            self.mimetype, self.extension, self.filename,
            self.local_path, self.url
        ])