"""
Voidlight Markdown MCP Server

Enhanced MarkItDown MCP Server with Korean support and additional features.
"""

from .core.markitdown import MarkItDown
from .core.base_converter import DocumentConverter, DocumentConverterResult
from .core.stream_info import StreamInfo
from .core.exceptions import *
from .config.settings import load_config, create_default_config_file

# Optional MCP server imports (only if mcp is available)
try:
    from .server import MarkItDownMCPServer, create_server
    _MCP_AVAILABLE = True
except ImportError:
    MarkItDownMCPServer = None
    create_server = None
    _MCP_AVAILABLE = False

__version__ = "1.0.0"
__author__ = "VoidLight"
__email__ = "voidlight@example.com"
__license__ = "MIT"
__description__ = "Enhanced MarkItDown MCP Server with Korean support and advanced document conversion"

__all__ = [
    "MarkItDown",
    "DocumentConverter",
    "DocumentConverterResult", 
    "StreamInfo",
    "MarkItDownMCPServer",
    "create_server",
    "load_config",
    "create_default_config_file",
    # Exceptions
    "MarkItDownException",
    "UnsupportedFormatException",
    "FileConversionException",
    "MissingDependencyException",
    "NetworkException",
    "AuthenticationException",
    "ConfigurationException",
]