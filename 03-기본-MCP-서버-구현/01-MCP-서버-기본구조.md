# MCP 서버 기본 구조 설계

## 1. 프로젝트 구조

### 1.1 디렉터리 구조
```
markitdown-mcp-enhanced/
├── src/
│   └── markitdown_mcp_enhanced/
│       ├── __init__.py
│       ├── server.py              # MCP 서버 메인
│       ├── core/                  # 핵심 변환 엔진
│       │   ├── __init__.py
│       │   ├── markitdown.py      # 메인 변환기
│       │   ├── base_converter.py  # 기본 변환기 클래스
│       │   ├── stream_info.py     # 스트림 정보 관리
│       │   └── exceptions.py      # 예외 클래스
│       ├── converters/            # 변환기 구현
│       │   ├── __init__.py
│       │   ├── pdf_converter.py
│       │   ├── docx_converter.py
│       │   ├── image_converter.py
│       │   ├── audio_converter.py
│       │   ├── html_converter.py
│       │   └── ...
│       ├── plugins/               # 플러그인 시스템
│       │   ├── __init__.py
│       │   ├── plugin_manager.py
│       │   └── sample_plugin.py
│       ├── utils/                 # 유틸리티
│       │   ├── __init__.py
│       │   ├── file_detector.py
│       │   ├── stream_utils.py
│       │   └── format_utils.py
│       └── config/                # 설정 관리
│           ├── __init__.py
│           ├── settings.py
│           └── logging_config.py
├── tests/                         # 테스트 파일
│   ├── unit/
│   ├── integration/
│   └── test_files/
├── docs/                          # 문서
├── pyproject.toml                 # 프로젝트 설정
├── README.md
└── requirements.txt
```

### 1.2 핵심 패키지 구조
```python
# src/markitdown_mcp_enhanced/__init__.py
from .core.markitdown import MarkItDown
from .core.base_converter import DocumentConverter, DocumentConverterResult
from .core.stream_info import StreamInfo
from .core.exceptions import *

__version__ = "1.0.0"
__all__ = [
    "MarkItDown",
    "DocumentConverter", 
    "DocumentConverterResult",
    "StreamInfo"
]
```

## 2. MCP 서버 메인 구조

