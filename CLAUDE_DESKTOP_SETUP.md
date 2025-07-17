# Claude Desktop 설정 가이드

## 🚀 빠른 설치 (npx 사용)

### 1. Claude Desktop 설정 파일 수정

Claude Desktop의 설정 파일을 열어주세요:

**macOS:**
```bash
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Windows:**
```bash
code %APPDATA%\Claude\claude_desktop_config.json
```

### 2. MCP 서버 설정 추가

설정 파일에 다음 내용을 추가하세요:

```json
{
  "mcpServers": {
    "markitdown-mcp-enhanced": {
      "command": "npx",
      "args": ["markitdown-mcp-enhanced"],
      "env": {
        "KOREAN_SUPPORT": "true",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### 3. 고급 설정 (선택사항)

API 키와 고급 기능을 사용하려면 환경 변수를 추가하세요:

```json
{
  "mcpServers": {
    "markitdown-mcp-enhanced": {
      "command": "npx",
      "args": ["markitdown-mcp-enhanced"],
      "env": {
        "KOREAN_SUPPORT": "true",
        "LOG_LEVEL": "INFO",
        "OPENAI_API_KEY": "your-openai-api-key-here",
        "AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT": "your-azure-endpoint",
        "AZURE_DOCUMENT_INTELLIGENCE_KEY": "your-azure-key"
      }
    }
  }
}
```

### 4. Claude Desktop 재시작

설정을 저장한 후 Claude Desktop을 완전히 종료하고 다시 시작하세요.

## 🛠️ 사용 가능한 도구

Claude Desktop에서 다음 도구들을 사용할 수 있습니다:

### `convert_file` - 파일 변환
로컬 문서 파일을 마크다운으로 변환합니다.

**예시:**
```
/Users/username/document.pdf 파일을 마크다운으로 변환해주세요.
```

### `convert_url` - URL 변환  
웹 페이지나 온라인 문서를 마크다운으로 변환합니다.

**예시:**
```
https://example.com/document.html 페이지를 마크다운으로 변환해주세요.
```

### `analyze_document` - 문서 분석
문서의 구조와 메타데이터를 분석합니다.

**예시:**
```
/Users/username/document.docx 파일을 분석해주세요.
```

### `get_supported_formats` - 지원 형식 확인
지원되는 모든 파일 형식을 확인합니다.

**예시:**
```
지원되는 파일 형식을 알려주세요.
```

### `convert_batch` - 일괄 변환
여러 파일을 한 번에 변환합니다.

**예시:**
```
/Users/username/documents/ 폴더의 모든 PDF 파일을 마크다운으로 변환해주세요.
```

## 📋 지원되는 파일 형식

- **문서**: PDF, DOCX, TXT, MD
- **이미지**: JPG, PNG, GIF, BMP, TIFF, WEBP (OCR 지원)
- **오디오**: MP3, WAV, FLAC, M4A, OGG (음성-텍스트 변환)
- **웹**: HTML, HTM

## 🇰🇷 한국어 지원 기능

- 한국어 OCR (EasyOCR + Tesseract)
- 한국어 텍스트 정규화 및 간격 최적화
- 한국어 음성 인식 (Whisper)
- 한국어 문서 메타데이터 처리

## 🔧 문제 해결

### Python이 없다는 오류가 나는 경우
```bash
# Python 3.8+ 설치 확인
python3 --version

# Python이 없으면 설치
# macOS (Homebrew)
brew install python3

# Windows
# https://www.python.org/downloads/ 에서 다운로드
```

### 의존성 설치 실패
```bash
# 수동으로 설치
cd /path/to/markitdown-mcp-enhanced
pip install -e .
```

### 로그 확인
Claude Desktop의 로그를 확인하려면:
- macOS: `~/Library/Logs/Claude/mcp.log`
- Windows: `%APPDATA%\Claude\logs\mcp.log`

## 📞 지원

문제가 발생하면 GitHub Issues에 문의해주세요:
https://github.com/VoidLight00/voidlight-markdown-mcp-server/issues

---

**참고**: 이 MCP 서버는 Microsoft MarkItDown을 기반으로 한국어 지원과 추가 기능을 구현한 향상된 버전입니다.