# 빠른 참조 가이드

## 🚀 즉시 사용법

### 설치 (한 줄)
```bash
npx markitdown-mcp-enhanced
```

### Claude Desktop 설정 (복사 붙여넣기)
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

### 설정 파일 위치
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

## 💬 Claude Desktop 사용 예시

```
PDF 파일을 마크다운으로 변환해주세요: /path/to/document.pdf
```

```
이 이미지에서 텍스트를 추출해주세요: /path/to/image.jpg
```

```
HTML 페이지를 마크다운으로 변환해주세요: https://example.com/page.html
```

```
지원되는 파일 형식을 알려주세요
```

## 🔧 문제 해결

### 일반적인 오류
1. **"command not found: npx"** → Node.js 설치 필요
2. **"Python not found"** → Python 3.8+ 설치 필요
3. **"MCP server failed"** → Claude Desktop 재시작

### 디버그 모드
```json
{
  "env": {
    "LOG_LEVEL": "DEBUG"
  }
}
```

### 수동 테스트
```bash
node bin/markitdown-mcp-enhanced.js --version
```

## 📁 지원 파일 형식

| 카테고리 | 확장자 | 변환기 |
|----------|--------|--------|
| **문서** | .pdf, .docx, .txt, .md | PDF, DOCX, Text |
| **이미지** | .jpg, .png, .gif, .bmp | Image + OCR |
| **오디오** | .mp3, .wav, .flac | Audio + STT |
| **웹** | .html, .htm | HTML |

## 🇰🇷 한국어 특화 기능

- ✅ **한국어 OCR**: EasyOCR + Tesseract
- ✅ **한국어 STT**: Whisper 한국어 모델
- ✅ **텍스트 정규화**: 한국어 간격 최적화
- ✅ **메타데이터**: 한국어 제목/내용 추출

## 🔑 API 키 설정 (선택사항)

### OpenAI (이미지 설명)
```json
{
  "env": {
    "OPENAI_API_KEY": "your-api-key"
  }
}
```

### Azure Document Intelligence (고급 PDF)
```json
{
  "env": {
    "AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT": "your-endpoint",
    "AZURE_DOCUMENT_INTELLIGENCE_KEY": "your-key"
  }
}
```

## 🖥️ Windows 전용

### PowerShell에서 직접 실행
```powershell
.\bin\markitdown-mcp-enhanced.ps1 -Version
```

### 실행 정책 문제
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 🔄 업데이트

### 최신 버전 확인
```bash
npx markitdown-mcp-enhanced@latest
```

### 캐시 클리어
```bash
npx clear-npx-cache
npm cache clean --force
```

## 📞 지원

- **GitHub**: https://github.com/VoidLight00/voidlight-markdown-mcp-server
- **Issues**: GitHub Issues 탭에서 문제 보고
- **문서**: 프로젝트 폴더의 `docs/` 디렉토리

## 🎯 핵심 명령어 모음

```bash
# 설치 및 실행
npx markitdown-mcp-enhanced

# 버전 확인
node bin/markitdown-mcp-enhanced.js --version

# 도움말
node bin/markitdown-mcp-enhanced.js --help

# Windows PowerShell
.\bin\markitdown-mcp-enhanced.ps1 -Version

# Windows CMD
bin\markitdown-mcp-enhanced.cmd
```

---
**업데이트**: 2025-07-18  
**버전**: 1.0.0  
**상태**: ✅ 배포 준비 완료