### 2.1 서버 기본 구조
```python
# src/markitdown_mcp_enhanced/server.py
import asyncio
import os
from typing import List, Dict, Any, Optional
from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from mcp.server.models import InitializationOptions

from .core.markitdown import MarkItDown
from .core.exceptions import MarkItDownException
from .config.settings import ServerSettings
from .config.logging_config import setup_logging

# 로깅 설정
logger = setup_logging()

class MarkItDownMCPServer:
    """Enhanced MarkItDown MCP Server"""
    
    def __init__(self, settings: Optional[ServerSettings] = None):
        self.settings = settings or ServerSettings()
        self.app = Server("markitdown-enhanced")
        self.markitdown = MarkItDown(
            enable_plugins=self.settings.enable_plugins,
            llm_client=self.settings.llm_client,
            llm_model=self.settings.llm_model,
            enable_korean_support=self.settings.enable_korean_support
        )
        
        # MCP 서버 핸들러 등록
        self._register_handlers()
    
    def _register_handlers(self):
        """MCP 서버 핸들러 등록"""
        
        @self.app.list_tools()
        async def list_tools() -> List[Tool]:
            return [
                Tool(
                    name="convert_to_markdown",
                    description="Convert various file formats to markdown",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "uri": {
                                "type": "string",
                                "description": "URI (http:, https:, file:, or data:) of the resource to convert"
                            },
                            "options": {
                                "type": "object",
                                "properties": {
                                    "include_metadata": {
                                        "type": "boolean",
                                        "description": "Include file metadata in output",
                                        "default": False
                                    },
                                    "extract_images": {
                                        "type": "boolean", 
                                        "description": "Extract and describe images",
                                        "default": False
                                    },
                                    "korean_optimization": {
                                        "type": "boolean",
                                        "description": "Apply Korean language optimizations",
                                        "default": False
                                    }
                                },
                                "additionalProperties": False
                            }
                        },
                        "required": ["uri"],
                        "additionalProperties": False
                    }
                ),
                Tool(
                    name="analyze_document_structure",
                    description="Analyze document structure and extract metadata",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "uri": {
                                "type": "string",
                                "description": "URI of the document to analyze"
                            }
                        },
                        "required": ["uri"],
                        "additionalProperties": False
                    }
                ),
                Tool(
                    name="list_supported_formats",
                    description="List all supported file formats",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False
                    }
                )
            ]
        
        @self.app.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            try:
                if name == "convert_to_markdown":
                    return await self._convert_to_markdown(arguments)
                elif name == "analyze_document_structure":
                    return await self._analyze_document_structure(arguments)
                elif name == "list_supported_formats":
                    return await self._list_supported_formats()
                else:
                    raise ValueError(f"Unknown tool: {name}")
            
            except Exception as e:
                logger.error(f"Tool '{name}' failed: {str(e)}")
                return [TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]
    
    async def _convert_to_markdown(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """마크다운 변환 도구 구현"""
        uri = arguments["uri"]
        options = arguments.get("options", {})
        
        logger.info(f"Converting {uri} to markdown")
        
        # 옵션 설정
        self.markitdown.set_options(
            include_metadata=options.get("include_metadata", False),
            extract_images=options.get("extract_images", False),
            korean_optimization=options.get("korean_optimization", False)
        )
        
        # 변환 수행
        result = self.markitdown.convert_uri(uri)
        
        # 결과 반환
        response = [TextContent(type="text", text=result.markdown)]
        
        # 메타데이터 포함 시 추가 정보 제공
        if options.get("include_metadata") and result.metadata:
            metadata_text = self._format_metadata(result.metadata)
            response.append(TextContent(type="text", text=metadata_text))
        
        return response
    
    async def _analyze_document_structure(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """문서 구조 분석 도구 구현"""
        uri = arguments["uri"]
        
        logger.info(f"Analyzing document structure for {uri}")
        
        # 문서 분석
        analysis = self.markitdown.analyze_structure(uri)
        
        return [TextContent(
            type="text",
            text=self._format_structure_analysis(analysis)
        )]
    
    async def _list_supported_formats(self) -> List[TextContent]:
        """지원 형식 목록 도구 구현"""
        formats = self.markitdown.get_supported_formats()
        
        format_list = "# Supported File Formats\n\n"
        for category, formats_in_category in formats.items():
            format_list += f"## {category}\n\n"
            for fmt in formats_in_category:
                format_list += f"- **{fmt['name']}**: {fmt['description']}\n"
                format_list += f"  - Extensions: {', '.join(fmt['extensions'])}\n"
                format_list += f"  - MIME types: {', '.join(fmt['mimetypes'])}\n\n"
        
        return [TextContent(type="text", text=format_list)]
    
    def _format_metadata(self, metadata: Dict[str, Any]) -> str:
        """메타데이터 포맷팅"""
        formatted = "\n## Document Metadata\n\n"
        
        for key, value in metadata.items():
            formatted += f"- **{key}**: {value}\n"
        
        return formatted
    
    def _format_structure_analysis(self, analysis: Dict[str, Any]) -> str:
        """구조 분석 결과 포맷팅"""
        formatted = "# Document Structure Analysis\n\n"
        
        formatted += f"## Overview\n"
        formatted += f"- **Document Type**: {analysis.get('document_type', 'Unknown')}\n"
        formatted += f"- **Page Count**: {analysis.get('page_count', 'N/A')}\n"
        formatted += f"- **Word Count**: {analysis.get('word_count', 'N/A')}\n"
        formatted += f"- **Language**: {analysis.get('language', 'Unknown')}\n\n"
        
        if analysis.get('headings'):
            formatted += "## Headings Structure\n\n"
            for heading in analysis['headings']:
                formatted += f"{'  ' * (heading['level'] - 1)}- {heading['text']}\n"
            formatted += "\n"
        
        if analysis.get('images'):
            formatted += "## Images\n\n"
            for i, image in enumerate(analysis['images'], 1):
                formatted += f"{i}. {image.get('alt_text', 'No alt text')}\n"
                if image.get('caption'):
                    formatted += f"   Caption: {image['caption']}\n"
            formatted += "\n"
        
        if analysis.get('tables'):
            formatted += "## Tables\n\n"
            for i, table in enumerate(analysis['tables'], 1):
                formatted += f"{i}. {table['rows']} rows × {table['columns']} columns\n"
                if table.get('caption'):
                    formatted += f"   Caption: {table['caption']}\n"
            formatted += "\n"
        
        return formatted
    
    def run(self):
        """서버 실행"""
        import mcp.server.stdio
        
        logger.info("Starting MarkItDown MCP Server")
        mcp.server.stdio.run_server(self.app)

# 서버 인스턴스 생성 및 실행
def main():
    """메인 실행 함수"""
    settings = ServerSettings()
    server = MarkItDownMCPServer(settings)
    server.run()

if __name__ == "__main__":
    main()
```

