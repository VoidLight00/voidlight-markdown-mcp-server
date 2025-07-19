# Voidlight 마크다운 MCP 서버

한국어 지원을 강화하고 더 많은 파일 형식을 지원합니다.

## 🚀 빠른 시작 (Claude Desktop)

### npx로 간편 설치
```bash
# macOS/Linux
npx markitdown-mcp-enhanced

# Windows (명령 프롬프트)
npx markitdown-mcp-enhanced

# Windows (PowerShell)
npx markitdown-mcp-enhanced
```

### Claude Desktop 설정

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

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

Claude Desktop을 재시작하면 바로 사용 가능합니다! 🎉

### 📋 상세 설치 가이드
- **Windows 사용자**: [WINDOWS_SETUP.md](WINDOWS_SETUP.md) 참조
- **일반 사용자**: [CLAUDE_DESKTOP_SETUP.md](CLAUDE_DESKTOP_SETUP.md) 참조

## 🎯 주요 특징

### 1차 목표: 완전한 기능
- ✅ MarkItDown의 모든 기능을 MCP 서버로 구현
- ✅ 동일한 입출력 형식 지원 (PDF, DOCX, 이미지, 오디오, HTML 등)
- ✅ 같은 변환 품질 제공
- ✅ 확장 가능한 플러그인 시스템

### 2차 목표: 업그레이드 기능
- 🇰🇷 **한국어 지원 강화**: 한국어 텍스트 정규화, 한국어 OCR 최적화, HWP 파일 지원
- 📄 **더 많은 파일 형식**: RTF, 로그 파일, 설정 파일, RST, LaTeX 등
- ⚡ **성능 최적화**: 스트림 기반 처리, 메모리 효율성
- 📊 **고급 메타데이터**: 문서 구조 분석, 통계 정보

## 🔧 지원 기능

### MCP 도구 (3개)
1. **`convert_to_markdown`**: 다양한 파일 형식을 마크다운으로 변환
2. **`analyze_document_structure`**: 문서 구조 분석 및 메타데이터 추출
3. **`list_supported_formats`**: 지원하는 파일 형식 목록 조회

### 지원 파일 형식 (20+)

#### 📄 문서
- **PDF**: pdfminer.six, Azure Document Intelligence
- **DOCX**: mammoth, python-docx
- **PPTX**: python-pptx
- **XLSX/XLS**: pandas, openpyxl, xlrd
- **HWP**: pyhwp, olefile (한국어 특화)
- **RTF**: striprtf
- **텍스트**: TXT, LOG, CFG, INI, MD, RST, TEX

#### 🖼️ 이미지
- **JPEG/PNG/GIF**: PIL, LLM 설명 생성, EXIF 메타데이터
- **한국어 OCR**: 네이버 클로바, Google Vision, Tesseract, EasyOCR

#### 🎵 오디오
- **MP3/WAV/M4A**: mutagen, 음성 전사, 메타데이터 추출

#### 🌐 웹
- **HTML**: BeautifulSoup, markdownify
- **RSS**: feedparser
- **YouTube**: 자막 추출

#### 📊 데이터
- **JSON/XML/CSV**: 구조화된 데이터 변환

## 🚀 빠른 시작

### 환경 설정
```bash
# 저장소 클론
git clone https://github.com/voidlight/voidlight-markdown-mcp-server.git
cd voidlight-markdown-mcp-server

# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일을 편집하여 API 키 설정
```

### 시스템 의존성 설치
```bash
# macOS
brew install exiftool ffmpeg

# Ubuntu/Debian
sudo apt-get install exiftool ffmpeg

# Windows - 수동 설치 필요
# ExifTool: https://exiftool.org/
# FFmpeg: https://ffmpeg.org/
```

### MCP 서버 실행
```bash
# 개발 모드
python -m src.markitdown_mcp_enhanced.server

# 프로덕션 모드
pip install -e .
markitdown-mcp-enhanced
```

### Docker 사용
```bash
# 이미지 빌드
docker build -t voidlight-markdown-mcp .

# 컨테이너 실행
docker run -p 8000:8000 voidlight-markdown-mcp
```

## 📖 사용법

### 기본 변환
```python
from markitdown_mcp_enhanced import MarkItDown

# 기본 사용
md = MarkItDown()
result = md.convert("document.pdf")
print(result.markdown)

# 한국어 최적화
md = MarkItDown(enable_korean_support=True)
result = md.convert("한글문서.hwp")
print(result.markdown)

# LLM 통합 (이미지 설명)
from openai import OpenAI
client = OpenAI()
md = MarkItDown(llm_client=client)
result = md.convert("image.jpg")
print(result.markdown)
```

