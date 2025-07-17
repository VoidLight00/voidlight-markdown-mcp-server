# Windows 설치 가이드

## 🚀 Windows에서 빠른 설치

### 방법 1: npx 사용 (권장)

**전제 조건:**
- Node.js 18+ 설치 필요 ([다운로드](https://nodejs.org/))
- Python 3.8+ 설치 필요 ([다운로드](https://www.python.org/downloads/))

```cmd
npx markitdown-mcp-enhanced
```

### 방법 2: 직접 실행

**PowerShell에서:**
```powershell
.\bin\markitdown-mcp-enhanced.ps1
```

**명령 프롬프트에서:**
```cmd
bin\markitdown-mcp-enhanced.cmd
```

## 🔧 Claude Desktop 설정 (Windows)

### 1. 설정 파일 위치
Claude Desktop 설정 파일을 열어주세요:

```cmd
notepad %APPDATA%\Claude\claude_desktop_config.json
```

또는 PowerShell에서:
```powershell
notepad $env:APPDATA\Claude\claude_desktop_config.json
```

### 2. MCP 서버 설정 추가

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

### 3. 고급 설정 (API 키 사용)

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

## 🛠️ 문제 해결

### Python이 없다는 오류
```cmd
# Python 설치 확인
python --version
# 또는
py --version

# Python이 없으면 https://www.python.org/downloads/ 에서 설치
```

### Node.js가 없다는 오류
```cmd
# Node.js 설치 확인
node --version

# Node.js가 없으면 https://nodejs.org/ 에서 설치
```

### PowerShell 실행 정책 오류
```powershell
# 실행 정책 확인
Get-ExecutionPolicy

# 실행 정책 변경 (관리자 권한 필요)
Set-ExecutionPolicy RemoteSigned

# 현재 세션에만 적용
Set-ExecutionPolicy Bypass -Scope Process
```

### 의존성 설치 실패
```cmd
# 수동으로 의존성 설치
cd path\to\markitdown-mcp-enhanced
pip install -r requirements.txt
```

### 환경 변수 설정 (PowerShell)
```powershell
# 현재 세션에만 적용
$env:OPENAI_API_KEY = "your-api-key"
$env:KOREAN_SUPPORT = "true"

# 영구 설정 (사용자 수준)
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "your-api-key", "User")
```

### 환경 변수 설정 (명령 프롬프트)
```cmd
REM 현재 세션에만 적용
set OPENAI_API_KEY=your-api-key
set KOREAN_SUPPORT=true

REM 영구 설정
setx OPENAI_API_KEY "your-api-key"
setx KOREAN_SUPPORT "true"
```

## 📋 로그 확인

**Claude Desktop 로그 위치:**
```
%APPDATA%\Claude\logs\mcp.log
```

**PowerShell에서 로그 보기:**
```powershell
Get-Content $env:APPDATA\Claude\logs\mcp.log -Tail 50
```

## 🔍 테스트

**로컬 테스트:**
```cmd
# 버전 확인
node bin\markitdown-mcp-enhanced.js --version

# 도움말 보기
node bin\markitdown-mcp-enhanced.js --help
```

**PowerShell 테스트:**
```powershell
# 버전 확인
.\bin\markitdown-mcp-enhanced.ps1 -Version

# 도움말 보기
.\bin\markitdown-mcp-enhanced.ps1 -Help
```

## 🎯 사용 예시

Claude Desktop에서 다음과 같이 사용하세요:

```
C:\Users\사용자명\Documents\문서.pdf 파일을 마크다운으로 변환해주세요.
```

```
https://example.com/페이지.html 을 마크다운으로 변환해주세요.
```

```
C:\Users\사용자명\Pictures\이미지.jpg 파일의 텍스트를 추출해주세요.
```

## 📞 지원

문제가 발생하면 GitHub Issues에 문의해주세요:
https://github.com/VoidLight00/voidlight-markdown-mcp-server/issues

---

**참고**: Windows Defender나 백신 소프트웨어가 Node.js/Python 스크립트 실행을 차단할 수 있습니다. 필요시 예외 처리를 추가해주세요.