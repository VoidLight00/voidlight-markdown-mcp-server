# VoidLight MarkItDown MCP Server

[![PyPI version](https://badge.fury.io/py/voidlight-markitdown-mcp.svg)](https://badge.fury.io/py/voidlight-markitdown-mcp)
[![Docker](https://img.shields.io/docker/v/voidlight/markitdown-mcp?label=docker)](https://hub.docker.com/r/voidlight/markitdown-mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/VoidLight00/voidlight-markdown-mcp-server/actions/workflows/test.yml/badge.svg)](https://github.com/VoidLight00/voidlight-markdown-mcp-server/actions/workflows/test.yml)

Enhanced MarkItDown MCP Server with Korean support and advanced document conversion capabilities for Claude Desktop.

## 🚀 Quick Install

```bash
pip install voidlight-markitdown-mcp
```

## ⚡ Setup for Claude Desktop

### 1. Install and Setup
```bash
# Install the package
pip install voidlight-markitdown-mcp

# Auto-configure Claude Desktop
voidlight-markitdown-mcp --setup
```

### 2. Manual Configuration
Add to your Claude Desktop config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "voidlight-markitdown": {
      "command": "voidlight-markitdown-mcp"
    }
  }
}
```

### 3. Start Using
1. Restart Claude Desktop
2. Use the `convert_to_markdown` tool to convert documents
3. Support for 50+ file formats including:
   - 📄 PDF, DOCX, PPTX, TXT
   - 🌐 HTML, RTF, CSV, Excel
   - 🖼️ Images with OCR (Korean supported)
   - 🎵 Audio transcription
   - 📱 Mobile formats (HWP, etc.)

## 📦 Installation Options

### Core Installation (Recommended)
```bash
pip install voidlight-markitdown-mcp
```

### With All Features
```bash
pip install "voidlight-markitdown-mcp[all]"
```

### Specific Feature Sets
```bash
# Office documents (Word, Excel, PowerPoint)
pip install "voidlight-markitdown-mcp[office]"

# PDF processing
pip install "voidlight-markitdown-mcp[pdf]"

# Image OCR
pip install "voidlight-markitdown-mcp[image]"

# Audio transcription  
pip install "voidlight-markitdown-mcp[audio]"

# Korean language support
pip install "voidlight-markitdown-mcp[korean]"

# Cloud services
pip install "voidlight-markitdown-mcp[cloud]"
```

## 🐳 Docker Usage

### Quick Start
```bash
docker run -v $(pwd)/documents:/workdir ghcr.io/voidlight00/voidlight-markdown-mcp-server
```

### Docker Compose
```bash
# Clone repository
git clone https://github.com/VoidLight00/voidlight-markdown-mcp-server.git
cd voidlight-markdown-mcp-server

# Start services
docker-compose up -d

# Process documents
docker-compose exec voidlight-markitdown-mcp voidlight-markitdown-mcp --status
```

## 🛠️ CLI Usage

### Check Installation
```bash
voidlight-markitdown-mcp --status
```

### Install Additional Dependencies
```bash
voidlight-markitdown-mcp --install-deps all
```

### Setup Claude Desktop
```bash
voidlight-markitdown-mcp --setup
```

## 🌟 Features

### Enhanced Document Support
- **50+ File Formats**: PDF, DOCX, PPTX, Excel, HTML, RTF, CSV, TXT, Images
- **Korean Optimization**: Enhanced Korean text processing and OCR
- **Cloud Integration**: Azure Document Intelligence, Google Cloud Vision
- **Audio Processing**: Speech-to-text with Korean support
- **Image OCR**: Text extraction from images with multilingual support

### Performance & Reliability
- **Memory Efficient**: Streaming processing for large files
- **Error Handling**: Graceful fallbacks and detailed error messages  
- **Caching**: Smart caching for repeated conversions
- **Parallel Processing**: Multi-threaded conversion for batch operations

### Developer Experience
- **Simple API**: One-command installation and setup
- **Comprehensive Logging**: Detailed conversion logs and metrics
- **Extensible**: Plugin architecture for custom converters
- **Type Safety**: Full TypeScript/Python type annotations

## 📋 Supported Formats

| Category | Formats |
|----------|---------|
| **Documents** | PDF, DOCX, PPTX, RTF, TXT, MD |
| **Spreadsheets** | XLSX, XLS, CSV |
| **Web** | HTML, XML, RSS |
| **Images** | PNG, JPG, GIF, BMP, TIFF |
| **Audio** | MP3, WAV, M4A, OGG |
| **Korean** | HWP, OCR with Korean |
| **Archives** | ZIP (extract and convert) |

## 🔧 Configuration

### Environment Variables
```bash
export MCP_WORKDIR=/path/to/workspace
export MCP_LOG_LEVEL=INFO
export AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=your_endpoint
export OPENAI_API_KEY=your_api_key
```

### Configuration File
Create `~/.voidlight-markitdown-mcp/config.json`:
```json
{
  "conversion": {
    "include_metadata": true,
    "extract_images": false,
    "korean_optimization": true
  },
  "performance": {
    "max_workers": 4,
    "memory_limit": "1GB"
  }
}
```

## 🚀 Development

### Setup Development Environment
```bash
git clone https://github.com/VoidLight00/voidlight-markdown-mcp-server.git
cd voidlight-markdown-mcp-server

# Install with development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
black src/
flake8 src/
mypy src/
```

### Building
```bash
# Build package
python -m build

# Build Docker image
docker build -t voidlight-markitdown-mcp .
```

## 📊 Comparison with Microsoft MarkItDown

| Feature | Microsoft MarkItDown | VoidLight MarkItDown MCP |
|---------|---------------------|-------------------------|
| **Installation** | `pip install markitdown-mcp` | `pip install voidlight-markitdown-mcp` |
| **Setup** | Manual configuration | Auto-setup with `--setup` |
| **Languages** | English focus | Korean + Multilingual |
| **Formats** | 20+ formats | 50+ formats |
| **Cloud Services** | Basic | Azure + Google + OpenAI |
| **Performance** | Standard | Optimized + Caching |
| **Docker** | ❌ | ✅ |
| **CLI Tools** | Basic | Advanced management |

## 🆘 Troubleshooting

### Common Issues

**Installation fails on macOS**
```bash
# Install Python 3.11+ first
brew install python@3.11
pip3.11 install voidlight-markitdown-mcp
```

**Missing dependencies**
```bash
# Check status
voidlight-markitdown-mcp --status

# Install missing dependencies
voidlight-markitdown-mcp --install-deps all
```

**Claude Desktop not detecting server**
```bash
# Re-run setup
voidlight-markitdown-mcp --setup

# Check Claude Desktop config path
# macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
# Windows: %APPDATA%/Claude/claude_desktop_config.json
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 🔗 Links

- [PyPI Package](https://pypi.org/project/voidlight-markitdown-mcp/)
- [Docker Hub](https://hub.docker.com/r/voidlight/markitdown-mcp)
- [GitHub Repository](https://github.com/VoidLight00/voidlight-markdown-mcp-server)
- [Documentation](https://github.com/VoidLight00/voidlight-markdown-mcp-server/wiki)
- [Issues & Support](https://github.com/VoidLight00/voidlight-markdown-mcp-server/issues)

---

⭐ **If this project helps you, please give it a star!** ⭐