### MCP 클라이언트 사용
```python
import mcp

# MCP 클라이언트 연결
client = mcp.Client()

# 파일 변환
result = client.call_tool(
    "convert_to_markdown",
    {"uri": "file:///path/to/document.pdf"}
)

# 문서 구조 분석
analysis = client.call_tool(
    "analyze_document_structure", 
    {"uri": "file:///path/to/document.docx"}
)
```

## 🔌 플러그인 시스템

### 플러그인 개발
```python
from markitdown_mcp_enhanced.core.base_converter import DocumentConverter

class MyConverter(DocumentConverter):
    supported_extensions = ['.myext']
    supported_mimetypes = ['application/my-format']
    
    def accepts(self, file_stream, stream_info, **kwargs):
        return stream_info.matches_extension(self.supported_extensions)
    
    def convert(self, file_stream, stream_info, **kwargs):
        # 변환 로직
        return DocumentConverterResult(markdown=converted_text)
```

### 플러그인 등록
```python
# setup.py
entry_points={
    "markitdown.plugin": [
        "my_converter = my_plugin:MyConverter",
    ],
}
```

## 🇰🇷 한국어 지원

### 한국어 텍스트 정규화
- 한국어 조사 및 어미 처리
- 한국어 문장 부호 정규화
- 띄어쓰기 자동 교정

### 한국어 OCR
- 네이버 클로바 OCR API 지원
- 한국어 전용 Tesseract 설정
- OCR 결과 후처리 및 품질 향상

### HWP 파일 지원
- 한글 문서 (.hwp, .hwpx) 변환
- 한국어 메타데이터 추출
- 한국어 제목 자동 인식

## 🛠️ 개발

### 개발 환경 설정
```bash
# 개발 의존성 설치
pip install -r requirements-dev.txt

# pre-commit 설정
pre-commit install

# 테스트 실행
pytest

# 코드 품질 검사
black .
isort .
pylint src/
mypy src/
```

### 프로젝트 구조
```
src/
├── markitdown_mcp_enhanced/
│   ├── __init__.py
│   ├── server.py              # MCP 서버 메인
│   ├── core/                  # 핵심 엔진
│   │   ├── markitdown.py
│   │   ├── base_converter.py
│   │   └── stream_info.py
│   ├── converters/            # 변환기들
│   │   ├── pdf_converter.py
│   │   ├── docx_converter.py
│   │   └── ...
│   ├── plugins/               # 플러그인 시스템
│   ├── utils/                 # 유틸리티
│   └── config/                # 설정 관리
tests/                         # 테스트
docs/                          # 문서
```

## 📋 요구사항

### 필수 요구사항
- Python 3.10+
- 메모리 8GB 이상
- 저장공간 10GB 이상

### 선택적 요구사항
- ExifTool (이미지 메타데이터)
- FFmpeg (오디오 처리)
- GPU (AI 기능 가속)

## 🔒 보안

- API 키는 환경 변수로 관리
- 임시 파일 자동 삭제
- 입력 검증 및 제한
- 안전한 XML 파싱

## 📄 라이선스

MIT License - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🤝 기여

1. 포크 생성
2. 기능 브랜치 생성 (`git checkout -b feature/amazing-feature`)
3. 변경사항 커밋 (`git commit -m 'Add amazing feature'`)
4. 브랜치 푸시 (`git push origin feature/amazing-feature`)
5. Pull Request 생성

## 📞 지원

- 이슈 리포트: [GitHub Issues](https://github.com/voidlight/voidlight-markdown-mcp-server/issues)
- 문서: [프로젝트 문서](./docs/)
- 이메일: voidlight@example.com

## 📈 로드맵

- [ ] 더 많은 파일 형식 지원
- [ ] 성능 최적화
- [ ] 웹 UI 제공
- [ ] 클라우드 배포 지원
- [ ] 다국어 지원 확장

## 🙏 감사

- [Microsoft MarkItDown](https://github.com/microsoft/markitdown) - 원본 프로젝트
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP 프로토콜
- 모든 오픈소스 라이브러리 기여자들

---

**Voidlight 마크다운 MCP 서버**로 더 나은 문서 변환 경험을 시작하세요! 🚀
