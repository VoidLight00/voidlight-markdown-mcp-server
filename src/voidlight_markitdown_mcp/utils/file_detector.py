"""
File type detection utilities
"""

from typing import Optional, BinaryIO, List
import logging

from ..core.stream_info import StreamInfo

logger = logging.getLogger(__name__)


class FileTypeDetector:
    """File type detection based on content and metadata"""
    
    def __init__(self):
        # Initialize python-magic if available
        try:
            import magic
            self.magic = magic.Magic(mime=True)
            self.magic_available = True
        except ImportError:
            logger.warning("python-magic not available, falling back to extension detection")
            self.magic_available = False
        
        # Extension to MIME type mapping
        self.extension_mapping = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.doc': 'application/msword',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            '.ppt': 'application/vnd.ms-powerpoint',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.xls': 'application/vnd.ms-excel',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.tiff': 'image/tiff',
            '.webp': 'image/webp',
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.m4a': 'audio/mp4',
            '.flac': 'audio/flac',
            '.ogg': 'audio/ogg',
            '.html': 'text/html',
            '.htm': 'text/html',
            '.xml': 'application/xml',
            '.json': 'application/json',
            '.csv': 'text/csv',
            '.txt': 'text/plain',
            '.md': 'text/markdown',
            '.rtf': 'application/rtf',
            '.epub': 'application/epub+zip',
            '.zip': 'application/zip',
            '.tar': 'application/x-tar',
            '.gz': 'application/gzip',
            '.7z': 'application/x-7z-compressed',
            '.rar': 'application/x-rar-compressed',
            '.msg': 'application/vnd.ms-outlook',
            '.eml': 'message/rfc822',
            '.ipynb': 'application/x-ipynb+json',
            '.hwp': 'application/haansofthwp',
            '.hwpx': 'application/haansofthwp'
        }
        
        # Reverse mapping
        self.mimetype_mapping = {v: k for k, v in self.extension_mapping.items()}
    
    def detect_from_stream(self, stream: BinaryIO) -> Optional[StreamInfo]:
        """Detect file type from stream content"""
        if not self.magic_available:
            return None
        
        try:
            # Save current position
            current_pos = stream.tell()
            
            # Read header
            stream.seek(0)
            header = stream.read(8192)  # Read 8KB
            
            # Restore position
            stream.seek(current_pos)
            
            if not header:
                return None
            
            # Detect MIME type
            mimetype = self.magic.from_buffer(header)
            
            # Get extension from MIME type
            extension = self.mimetype_mapping.get(mimetype)
            
            return StreamInfo(
                mimetype=mimetype,
                extension=extension
            )
            
        except Exception as e:
            logger.debug(f"Stream detection failed: {e}")
            return None
    
    def detect_from_filename(self, filename: str) -> Optional[StreamInfo]:
        """Detect file type from filename"""
        from pathlib import Path
        
        path = Path(filename)
        extension = path.suffix.lower()
        
        if extension in self.extension_mapping:
            mimetype = self.extension_mapping[extension]
            return StreamInfo(
                mimetype=mimetype,
                extension=extension,
                filename=filename
            )
        
        return None
    
    def detect_from_extension(self, extension: str) -> Optional[StreamInfo]:
        """Detect file type from extension"""
        if not extension.startswith('.'):
            extension = '.' + extension
        
        extension = extension.lower()
        
        if extension in self.extension_mapping:
            mimetype = self.extension_mapping[extension]
            return StreamInfo(
                mimetype=mimetype,
                extension=extension
            )
        
        return None
    
    def detect_from_mimetype(self, mimetype: str) -> Optional[StreamInfo]:
        """Create StreamInfo from MIME type"""
        # Exact match
        extension = self.mimetype_mapping.get(mimetype)
        if extension:
            return StreamInfo(
                mimetype=mimetype,
                extension=extension
            )
        
        # Partial match
        for mime, ext in self.mimetype_mapping.items():
            if mimetype.startswith(mime.split('/')[0]):
                return StreamInfo(
                    mimetype=mimetype,
                    extension=ext
                )
        
        return StreamInfo(mimetype=mimetype)
    
    def get_supported_extensions(self) -> List[str]:
        """Get list of supported extensions"""
        return list(self.extension_mapping.keys())
    
    def get_supported_mimetypes(self) -> List[str]:
        """Get list of supported MIME types"""
        return list(self.extension_mapping.values())
    
    def is_text_file(self, stream: BinaryIO) -> bool:
        """Check if stream contains text content"""
        try:
            current_pos = stream.tell()
            stream.seek(0)
            sample = stream.read(8192)
            stream.seek(current_pos)
            
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