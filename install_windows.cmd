@echo off
REM Voidlight 마크다운 MCP 서버 Windows 간단 설치 스크립트
REM 2025-07-18

echo.
echo ========================================
echo  Voidlight 마크다운 MCP 서버 설치
echo ========================================
echo.

REM 관리자 권한 확인
net session >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] 관리자 권한으로 실행 중
) else (
    echo [경고] 일부 기능을 위해 관리자 권한이 필요할 수 있습니다.
)

echo.
echo 1단계: Node.js 확인 중...
where node >nul 2>&1
if %errorlevel% == 0 (
    for /f "tokens=*" %%i in ('node --version 2^>nul') do set NODE_VERSION=%%i
    echo [OK] Node.js 발견: !NODE_VERSION!
) else (
    echo [오류] Node.js가 설치되지 않았습니다.
    echo https://nodejs.org/ 에서 LTS 버전을 다운로드하여 설치해주세요.
    echo 설치 시 "Add to PATH" 옵션을 체크해주세요.
    pause
    exit /b 1
)

echo.
echo 2단계: Python 확인 중...
set PYTHON_FOUND=0
python --version >nul 2>&1
if %errorlevel% == 0 (
    for /f "tokens=*" %%i in ('python --version 2^>nul') do set PYTHON_VERSION=%%i
    echo [OK] Python 발견: !PYTHON_VERSION!
    set PYTHON_FOUND=1
) else (
    py --version >nul 2>&1
    if %errorlevel% == 0 (
        for /f "tokens=*" %%i in ('py --version 2^>nul') do set PYTHON_VERSION=%%i
        echo [OK] Python 발견: !PYTHON_VERSION!
        set PYTHON_FOUND=1
    )
)

if %PYTHON_FOUND% == 0 (
    echo [오류] Python 3.8+가 설치되지 않았습니다.
    echo https://www.python.org/downloads/ 에서 Python 3.8 이상을 다운로드하여 설치해주세요.
    echo 설치 시 "Add Python to PATH" 옵션을 체크해주세요.
    pause
    exit /b 1
)

echo.
echo 3단계: MCP 서버 설치 중...
echo npx markitdown-mcp-enhanced를 실행합니다...
npx markitdown-mcp-enhanced --version
if %errorlevel% == 0 (
    echo [OK] MCP 서버 설치 및 테스트 완료
) else (
    echo [오류] MCP 서버 설치에 실패했습니다.
    echo 인터넷 연결을 확인하고 다시 시도해주세요.
    pause
    exit /b 1
)

echo.
echo 4단계: Claude Desktop 설정 확인...
if exist "%APPDATA%\Claude" (
    echo [OK] Claude Desktop 설치 폴더 발견
    
    REM 설정 파일 생성
    set CONFIG_FILE=%APPDATA%\Claude\claude_desktop_config.json
    
    if exist "!CONFIG_FILE!" (
        echo [정보] 기존 설정 파일 발견. 백업을 생성합니다.
        copy "!CONFIG_FILE!" "!CONFIG_FILE!.backup.%date:~0,4%%date:~5,2%%date:~8,2%-%time:~0,2%%time:~3,2%%time:~6,2%" >nul
    )
    
    echo [정보] Claude Desktop 설정 파일을 생성합니다...
    (
        echo {
        echo   "mcpServers": {
        echo     "markitdown-mcp-enhanced": {
        echo       "command": "npx",
        echo       "args": ["markitdown-mcp-enhanced"],
        echo       "env": {
        echo         "KOREAN_SUPPORT": "true",
        echo         "LOG_LEVEL": "INFO"
        echo       }
        echo     }
        echo   }
        echo }
    ) > "!CONFIG_FILE!"
    
    echo [OK] Claude Desktop 설정 완료
    echo 설정 파일: !CONFIG_FILE!
) else (
    echo [경고] Claude Desktop이 설치되지 않았습니다.
    echo https://claude.ai/download 에서 Claude Desktop을 다운로드하여 설치해주세요.
)

echo.
echo ========================================
echo  설치 완료!
echo ========================================
echo.
echo [성공] Voidlight 마크다운 MCP 서버가 설치되었습니다.
echo.
echo 다음 단계:
echo 1. Claude Desktop을 재시작하세요
echo 2. Claude Desktop에서 테스트해보세요:
echo    "지원되는 파일 형식을 알려주세요"
echo.
echo 수동 테스트:
echo    npx markitdown-mcp-enhanced --version
echo.
echo 문제 발생 시:
echo - WINDOWS_SERVER_GUIDE.md 파일 참조
echo - GitHub Issues: https://github.com/VoidLight00/voidlight-markdown-mcp-server/issues
echo.
pause