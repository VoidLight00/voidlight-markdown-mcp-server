# Windows npm install 오류 해결 가이드

## 🚨 문제 상황
Windows에서 `npm install` 실행 시 다음과 같은 오류가 발생:

```
npm ERR! Could not resolve dependency:
npm ERR! peer python3@">=3.8.0" from markitdown-mcp-enhanced@1.0.0
npm ERR! peerDependencies python3@">=3.8.0" could not be resolved
```

## 🔍 원인 분석
`package.json` 파일에서 **존재하지 않는 npm 패키지**를 의존성으로 설정했기 때문:

```json
"peerDependencies": {
  "python3": ">=3.8.0"  // ❌ 'python3'는 npm 패키지가 아님
}
```

## ✅ 해결 방법

### 1. package.json 수정
**수정 전:**
```json
"engines": {
  "node": ">=14.0.0",
  "python": ">=3.8.0"
},
"peerDependencies": {
  "python3": ">=3.8.0"
}
```

**수정 후:**
```json
"engines": {
  "node": ">=14.0.0"
}
```

### 2. Python 요구사항 확인 방법
**npm 스크립트 수정:**
```json
"scripts": {
  "preinstall": "python --version || python3 --version",
  "install": "python -m pip install -e . || python3 -m pip install -e .",
  "postinstall": "echo 'MCP Server installation complete'"
}
```

### 3. Windows 사용자를 위한 설치 가이드

#### 전제 조건 확인
```cmd
:: Node.js 확인
node --version

:: Python 확인 (둘 중 하나가 작동하면 됨)
python --version
python3 --version
py --version
```

#### 수동 설치 단계
1. **Node.js 의존성 설치**
   ```cmd
   npm install
   ```

2. **Python 의존성 설치**
   ```cmd
   pip install -r requirements.txt
   ```
   또는
   ```cmd
   python -m pip install -r requirements.txt
   ```

3. **MCP 서버 설치**
   ```cmd
   python -m pip install -e .
   ```

### 4. 개선된 설치 스크립트 (install.bat)
```batch
@echo off
echo Installing Markitdown MCP Enhanced...

:: Check Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    python3 --version >nul 2>&1
    if %errorlevel% neq 0 (
        py --version >nul 2>&1
        if %errorlevel% neq 0 (
            echo ERROR: Python is not installed or not in PATH
            echo Please install Python from https://www.python.org/downloads/
            pause
            exit /b 1
        )
        set PYTHON_CMD=py
    ) else (
        set PYTHON_CMD=python3
    )
) else (
    set PYTHON_CMD=python
)

:: Install npm dependencies
echo Installing npm dependencies...
npm install

:: Install Python dependencies
echo Installing Python dependencies...
%PYTHON_CMD% -m pip install -r requirements.txt

:: Install MCP server
echo Installing MCP server...
%PYTHON_CMD% -m pip install -e .

echo Installation complete!
echo.
echo To configure Claude Desktop, run:
echo   notepad %APPDATA%\Claude\claude_desktop_config.json
echo.
pause
```

### 5. 개선된 Claude Desktop 설정
```json
{
  "mcpServers": {
    "markitdown-mcp-enhanced": {
      "command": "python",
      "args": ["-m", "markitdown_mcp_enhanced.server"],
      "cwd": "C:\\path\\to\\your\\project",
      "env": {
        "KOREAN_SUPPORT": "true",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

## 🎯 테스트 방법

### 1. 로컬 테스트
```cmd
:: MCP 서버 직접 실행
python -m markitdown_mcp_enhanced.server

:: 또는 npx 사용
npx markitdown-mcp-enhanced
```

### 2. Claude Desktop에서 테스트
1. Claude Desktop 재시작
2. 다음 명령어 테스트:
   ```
   C:\Users\사용자명\Documents\test.pdf 파일을 마크다운으로 변환해주세요.
   ```

## 📋 문제 해결 체크리스트

- [ ] Node.js 14+ 설치 확인
- [ ] Python 3.8+ 설치 확인
- [ ] package.json에서 잘못된 의존성 제거
- [ ] requirements.txt 파일 존재 확인
- [ ] Python 패키지 수동 설치
- [ ] Claude Desktop 설정 확인
- [ ] 로그 파일 확인 (`%APPDATA%\Claude\logs\mcp.log`)

## 🔧 추가 문제 해결

### PowerShell 실행 정책 오류
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 경로 공백 문제
```json
"cwd": "C:\\Users\\사용자명\\프로젝트 폴더"
```
위와 같은 경로에 공백이 있으면 문제가 될 수 있습니다. 다음과 같이 수정:
```json
"cwd": "C:\\Users\\사용자명\\프로젝트폴더"
```

### 한국어 경로 문제
가능하면 영어 경로를 사용하세요:
```json
"cwd": "C:\\Projects\\markitdown-mcp-enhanced"
```

---

이 가이드로 Windows에서 npm install 오류를 해결하고 MCP 서버를 성공적으로 설치할 수 있습니다! 🚀