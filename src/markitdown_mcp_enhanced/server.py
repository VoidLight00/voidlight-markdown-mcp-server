"""
MCP Server for MarkItDown Enhanced
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import tempfile
import os

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool, 
    TextContent, 
    ImageContent, 
    EmbeddedResource,
    CallToolResult
)

from .core.markitdown import MarkItDown
from .core.exceptions import MarkItDownException, UnsupportedFormatException
from .utils.format_utils import normalize_whitespace

logger = logging.getLogger(__name__)


class MarkItDownMCPServer:
    """MCP Server for MarkItDown Enhanced"""
    
    def __init__(self, 
                 enable_builtins: bool = True,
                 enable_plugins: bool = True,
                 llm_client=None,
                 llm_model: str = "gpt-4o",
                 docintel_endpoint: Optional[str] = None,
                 docintel_key: Optional[str] = None,
                 openai_api_key: Optional[str] = None,
                 exiftool_path: Optional[str] = None,
                 enable_korean_support: bool = True,
                 max_workers: int = 4):
        
        self.server = Server("markitdown-mcp-enhanced")
        
        # Initialize MarkItDown
        self.markitdown = MarkItDown(
            enable_builtins=enable_builtins,
            enable_plugins=enable_plugins,
            llm_client=llm_client,
            llm_model=llm_model,
            docintel_endpoint=docintel_endpoint,
            enable_korean_support=enable_korean_support,
            max_workers=max_workers
        )
        
        # Configure converters with additional parameters
        self._configure_converters(
            docintel_key=docintel_key,
            openai_api_key=openai_api_key,
            exiftool_path=exiftool_path
        )
        
        # Register MCP tools
        self._register_tools()
    
    def _configure_converters(self, **kwargs):
        """Configure converters with additional parameters"""
        # This would involve updating converter configurations
        # For now, we'll keep the basic initialization
        pass
    
    def _register_tools(self):
        """Register MCP tools"""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available tools"""
            return [
                Tool(
                    name="convert_file",
                    description="Convert a document file to markdown format",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file to convert"
                            },
                            "options": {
                                "type": "object", 
                                "description": "Conversion options",
                                "properties": {
                                    "include_metadata": {
                                        "type": "boolean",
                                        "description": "Include metadata in output"
                                    },
                                    "extract_images": {
                                        "type": "boolean",
                                        "description": "Extract and describe images"
                                    },
                                    "korean_optimization": {
                                        "type": "boolean",
                                        "description": "Apply Korean text optimization"
                                    }
                                }
                            }
                        },
                        "required": ["file_path"]
                    }
                ),
                Tool(
                    name="convert_url",
                    description="Convert a document from URL to markdown format",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "URL of the document to convert"
                            },
                            "options": {
                                "type": "object",
                                "description": "Conversion options",
                                "properties": {
                                    "include_metadata": {
                                        "type": "boolean",
                                        "description": "Include metadata in output"
                                    },
                                    "extract_images": {
                                        "type": "boolean",
                                        "description": "Extract and describe images"
                                    },
                                    "korean_optimization": {
                                        "type": "boolean",
                                        "description": "Apply Korean text optimization"
                                    }
                                }
                            }
                        },
                        "required": ["url"]
                    }
                ),
                Tool(
                    name="analyze_document",
                    description="Analyze document structure and extract metadata",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file to analyze"
                            }
                        },
                        "required": ["file_path"]
                    }
                ),
                Tool(
                    name="get_supported_formats",
                    description="Get list of supported document formats",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="convert_batch",
                    description="Convert multiple files in batch",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_paths": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of file paths to convert"
                            },
                            "output_dir": {
                                "type": "string",
                                "description": "Output directory for converted files"
                            },
                            "options": {
                                "type": "object",
                                "description": "Conversion options",
                                "properties": {
                                    "include_metadata": {
                                        "type": "boolean",
                                        "description": "Include metadata in output"
                                    },
                                    "extract_images": {
                                        "type": "boolean",
                                        "description": "Extract and describe images"
                                    },
                                    "korean_optimization": {
                                        "type": "boolean",
                                        "description": "Apply Korean text optimization"
                                    }
                                }
                            }
                        },
                        "required": ["file_paths"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool calls"""
            try:
                if name == "convert_file":
                    return await self._handle_convert_file(arguments)
                elif name == "convert_url":
                    return await self._handle_convert_url(arguments)
                elif name == "analyze_document":
                    return await self._handle_analyze_document(arguments)
                elif name == "get_supported_formats":
                    return await self._handle_get_supported_formats(arguments)
                elif name == "convert_batch":
                    return await self._handle_convert_batch(arguments)
                else:
                    return CallToolResult(
                        content=[TextContent(
                            type="text",
                            text=f"Unknown tool: {name}"
                        )],
                        isError=True
                    )
            
            except Exception as e:
                logger.error(f"Tool call failed: {e}")
                return CallToolResult(
                    content=[TextContent(
                        type="text", 
                        text=f"Error: {str(e)}"
                    )],
                    isError=True
                )
    
    async def _handle_convert_file(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle file conversion"""
        file_path = arguments.get("file_path")
        options = arguments.get("options", {})
        
        if not file_path:
            return CallToolResult(
                content=[TextContent(type="text", text="file_path is required")],
                isError=True
            )
        
        try:
            # Set options
            self.markitdown.set_options(**options)
            
            # Convert file
            result = self.markitdown.convert_local(file_path)
            
            # Prepare response
            response_parts = [
                TextContent(
                    type="text",
                    text=f"# Converted: {Path(file_path).name}\n\n{result.markdown}"
                )
            ]
            
            # Add metadata if requested
            if options.get("include_metadata") and result.metadata:
                metadata_text = json.dumps(result.metadata, indent=2, ensure_ascii=False)
                response_parts.append(TextContent(
                    type="text",
                    text=f"\n\n## Metadata\n\n```json\n{metadata_text}\n```"
                ))
            
            return CallToolResult(content=response_parts)
            
        except FileNotFoundError:
            return CallToolResult(
                content=[TextContent(type="text", text=f"File not found: {file_path}")],
                isError=True
            )
        except UnsupportedFormatException as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Unsupported format: {e}")],
                isError=True
            )
        except MarkItDownException as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Conversion error: {e}")],
                isError=True
            )
    
    async def _handle_convert_url(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle URL conversion"""
        url = arguments.get("url")
        options = arguments.get("options", {})
        
        if not url:
            return CallToolResult(
                content=[TextContent(type="text", text="url is required")],
                isError=True
            )
        
        try:
            # Set options
            self.markitdown.set_options(**options)
            
            # Convert URL
            result = self.markitdown.convert_uri(url)
            
            # Prepare response
            response_parts = [
                TextContent(
                    type="text",
                    text=f"# Converted: {url}\n\n{result.markdown}"
                )
            ]
            
            # Add metadata if requested
            if options.get("include_metadata") and result.metadata:
                metadata_text = json.dumps(result.metadata, indent=2, ensure_ascii=False)
                response_parts.append(TextContent(
                    type="text",
                    text=f"\n\n## Metadata\n\n```json\n{metadata_text}\n```"
                ))
            
            return CallToolResult(content=response_parts)
            
        except UnsupportedFormatException as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Unsupported format: {e}")],
                isError=True
            )
        except MarkItDownException as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Conversion error: {e}")],
                isError=True
            )
    
    async def _handle_analyze_document(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle document analysis"""
        file_path = arguments.get("file_path")
        
        if not file_path:
            return CallToolResult(
                content=[TextContent(type="text", text="file_path is required")],
                isError=True
            )
        
        try:
            # Analyze document
            analysis = self.markitdown.analyze_structure(file_path)
            
            # Format analysis results
            analysis_text = json.dumps(analysis, indent=2, ensure_ascii=False)
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"# Document Analysis: {Path(file_path).name}\n\n```json\n{analysis_text}\n```"
                )]
            )
            
        except FileNotFoundError:
            return CallToolResult(
                content=[TextContent(type="text", text=f"File not found: {file_path}")],
                isError=True
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Analysis error: {e}")],
                isError=True
            )
    
    async def _handle_get_supported_formats(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle get supported formats"""
        try:
            formats = self.markitdown.get_supported_formats()
            formats_text = json.dumps(formats, indent=2, ensure_ascii=False)
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"# Supported Formats\n\n```json\n{formats_text}\n```"
                )]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error getting formats: {e}")],
                isError=True
            )
    
    async def _handle_convert_batch(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle batch conversion"""
        file_paths = arguments.get("file_paths", [])
        output_dir = arguments.get("output_dir")
        options = arguments.get("options", {})
        
        if not file_paths:
            return CallToolResult(
                content=[TextContent(type="text", text="file_paths is required")],
                isError=True
            )
        
        try:
            # Set options
            self.markitdown.set_options(**options)
            
            results = []
            errors = []
            
            for file_path in file_paths:
                try:
                    # Convert file
                    result = self.markitdown.convert_local(file_path)
                    
                    # Save to output directory if specified
                    if output_dir:
                        output_path = Path(output_dir) / f"{Path(file_path).stem}.md"
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        with open(output_path, 'w', encoding='utf-8') as f:
                            f.write(result.markdown)
                        
                        results.append(f"✓ {file_path} → {output_path}")
                    else:
                        results.append(f"✓ {file_path} (converted)")
                
                except Exception as e:
                    errors.append(f"✗ {file_path}: {e}")
            
            # Prepare summary
            summary = f"# Batch Conversion Results\n\n"
            summary += f"**Total files:** {len(file_paths)}\n"
            summary += f"**Successful:** {len(results)}\n"
            summary += f"**Failed:** {len(errors)}\n\n"
            
            if results:
                summary += "## Successful Conversions\n\n"
                for result in results:
                    summary += f"- {result}\n"
                summary += "\n"
            
            if errors:
                summary += "## Failed Conversions\n\n"
                for error in errors:
                    summary += f"- {error}\n"
                summary += "\n"
            
            return CallToolResult(
                content=[TextContent(type="text", text=summary)]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Batch conversion error: {e}")],
                isError=True
            )
    
    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


def create_server(**kwargs) -> MarkItDownMCPServer:
    """Create MCP server instance"""
    return MarkItDownMCPServer(**kwargs)


async def main():
    """Main entry point"""
    import argparse
    import os
    import sys
    
    parser = argparse.ArgumentParser(description="MarkItDown MCP Enhanced Server")
    parser.add_argument("--log-level", default="INFO", help="Log level")
    parser.add_argument("--korean-support", action="store_true", default=True, help="Enable Korean support")
    parser.add_argument("--openai-api-key", help="OpenAI API key for image descriptions and audio transcription")
    parser.add_argument("--azure-endpoint", help="Azure Document Intelligence endpoint")
    parser.add_argument("--azure-key", help="Azure Document Intelligence key")
    
    args = parser.parse_args()
    
    # Configure logging to stderr to avoid interfering with MCP protocol
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr
    )
    
    # Get configuration from environment variables
    openai_api_key = args.openai_api_key or os.getenv("OPENAI_API_KEY")
    azure_endpoint = args.azure_endpoint or os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
    azure_key = args.azure_key or os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")
    korean_support = args.korean_support or os.getenv("KOREAN_SUPPORT", "true").lower() == "true"
    
    # Create server
    server = create_server(
        enable_korean_support=korean_support,
        docintel_endpoint=azure_endpoint,
        docintel_key=azure_key,
        openai_api_key=openai_api_key
    )
    
    # Run server
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())