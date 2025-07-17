"""
Base converter classes for MarkItDown MCP Enhanced
"""

from abc import ABC, abstractmethod
from typing import BinaryIO, Dict, Any, Optional, List
from dataclasses import dataclass

from .stream_info import StreamInfo


@dataclass
class DocumentConverterResult:
    """Result of document conversion"""
    
    markdown: str
    title: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @property
    def text_content(self) -> str:
        """Backward compatibility alias for markdown"""
        return self.markdown


class DocumentConverter(ABC):
    """Base class for document converters"""
    
    def __init__(self, korean_support: bool = False):
        self.korean_support = korean_support
        self.priority = 0.0
        
        # Default format information
        self.supported_extensions: List[str] = []
        self.supported_mimetypes: List[str] = []
        self.category: str = "documents"
    
    @abstractmethod
    def accepts(self, file_stream: BinaryIO, stream_info: StreamInfo, **kwargs) -> bool:
        """
        Determine if this converter can handle the given file.
        
        Args:
            file_stream: The file stream to check
            stream_info: Information about the stream
            **kwargs: Additional arguments
            
        Returns:
            True if this converter can handle the file, False otherwise
        """
        pass
    
    @abstractmethod
    def convert(self, file_stream: BinaryIO, stream_info: StreamInfo, **kwargs) -> DocumentConverterResult:
        """
        Convert the file to markdown.
        
        Args:
            file_stream: The file stream to convert
            stream_info: Information about the stream
            **kwargs: Additional arguments
            
        Returns:
            DocumentConverterResult containing the markdown and metadata
        """
        pass
    
    def get_format_info(self) -> Dict[str, Any]:
        """Get information about supported formats"""
        return {
            'name': self.__class__.__name__.replace('Converter', ''),
            'description': self.__doc__ or 'No description',
            'extensions': getattr(self, 'supported_extensions', []),
            'mimetypes': getattr(self, 'supported_mimetypes', []),
            'category': getattr(self, 'category', 'documents'),
            'korean_support': self.korean_support,
            'priority': self.priority
        }
    
    def _normalize_korean_text(self, text: str) -> str:
        """Normalize Korean text if Korean support is enabled"""
        if not self.korean_support or not text:
            return text
        
        import re
        
        # Korean spacing normalization
        text = re.sub(r'(\S)\s+(\S)', r'\1 \2', text)
        
        # Korean punctuation normalization
        korean_punctuation = {
            '․': '.', '，': ',', '：': ':', '；': ';', '？': '?', '！': '!',
            '（': '(', '）': ')', '「': '"', '」': '"', '『': '"', '』': '"'
        }
        
        for korean, english in korean_punctuation.items():
            text = text.replace(korean, english)
        
        return text
    
    def _extract_metadata(self, stream: Optional[BinaryIO], stream_info: StreamInfo) -> Dict[str, Any]:
        """Extract basic metadata from stream and stream info"""
        metadata = {}
        
        if stream_info.filename:
            metadata['filename'] = stream_info.filename
        
        if stream_info.mimetype:
            metadata['mimetype'] = stream_info.mimetype
        
        if stream_info.url:
            metadata['source_url'] = stream_info.url
        
        if stream_info.local_path:
            from pathlib import Path
            try:
                path = Path(stream_info.local_path)
                if path.exists():
                    metadata['file_size'] = path.stat().st_size
                    metadata['modification_time'] = path.stat().st_mtime
            except:
                pass
        
        return metadata
    
    def _format_title(self, title: str) -> str:
        """Format and clean title"""
        if not title:
            return ""
        
        # Clean title
        title = title.strip()
        
        # Apply Korean normalization if enabled
        if self.korean_support:
            title = self._normalize_korean_text(title)
        
        # Truncate if too long
        if len(title) > 100:
            title = title[:97] + "..."
        
        return title
    
    def _clean_markdown(self, markdown: str) -> str:
        """Clean and normalize markdown output"""
        if not markdown:
            return ""
        
        import re
        
        # Remove excessive blank lines
        markdown = re.sub(r'\n\s*\n\s*\n', '\n\n', markdown)
        
        # Strip leading and trailing whitespace
        markdown = markdown.strip()
        
        # Apply Korean normalization if enabled
        if self.korean_support:
            markdown = self._normalize_korean_text(markdown)
        
        return markdown