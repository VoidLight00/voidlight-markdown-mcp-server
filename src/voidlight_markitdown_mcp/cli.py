#!/usr/bin/env python3
"""
VoidLight MarkItDown MCP Server CLI

Command-line interface for the VoidLight MarkItDown MCP Server.
Provides easy installation and setup for Claude Desktop integration.
"""

import argparse
import json
import os
import sys
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

from . import __version__, __description__


def get_claude_config_path() -> Optional[Path]:
    """Get the path to Claude Desktop configuration file."""
    home = Path.home()
    
    # macOS
    claude_config = home / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    if claude_config.parent.exists():
        return claude_config
        
    # Windows
    claude_config = home / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json"
    if claude_config.parent.exists():
        return claude_config
        
    # Linux
    claude_config = home / ".config" / "claude" / "claude_desktop_config.json"
    if claude_config.parent.exists():
        return claude_config
        
    return None


def setup_claude_desktop() -> bool:
    """Setup Claude Desktop configuration for VoidLight MarkItDown MCP."""
    config_path = get_claude_config_path()
    if not config_path:
        print("❌ Claude Desktop configuration directory not found.")
        print("Please install Claude Desktop first.")
        return False
        
    # Create config directory if it doesn't exist
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Load existing config or create new one
    config = {}
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️  Warning: Could not read existing config: {e}")
            config = {}
    
    # Ensure mcpServers section exists
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    
    # Add VoidLight MarkItDown MCP configuration
    config["mcpServers"]["voidlight-markitdown"] = {
        "command": "voidlight-markitdown-mcp",
        "args": [],
        "env": {}
    }
    
    # Write updated config
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"✅ Claude Desktop configuration updated: {config_path}")
        print("✅ VoidLight MarkItDown MCP server configured successfully!")
        print("\n📖 Usage:")
        print("1. Restart Claude Desktop")
        print("2. Use the 'convert_to_markdown' tool to convert documents")
        return True
    except IOError as e:
        print(f"❌ Failed to write configuration: {e}")
        return False


def check_dependencies() -> Dict[str, bool]:
    """Check status of optional dependencies."""
    dependencies = {
        'magika': False,
        'python-magic': False,
        'easyocr': False,
        'pdfminer.six': False,
        'mammoth': False,
        'python-pptx': False,
        'openpyxl': False,
        'Pillow': False,
    }
    
    for dep in dependencies:
        try:
            __import__(dep.replace('-', '_').replace('.', '_'))
            dependencies[dep] = True
        except ImportError:
            pass
    
    return dependencies


def print_status():
    """Print current installation status."""
    print(f"🚀 VoidLight MarkItDown MCP Server v{__version__}")
    print(f"📝 {__description__}")
    print()
    
    # Check dependencies
    deps = check_dependencies()
    print("📦 Dependencies Status:")
    for dep, installed in deps.items():
        status = "✅" if installed else "❌"
        print(f"  {status} {dep}")
    
    print()
    
    # Check Claude Desktop config
    config_path = get_claude_config_path()
    if config_path and config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            if "mcpServers" in config and "voidlight-markitdown" in config["mcpServers"]:
                print("✅ Claude Desktop configuration: OK")
            else:
                print("❌ Claude Desktop configuration: Not configured")
                print("   Run 'voidlight-markitdown-mcp --setup' to configure")
        except Exception:
            print("❌ Claude Desktop configuration: Error reading config")
    else:
        print("❌ Claude Desktop configuration: Not found")


def run_server():
    """Run the MCP server."""
    try:
        from .server import MarkItDownMCPServer
        server = MarkItDownMCPServer()
        server.run()
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="voidlight-markitdown-mcp",
        description=__description__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  voidlight-markitdown-mcp                 # Run MCP server
  voidlight-markitdown-mcp --setup         # Setup Claude Desktop
  voidlight-markitdown-mcp --status        # Check installation status
  voidlight-markitdown-mcp --version       # Show version
        """
    )
    
    parser.add_argument(
        "--version", 
        action="version", 
        version=f"%(prog)s {__version__}"
    )
    
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Setup Claude Desktop configuration"
    )
    
    parser.add_argument(
        "--status",
        action="store_true", 
        help="Show installation and configuration status"
    )
    
    parser.add_argument(
        "--install-deps",
        choices=["all", "office", "pdf", "image", "audio", "web", "korean", "cloud"],
        help="Install optional dependencies"
    )
    
    args = parser.parse_args()
    
    if args.setup:
        success = setup_claude_desktop()
        sys.exit(0 if success else 1)
    
    elif args.status:
        print_status()
        sys.exit(0)
    
    elif args.install_deps:
        print(f"Installing '{args.install_deps}' dependencies...")
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", 
                f"voidlight-markitdown-mcp[{args.install_deps}]"
            ], check=True)
            print(f"✅ Dependencies '{args.install_deps}' installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            sys.exit(1)
    
    else:
        # Default: Run MCP server
        run_server()


if __name__ == "__main__":
    main()