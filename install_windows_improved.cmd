@echo off
setlocal enabledelayedexpansion

:: ===========================================
:: Voidlight Markitdown MCP Server Installer
:: Windows Installation Script (개선된 버전)
:: ===========================================

echo.
echo =====================================
echo  Voidlight Markitdown MCP Installer
echo =====================================
echo.

:: 관리자 권한 확인
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [WARNING] 관리자 권한이 없습니다. 일부 기능이 제한될 수 있습니다.
    echo.
    timeout /t 3 /nobreak >nul
)

:: 1. 시스템 요구사항 확인
echo [1/8] 시스템 요구사항 확인 중...
echo.

:: Node.js 확인
echo Checking Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js가 설치되지 않았습니다.
    echo 다운로드: https://nodejs.org/
    echo.
    set /p choice="Node.js 다운로드 페이지를 여시겠습니까? (y/n): "
    if /i "!choice!"=="y" start https://nodejs.org/
    pause
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
    echo ✅ Node.js !NODE_VERSION! 발견
)

:: Python 확인 (여러 명령어 시도)
echo Checking Python...
set PYTHON_CMD=
set PYTHON_VERSION=

:: python 명령어 시도
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
    goto :python_found
)

:: python3 명령어 시도
python3 --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python3
    for /f "tokens=2" %%i in ('python3 --version') do set PYTHON_VERSION=%%i
    goto :python_found
)

:: py 명령어 시도
py --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py
    for /f "tokens=2" %%i in ('py --version') do set PYTHON_VERSION=%%i
    goto :python_found
)

:: Python 없음
echo [ERROR] Python이 설치되지 않았습니다.
echo 다운로드: https://www.python.org/downloads/
echo.
set /p choice="Python 다운로드 페이지를 여시겠습니까? (y/n): "
if /i "!choice!"=="y" start https://www.python.org/downloads/
pause
exit /b 1

:python_found
echo ✅ Python !PYTHON_VERSION! 발견 (명령어: !PYTHON_CMD!)
echo.

:: 2. 기존 설치 확인
echo [2/8] 기존 설치 확인 중...
if exist "node_modules" (
    echo [WARNING] 기존 node_modules 폴더가 발견되었습니다.
    set /p choice="기존 설치를 제거하시겠습니까? (y/n): "
    if /i "!choice!"=="y" (
        echo Removing existing node_modules...
        rmdir /s /q node_modules 2>nul
        echo ✅ 기존 설치 제거 완료
    )
)
echo.

:: 3. NPM 캐시 정리
echo [3/8] NPM 캐시 정리 중...
npm cache clean --force >nul 2>&1
echo ✅ NPM 캐시 정리 완료
echo.

:: 4. NPM 의존성 설치
echo [4/8] NPM 의존성 설치 중...
npm install
if %errorlevel% neq 0 (
    echo [ERROR] NPM 설치 실패
    echo.
    echo 대안 설치 방법을 시도하시겠습니까?
    set /p choice="(y/n): "
    if /i "!choice!"=="y" (
        echo NPM 글로벌 prefix 설정 중...
        npm config set prefix "%USERPROFILE%\AppData\Roaming\npm"
        echo 재시도 중...
        npm install
        if %errorlevel% neq 0 (
            echo [ERROR] 대안 설치도 실패했습니다.
            pause
            exit /b 1
        )
    ) else (
        pause
        exit /b 1
    )
)
echo ✅ NPM 의존성 설치 완료
echo.

:: 5. Python 의존성 설치
echo [5/8] Python 의존성 설치 중...
if not exist "requirements.txt" (
    echo [WARNING] requirements.txt 파일이 없습니다.
    echo 기본 의존성을 설치합니다...
    !PYTHON_CMD! -m pip install markitdown pdfminer.six python-docx openpyxl beautifulsoup4 requests
) else (
    !PYTHON_CMD! -m pip install -r requirements.txt
)

if %errorlevel% neq 0 (
    echo [ERROR] Python 의존성 설치 실패
    echo.
    echo 가상환경을 사용하여 재시도하시겠습니까?
    set /p choice="(y/n): "
    if /i "!choice!"=="y" (
        echo 가상환경 생성 중...
        !PYTHON_CMD! -m venv venv
        call venv\Scripts\activate.bat
        echo 가상환경에서 의존성 설치 중...
        python -m pip install --upgrade pip
        if exist "requirements.txt" (
            python -m pip install -r requirements.txt
        ) else (
            python -m pip install markitdown pdfminer.six python-docx openpyxl beautifulsoup4 requests
        )
        if %errorlevel% neq 0 (
            echo [ERROR] 가상환경에서도 설치 실패
            pause
            exit /b 1
        )
    ) else (
        pause
        exit /b 1
    )
) else (
    echo ✅ Python 의존성 설치 완료
)
echo.

