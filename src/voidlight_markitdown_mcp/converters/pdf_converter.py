"""
PDF file converter
"""

from typing import BinaryIO, Dict, Any, Optional
import logging

from ..core.base_converter import DocumentConverter, DocumentConverterResult
from ..core.stream_info import StreamInfo
from ..core.exceptions import MissingDependencyException, FileConversionException
from ..utils.format_utils import normalize_whitespace

logger = logging.getLogger(__name__)


class PdfConverter(DocumentConverter):
    """PDF file converter"""
    
    def __init__(self, docintel_endpoint: Optional[str] = None, 
                 docintel_key: Optional[str] = None,
                 korean_support: bool = True):
        super().__init__(korean_support=korean_support)
        self.docintel_endpoint = docintel_endpoint
        self.docintel_key = docintel_key
        self.priority = 0.0
        
        self.supported_extensions = ['.pdf']
        self.supported_mimetypes = ['application/pdf']
        self.category = 'documents'
        
        # Check dependencies
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Check for available dependencies"""
        try:
            import pdfminer.six
            self.pdfminer_available = True
        except ImportError:
            self.pdfminer_available = False
        
        self.azure_available = bool(self.docintel_endpoint and self.docintel_key)
    
    def accepts(self, file_stream: BinaryIO, stream_info: StreamInfo, **kwargs) -> bool:
        """Check if this converter can handle the file"""
        return (stream_info.matches_mimetype(['application/pdf']) or 
                stream_info.matches_extension(['.pdf']))
    
    def convert(self, file_stream: BinaryIO, stream_info: StreamInfo, **kwargs) -> DocumentConverterResult:
        """Convert PDF file"""
        logger.info(f"Converting PDF: {stream_info.filename}")
        
        # Try Azure Document Intelligence first
        if self.azure_available:
            try:
                return self._convert_with_azure(file_stream, stream_info, **kwargs)
            except Exception as e:
                logger.warning(f"Azure Document Intelligence failed: {e}")
        
        # Use pdfminer as fallback
        if self.pdfminer_available:
            return self._convert_with_pdfminer(file_stream, stream_info, **kwargs)
        
        raise MissingDependencyException(
            "No PDF processing library available. Install pdfminer.six or configure Azure Document Intelligence"
        )
    
    def _convert_with_azure(self, file_stream: BinaryIO, stream_info: StreamInfo, **kwargs) -> DocumentConverterResult:
        """Convert using Azure Document Intelligence"""
        try:
            from azure.ai.documentintelligence import DocumentIntelligenceClient
            from azure.core.credentials import AzureKeyCredential
            
            # Create client
            client = DocumentIntelligenceClient(
                endpoint=self.docintel_endpoint,
                credential=AzureKeyCredential(self.docintel_key)
            )
            
            # Analyze document
            file_stream.seek(0)
            poller = client.begin_analyze_document(
                "prebuilt-layout",
                file_stream,
                content_type="application/pdf"
            )
            
            result = poller.result()
            
            # Convert to markdown
            markdown = self._azure_result_to_markdown(result)
            
            # Extract metadata
            metadata = self._extract_metadata(file_stream, stream_info)
            if hasattr(result, 'pages') and result.pages:
                metadata['page_count'] = len(result.pages)
            
            # Extract title
            title = self._extract_title_from_azure_result(result)
            
            return DocumentConverterResult(
                markdown=self._clean_markdown(markdown),
                title=title,
                metadata=metadata
            )
            
        except Exception as e:
            raise FileConversionException(f"Azure Document Intelligence conversion failed: {e}")
    
    def _convert_with_pdfminer(self, file_stream: BinaryIO, stream_info: StreamInfo, **kwargs) -> DocumentConverterResult:
        """Convert using pdfminer"""
        try:
            from pdfminer.high_level import extract_text
            
            file_stream.seek(0)
            text = extract_text(file_stream)
            
            # Convert to markdown
            markdown = self._text_to_markdown(text)
            
            # Extract metadata
            metadata = self._extract_metadata(file_stream, stream_info)
            
            # Extract title
            title = self._extract_title_from_text(text)
            
            return DocumentConverterResult(
                markdown=self._clean_markdown(markdown),
                title=title,
                metadata=metadata
            )
            
        except Exception as e:
            raise FileConversionException(f"PDF conversion failed: {e}")
    
    def _azure_result_to_markdown(self, result) -> str:
        """Convert Azure result to markdown"""
        markdown = ""
        
        if hasattr(result, 'paragraphs') and result.paragraphs:
            for paragraph in result.paragraphs:
                content = paragraph.content.strip()
                if content:
                    if self._is_heading(content):
                        level = self._get_heading_level(content)
                        markdown += f"{'#' * level} {content}\\n\\n"
                    else:
                        markdown += f"{content}\\n\\n"
        
        return markdown
    
    def _text_to_markdown(self, text: str) -> str:
        """Convert plain text to markdown"""
        if not text:
            return ""
        
        text = normalize_whitespace(text)
        paragraphs = text.split('\\n\\n')
        
        markdown = ""
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            if self._is_heading(paragraph):
                level = self._get_heading_level(paragraph)
                markdown += f"{'#' * level} {paragraph}\\n\\n"
            else:
                markdown += f"{paragraph}\\n\\n"
        
        return markdown
    
    def _is_heading(self, text: str) -> bool:
        """Check if text is a heading"""
        text = text.strip()
        
        if len(text) > 100:
            return False
        
        if len(text) < 100 and not text.endswith('.'):
            return True
        
        if text.startswith(tuple('0123456789')):
            return True
        
        return False
    
    def _get_heading_level(self, text: str) -> int:
        """Get heading level"""
        text = text.strip()
        
        if text.startswith(tuple('0123456789')):
            dots = text.split()[0].count('.')
            return min(dots + 1, 6)
        
        return 2
    
    def _extract_title_from_azure_result(self, result) -> Optional[str]:
        """Extract title from Azure result"""
        if hasattr(result, 'paragraphs') and result.paragraphs:
            for paragraph in result.paragraphs:
                if paragraph.content:
                    text = paragraph.content.strip()
                    if text and len(text) < 100:
                        return self._format_title(text)
        return None
    
    def _extract_title_from_text(self, text: str) -> Optional[str]:
        """Extract title from text"""
        if not text:
            return None
        
        lines = text.split('\\n')
        for line in lines:
            line = line.strip()
            if line and len(line) < 100:
                return self._format_title(line)
        
        return None
    
    def get_format_info(self) -> Dict[str, Any]:
        """Get format information"""
        return {
            'name': 'PDF',
            'description': 'PDF document converter with Azure Document Intelligence support',
            'extensions': self.supported_extensions,
            'mimetypes': self.supported_mimetypes,
            'category': self.category,
            'features': [
                'Text extraction',
                'Layout preservation',
                'Azure Document Intelligence integration',
                'Metadata extraction'
            ]
        }