## 3. 설정 관리 시스템

### 3.1 서버 설정 클래스
```python
# src/markitdown_mcp_enhanced/config/settings.py
import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ServerSettings:
    """서버 설정 클래스"""
    
    # 기본 설정
    enable_plugins: bool = True
    enable_korean_support: bool = True
    log_level: str = "INFO"
    
    # LLM 설정
    llm_client: Optional[Any] = None
    llm_model: str = "gpt-4o"
    openai_api_key: Optional[str] = None
    
    # Azure Document Intelligence 설정
    azure_docintel_endpoint: Optional[str] = None
    azure_docintel_key: Optional[str] = None
    
    # 파일 처리 설정
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    temp_dir: Optional[Path] = None
    
    # 성능 설정
    worker_threads: int = 4
    cache_enabled: bool = True
    cache_size: int = 1000
    
    # 한국어 지원 설정
    korean_font_path: Optional[str] = None
    korean_dict_path: Optional[str] = None
    
    def __post_init__(self):
        """환경 변수에서 설정 로드"""
        self.enable_plugins = os.getenv("MARKITDOWN_ENABLE_PLUGINS", "true").lower() == "true"
        self.enable_korean_support = os.getenv("MARKITDOWN_KOREAN_SUPPORT", "true").lower() == "true"
        self.log_level = os.getenv("MARKITDOWN_LOG_LEVEL", "INFO")
        
        # LLM 설정
        self.llm_model = os.getenv("MARKITDOWN_LLM_MODEL", "gpt-4o")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Azure 설정
        self.azure_docintel_endpoint = os.getenv("AZURE_DOCINTEL_ENDPOINT")
        self.azure_docintel_key = os.getenv("AZURE_DOCINTEL_KEY")
        
        # 파일 처리 설정
        if max_size := os.getenv("MARKITDOWN_MAX_FILE_SIZE"):
            self.max_file_size = int(max_size)
        
        if temp_dir := os.getenv("MARKITDOWN_TEMP_DIR"):
            self.temp_dir = Path(temp_dir)
        
        # 성능 설정
        if worker_threads := os.getenv("MARKITDOWN_WORKER_THREADS"):
            self.worker_threads = int(worker_threads)
        
        self.cache_enabled = os.getenv("MARKITDOWN_CACHE_ENABLED", "true").lower() == "true"
        
        if cache_size := os.getenv("MARKITDOWN_CACHE_SIZE"):
            self.cache_size = int(cache_size)
        
        # 한국어 지원 설정
        self.korean_font_path = os.getenv("MARKITDOWN_KOREAN_FONT_PATH")
        self.korean_dict_path = os.getenv("MARKITDOWN_KOREAN_DICT_PATH")
        
        # LLM 클라이언트 초기화
        if self.openai_api_key:
            self._initialize_llm_client()
    
    def _initialize_llm_client(self):
        """LLM 클라이언트 초기화"""
        try:
            from openai import OpenAI
            self.llm_client = OpenAI(api_key=self.openai_api_key)
        except ImportError:
            print("Warning: OpenAI client not available. Install with: pip install openai")
```

