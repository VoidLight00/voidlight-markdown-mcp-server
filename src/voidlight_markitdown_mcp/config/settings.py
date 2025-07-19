"""
Configuration management for MarkItDown MCP Enhanced
"""

import os
import json
import logging
from typing import Dict, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass, asdict, field

logger = logging.getLogger(__name__)


@dataclass
class ConverterSettings:
    """Settings for document converters"""
    enable_builtins: bool = True
    enable_plugins: bool = True
    korean_support: bool = True
    max_workers: int = 4


@dataclass
class LLMSettings:
    """Settings for LLM integration"""
    openai_api_key: Optional[str] = None
    llm_model: str = "gpt-4o"
    max_tokens: int = 300
    temperature: float = 0.1


@dataclass
class AzureSettings:
    """Settings for Azure Document Intelligence"""
    endpoint: Optional[str] = None
    key: Optional[str] = None
    enabled: bool = False


@dataclass
class OCRSettings:
    """Settings for OCR processing"""
    tesseract_path: Optional[str] = None
    easyocr_enabled: bool = True
    tesseract_enabled: bool = True
    languages: list = field(default_factory=lambda: ["ko", "en"])


@dataclass
class AudioSettings:
    """Settings for audio processing"""
    whisper_model: str = "base"
    local_whisper_enabled: bool = True
    openai_whisper_enabled: bool = False


@dataclass
class ServerSettings:
    """Settings for MCP server"""
    log_level: str = "INFO"
    log_file: Optional[str] = None
    enable_cors: bool = False
    max_file_size_mb: int = 100


@dataclass
class ConversionOptions:
    """Default conversion options"""
    include_metadata: bool = False
    extract_images: bool = False
    korean_optimization: bool = False
    preserve_formatting: bool = True


@dataclass
class MarkItDownConfig:
    """Main configuration class"""
    converters: ConverterSettings = field(default_factory=ConverterSettings)
    llm: LLMSettings = field(default_factory=LLMSettings)
    azure: AzureSettings = field(default_factory=AzureSettings)
    ocr: OCRSettings = field(default_factory=OCRSettings)
    audio: AudioSettings = field(default_factory=AudioSettings)
    server: ServerSettings = field(default_factory=ServerSettings)
    conversion: ConversionOptions = field(default_factory=ConversionOptions)


class ConfigManager:
    """Configuration manager"""
    
    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        self.config_path = self._resolve_config_path(config_path)
        self.config = self._load_config()
    
    def _resolve_config_path(self, config_path: Optional[Union[str, Path]]) -> Path:
        """Resolve configuration file path"""
        if config_path:
            return Path(config_path)
        
        # Try environment variable
        env_path = os.getenv("MARKITDOWN_CONFIG")
        if env_path:
            return Path(env_path)
        
        # Try current directory
        current_config = Path("markitdown_config.json")
        if current_config.exists():
            return current_config
        
        # Try user home directory
        home_config = Path.home() / ".markitdown" / "config.json"
        if home_config.exists():
            return home_config
        
        # Default to current directory
        return current_config
    
    def _load_config(self) -> MarkItDownConfig:
        """Load configuration from file or environment"""
        config = MarkItDownConfig()
        
        # Load from file if exists
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                config = self._dict_to_config(data)
                logger.info(f"Loaded configuration from {self.config_path}")
            except Exception as e:
                logger.warning(f"Failed to load config from {self.config_path}: {e}")
        
        # Override with environment variables
        self._load_from_environment(config)
        
        return config
    
    def _dict_to_config(self, data: Dict[str, Any]) -> MarkItDownConfig:
        """Convert dictionary to configuration object"""
        config = MarkItDownConfig()
        
        # Update each section
        if "converters" in data:
            config.converters = ConverterSettings(**data["converters"])
        
        if "llm" in data:
            config.llm = LLMSettings(**data["llm"])
        
        if "azure" in data:
            config.azure = AzureSettings(**data["azure"])
        
        if "ocr" in data:
            config.ocr = OCRSettings(**data["ocr"])
        
        if "audio" in data:
            config.audio = AudioSettings(**data["audio"])
        
        if "server" in data:
            config.server = ServerSettings(**data["server"])
        
        if "conversion" in data:
            config.conversion = ConversionOptions(**data["conversion"])
        
        return config
    
    def _load_from_environment(self, config: MarkItDownConfig):
        """Load settings from environment variables"""
        env_mappings = {
            # LLM settings
            "OPENAI_API_KEY": ("llm", "openai_api_key"),
            "LLM_MODEL": ("llm", "llm_model"),
            
            # Azure settings
            "AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT": ("azure", "endpoint"),
            "AZURE_DOCUMENT_INTELLIGENCE_KEY": ("azure", "key"),
            
            # OCR settings
            "TESSERACT_PATH": ("ocr", "tesseract_path"),
            
            # Audio settings
            "WHISPER_MODEL": ("audio", "whisper_model"),
            
            # Server settings
            "LOG_LEVEL": ("server", "log_level"),
            "LOG_FILE": ("server", "log_file"),
            
            # Converter settings
            "KOREAN_SUPPORT": ("converters", "korean_support"),
            "MAX_WORKERS": ("converters", "max_workers"),
        }
        
        for env_var, (section, field_name) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                section_obj = getattr(config, section)
                
                # Type conversion
                field_type = type(getattr(section_obj, field_name))
                if field_type == bool:
                    value = value.lower() in ("true", "1", "yes", "on")
                elif field_type == int:
                    try:
                        value = int(value)
                    except ValueError:
                        logger.warning(f"Invalid integer value for {env_var}: {value}")
                        continue
                elif field_type == float:
                    try:
                        value = float(value)
                    except ValueError:
                        logger.warning(f"Invalid float value for {env_var}: {value}")
                        continue
                
                setattr(section_obj, field_name, value)
                logger.debug(f"Set {section}.{field_name} = {value} from environment")
    
    def save_config(self, path: Optional[Union[str, Path]] = None):
        """Save configuration to file"""
        save_path = Path(path) if path else self.config_path
        
        try:
            # Create directory if needed
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert to dictionary
            config_dict = asdict(self.config)
            
            # Save to file
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved configuration to {save_path}")
            
        except Exception as e:
            logger.error(f"Failed to save config to {save_path}: {e}")
            raise
    
    def get_config(self) -> MarkItDownConfig:
        """Get current configuration"""
        return self.config
    
    def update_config(self, updates: Dict[str, Any]):
        """Update configuration with new values"""
        for section_name, section_data in updates.items():
            if hasattr(self.config, section_name):
                section_obj = getattr(self.config, section_name)
                for field_name, value in section_data.items():
                    if hasattr(section_obj, field_name):
                        setattr(section_obj, field_name, value)
                        logger.debug(f"Updated {section_name}.{field_name} = {value}")
    
    def create_default_config(self, path: Optional[Union[str, Path]] = None):
        """Create a default configuration file"""
        save_path = Path(path) if path else self.config_path
        
        # Create default config
        default_config = MarkItDownConfig()
        
        # Save as template
        save_path.parent.mkdir(parents=True, exist_ok=True)
        config_dict = asdict(default_config)
        
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Created default configuration at {save_path}")
        return save_path


def load_config(config_path: Optional[Union[str, Path]] = None) -> MarkItDownConfig:
    """Load configuration (convenience function)"""
    manager = ConfigManager(config_path)
    return manager.get_config()


def create_default_config_file(path: Optional[Union[str, Path]] = None) -> Path:
    """Create default configuration file (convenience function)"""
    manager = ConfigManager()
    return manager.create_default_config(path)