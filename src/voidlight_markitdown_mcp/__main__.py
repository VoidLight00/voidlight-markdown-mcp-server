"""
Main entry point for MarkItDown MCP Enhanced
"""

import asyncio
import sys
from .server import main

if __name__ == "__main__":
    asyncio.run(main())