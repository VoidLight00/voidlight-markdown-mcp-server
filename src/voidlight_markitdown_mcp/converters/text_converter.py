"""
Text file converter
"""

from typing import BinaryIO, Dict, Any, Optional
import logging

from ..core.base_converter import DocumentConverter, DocumentConverterResult
from ..core.stream_info import StreamInfo
from ..core.exceptions import FileConversionException
from ..utils.stream_utils import read_stream_with_encoding
from ..utils.format_utils import normalize_whitespace, extract_title_from_content

logger = logging.getLogger(__name__)


class TextConverter(DocumentConverter):
    """Plain text file converter"""
    
    def __init__(self, korean_support: bool = True):
        super().__init__(korean_support=korean_support)
        self.priority = 10.0  # Lowest priority (fallback converter)
        
        self.supported_extensions = ['.txt', '.text', '.log', '.md', '.rst']
        self.supported_mimetypes = ['text/plain', 'text/markdown', 'text/x-rst']
        self.category = 'documents'
    
    def accepts(self, file_stream: BinaryIO, stream_info: StreamInfo, **kwargs) -> bool:
        """Check if this converter can handle the file"""
        # Check extension
        if stream_info.matches_extension(self.supported_extensions):
            return True
        
        # Check MIME type
        if stream_info.matches_mimetype(self.supported_mimetypes):
            return True
        
        # Check if it's a text file by trying to decode
        try:
            current_pos = file_stream.tell()
            file_stream.seek(0)
            sample = file_stream.read(8192)
            file_stream.seek(current_pos)
            
            # Try to decode as text
            try:
                sample.decode('utf-8')
                return True
            except UnicodeDecodeError:
                # Try other encodings
                for encoding in ['cp949', 'euc-kr', 'latin-1']:
                    try:
                        sample.decode(encoding)
                        return True
                    except UnicodeDecodeError:
                        continue
            
            return False
            
        except Exception:
            return False
    
    def convert(self, file_stream: BinaryIO, stream_info: StreamInfo, **kwargs) -> DocumentConverterResult:
        """Convert text file to markdown"""
        logger.info(f"Converting text file: {stream_info.filename}")
        
        try:
            # Read text content
            text_content = read_stream_with_encoding(file_stream, stream_info.charset)
            
            # Normalize whitespace
            text_content = normalize_whitespace(text_content)
            
            # Extract title
            title = extract_title_from_content(text_content) or self._extract_title_from_filename(stream_info.filename)
            
            # Create markdown
            markdown = self._text_to_markdown(text_content, title)
            
            # Extract metadata
            metadata = self._extract_metadata(file_stream, stream_info)
            metadata.update({
                'word_count': len(text_content.split()),
                'character_count': len(text_content),
                'line_count': len(text_content.split('\\n'))
            })
            
            return DocumentConverterResult(
                markdown=self._clean_markdown(markdown),
                title=self._format_title(title) if title else None,
                metadata=metadata
            )
            
        except Exception as e:
            raise FileConversionException(f"Text conversion failed: {e}")
    
    def _text_to_markdown(self, text: str, title: Optional[str] = None) -> str:
        """Convert plain text to markdown format"""
        markdown = ""
        
        # Add title if available
        if title:
            markdown += f"# {title}\\n\\n"
        
        # Handle different text formats
        if self._looks_like_markdown(text):
            # Already markdown, return as-is
            markdown += text
        else:
            # Convert plain text to markdown
            markdown += self._plain_text_to_markdown(text)
        
        return markdown
    
    def _looks_like_markdown(self, text: str) -> bool:
        """Check if text already looks like markdown"""
        import re
        
        # Check for markdown syntax
        markdown_patterns = [
            r'^#+\\s',  # Headers
            r'^\\*\\s',  # Unordered lists
            r'^\\d+\\.\\s',  # Ordered lists
            r'\\*\\*[^*]+\\*\\*',  # Bold
            r'\\*[^*]+\\*',  # Italic
            r'\\[[^\\]]+\\]\\([^\\)]+\\)',  # Links
            r'```',  # Code blocks
        ]
        
        for pattern in markdown_patterns:
            if re.search(pattern, text, re.MULTILINE):
                return True
        
        return False
    
    def _plain_text_to_markdown(self, text: str) -> str:
        """Convert plain text to markdown"""
        lines = text.split('\\n')
        markdown_lines = []
        
        for line in lines:
            line = line.strip()
            
            if not line:
                markdown_lines.append("")
                continue
            
            # Try to detect structure
            if self._looks_like_heading(line):
                # Convert to heading
                level = self._get_heading_level(line)
                markdown_lines.append(f"{'#' * level} {line}")
            elif self._looks_like_list_item(line):
                # Convert to list item
                markdown_lines.append(f"- {line}")
            else:
                # Regular paragraph
                markdown_lines.append(line)
        
        return '\\n'.join(markdown_lines)
    
    def _looks_like_heading(self, line: str) -> bool:
        """Check if line looks like a heading"""
        # Short lines that don't end with punctuation
        if len(line) < 100 and not line.endswith(('.', '!', '?', ':')):
            return True
        
        # Lines that start with numbers (1. Introduction)
        if line.startswith(tuple('0123456789')):
            return True
        
        return False
    
    def _get_heading_level(self, line: str) -> int:
        """Determine heading level"""
        # Count dots in numbered headings (1.1.1 -> level 3)
        if line.startswith(tuple('0123456789')):
            dots = line.split()[0].count('.')
            return min(dots + 1, 6)
        
        # Default to level 2
        return 2
    
    def _looks_like_list_item(self, line: str) -> bool:
        """Check if line looks like a list item"""
        # Lines starting with bullet points or dashes
        if line.startswith(('•', '·', '-', '*')):
            return True
        
        # Lines starting with numbers followed by )
        import re
        if re.match(r'^\\d+\\)\\s', line):
            return True
        
        return False
    
    def _extract_title_from_filename(self, filename: Optional[str]) -> Optional[str]:
        """Extract title from filename"""
        if not filename:
            return None
        
        # Remove extension
        title = filename
        if '.' in title:
            title = title.rsplit('.', 1)[0]
        
        # Replace underscores and hyphens with spaces
        title = title.replace('_', ' ').replace('-', ' ')
        
        # Capitalize first letter
        title = title.strip().capitalize()
        
        return title if title else None
    
    def get_format_info(self) -> Dict[str, Any]:
        """Get format information"""
        return {
            'name': 'Text',
            'description': 'Plain text file converter with smart formatting detection',
            'extensions': self.supported_extensions,
            'mimetypes': self.supported_mimetypes,
            'category': self.category,
            'features': [
                'Automatic encoding detection',
                'Smart heading detection', 
                'List item detection',
                'Markdown preservation',
                'Korean text support'
            ]
        }