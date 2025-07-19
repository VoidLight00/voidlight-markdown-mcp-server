"""
Main MarkItDown class for document conversion
"""

import io
import shutil
from typing import List, Optional, Dict, Any, BinaryIO, Union
from pathlib import Path
import requests
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import logging

from .base_converter import DocumentConverter, DocumentConverterResult
from .stream_info import StreamInfo
from .exceptions import MarkItDownException, UnsupportedFormatException
from ..utils.file_detector import FileTypeDetector
from ..utils.stream_utils import make_stream_seekable
from ..utils.format_utils import normalize_whitespace

logger = logging.getLogger(__name__)


@dataclass
class ConverterRegistration:
    """Registration information for a converter"""
    converter: DocumentConverter
    priority: float


class MarkItDown:
    """Enhanced MarkItDown with Korean support and additional features"""
    
    def __init__(self, 
                 enable_builtins: bool = True,
                 enable_plugins: bool = True,
                 llm_client=None,
                 llm_model: str = "gpt-4o",
                 docintel_endpoint: Optional[str] = None,
                 exiftool_path: Optional[str] = None,
                 enable_korean_support: bool = True,
                 max_workers: int = 4):
        
        self.enable_builtins = enable_builtins
        self.enable_plugins = enable_plugins
        self.llm_client = llm_client
        self.llm_model = llm_model
        self.docintel_endpoint = docintel_endpoint
        self.exiftool_path = exiftool_path
        self.enable_korean_support = enable_korean_support
        self.max_workers = max_workers
        
        # Converter registration list
        self._converters: List[ConverterRegistration] = []
        
        # Utilities
        self._file_detector = FileTypeDetector()
        self._plugin_manager = None
        
        # Options
        self._options = {
            'include_metadata': False,
            'extract_images': False,
            'korean_optimization': False
        }
        
        # Register converters
        self._register_converters()
        
        # Load plugins
        if enable_plugins:
            self._load_plugins()
    
    def _register_converters(self):
        """Register built-in converters"""
        if not self.enable_builtins:
            return
        
        # Import converters
        try:
            from ..converters.text_converter import TextConverter
            self.register_converter(TextConverter(
                korean_support=self.enable_korean_support
            ), priority=10.0)  # Lowest priority
        except ImportError:
            logger.debug("TextConverter not available")
        
        try:
            from ..converters.pdf_converter import PdfConverter
            self.register_converter(PdfConverter(
                docintel_endpoint=self.docintel_endpoint,
                korean_support=self.enable_korean_support
            ), priority=0.0)
        except ImportError:
            logger.debug("PdfConverter not available")
        
        try:
            from ..converters.docx_converter import DocxConverter
            self.register_converter(DocxConverter(
                korean_support=self.enable_korean_support
            ), priority=0.1)
        except ImportError:
            logger.debug("DocxConverter not available")
        
        try:
            from ..converters.image_converter import ImageConverter
            self.register_converter(ImageConverter(
                llm_client=self.llm_client,
                llm_model=self.llm_model,
                exiftool_path=self.exiftool_path,
                korean_support=self.enable_korean_support
            ), priority=1.0)
        except ImportError:
            logger.debug("ImageConverter not available")
        
        try:
            from ..converters.html_converter import HtmlConverter
            self.register_converter(HtmlConverter(
                korean_support=self.enable_korean_support
            ), priority=2.0)
        except ImportError:
            logger.debug("HtmlConverter not available")
        
        try:
            from ..converters.audio_converter import AudioConverter
            self.register_converter(AudioConverter(
                korean_support=self.enable_korean_support
            ), priority=3.0)
        except ImportError:
            logger.debug("AudioConverter not available")
    
    def _load_plugins(self):
        """Load plugins"""
        try:
            from ..plugins.plugin_manager import PluginManager
            self._plugin_manager = PluginManager()
            plugins = self._plugin_manager.load_plugins()
            
            for plugin in plugins:
                self.register_converter(plugin, priority=0.5)
                logger.info(f"Loaded plugin: {plugin.__class__.__name__}")
        except ImportError:
            logger.debug("Plugin system not available")
    
    def register_converter(self, converter: DocumentConverter, *, priority: float = 0.0):
        """Register a converter with given priority"""
        registration = ConverterRegistration(
            converter=converter,
            priority=priority
        )
        
        # Insert in priority order (lower priority = higher precedence)
        insert_pos = 0
        for i, reg in enumerate(self._converters):
            if reg.priority > priority:
                insert_pos = i
                break
            insert_pos = i + 1
        
        self._converters.insert(insert_pos, registration)
        logger.debug(f"Registered converter: {converter.__class__.__name__} (priority: {priority})")
    
    def set_options(self, **kwargs):
        """Set conversion options"""
        self._options.update(kwargs)
    
    def convert(self, source: Union[str, Path, BinaryIO], **kwargs) -> DocumentConverterResult:
        """Universal conversion method"""
        if isinstance(source, (str, Path)):
            source_path = Path(source)
            if source_path.exists():
                return self.convert_local(source_path, **kwargs)
            else:
                # Treat as URL
                return self.convert_uri(str(source), **kwargs)
        
        elif hasattr(source, 'read'):
            return self.convert_stream(source, **kwargs)
        
        else:
            raise ValueError(f"Unsupported source type: {type(source)}")
    
    def convert_local(self, file_path: Union[str, Path], **kwargs) -> DocumentConverterResult:
        """Convert local file"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Check file size
        file_size = file_path.stat().st_size
        if file_size > 100 * 1024 * 1024:  # 100MB
            logger.warning(f"Large file detected: {file_path} ({file_size} bytes)")
        
        # Create stream info
        stream_info = StreamInfo(
            extension=file_path.suffix.lower(),
            filename=file_path.name,
            local_path=str(file_path)
        )
        
        # Open and convert
        with open(file_path, 'rb') as f:
            return self.convert_stream(f, stream_info=stream_info, **kwargs)
    
    def convert_stream(self, stream: BinaryIO, *, stream_info: Optional[StreamInfo] = None, **kwargs) -> DocumentConverterResult:
        """Convert stream"""
        # Make stream seekable
        stream = make_stream_seekable(stream)
        
        # Create or update stream info
        if stream_info is None:
            stream_info = StreamInfo()
        
        # Detect file type
        stream_info_guesses = self._get_stream_info_guesses(stream, stream_info)
        
        # Attempt conversion
        return self._convert_with_guesses(stream, stream_info_guesses, **kwargs)
    
    def convert_uri(self, uri: str, **kwargs) -> DocumentConverterResult:
        """Convert URI"""
        logger.info(f"Converting URI: {uri}")
        
        # Check URI scheme
        if uri.startswith('file://'):
            # Local file URI
            file_path = uri[7:]  # Remove 'file://'
            return self.convert_local(file_path, **kwargs)
        
        elif uri.startswith('data:'):
            # Data URI
            return self._convert_data_uri(uri, **kwargs)
        
        elif uri.startswith(('http://', 'https://')):
            # HTTP/HTTPS URI
            return self._convert_http_uri(uri, **kwargs)
        
        else:
            # Treat as local file path
            return self.convert_local(uri, **kwargs)
    
    def _convert_data_uri(self, data_uri: str, **kwargs) -> DocumentConverterResult:
        """Convert data URI"""
        import base64
        from urllib.parse import unquote
        
        # Parse data URI
        if not data_uri.startswith('data:'):
            raise ValueError("Invalid data URI")
        
        # Split header and data
        header, data = data_uri[5:].split(',', 1)
        
        # Extract media type
        if ';' in header:
            media_type, encoding = header.split(';', 1)
            is_base64 = 'base64' in encoding
        else:
            media_type = header
            is_base64 = False
        
        # Decode data
        if is_base64:
            binary_data = base64.b64decode(data)
        else:
            binary_data = unquote(data).encode('utf-8')
        
        # Create stream
        stream = io.BytesIO(binary_data)
        stream_info = StreamInfo(mimetype=media_type)
        
        return self.convert_stream(stream, stream_info=stream_info, **kwargs)
    
    def _convert_http_uri(self, uri: str, **kwargs) -> DocumentConverterResult:
        """Convert HTTP/HTTPS URI"""
        try:
            # Make HTTP request
            response = requests.get(uri, stream=True, timeout=30)
            response.raise_for_status()
            
            # Create stream info
            stream_info = StreamInfo(
                mimetype=response.headers.get('content-type'),
                url=uri,
                charset=response.encoding
            )
            
            # Extract filename from Content-Disposition
            content_disposition = response.headers.get('content-disposition')
            if content_disposition:
                filename = self._extract_filename_from_disposition(content_disposition)
                if filename:
                    stream_info.filename = filename
                    stream_info.extension = Path(filename).suffix.lower()
            
            # Convert stream
            return self.convert_stream(response.raw, stream_info=stream_info, **kwargs)
        
        except requests.RequestException as e:
            raise MarkItDownException(f"Failed to fetch URI {uri}: {e}")
    
    def _extract_filename_from_disposition(self, disposition: str) -> Optional[str]:
        """Extract filename from Content-Disposition header"""
        import re
        from urllib.parse import unquote
        
        # filename* format (RFC 5987)
        match = re.search(r"filename\*=(?:UTF-8'')?([^;]+)", disposition)
        if match:
            return unquote(match.group(1))
        
        # filename format
        match = re.search(r'filename="([^"]+)"', disposition)
        if match:
            return match.group(1)
        
        match = re.search(r'filename=([^;]+)', disposition)
        if match:
            return match.group(1).strip()
        
        return None
    
    def _get_stream_info_guesses(self, stream: BinaryIO, base_info: StreamInfo) -> List[StreamInfo]:
        """Get stream info guesses"""
        guesses = []
        
        # Add base info if it has useful information
        if base_info.mimetype or base_info.extension:
            guesses.append(base_info)
        
        # Content-based detection
        content_guess = self._file_detector.detect_from_stream(stream)
        if content_guess and content_guess not in guesses:
            guesses.append(content_guess)
        
        # Filename-based detection
        if base_info.filename:
            filename_guess = self._file_detector.detect_from_filename(base_info.filename)
            if filename_guess and filename_guess not in guesses:
                guesses.append(filename_guess)
        
        # Extension-based detection
        if base_info.extension:
            extension_guess = self._file_detector.detect_from_extension(base_info.extension)
            if extension_guess and extension_guess not in guesses:
                guesses.append(extension_guess)
        
        # MIME type-based detection
        if base_info.mimetype:
            mimetype_guess = self._file_detector.detect_from_mimetype(base_info.mimetype)
            if mimetype_guess and mimetype_guess not in guesses:
                guesses.append(mimetype_guess)
        
        return guesses or [StreamInfo()]
    
    def _convert_with_guesses(self, stream: BinaryIO, 
                            stream_info_guesses: List[StreamInfo], 
                            **kwargs) -> DocumentConverterResult:
        """Attempt conversion with guessed stream info"""
        
        failed_attempts = []
        
        for stream_info in stream_info_guesses:
            for converter_reg in self._converters:
                converter = converter_reg.converter
                
                try:
                    # Check if converter accepts the file
                    if converter.accepts(stream, stream_info, **kwargs):
                        logger.debug(f"Trying converter: {converter.__class__.__name__}")
                        
                        # Perform conversion
                        result = converter.convert(stream, stream_info, **kwargs)
                        
                        # Apply post-processing
                        if self._options.get('korean_optimization'):
                            result = self._apply_korean_optimization(result)
                        
                        logger.info(f"Successfully converted with {converter.__class__.__name__}")
                        return result
                
                except Exception as e:
                    failed_attempts.append({
                        'converter': converter.__class__.__name__,
                        'stream_info': stream_info,
                        'error': str(e)
                    })
                    logger.debug(f"Converter {converter.__class__.__name__} failed: {e}")
        
        # All converters failed
        error_msg = f"No suitable converter found for stream"
        if stream_info_guesses:
            error_msg += f" (guessed types: {[str(si) for si in stream_info_guesses]})"
        
        if failed_attempts:
            error_msg += f"\\nFailed attempts: {failed_attempts}"
        
        raise UnsupportedFormatException(error_msg)
    
    def _apply_korean_optimization(self, result: DocumentConverterResult) -> DocumentConverterResult:
        """Apply Korean text optimization"""
        if not self.enable_korean_support:
            return result
        
        # Korean text normalization
        from ..utils.format_utils import normalize_korean_spacing
        optimized_markdown = normalize_korean_spacing(result.markdown)
        
        return DocumentConverterResult(
            markdown=optimized_markdown,
            title=result.title,
            metadata=result.metadata
        )
    
    def analyze_structure(self, source: Union[str, Path, BinaryIO]) -> Dict[str, Any]:
        """Analyze document structure"""
        result = self.convert(source)
        
        return {
            'document_type': self._detect_document_type(result),
            'word_count': len(result.markdown.split()),
            'character_count': len(result.markdown),
            'headings': self._extract_headings(result.markdown),
            'images': self._extract_images(result.markdown),
            'tables': self._extract_tables(result.markdown),
            'links': self._extract_links(result.markdown),
            'language': self._detect_language(result.markdown),
            'metadata': result.metadata
        }
    
    def _detect_document_type(self, result: DocumentConverterResult) -> str:
        """Detect document type"""
        markdown = result.markdown
        
        # Many tables = spreadsheet
        if markdown.count('|') > 20:
            return 'spreadsheet'
        
        # Many code blocks = technical document
        if markdown.count('```') > 5:
            return 'technical'
        
        # Many images = presentation
        if markdown.count('![') > 5:
            return 'presentation'
        
        # Many links = webpage
        if markdown.count('](') > 10:
            return 'webpage'
        
        return 'document'
    
    def _extract_headings(self, markdown: str) -> List[Dict[str, Any]]:
        """Extract headings from markdown"""
        import re
        
        headings = []
        for match in re.finditer(r'^(#{1,6})\\s+(.+)$', markdown, re.MULTILINE):
            level = len(match.group(1))
            text = match.group(2).strip()
            headings.append({
                'level': level,
                'text': text,
                'line': markdown[:match.start()].count('\\n') + 1
            })
        
        return headings
    
    def _extract_images(self, markdown: str) -> List[Dict[str, Any]]:
        """Extract images from markdown"""
        import re
        
        images = []
        for match in re.finditer(r'!\\[([^\\]]*)\\]\\(([^\\)]+)\\)', markdown):
            alt_text = match.group(1)
            url = match.group(2)
            images.append({
                'alt_text': alt_text,
                'url': url,
                'line': markdown[:match.start()].count('\\n') + 1
            })
        
        return images
    
    def _extract_tables(self, markdown: str) -> List[Dict[str, Any]]:
        """Extract tables from markdown"""
        import re
        
        tables = []
        table_pattern = r'(\\|[^\\n]+\\|(?:\\n\\|[^\\n]+\\|)+)'
        
        for match in re.finditer(table_pattern, markdown, re.MULTILINE):
            table_text = match.group(1)
            lines = table_text.split('\\n')
            
            # Count columns and rows
            header_line = lines[0] if lines else ''
            data_lines = lines[2:] if len(lines) > 2 else []
            
            columns = len(header_line.split('|')) - 2  # Exclude leading/trailing empty parts
            rows = len(data_lines)
            
            tables.append({
                'columns': columns,
                'rows': rows,
                'header': header_line.strip(),
                'line': markdown[:match.start()].count('\\n') + 1
            })
        
        return tables
    
    def _extract_links(self, markdown: str) -> List[Dict[str, Any]]:
        """Extract links from markdown"""
        import re
        
        links = []
        for match in re.finditer(r'\\[([^\\]]+)\\]\\(([^\\)]+)\\)', markdown):
            text = match.group(1)
            url = match.group(2)
            links.append({
                'text': text,
                'url': url,
                'line': markdown[:match.start()].count('\\n') + 1
            })
        
        return links
    
    def _detect_language(self, text: str) -> str:
        """Detect text language"""
        from ..utils.format_utils import is_korean_text
        
        if is_korean_text(text):
            return 'korean'
        
        # Simple English detection
        import re
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        total_chars = len(re.findall(r'[a-zA-Z가-힣]', text))
        
        if total_chars > 0:
            english_ratio = english_chars / total_chars
            if english_ratio > 0.7:
                return 'english'
        
        return 'unknown'
    
    def get_supported_formats(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get supported formats"""
        formats = {
            'documents': [],
            'images': [],
            'audio': [],
            'web': [],
            'data': [],
            'archives': []
        }
        
        for converter_reg in self._converters:
            converter = converter_reg.converter
            format_info = converter.get_format_info()
            
            category = format_info.get('category', 'documents')
            if category in formats:
                formats[category].append(format_info)
        
        return formats