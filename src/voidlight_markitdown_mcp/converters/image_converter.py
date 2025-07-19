"""
Image file converter with OCR and AI description
"""

import base64
from typing import BinaryIO, Dict, Any, Optional
import logging

from ..core.base_converter import DocumentConverter, DocumentConverterResult
from ..core.stream_info import StreamInfo
from ..core.exceptions import MissingDependencyException, FileConversionException
from ..utils.format_utils import normalize_whitespace

logger = logging.getLogger(__name__)


class ImageConverter(DocumentConverter):
    """Image file converter with OCR and AI description"""
    
    def __init__(self, 
                 llm_client=None, 
                 llm_model: str = "gpt-4o",
                 exiftool_path: Optional[str] = None,
                 korean_support: bool = True):
        super().__init__(korean_support=korean_support)
        self.llm_client = llm_client
        self.llm_model = llm_model
        self.exiftool_path = exiftool_path
        self.priority = 1.0
        
        self.supported_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
        self.supported_mimetypes = [
            'image/jpeg', 'image/png', 'image/gif', 'image/bmp', 
            'image/tiff', 'image/webp'
        ]
        self.category = 'images'
        
        # Check dependencies
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Check for available dependencies"""
        try:
            from PIL import Image
            self.pil_available = True
        except ImportError:
            self.pil_available = False
        
        try:
            import pytesseract
            self.tesseract_available = True
        except ImportError:
            self.tesseract_available = False
        
        try:
            import easyocr
            self.easyocr_available = True
        except ImportError:
            self.easyocr_available = False
        
        self.llm_available = bool(self.llm_client)
        self.exiftool_available = bool(self.exiftool_path)
    
    def accepts(self, file_stream: BinaryIO, stream_info: StreamInfo, **kwargs) -> bool:
        """Check if this converter can handle the file"""
        return (stream_info.matches_mimetype(self.supported_mimetypes) or
                stream_info.matches_extension(self.supported_extensions))
    
    def convert(self, file_stream: BinaryIO, stream_info: StreamInfo, **kwargs) -> DocumentConverterResult:
        """Convert image file"""
        logger.info(f"Converting image: {stream_info.filename}")
        
        if not self.pil_available:
            raise MissingDependencyException("Pillow is required for image conversion")
        
        try:
            from PIL import Image
            
            # Load image
            file_stream.seek(0)
            image = Image.open(file_stream)
            
            # Extract text using OCR
            ocr_text = self._extract_text_with_ocr(image)
            
            # Generate AI description
            ai_description = self._generate_ai_description(file_stream, stream_info)
            
            # Extract metadata
            metadata = self._extract_image_metadata(image, file_stream, stream_info)
            
            # Create markdown content
            markdown = self._create_image_markdown(
                ocr_text=ocr_text,
                ai_description=ai_description,
                metadata=metadata,
                stream_info=stream_info
            )
            
            # Extract title
            title = self._extract_image_title(ocr_text, ai_description, stream_info)
            
            return DocumentConverterResult(
                markdown=self._clean_markdown(markdown),
                title=title,
                metadata=metadata
            )
            
        except Exception as e:
            raise FileConversionException(f"Image conversion failed: {e}")
    
    def _extract_text_with_ocr(self, image) -> str:
        """Extract text from image using OCR"""
        text = ""
        
        # Try EasyOCR first (better for Korean)
        if self.easyocr_available and self.korean_support:
            try:
                import easyocr
                import numpy as np
                
                # Convert PIL image to numpy array
                img_array = np.array(image)
                
                # Initialize reader with Korean and English
                reader = easyocr.Reader(['ko', 'en'])
                
                # Extract text
                results = reader.readtext(img_array)
                text_parts = [result[1] for result in results if result[2] > 0.5]  # Confidence > 0.5
                text = " ".join(text_parts)
                
                logger.debug(f"EasyOCR extracted {len(text_parts)} text segments")
                
            except Exception as e:
                logger.warning(f"EasyOCR failed: {e}")
        
        # Fallback to Tesseract
        if not text and self.tesseract_available:
            try:
                import pytesseract
                
                # Configure for Korean if supported
                if self.korean_support:
                    # Try Korean + English
                    try:
                        text = pytesseract.image_to_string(image, lang='kor+eng')
                    except:
                        # Fallback to English only
                        text = pytesseract.image_to_string(image, lang='eng')
                else:
                    text = pytesseract.image_to_string(image, lang='eng')
                
                logger.debug(f"Tesseract extracted text: {len(text)} characters")
                
            except Exception as e:
                logger.warning(f"Tesseract OCR failed: {e}")
        
        return normalize_whitespace(text) if text else ""
    
    def _generate_ai_description(self, file_stream: BinaryIO, stream_info: StreamInfo) -> str:
        """Generate AI description of the image"""
        if not self.llm_available:
            return ""
        
        try:
            # Encode image to base64
            file_stream.seek(0)
            image_data = file_stream.read()
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # Prepare prompt
            prompt = "Describe this image in detail. Focus on the main content, text, objects, and any notable features."
            if self.korean_support:
                prompt += " If there is Korean text, please mention it."
            
            # Call LLM (this would need to be implemented based on the specific LLM client)
            # For now, return a placeholder
            description = self._call_llm_for_image_description(base64_image, prompt)
            
            return description
            
        except Exception as e:
            logger.warning(f"AI description generation failed: {e}")
            return ""
    
    def _call_llm_for_image_description(self, base64_image: str, prompt: str) -> str:
        """Call LLM for image description"""
        try:
            # This is a placeholder implementation
            # In a real implementation, you would use the actual LLM client
            if hasattr(self.llm_client, 'chat') and hasattr(self.llm_client.chat, 'completions'):
                # OpenAI-style client
                response = self.llm_client.chat.completions.create(
                    model=self.llm_model,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": prompt
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}"
                                    }
                                }
                            ]
                        }
                    ],
                    max_tokens=300
                )
                return response.choices[0].message.content
            
        except Exception as e:
            logger.warning(f"LLM call failed: {e}")
        
        return ""
    
    def _extract_image_metadata(self, image, file_stream: BinaryIO, stream_info: StreamInfo) -> Dict[str, Any]:
        """Extract image metadata"""
        metadata = self._extract_metadata(file_stream, stream_info)
        
        # Basic image info
        metadata.update({
            'width': image.width,
            'height': image.height,
            'format': image.format,
            'mode': image.mode
        })
        
        # EXIF data
        if hasattr(image, '_getexif') and image._getexif():
            try:
                exif_data = image._getexif()
                if exif_data:
                    # Extract common EXIF tags
                    exif_tags = {
                        'DateTime': 306,
                        'Make': 271,
                        'Model': 272,
                        'Software': 305,
                        'Artist': 315,
                        'Copyright': 33432
                    }
                    
                    for tag_name, tag_id in exif_tags.items():
                        if tag_id in exif_data:
                            metadata[f'exif_{tag_name.lower()}'] = str(exif_data[tag_id])
            
            except Exception as e:
                logger.debug(f"EXIF extraction failed: {e}")
        
        # File size
        file_stream.seek(0, 2)  # Seek to end
        metadata['file_size'] = file_stream.tell()
        
        return metadata
    
    def _create_image_markdown(self, 
                             ocr_text: str, 
                             ai_description: str, 
                             metadata: Dict[str, Any],
                             stream_info: StreamInfo) -> str:
        """Create markdown content for image"""
        markdown = ""
        
        # Image reference
        if stream_info.filename:
            markdown += f"![{stream_info.filename}]({stream_info.filename})\n\n"
        
        # AI description
        if ai_description:
            markdown += f"## Image Description\n\n{ai_description}\n\n"
        
        # OCR text
        if ocr_text:
            markdown += f"## Extracted Text\n\n{ocr_text}\n\n"
        
        # Image properties
        width = metadata.get('width')
        height = metadata.get('height')
        format_name = metadata.get('format')
        
        if width and height and format_name:
            markdown += f"## Image Properties\n\n"
            markdown += f"- **Format**: {format_name}\n"
            markdown += f"- **Dimensions**: {width} × {height} pixels\n"
            
            if 'file_size' in metadata:
                size_kb = metadata['file_size'] / 1024
                markdown += f"- **File Size**: {size_kb:.1f} KB\n"
            
            markdown += "\n"
        
        return markdown
    
    def _extract_image_title(self, ocr_text: str, ai_description: str, stream_info: StreamInfo) -> Optional[str]:
        """Extract title from image"""
        # Try OCR text first
        if ocr_text:
            lines = ocr_text.split('\n')
            for line in lines:
                line = line.strip()
                if line and len(line) < 100:
                    return self._format_title(line)
        
        # Try AI description
        if ai_description:
            sentences = ai_description.split('.')
            if sentences:
                first_sentence = sentences[0].strip()
                if len(first_sentence) < 100:
                    return self._format_title(first_sentence)
        
        # Use filename as fallback
        if stream_info.filename:
            title = stream_info.filename
            if '.' in title:
                title = title.rsplit('.', 1)[0]
            title = title.replace('_', ' ').replace('-', ' ')
            return self._format_title(title)
        
        return None
    
    def get_format_info(self) -> Dict[str, Any]:
        """Get format information"""
        features = [
            'Image metadata extraction',
            'AI-powered image description'
        ]
        
        if self.tesseract_available or self.easyocr_available:
            features.append('OCR text extraction')
        
        if self.korean_support:
            features.append('Korean text recognition')
        
        return {
            'name': 'Image',
            'description': 'Image converter with OCR and AI description',
            'extensions': self.supported_extensions,
            'mimetypes': self.supported_mimetypes,
            'category': self.category,
            'features': features
        }