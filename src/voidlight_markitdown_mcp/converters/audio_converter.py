"""
Audio file converter with speech-to-text
"""

from typing import BinaryIO, Dict, Any, Optional
import logging
import tempfile
import os

from ..core.base_converter import DocumentConverter, DocumentConverterResult
from ..core.stream_info import StreamInfo
from ..core.exceptions import MissingDependencyException, FileConversionException
from ..utils.format_utils import normalize_whitespace

logger = logging.getLogger(__name__)


class AudioConverter(DocumentConverter):
    """Audio file converter with speech-to-text"""
    
    def __init__(self, 
                 whisper_model: str = "base",
                 openai_api_key: Optional[str] = None,
                 korean_support: bool = True):
        super().__init__(korean_support=korean_support)
        self.whisper_model = whisper_model
        self.openai_api_key = openai_api_key
        self.priority = 3.0
        
        self.supported_extensions = ['.mp3', '.wav', '.flac', '.m4a', '.ogg', '.wma']
        self.supported_mimetypes = [
            'audio/mpeg', 'audio/wav', 'audio/flac', 'audio/mp4', 
            'audio/ogg', 'audio/x-ms-wma'
        ]
        self.category = 'audio'
        
        # Check dependencies
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Check for available dependencies"""
        try:
            import whisper
            self.whisper_available = True
        except ImportError:
            self.whisper_available = False
        
        try:
            import openai
            self.openai_available = bool(self.openai_api_key)
        except ImportError:
            self.openai_available = False
        
        try:
            import pydub
            self.pydub_available = True
        except ImportError:
            self.pydub_available = False
    
    def accepts(self, file_stream: BinaryIO, stream_info: StreamInfo, **kwargs) -> bool:
        """Check if this converter can handle the file"""
        return (stream_info.matches_mimetype(self.supported_mimetypes) or
                stream_info.matches_extension(self.supported_extensions))
    
    def convert(self, file_stream: BinaryIO, stream_info: StreamInfo, **kwargs) -> DocumentConverterResult:
        """Convert audio file"""
        logger.info(f"Converting audio: {stream_info.filename}")
        
        if not (self.whisper_available or self.openai_available):
            raise MissingDependencyException(
                "OpenAI Whisper or OpenAI API is required for audio conversion"
            )
        
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=stream_info.extension or '.mp3') as tmp_file:
                file_stream.seek(0)
                tmp_file.write(file_stream.read())
                tmp_file_path = tmp_file.name
            
            try:
                # Convert audio if needed
                audio_path = self._prepare_audio(tmp_file_path, stream_info)
                
                # Transcribe audio
                transcription = self._transcribe_audio(audio_path)
                
                # Extract metadata
                metadata = self._extract_audio_metadata(tmp_file_path, stream_info)
                
                # Create markdown
                markdown = self._create_audio_markdown(transcription, metadata, stream_info)
                
                # Extract title
                title = self._extract_audio_title(transcription, metadata, stream_info)
                
                return DocumentConverterResult(
                    markdown=self._clean_markdown(markdown),
                    title=title,
                    metadata=metadata
                )
                
            finally:
                # Clean up temporary files
                try:
                    os.unlink(tmp_file_path)
                    if audio_path != tmp_file_path:
                        os.unlink(audio_path)
                except OSError:
                    pass
            
        except Exception as e:
            raise FileConversionException(f"Audio conversion failed: {e}")
    
    def _prepare_audio(self, file_path: str, stream_info: StreamInfo) -> str:
        """Prepare audio file for transcription"""
        # Check if conversion is needed
        extension = stream_info.extension or '.mp3'
        
        if extension in ['.mp3', '.wav'] and self.whisper_available:
            # Whisper can handle these formats directly
            return file_path
        
        if not self.pydub_available:
            logger.warning("pydub not available for audio conversion")
            return file_path
        
        try:
            from pydub import AudioSegment
            
            # Load audio
            if extension == '.mp3':
                audio = AudioSegment.from_mp3(file_path)
            elif extension == '.wav':
                audio = AudioSegment.from_wav(file_path)
            elif extension == '.flac':
                audio = AudioSegment.from_file(file_path, format="flac")
            elif extension == '.m4a':
                audio = AudioSegment.from_file(file_path, format="m4a")
            elif extension == '.ogg':
                audio = AudioSegment.from_ogg(file_path)
            else:
                audio = AudioSegment.from_file(file_path)
            
            # Convert to WAV for better compatibility
            wav_path = file_path.rsplit('.', 1)[0] + '_converted.wav'
            audio.export(wav_path, format="wav")
            
            return wav_path
            
        except Exception as e:
            logger.warning(f"Audio conversion failed: {e}")
            return file_path
    
    def _transcribe_audio(self, audio_path: str) -> str:
        """Transcribe audio to text"""
        # Try OpenAI API first (more accurate)
        if self.openai_available:
            try:
                import openai
                
                client = openai.OpenAI(api_key=self.openai_api_key)
                
                with open(audio_path, 'rb') as audio_file:
                    transcript = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language="ko" if self.korean_support else "en"
                    )
                
                logger.debug("Used OpenAI API for transcription")
                return transcript.text
                
            except Exception as e:
                logger.warning(f"OpenAI API transcription failed: {e}")
        
        # Fallback to local Whisper
        if self.whisper_available:
            try:
                import whisper
                
                # Load model
                model = whisper.load_model(self.whisper_model)
                
                # Transcribe
                options = {}
                if self.korean_support:
                    options['language'] = 'ko'
                
                result = model.transcribe(audio_path, **options)
                
                logger.debug("Used local Whisper for transcription")
                return result['text']
                
            except Exception as e:
                logger.warning(f"Local Whisper transcription failed: {e}")
        
        return ""
    
    def _extract_audio_metadata(self, file_path: str, stream_info: StreamInfo) -> Dict[str, Any]:
        """Extract audio metadata"""
        metadata = self._extract_metadata(None, stream_info)
        
        try:
            if self.pydub_available:
                from pydub import AudioSegment
                
                # Load audio to get basic properties
                if stream_info.extension == '.mp3':
                    audio = AudioSegment.from_mp3(file_path)
                elif stream_info.extension == '.wav':
                    audio = AudioSegment.from_wav(file_path)
                else:
                    audio = AudioSegment.from_file(file_path)
                
                metadata.update({
                    'duration_seconds': len(audio) / 1000.0,
                    'channels': audio.channels,
                    'frame_rate': audio.frame_rate,
                    'sample_width': audio.sample_width
                })
                
                # Format duration as human-readable
                duration = len(audio) / 1000.0
                minutes = int(duration // 60)
                seconds = int(duration % 60)
                metadata['duration_formatted'] = f"{minutes}:{seconds:02d}"
        
        except Exception as e:
            logger.debug(f"Could not extract audio metadata: {e}")
        
        # File size
        try:
            file_size = os.path.getsize(file_path)
            metadata['file_size'] = file_size
        except OSError:
            pass
        
        return metadata
    
    def _create_audio_markdown(self, 
                             transcription: str, 
                             metadata: Dict[str, Any],
                             stream_info: StreamInfo) -> str:
        """Create markdown content for audio"""
        markdown = ""
        
        # Audio file reference
        if stream_info.filename:
            markdown += f"# Audio: {stream_info.filename}\n\n"
        
        # Audio properties
        duration = metadata.get('duration_formatted')
        channels = metadata.get('channels')
        frame_rate = metadata.get('frame_rate')
        
        if duration or channels or frame_rate:
            markdown += "## Audio Properties\n\n"
            
            if duration:
                markdown += f"- **Duration**: {duration}\n"
            if channels:
                channel_desc = "Mono" if channels == 1 else "Stereo" if channels == 2 else f"{channels} channels"
                markdown += f"- **Channels**: {channel_desc}\n"
            if frame_rate:
                markdown += f"- **Sample Rate**: {frame_rate} Hz\n"
            
            if 'file_size' in metadata:
                size_mb = metadata['file_size'] / (1024 * 1024)
                markdown += f"- **File Size**: {size_mb:.1f} MB\n"
            
            markdown += "\n"
        
        # Transcription
        if transcription:
            markdown += "## Transcription\n\n"
            markdown += f"{transcription}\n\n"
        else:
            markdown += "## Transcription\n\n"
            markdown += "*No transcription available*\n\n"
        
        return markdown
    
    def _extract_audio_title(self, 
                           transcription: str, 
                           metadata: Dict[str, Any], 
                           stream_info: StreamInfo) -> Optional[str]:
        """Extract title from audio"""
        # Try first sentence of transcription
        if transcription:
            sentences = transcription.split('.')
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
        features = ['Audio metadata extraction']
        
        if self.whisper_available:
            features.append('Local Whisper transcription')
        
        if self.openai_available:
            features.append('OpenAI API transcription')
        
        if self.korean_support:
            features.append('Korean speech recognition')
        
        if self.pydub_available:
            features.append('Audio format conversion')
        
        return {
            'name': 'Audio',
            'description': 'Audio converter with speech-to-text transcription',
            'extensions': self.supported_extensions,
            'mimetypes': self.supported_mimetypes,
            'category': self.category,
            'features': features
        }