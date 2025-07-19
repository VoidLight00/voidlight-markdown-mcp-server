"""
Exception classes for MarkItDown MCP Enhanced
"""


class MarkItDownException(Exception):
    """Base exception for MarkItDown MCP Enhanced"""
    pass


class UnsupportedFormatException(MarkItDownException):
    """Raised when a file format is not supported"""
    pass


class FileConversionException(MarkItDownException):
    """Raised when file conversion fails"""
    pass


class MissingDependencyException(MarkItDownException):
    """Raised when required dependencies are missing"""
    pass


class NetworkException(MarkItDownException):
    """Raised when network operations fail"""
    pass


class AuthenticationException(MarkItDownException):
    """Raised when authentication fails"""
    pass


class ConfigurationException(MarkItDownException):
    """Raised when configuration is invalid"""
    pass