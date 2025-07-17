"""
Setup script for MarkItDown MCP Enhanced
"""

from setuptools import setup, find_packages
import os

# Read README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="markitdown-mcp-enhanced",
    version="1.0.0",
    author="Voidlight",
    author_email="voidlight@example.com",
    description="Enhanced MarkItDown MCP Server with Korean support and additional features",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/voidlight/markitdown-mcp-enhanced",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Text Processing :: Markup",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Office Suites",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "pdf": ["pdfminer.six"],
        "docx": ["python-docx"],
        "image": ["Pillow", "pytesseract", "easyocr"],
        "audio": ["openai-whisper", "pydub"],
        "html": ["beautifulsoup4", "markdownify"],
        "azure": ["azure-ai-documentintelligence"],
        "openai": ["openai"],
        "all": [
            "pdfminer.six",
            "python-docx", 
            "Pillow",
            "pytesseract",
            "easyocr",
            "openai-whisper",
            "pydub",
            "beautifulsoup4",
            "markdownify",
            "azure-ai-documentintelligence",
            "openai"
        ]
    },
    entry_points={
        "console_scripts": [
            "markitdown-mcp=markitdown_mcp_enhanced.cli:main",
            "markitdown-mcp-server=markitdown_mcp_enhanced.__main__:main",
        ],
        "markitdown_mcp_converters": [
            # Entry point for plugin converters
            # Plugins can register themselves here
        ],
    },
    include_package_data=True,
    package_data={
        "markitdown_mcp_enhanced": [
            "config/*.json",
            "plugins/converters/*.py",
        ],
    },
    keywords=[
        "document conversion",
        "markdown",
        "pdf",
        "docx", 
        "korean",
        "mcp",
        "server",
        "text processing",
        "ocr",
        "speech-to-text"
    ],
    project_urls={
        "Bug Reports": "https://github.com/voidlight/markitdown-mcp-enhanced/issues",
        "Source": "https://github.com/voidlight/markitdown-mcp-enhanced",
        "Documentation": "https://github.com/voidlight/markitdown-mcp-enhanced/blob/main/README.md",
    },
)