"""
Command line interface for MarkItDown MCP Enhanced
"""

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import List, Optional

from .core.markitdown import MarkItDown
from .config.settings import ConfigManager, create_default_config_file
from .server import create_server


def setup_logging(level: str = "INFO", log_file: Optional[str] = None):
    """Setup logging configuration"""
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    handlers.append(console_handler)
    
    # File handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        handlers.append(file_handler)
    
    logging.basicConfig(
        level=log_level,
        handlers=handlers,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


def convert_command(args):
    """Handle convert command"""
    config_manager = ConfigManager(args.config)
    config = config_manager.get_config()
    
    # Setup logging
    setup_logging(config.server.log_level, config.server.log_file)
    
    # Create MarkItDown instance
    markitdown = MarkItDown(
        enable_builtins=config.converters.enable_builtins,
        enable_plugins=config.converters.enable_plugins,
        llm_client=None,  # TODO: Initialize LLM client
        llm_model=config.llm.llm_model,
        docintel_endpoint=config.azure.endpoint,
        enable_korean_support=config.converters.korean_support,
        max_workers=config.converters.max_workers
    )
    
    # Set conversion options
    markitdown.set_options(
        include_metadata=args.include_metadata or config.conversion.include_metadata,
        extract_images=args.extract_images or config.conversion.extract_images,
        korean_optimization=args.korean_optimization or config.conversion.korean_optimization
    )
    
    try:
        if args.url:
            # Convert URL
            result = markitdown.convert_uri(args.url)
        else:
            # Convert file
            result = markitdown.convert_local(args.input)
        
        # Output result
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result.markdown)
            
            print(f"Converted to: {output_path}")
        else:
            print(result.markdown)
        
        # Output metadata if requested
        if args.metadata and result.metadata:
            metadata_output = args.metadata if args.metadata != "-" else None
            metadata_text = json.dumps(result.metadata, indent=2, ensure_ascii=False)
            
            if metadata_output:
                with open(metadata_output, 'w', encoding='utf-8') as f:
                    f.write(metadata_text)
                print(f"Metadata saved to: {metadata_output}")
            else:
                print("\n--- Metadata ---")
                print(metadata_text)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def analyze_command(args):
    """Handle analyze command"""
    config_manager = ConfigManager(args.config)
    config = config_manager.get_config()
    
    # Setup logging
    setup_logging(config.server.log_level, config.server.log_file)
    
    # Create MarkItDown instance
    markitdown = MarkItDown(
        enable_builtins=config.converters.enable_builtins,
        enable_plugins=config.converters.enable_plugins,
        enable_korean_support=config.converters.korean_support,
        max_workers=config.converters.max_workers
    )
    
    try:
        analysis = markitdown.analyze_structure(args.input)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            print(f"Analysis saved to: {args.output}")
        else:
            print(json.dumps(analysis, indent=2, ensure_ascii=False))
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def formats_command(args):
    """Handle formats command"""
    config_manager = ConfigManager(args.config)
    config = config_manager.get_config()
    
    # Create MarkItDown instance
    markitdown = MarkItDown(
        enable_builtins=config.converters.enable_builtins,
        enable_plugins=config.converters.enable_plugins,
        enable_korean_support=config.converters.korean_support
    )
    
    formats = markitdown.get_supported_formats()
    print(json.dumps(formats, indent=2, ensure_ascii=False))


async def server_command(args):
    """Handle server command"""
    config_manager = ConfigManager(args.config)
    config = config_manager.get_config()
    
    # Override config with command line arguments
    if args.korean_support is not None:
        config.converters.korean_support = args.korean_support
    if args.log_level:
        config.server.log_level = args.log_level
    
    # Setup logging
    setup_logging(config.server.log_level, config.server.log_file)
    
    # Create and run server
    server = create_server(
        enable_builtins=config.converters.enable_builtins,
        enable_plugins=config.converters.enable_plugins,
        enable_korean_support=config.converters.korean_support,
        docintel_endpoint=config.azure.endpoint,
        docintel_key=config.azure.key,
        openai_api_key=config.llm.openai_api_key,
        max_workers=config.converters.max_workers
    )
    
    await server.run()


def config_command(args):
    """Handle config command"""
    if args.action == "create":
        config_path = create_default_config_file(args.output)
        print(f"Created default configuration at: {config_path}")
    
    elif args.action == "show":
        config_manager = ConfigManager(args.config)
        config = config_manager.get_config()
        
        from dataclasses import asdict
        config_dict = asdict(config)
        print(json.dumps(config_dict, indent=2, ensure_ascii=False))
    
    elif args.action == "validate":
        try:
            config_manager = ConfigManager(args.config)
            config = config_manager.get_config()
            print("Configuration is valid")
        except Exception as e:
            print(f"Configuration error: {e}", file=sys.stderr)
            sys.exit(1)


