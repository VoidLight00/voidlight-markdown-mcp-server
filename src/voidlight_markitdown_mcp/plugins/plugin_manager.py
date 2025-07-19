"""
Plugin management system for MarkItDown MCP Enhanced
"""

import importlib
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import pkg_resources

from ..core.base_converter import DocumentConverter

logger = logging.getLogger(__name__)


class PluginManager:
    """Plugin manager for loading and managing converters"""
    
    def __init__(self):
        self.loaded_plugins: List[DocumentConverter] = []
        self.plugin_registry: Dict[str, Dict[str, Any]] = {}
    
    def load_plugins(self) -> List[DocumentConverter]:
        """Load all available plugins"""
        plugins = []
        
        # Load entry point plugins
        plugins.extend(self._load_entry_point_plugins())
        
        # Load file-based plugins
        plugins.extend(self._load_file_plugins())
        
        self.loaded_plugins = plugins
        return plugins
    
    def _load_entry_point_plugins(self) -> List[DocumentConverter]:
        """Load plugins via entry points"""
        plugins = []
        
        try:
            # Load plugins from markitdown_mcp_converters entry point group
            for entry_point in pkg_resources.iter_entry_points('markitdown_mcp_converters'):
                try:
                    converter_class = entry_point.load()
                    
                    # Validate that it's a DocumentConverter
                    if not issubclass(converter_class, DocumentConverter):
                        logger.warning(f"Plugin {entry_point.name} is not a DocumentConverter")
                        continue
                    
                    # Instantiate the converter
                    converter = converter_class()
                    plugins.append(converter)
                    
                    # Register plugin info
                    self.plugin_registry[entry_point.name] = {
                        'name': entry_point.name,
                        'class': converter_class.__name__,
                        'module': converter_class.__module__,
                        'type': 'entry_point',
                        'converter': converter
                    }
                    
                    logger.info(f"Loaded entry point plugin: {entry_point.name}")
                    
                except Exception as e:
                    logger.error(f"Failed to load entry point plugin {entry_point.name}: {e}")
        
        except Exception as e:
            logger.debug(f"Entry point plugin loading failed: {e}")
        
        return plugins
    
    def _load_file_plugins(self) -> List[DocumentConverter]:
        """Load plugins from plugin directory"""
        plugins = []
        
        # Get plugin directory
        plugin_dir = Path(__file__).parent / "converters"
        if not plugin_dir.exists():
            return plugins
        
        # Load Python files in the plugin directory
        for plugin_file in plugin_dir.glob("*.py"):
            if plugin_file.name.startswith("_"):
                continue  # Skip private files
            
            try:
                # Import the module
                module_name = f"markitdown_mcp_enhanced.plugins.converters.{plugin_file.stem}"
                module = importlib.import_module(module_name)
                
                # Look for DocumentConverter subclasses
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    
                    if (isinstance(attr, type) and 
                        issubclass(attr, DocumentConverter) and 
                        attr != DocumentConverter):
                        
                        # Instantiate the converter
                        converter = attr()
                        plugins.append(converter)
                        
                        # Register plugin info
                        plugin_name = f"{plugin_file.stem}.{attr_name}"
                        self.plugin_registry[plugin_name] = {
                            'name': plugin_name,
                            'class': attr_name,
                            'module': module_name,
                            'type': 'file',
                            'file': str(plugin_file),
                            'converter': converter
                        }
                        
                        logger.info(f"Loaded file plugin: {plugin_name}")
            
            except Exception as e:
                logger.error(f"Failed to load plugin from {plugin_file}: {e}")
        
        return plugins
    
    def get_plugin_info(self) -> Dict[str, Any]:
        """Get information about all loaded plugins"""
        return {
            'loaded_count': len(self.loaded_plugins),
            'plugins': {
                name: {
                    'name': info['name'],
                    'class': info['class'],
                    'module': info['module'],
                    'type': info['type'],
                    'format_info': info['converter'].get_format_info()
                }
                for name, info in self.plugin_registry.items()
            }
        }
    
    def reload_plugins(self) -> List[DocumentConverter]:
        """Reload all plugins"""
        self.loaded_plugins.clear()
        self.plugin_registry.clear()
        return self.load_plugins()
    
    def get_plugin_by_name(self, name: str) -> Optional[DocumentConverter]:
        """Get a specific plugin by name"""
        plugin_info = self.plugin_registry.get(name)
        return plugin_info['converter'] if plugin_info else None
    
    def unload_plugin(self, name: str) -> bool:
        """Unload a specific plugin"""
        if name not in self.plugin_registry:
            return False
        
        # Remove from registry
        plugin_info = self.plugin_registry.pop(name)
        converter = plugin_info['converter']
        
        # Remove from loaded plugins
        if converter in self.loaded_plugins:
            self.loaded_plugins.remove(converter)
        
        logger.info(f"Unloaded plugin: {name}")
        return True


def create_plugin_template(plugin_name: str, output_dir: Path) -> Path:
    """Create a plugin template file"""
    template_content = f'''"""
{plugin_name} converter plugin for MarkItDown MCP Enhanced
"""

from typing import BinaryIO, Dict, Any, Optional
import logging

from markitdown_mcp_enhanced.core.base_converter import DocumentConverter, DocumentConverterResult
from markitdown_mcp_enhanced.core.stream_info import StreamInfo
from markitdown_mcp_enhanced.core.exceptions import FileConversionException

logger = logging.getLogger(__name__)


class {plugin_name}Converter(DocumentConverter):
    """{plugin_name} file converter"""
    
    def __init__(self, korean_support: bool = True):
        super().__init__(korean_support=korean_support)
        self.priority = 5.0  # Medium priority
        
        # TODO: Define supported extensions and MIME types
        self.supported_extensions = ['.example']
        self.supported_mimetypes = ['application/example']
        self.category = 'documents'  # or 'images', 'audio', 'web', etc.
    
    def accepts(self, file_stream: BinaryIO, stream_info: StreamInfo, **kwargs) -> bool:
        """Check if this converter can handle the file"""
        return (stream_info.matches_mimetype(self.supported_mimetypes) or
                stream_info.matches_extension(self.supported_extensions))
    
    def convert(self, file_stream: BinaryIO, stream_info: StreamInfo, **kwargs) -> DocumentConverterResult:
        """Convert {plugin_name.lower()} file"""
        logger.info(f"Converting {{stream_info.filename}} with {plugin_name}Converter")
        
        try:
            # TODO: Implement conversion logic
            file_stream.seek(0)
            content = file_stream.read()
            
            # TODO: Process content and convert to markdown
            markdown = "# {plugin_name} Content\\n\\nTODO: Implement conversion logic"
            
            # Extract metadata
            metadata = self._extract_metadata(file_stream, stream_info)
            
            # TODO: Extract title from content
            title = "TODO: Extract title"
            
            return DocumentConverterResult(
                markdown=self._clean_markdown(markdown),
                title=self._format_title(title) if title else None,
                metadata=metadata
            )
            
        except Exception as e:
            raise FileConversionException(f"{plugin_name} conversion failed: {{e}}")
    
    def get_format_info(self) -> Dict[str, Any]:
        """Get format information"""
        return {{
            'name': '{plugin_name}',
            'description': '{plugin_name} file converter',
            'extensions': self.supported_extensions,
            'mimetypes': self.supported_mimetypes,
            'category': self.category,
            'features': [
                'TODO: List converter features'
            ]
        }}
'''
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Write template file
    plugin_file = output_dir / f"{plugin_name.lower()}_converter.py"
    with open(plugin_file, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    return plugin_file