### 3.2 로깅 설정
```python
# src/markitdown_mcp_enhanced/config/logging_config.py
import logging
import os
from typing import Optional

def setup_logging(log_level: Optional[str] = None) -> logging.Logger:
    """로깅 설정"""
    
    # 로그 레벨 설정
    level = log_level or os.getenv("MARKITDOWN_LOG_LEVEL", "INFO")
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # 로거 설정
    logger = logging.getLogger("markitdown_mcp_enhanced")
    logger.setLevel(numeric_level)
    
    # 핸들러가 이미 설정되어 있으면 스킵
    if logger.handlers:
        return logger
    
    # 콘솔 핸들러 설정
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    
    # 포맷터 설정
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # 로거에 핸들러 추가
    logger.addHandler(console_handler)
    
    # 파일 핸들러 설정 (선택사항)
    if log_file := os.getenv("MARKITDOWN_LOG_FILE"):
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger
```

## 4. 메인 실행 진입점

### 4.1 프로젝트 설정 파일
```toml
# pyproject.toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "markitdown-mcp-enhanced"
description = "Enhanced MarkItDown MCP Server with Korean support"
version = "1.0.0"
authors = [
    {name = "Your Name", email = "your.email@example.com"},
]
dependencies = [
    "mcp>=1.0.0",
    "beautifulsoup4>=4.12.0",
    "requests>=2.31.0",
    "markdownify>=0.11.6",
    "magika>=0.6.1",
    "charset-normalizer>=3.2.0",
    "defusedxml>=0.7.1",
    "pydantic>=2.0.0",
    "typing-extensions>=4.8.0",
]

[project.optional-dependencies]
all = [
    "python-pptx>=0.6.21",
    "mammoth>=1.6.0",
    "lxml>=4.9.3",
    "pandas>=2.0.0",
    "openpyxl>=3.1.0",
    "xlrd>=2.0.0",
    "pdfminer.six>=20221105",
    "olefile>=0.46",
    "pydub>=0.25.1",
    "SpeechRecognition>=3.10.0",
    "youtube-transcript-api>=0.6.0",
    "azure-ai-documentintelligence>=1.0.0",
    "azure-identity>=1.15.0",
    "openai>=1.0.0",
    "Pillow>=10.0.0",
    "korean-nlp>=0.1.0",
]

dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "black>=23.7.0",
    "isort>=5.12.0",
    "pylint>=2.17.0",
    "mypy>=1.5.0",
    "pre-commit>=3.4.0",
]

[project.scripts]
markitdown-mcp-enhanced = "markitdown_mcp_enhanced.server:main"

[tool.hatch.build.targets.wheel]
packages = ["src/markitdown_mcp_enhanced"]

[tool.black]
line-length = 88
target-version = ['py310']

[tool.isort]
profile = "black"
multi_line_output = 3

[tool.pylint.messages_control]
disable = [
    "missing-docstring",
    "invalid-name",
    "too-few-public-methods",
]

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

### 4.2 Docker 지원
```dockerfile
# Dockerfile
FROM python:3.10-slim

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    exiftool \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉터리 설정
WORKDIR /app

# 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 복사
COPY src/ ./src/
COPY pyproject.toml .

# 패키지 설치
RUN pip install -e .

# 서버 실행
CMD ["markitdown-mcp-enhanced"]
```

## 5. 다음 단계

1. **핵심 변환 엔진 구현**: `MarkItDown` 클래스 및 기본 변환기 구현
2. **변환기 시스템**: 각 파일 형식별 변환기 구현
3. **플러그인 시스템**: 확장 가능한 플러그인 아키텍처 구현
4. **테스트 시스템**: 종합적인 테스트 시스템 구축
5. **문서화**: 사용자 가이드 및 개발자 문서 작성

이 기본 구조를 바탕으로 단계적으로 기능을 구현해 나가면 완전한 MarkItDown MCP 서버를 구축할 수 있습니다.