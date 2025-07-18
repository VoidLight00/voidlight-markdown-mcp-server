# 🔧 종합 문제 해결 가이드

## 📋 목차
1. [설치 단계 오류](#설치-단계-오류)
2. [환경 설정 오류](#환경-설정-오류)
3. [Claude Desktop 연동 오류](#claude-desktop-연동-오류)
4. [런타임 오류](#런타임-오류)
5. [성능 및 메모리 문제](#성능-및-메모리-문제)
6. [보안 및 권한 문제](#보안-및-권한-문제)
7. [고급 문제 해결](#고급-문제-해결)

---

## 🚨 설치 단계 오류

### 1. npm install 실패

#### 오류 1: python3 패키지 없음
```bash
npm ERR! peer python3@">=3.8.0" could not be resolved
```

**해결책:**
```bash
# package.json에서 잘못된 의존성 제거 (이미 수정됨)
npm cache clean --force
npm install
```

#### 오류 2: Node.js 버전 호환성
```bash
npm ERR! engine Unsupported engine
```

**해결책:**
```bash
# Node.js 버전 확인
node --version

# 14.0.0 이상 필요
# 업데이트: https://nodejs.org/
```

#### 오류 3: 권한 문제 (Windows)
```bash
npm ERR! Error: EACCES: permission denied
```

**해결책:**
```cmd
# 관리자 권한으로 실행
# 또는 npm 글로벌 디렉토리 변경
npm config set prefix "C:\Users\%USERNAME%\AppData\Roaming\npm"
```

### 2. Python 의존성 설치 실패

#### 오류 1: pip 없음
```bash
'pip' is not recognized as an internal or external command
```

**해결책:**
```bash
# Python 재설치 (Add to PATH 체크)
# 또는 직접 실행
python -m pip install -r requirements.txt
python3 -m pip install -r requirements.txt
py -m pip install -r requirements.txt
```

#### 오류 2: 가상환경 문제
```bash
WARNING: pip is being invoked by an old script wrapper
```

**해결책:**
```bash
# 가상환경 생성
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

#### 오류 3: 컴파일 오류 (네이티브 모듈)
```bash
error: Microsoft Visual C++ 14.0 is required
```

**해결책:**
```bash
# Visual Studio Build Tools 설치
# https://visualstudio.microsoft.com/visual-cpp-build-tools/

# 또는 미리 컴파일된 바이너리 사용
pip install --only-binary=all -r requirements.txt
```

---

## ⚙️ 환경 설정 오류

### 1. 환경 변수 문제

#### 오류 1: PATH 설정 안됨
```bash
'python' is not recognized as an internal or external command
```

**해결책:**
```cmd
# 시스템 PATH 확인
echo %PATH%

# Python 경로 추가
set PATH=%PATH%;C:\Python39;C:\Python39\Scripts

# 영구 설정
setx PATH "%PATH%;C:\Python39;C:\Python39\Scripts"
```

#### 오류 2: API 키 설정 안됨
```bash
Error: OpenAI API key not found
```

**해결책:**
```cmd
# 환경 변수 설정
set OPENAI_API_KEY=your-api-key-here
setx OPENAI_API_KEY "your-api-key-here"

# PowerShell
$env:OPENAI_API_KEY = "your-api-key-here"
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "your-api-key-here", "User")
```

### 2. 파일 경로 문제

#### 오류 1: 공백 포함 경로
```bash
Error: cannot find path 'C:\Program Files\...'
```

**해결책:**
```json
// Claude Desktop 설정
"cwd": "C:\\Program Files\\project"
// 또는 공백 없는 경로 사용
"cwd": "C:\\Projects\\markitdown-mcp"
```

#### 오류 2: 한국어 경로
```bash
UnicodeDecodeError: 'ascii' codec can't decode byte
```

**해결책:**
```cmd
# 영어 경로 사용 권장
mkdir C:\Projects\markitdown-mcp
cd C:\Projects\markitdown-mcp

# 또는 환경 변수 설정
set PYTHONIOENCODING=utf-8
```

---

## 🔗 Claude Desktop 연동 오류

### 1. 설정 파일 오류

#### 오류 1: JSON 문법 오류
```json
Error: Unexpected token in JSON at position 123
```

**해결책:**
```bash
# JSON 유효성 검사
python -m json.tool claude_desktop_config.json

# 온라인 JSON 검사기 사용
# https://jsonlint.com/
```

#### 오류 2: 설정 파일 위치 틀림
```bash
Config file not found
```

**해결책:**
```cmd
# Windows 올바른 위치
notepad %APPDATA%\Claude\claude_desktop_config.json

# macOS 올바른 위치
open ~/Library/Application Support/Claude/claude_desktop_config.json
```

### 2. MCP 서버 연결 실패

#### 오류 1: 서버 시작 실패
```bash
MCP server failed to start
```

**해결책:**
```cmd
# 수동 테스트
python -m markitdown_mcp_enhanced.server

# 로그 확인
type %APPDATA%\Claude\logs\mcp.log
```

#### 오류 2: 포트 충돌
```bash
Error: Port 8000 is already in use
```

**해결책:**
```json
// 다른 포트 사용
"env": {
  "PORT": "8001"
}
```

---

## 🏃 런타임 오류

### 1. 메모리 부족

#### 오류 1: 큰 파일 처리 실패
```bash
MemoryError: Unable to allocate memory
```

**해결책:**
```python
# 환경 변수 설정
export MAX_FILE_SIZE=50MB
export CHUNK_SIZE=1024

# 또는 스트림 처리 사용
```

#### 오류 2: 메모리 누수
```bash
Process memory usage exceeding 2GB
```

**해결책:**
```python
# 가비지 컬렉션 강제 실행
import gc
gc.collect()

# 캐시 정리
import tempfile
tempfile.cleanup()
```

### 2. 파일 형식 오류

#### 오류 1: 지원하지 않는 파일
```bash
Error: Unsupported file format
```

**해결책:**
```bash
# 지원 형식 확인
python -c "from markitdown_mcp_enhanced import list_supported_formats; print(list_supported_formats())"
```

#### 오류 2: 손상된 파일
```bash
Error: File appears to be corrupted
```

**해결책:**
```bash
# 파일 복구 시도
# PDF: Adobe Acrobat 수리 기능
# DOCX: Microsoft Word 자동 복구
```

---

## ⚡ 성능 및 메모리 문제

### 1. 느린 처리 속도

#### 문제: 큰 파일 처리 시간 초과
**해결책:**
```python
# 병렬 처리 활성화
export PARALLEL_PROCESSING=true
export MAX_WORKERS=4

# 타임아웃 설정
export PROCESSING_TIMEOUT=300
```

#### 문제: OCR 처리 느림
**해결책:**
```python
# GPU 가속 활성화
export USE_GPU=true
# 또는 빠른 OCR 엔진 사용
export OCR_ENGINE=easyocr
```

### 2. 리소스 모니터링

#### 시스템 리소스 확인
```bash
# Windows
tasklist /FI "IMAGENAME eq python.exe"
wmic process where name="python.exe" get processid,workingsetsize

# PowerShell
Get-Process python | Select-Object ProcessName,WorkingSet,CPU
```

---

## 🔒 보안 및 권한 문제

### 1. 방화벽 문제

#### 오류: 네트워크 연결 차단
```bash
Error: Connection refused
```

**해결책:**
```cmd
# Windows 방화벽 예외 추가
netsh advfirewall firewall add rule name="Python MCP Server" dir=in action=allow program="C:\Python39\python.exe"
```

### 2. 바이러스 백신 문제

#### 오류: 실행 파일 차단
```bash
Error: Access denied
```

**해결책:**
```cmd
# Windows Defender 예외 추가
# 설정 > 업데이트 및 보안 > Windows 보안 > 바이러스 및 위협 방지
# 바이러스 및 위협 방지 설정 > 예외 추가
```

---

## 🛠️ 고급 문제 해결

### 1. 디버깅 모드 활성화

```json
{
  "mcpServers": {
    "markitdown-mcp-enhanced": {
      "command": "python",
      "args": ["-m", "markitdown_mcp_enhanced.server"],
      "env": {
        "DEBUG": "true",
        "LOG_LEVEL": "DEBUG",
        "VERBOSE": "true"
      }
    }
  }
}
```

### 2. 상세 로그 분석

```cmd
# 로그 파일 실시간 모니터링
# Windows
Get-Content %APPDATA%\Claude\logs\mcp.log -Wait -Tail 50

# 특정 오류 검색
findstr /i "error" %APPDATA%\Claude\logs\mcp.log
```

### 3. 네트워크 문제 진단

```cmd
# 포트 사용 확인
netstat -an | findstr :8000

# DNS 해결 확인
nslookup api.openai.com
```

### 4. 의존성 버전 충돌

```bash
# 의존성 트리 확인
pip list
pip show [package-name]

# 가상환경 재생성
rmdir /s venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## 📞 추가 지원

### 1. 로그 수집 스크립트

```cmd
@echo off
echo Collecting diagnostic information...
echo.

echo === System Information ===
systeminfo | findstr /B /C:"OS Name" /C:"OS Version" /C:"System Type"
echo.

echo === Python Information ===
python --version
pip --version
echo.

echo === Node.js Information ===
node --version
npm --version
echo.

echo === Claude Desktop Config ===
type %APPDATA%\Claude\claude_desktop_config.json
echo.

echo === Recent MCP Logs ===
powershell "Get-Content '%APPDATA%\Claude\logs\mcp.log' -Tail 50"
echo.

echo === Environment Variables ===
set | findstr /i "python\|node\|openai"
echo.

echo Diagnostic information collected.
echo Please share this output when reporting issues.
pause
```

### 2. 문제 보고 템플릿

```markdown
## 문제 상황
- OS: Windows 10/11
- Python 버전: 
- Node.js 버전:
- 오류 메시지:

## 재현 단계
1. 
2. 
3. 

## 예상 결과
<!-- 기대했던 동작 -->

## 실제 결과
<!-- 실제로 발생한 동작 -->

## 추가 정보
<!-- 로그, 스크린샷 등 -->
```

---

## 🎯 예방 조치

### 1. 정기 점검 스크립트

```python
#!/usr/bin/env python3
"""
MCP Server Health Check Script
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_python():
    """Python 설치 및 버전 확인"""
    try:
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            print("✅ Python version OK:", sys.version)
            return True
        else:
            print("❌ Python version too old:", sys.version)
            return False
    except Exception as e:
        print("❌ Python check failed:", e)
        return False

def check_nodejs():
    """Node.js 설치 및 버전 확인"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Node.js version OK:", result.stdout.strip())
            return True
        else:
            print("❌ Node.js not found")
            return False
    except Exception as e:
        print("❌ Node.js check failed:", e)
        return False

def check_dependencies():
    """Python 의존성 확인"""
    try:
        import markitdown_mcp_enhanced
        print("✅ MCP server module found")
        return True
    except ImportError:
        print("❌ MCP server module not found")
        return False

def check_config():
    """Claude Desktop 설정 확인"""
    config_path = Path.home() / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json"
    if not config_path.exists():
        print("❌ Claude Desktop config not found")
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        if 'mcpServers' in config and 'markitdown-mcp-enhanced' in config['mcpServers']:
            print("✅ MCP server configured in Claude Desktop")
            return True
        else:
            print("❌ MCP server not configured in Claude Desktop")
            return False
    except Exception as e:
        print("❌ Config check failed:", e)
        return False

def main():
    """메인 헬스 체크"""
    print("🔍 MCP Server Health Check")
    print("=" * 50)
    
    checks = [
        check_python,
        check_nodejs,
        check_dependencies,
        check_config
    ]
    
    results = [check() for check in checks]
    
    print("\n" + "=" * 50)
    if all(results):
        print("🎉 All checks passed! MCP server is ready.")
    else:
        print("⚠️  Some checks failed. Please review the issues above.")
    
    return all(results)

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
```

### 2. 자동 복구 스크립트

```cmd
@echo off
echo Starting automatic recovery...

echo Clearing npm cache...
npm cache clean --force

echo Reinstalling Python dependencies...
pip install --force-reinstall -r requirements.txt

echo Reinstalling MCP server...
python -m pip install -e . --force-reinstall

echo Restarting Claude Desktop...
taskkill /F /IM "Claude Desktop.exe" 2>nul
timeout /t 3 /nobreak >nul
start "" "C:\Program Files\Claude\Claude Desktop.exe"

echo Recovery completed.
pause
```

---

이 종합 가이드로 대부분의 설치 및 운영 문제를 해결할 수 있습니다! 🚀