:: 6. MCP 서버 설치
echo [6/8] MCP 서버 설치 중...
if exist "setup.py" (
    !PYTHON_CMD! -m pip install -e .
    if %errorlevel% neq 0 (
        echo [WARNING] MCP 서버 설치 실패, 직접 실행으로 대체합니다.
    ) else (
        echo ✅ MCP 서버 설치 완료
    )
) else (
    echo [WARNING] setup.py 파일이 없습니다. 직접 실행 모드로 설정합니다.
)
echo.

:: 7. 설치 테스트
echo [7/8] 설치 테스트 중...
echo Testing basic functionality...

:: 기본 테스트
if exist "src\markitdown_mcp_enhanced\server.py" (
    echo Testing Python module...
    !PYTHON_CMD! -c "import sys; sys.path.insert(0, 'src'); from markitdown_mcp_enhanced import server; print('✅ Python module test passed')"
    if %errorlevel% neq 0 (
        echo [WARNING] Python 모듈 테스트 실패
    )
) else (
    echo [WARNING] MCP 서버 소스 파일이 없습니다.
)

:: NPX 테스트
if exist "bin\markitdown-mcp-enhanced.js" (
    echo Testing NPX execution...
    node bin\markitdown-mcp-enhanced.js --help >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ NPX 실행 테스트 통과
    ) else (
        echo [WARNING] NPX 실행 테스트 실패
    )
)
echo.

:: 8. Claude Desktop 설정
echo [8/8] Claude Desktop 설정 안내...
echo.
set CLAUDE_CONFIG_PATH=%APPDATA%\Claude\claude_desktop_config.json

if exist "%CLAUDE_CONFIG_PATH%" (
    echo Claude Desktop 설정 파일 발견: %CLAUDE_CONFIG_PATH%
    echo.
    echo 설정 파일에 다음 내용을 추가하세요:
    echo.
    echo {
    echo   "mcpServers": {
    echo     "markitdown-mcp-enhanced": {
    echo       "command": "npx",
    echo       "args": ["markitdown-mcp-enhanced"],
    echo       "cwd": "%CD%",
    echo       "env": {
    echo         "KOREAN_SUPPORT": "true",
    echo         "LOG_LEVEL": "INFO"
    echo       }
    echo     }
    echo   }
    echo }
    echo.
    set /p choice="설정 파일을 지금 여시겠습니까? (y/n): "
    if /i "!choice!"=="y" (
        notepad "%CLAUDE_CONFIG_PATH%"
    )
) else (
    echo [WARNING] Claude Desktop 설정 파일이 없습니다.
    echo Claude Desktop이 설치되어 있고 한 번 실행되었는지 확인하세요.
    echo.
    echo 설정 파일 경로: %CLAUDE_CONFIG_PATH%
)

:: 9. 완료 및 정리
echo.
echo =====================================
echo     설치 완료!
echo =====================================
echo.
echo 다음 단계:
echo 1. Claude Desktop 설정 파일 편집
echo 2. Claude Desktop 재시작
echo 3. "파일을 마크다운으로 변환해주세요" 테스트
echo.
echo 문제가 발생하면 다음 파일을 참조하세요:
echo - TROUBLESHOOTING.md
echo - WINDOWS_INSTALL_FIX.md
echo - WINDOWS_SETUP.md
echo.
echo 로그 파일: %APPDATA%\Claude\logs\mcp.log
echo.

:: 진단 정보 생성
echo 진단 정보를 생성하시겠습니까? (문제 해결 시 유용)
set /p choice="(y/n): "
if /i "!choice!"=="y" (
    echo.
    echo === 진단 정보 ===
    echo OS: %OS%
    echo Node.js: !NODE_VERSION!
    echo Python: !PYTHON_VERSION! ^(!PYTHON_CMD!^)
    echo Current Directory: %CD%
    echo Claude Config: %CLAUDE_CONFIG_PATH%
    echo.
    echo 이 정보를 diagnostic_info.txt 파일로 저장하시겠습니까?
    set /p choice="(y/n): "
    if /i "!choice!"=="y" (
        echo === 진단 정보 === > diagnostic_info.txt
        echo OS: %OS% >> diagnostic_info.txt
        echo Node.js: !NODE_VERSION! >> diagnostic_info.txt
        echo Python: !PYTHON_VERSION! ^(!PYTHON_CMD!^) >> diagnostic_info.txt
        echo Current Directory: %CD% >> diagnostic_info.txt
        echo Claude Config: %CLAUDE_CONFIG_PATH% >> diagnostic_info.txt
        echo Installation Date: %DATE% %TIME% >> diagnostic_info.txt
        echo ✅ 진단 정보가 diagnostic_info.txt에 저장되었습니다.
    )
)

echo.
echo 설치 스크립트를 종료합니다.
pause
exit /b 0