def batch_command(args):
    """Handle batch command"""
    config_manager = ConfigManager(args.config)
    config = config_manager.get_config()
    
    # Setup logging
    setup_logging(config.server.log_level, config.server.log_file)
    
    # Create MarkItDown instance
    markitdown = MarkItDown(
        enable_builtins=config.converters.enable_builtins,
        enable_plugins=config.converters.enable_plugins,
        enable_korean_support=config.converters.korean_support,
        max_workers=config.converters.max_workers
    )
    
    # Set conversion options
    markitdown.set_options(
        include_metadata=args.include_metadata or config.conversion.include_metadata,
        extract_images=args.extract_images or config.conversion.extract_images,
        korean_optimization=args.korean_optimization or config.conversion.korean_optimization
    )
    
    # Get input files
    if args.input_list:
        with open(args.input_list, 'r', encoding='utf-8') as f:
            file_paths = [line.strip() for line in f if line.strip()]
    else:
        file_paths = args.files
    
    if not file_paths:
        print("No input files specified", file=sys.stderr)
        sys.exit(1)
    
    # Process files
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    successful = 0
    failed = 0
    
    for file_path in file_paths:
        try:
            result = markitdown.convert_local(file_path)
            
            # Generate output filename
            input_path = Path(file_path)
            output_path = output_dir / f"{input_path.stem}.md"
            
            # Save result
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result.markdown)
            
            print(f"✓ {file_path} → {output_path}")
            successful += 1
            
        except Exception as e:
            print(f"✗ {file_path}: {e}")
            failed += 1
    
    print(f"\nBatch conversion complete: {successful} successful, {failed} failed")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="MarkItDown MCP Enhanced - Document conversion with Korean support"
    )
    
    parser.add_argument(
        "--config", "-c",
        help="Configuration file path"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Convert command
    convert_parser = subparsers.add_parser("convert", help="Convert a document")
    convert_parser.add_argument("input", nargs="?", help="Input file path")
    convert_parser.add_argument("--url", help="Convert from URL instead of file")
    convert_parser.add_argument("--output", "-o", help="Output file path")
    convert_parser.add_argument("--metadata", help="Output metadata to file (use '-' for stdout)")
    convert_parser.add_argument("--include-metadata", action="store_true", help="Include metadata in output")
    convert_parser.add_argument("--extract-images", action="store_true", help="Extract and describe images")
    convert_parser.add_argument("--korean-optimization", action="store_true", help="Apply Korean text optimization")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze document structure")
    analyze_parser.add_argument("input", help="Input file path")
    analyze_parser.add_argument("--output", "-o", help="Output file path")
    
    # Formats command
    formats_parser = subparsers.add_parser("formats", help="List supported formats")
    
    # Server command
    server_parser = subparsers.add_parser("server", help="Run MCP server")
    server_parser.add_argument("--log-level", help="Log level")
    server_parser.add_argument("--korean-support", action="store_true", help="Enable Korean support")
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Configuration management")
    config_parser.add_argument("action", choices=["create", "show", "validate"], help="Config action")
    config_parser.add_argument("--output", "-o", help="Output path for create action")
    
    # Batch command
    batch_parser = subparsers.add_parser("batch", help="Batch convert files")
    batch_parser.add_argument("--files", nargs="+", help="Input file paths")
    batch_parser.add_argument("--input-list", help="File containing list of input paths")
    batch_parser.add_argument("--output-dir", "-o", required=True, help="Output directory")
    batch_parser.add_argument("--include-metadata", action="store_true", help="Include metadata in output")
    batch_parser.add_argument("--extract-images", action="store_true", help="Extract and describe images")
    batch_parser.add_argument("--korean-optimization", action="store_true", help="Apply Korean text optimization")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Handle commands
    if args.command == "convert":
        if not args.input and not args.url:
            print("Error: input file or --url is required", file=sys.stderr)
            sys.exit(1)
        convert_command(args)
    
    elif args.command == "analyze":
        analyze_command(args)
    
    elif args.command == "formats":
        formats_command(args)
    
    elif args.command == "server":
        asyncio.run(server_command(args))
    
    elif args.command == "config":
        config_command(args)
    
    elif args.command == "batch":
        batch_command(args)


if __name__ == "__main__":
    main()