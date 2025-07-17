"""
HTML file converter
"""

import re
from typing import BinaryIO, Dict, Any, Optional
import logging

from ..core.base_converter import DocumentConverter, DocumentConverterResult
from ..core.stream_info import StreamInfo
from ..core.exceptions import MissingDependencyException, FileConversionException
from ..utils.stream_utils import read_stream_with_encoding
from ..utils.format_utils import clean_html, normalize_whitespace

logger = logging.getLogger(__name__)


class HtmlConverter(DocumentConverter):
    """HTML file converter"""
    
    def __init__(self, korean_support: bool = True):
        super().__init__(korean_support=korean_support)
        self.priority = 2.0
        
        self.supported_extensions = ['.html', '.htm']
        self.supported_mimetypes = ['text/html', 'application/xhtml+xml']
        self.category = 'web'
        
        # Check dependencies
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Check for available dependencies"""
        try:
            from bs4 import BeautifulSoup
            self.bs4_available = True
        except ImportError:
            self.bs4_available = False
        
        try:
            import markdownify
            self.markdownify_available = True
        except ImportError:
            self.markdownify_available = False
    
    def accepts(self, file_stream: BinaryIO, stream_info: StreamInfo, **kwargs) -> bool:
        """Check if this converter can handle the file"""
        return (stream_info.matches_mimetype(['text/html', 'application/xhtml+xml']) or
                stream_info.matches_extension(['.html', '.htm']))
    
    def convert(self, file_stream: BinaryIO, stream_info: StreamInfo, **kwargs) -> DocumentConverterResult:
        """Convert HTML file"""
        logger.info(f"Converting HTML: {stream_info.filename}")
        
        if not self.bs4_available:
            raise MissingDependencyException("BeautifulSoup4 is required for HTML conversion")
        
        try:
            # Read HTML content
            html_content = read_stream_with_encoding(file_stream, stream_info.charset)
            
            # Parse with BeautifulSoup
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract metadata
            metadata = self._extract_html_metadata(soup, stream_info)
            
            # Extract title
            title = self._extract_html_title(soup)
            
            # Convert to markdown
            if self.markdownify_available:
                markdown = self._convert_with_markdownify(soup)
            else:
                markdown = self._convert_with_beautifulsoup(soup)
            
            return DocumentConverterResult(
                markdown=self._clean_markdown(markdown),
                title=title,
                metadata=metadata
            )
            
        except Exception as e:
            raise FileConversionException(f"HTML conversion failed: {e}")
    
    def _extract_html_metadata(self, soup, stream_info: StreamInfo) -> Dict[str, Any]:
        """Extract HTML metadata"""
        metadata = self._extract_metadata(None, stream_info)
        
        # Meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            
            if name and content:
                if name in ['description', 'keywords', 'author', 'generator']:
                    metadata[name] = content
                elif name.startswith('og:'):
                    metadata[name] = content
                elif name.startswith('twitter:'):
                    metadata[name] = content
        
        # Title
        title_tag = soup.find('title')
        if title_tag:
            metadata['html_title'] = title_tag.get_text().strip()
        
        # Language
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            metadata['language'] = html_tag['lang']
        
        return metadata
    
    def _extract_html_title(self, soup) -> Optional[str]:
        """Extract HTML title"""
        # Try title tag
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text().strip()
            if title:
                return self._format_title(title)
        
        # Try h1 tag
        h1_tag = soup.find('h1')
        if h1_tag:
            title = h1_tag.get_text().strip()
            if title:
                return self._format_title(title)
        
        # Try Open Graph title
        og_title = soup.find('meta', {'property': 'og:title'})
        if og_title:
            title = og_title.get('content', '').strip()
            if title:
                return self._format_title(title)
        
        return None
    
    def _convert_with_markdownify(self, soup) -> str:
        """Convert using markdownify library"""
        import markdownify
        
        # Remove unwanted tags
        for tag in soup(['script', 'style', 'meta', 'link', 'noscript']):
            tag.decompose()
        
        # Convert to markdown
        markdown = markdownify.markdownify(
            str(soup),
            heading_style="ATX",
            bullets="-",
            strip=['script', 'style', 'meta', 'link', 'noscript'],
            convert=[
                'a', 'b', 'blockquote', 'br', 'code', 'div', 'em', 
                'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i', 
                'img', 'li', 'ol', 'p', 'pre', 'span', 'strong', 
                'table', 'tbody', 'td', 'th', 'thead', 'tr', 'ul'
            ]
        )
        
        return markdown
    
    def _convert_with_beautifulsoup(self, soup) -> str:
        """Convert using BeautifulSoup only"""
        markdown = ""
        
        # Find body or use whole soup
        body = soup.find('body')
        if not body:
            body = soup
        
        # Process main content elements
        for element in body.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'article', 'section']):
            text = element.get_text().strip()
            if not text:
                continue
            
            # Handle headings
            if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                level = int(element.name[1])
                markdown += f"{'#' * level} {text}\\n\\n"
            else:
                # Regular paragraphs
                markdown += f"{text}\\n\\n"
        
        # Process lists
        for ul in body.find_all('ul'):
            for li in ul.find_all('li'):
                text = li.get_text().strip()
                if text:
                    markdown += f"- {text}\\n"
            markdown += "\\n"
        
        for ol in body.find_all('ol'):
            for i, li in enumerate(ol.find_all('li'), 1):
                text = li.get_text().strip()
                if text:
                    markdown += f"{i}. {text}\\n"
            markdown += "\\n"
        
        # Process tables
        for table in body.find_all('table'):
            markdown += self._table_to_markdown(table)
            markdown += "\\n"
        
        return markdown
    
    def _table_to_markdown(self, table) -> str:
        """Convert HTML table to markdown"""
        rows = []
        
        # Collect all rows
        for tr in table.find_all('tr'):
            cells = []
            for cell in tr.find_all(['td', 'th']):
                text = cell.get_text().strip()
                # Escape pipe characters
                text = text.replace('|', '\\\\|')
                cells.append(text)
            if cells:
                rows.append(cells)
        
        if not rows:
            return ""
        
        # Create markdown table
        markdown = "| " + " | ".join(rows[0]) + " |\\n"
        markdown += "| " + " | ".join(["---"] * len(rows[0])) + " |\\n"
        
        # Add remaining rows
        for row in rows[1:]:
            # Adjust row length to match header
            row = row[:len(rows[0])]
            row.extend([""] * (len(rows[0]) - len(row)))
            markdown += "| " + " | ".join(row) + " |\\n"
        
        return markdown
    
    def get_format_info(self) -> Dict[str, Any]:
        """Get format information"""
        return {
            'name': 'HTML',
            'description': 'HTML document converter with metadata extraction',
            'extensions': self.supported_extensions,
            'mimetypes': self.supported_mimetypes,
            'category': self.category,
            'features': [
                'HTML to Markdown conversion',
                'Metadata extraction',
                'Table conversion',
                'List processing',
                'Link preservation'
            ]
        }