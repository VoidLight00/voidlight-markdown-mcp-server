"""
Document converters for MarkItDown MCP Enhanced
"""

# Import converters with error handling
try:
    from .text_converter import TextConverter
except ImportError:
    TextConverter = None

try:
    from .pdf_converter import PdfConverter
except ImportError:
    PdfConverter = None

try:
    from .docx_converter import DocxConverter
except ImportError:
    DocxConverter = None

try:
    from .image_converter import ImageConverter
except ImportError:
    ImageConverter = None

try:
    from .html_converter import HtmlConverter
except ImportError:
    HtmlConverter = None

try:
    from .audio_converter import AudioConverter
except ImportError:
    AudioConverter = None

# Export available converters
__all__ = []

if TextConverter:
    __all__.append('TextConverter')
if PdfConverter:
    __all__.append('PdfConverter')
if DocxConverter:
    __all__.append('DocxConverter')
if ImageConverter:
    __all__.append('ImageConverter')
if HtmlConverter:
    __all__.append('HtmlConverter')
if AudioConverter:
    __all__.append('AudioConverter')