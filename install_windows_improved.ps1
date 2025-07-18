# ===========================================
# Voidlight Markitdown MCP Server Installer
# PowerShell Installation Script (개선된 버전)
# ===========================================

param(
    [switch]$Help,
    [switch]$Version,
    [switch]$Debug,
    [switch]$Force,
    [string]$PythonCommand = "",
    [string]$InstallPath = ""
)

# 도움말 표시
if ($Help) {
    Write-Host @"
Voidlight Markitdown MCP Server Installer

사용법:
    .\install_windows_improved.ps1 [옵션]

옵션:
    -Help               이 도움말 표시
    -Version            버전 정보 표시
    -Debug              디버그 모드 활성화
    -Force              강제 재설치
    -PythonCommand      Python 명령어 지정 (python, python3, py)
    -InstallPath        설치 경로 지정

예시:
    .\install_windows_improved.ps1
    .\install_windows_improved.ps1 -Debug
    .\install_windows_improved.ps1 -PythonCommand python3
    .\install_windows_improved.ps1 -Force -InstallPath "C:\MCP"
"@
    exit 0
}

# 버전 정보 표시
if ($Version) {
    Write-Host "Voidlight Markitdown MCP Server Installer v1.0.0"
    exit 0
}

# 스크립트 시작
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Voidlight Markitdown MCP Installer" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# 실행 정책 확인
$executionPolicy = Get-ExecutionPolicy
if ($executionPolicy -eq "Restricted") {
    Write-Host "[WARNING] PowerShell 실행 정책이 제한되어 있습니다." -ForegroundColor Yellow
    Write-Host "실행 정책을 변경하시겠습니까? (현재 세션에만 적용)" -ForegroundColor Yellow
    $response = Read-Host "(y/n)"
    if ($response -eq "y" -or $response -eq "Y") {
        Set-ExecutionPolicy Bypass -Scope Process -Force
        Write-Host "✅ 실행 정책이 변경되었습니다." -ForegroundColor Green
    } else {
        Write-Host "❌ 실행 정책 변경이 취소되었습니다." -ForegroundColor Red
        exit 1
    }
}

# 관리자 권한 확인
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "[WARNING] 관리자 권한이 없습니다. 일부 기능이 제한될 수 있습니다." -ForegroundColor Yellow
    Start-Sleep -Seconds 2
}

# 디버그 모드 설정
if ($Debug) {
    $DebugPreference = "Continue"
    Write-Host "[DEBUG] 디버그 모드 활성화" -ForegroundColor Magenta
}

# 설치 경로 설정
if ($InstallPath) {
    if (-not (Test-Path $InstallPath)) {
        New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
    }
    Set-Location $InstallPath
    Write-Host "설치 경로: $InstallPath" -ForegroundColor Blue
}

# 오류 처리 함수
function Handle-Error {
    param($ErrorMessage, $ExitCode = 1)
    Write-Host "[ERROR] $ErrorMessage" -ForegroundColor Red
    if ($Debug) {
        Write-Host "Stack Trace:" -ForegroundColor Magenta
        Write-Host $_.ScriptStackTrace -ForegroundColor Magenta
    }
    Read-Host "Press Enter to exit"
    exit $ExitCode
}

# 1. 시스템 요구사항 확인
Write-Host "[1/8] 시스템 요구사항 확인 중..." -ForegroundColor Yellow
Write-Host ""

# Node.js 확인
Write-Host "Checking Node.js..." -ForegroundColor Gray
try {
    $nodeVersion = node --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Node.js $nodeVersion 발견" -ForegroundColor Green
    } else {
        throw "Node.js not found"
    }
} catch {
    Write-Host "❌ Node.js가 설치되지 않았습니다." -ForegroundColor Red
    Write-Host "다운로드: https://nodejs.org/" -ForegroundColor Yellow
    $response = Read-Host "Node.js 다운로드 페이지를 여시겠습니까? (y/n)"
    if ($response -eq "y" -or $response -eq "Y") {
        Start-Process "https://nodejs.org/"
    }
    Handle-Error "Node.js가 필요합니다."
}

# Python 확인
Write-Host "Checking Python..." -ForegroundColor Gray
$pythonCommands = @("python", "python3", "py")
$pythonCmd = $null
$pythonVersion = $null

if ($PythonCommand) {
    $pythonCommands = @($PythonCommand)
}

foreach ($cmd in $pythonCommands) {
    try {
        $version = & $cmd --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            $pythonCmd = $cmd
            $pythonVersion = $version
            break
        }
    } catch {
        continue
    }
}

if ($pythonCmd) {
    Write-Host "✅ $pythonVersion 발견 (명령어: $pythonCmd)" -ForegroundColor Green
} else {
    Write-Host "❌ Python이 설치되지 않았습니다." -ForegroundColor Red
    Write-Host "다운로드: https://www.python.org/downloads/" -ForegroundColor Yellow
    $response = Read-Host "Python 다운로드 페이지를 여시겠습니까? (y/n)"
    if ($response -eq "y" -or $response -eq "Y") {
        Start-Process "https://www.python.org/downloads/"
    }
    Handle-Error "Python이 필요합니다."
}

Write-Host ""

# 2. 기존 설치 확인
Write-Host "[2/8] 기존 설치 확인 중..." -ForegroundColor Yellow
if (Test-Path "node_modules") {
    Write-Host "[WARNING] 기존 node_modules 폴더가 발견되었습니다." -ForegroundColor Yellow
    if ($Force) {
        Write-Host "강제 모드: 기존 설치를 제거합니다." -ForegroundColor Yellow
        Remove-Item -Recurse -Force "node_modules" -ErrorAction SilentlyContinue
        Write-Host "✅ 기존 설치 제거 완료" -ForegroundColor Green
    } else {
        $response = Read-Host "기존 설치를 제거하시겠습니까? (y/n)"
        if ($response -eq "y" -or $response -eq "Y") {
            Remove-Item -Recurse -Force "node_modules" -ErrorAction SilentlyContinue
            Write-Host "✅ 기존 설치 제거 완료" -ForegroundColor Green
        }
    }
}
Write-Host ""

# 3. NPM 캐시 정리
Write-Host "[3/8] NPM 캐시 정리 중..." -ForegroundColor Yellow
try {
    npm cache clean --force 2>$null | Out-Null
    Write-Host "✅ NPM 캐시 정리 완료" -ForegroundColor Green
} catch {
    Write-Host "[WARNING] NPM 캐시 정리 실패" -ForegroundColor Yellow
}
Write-Host ""

# 4. NPM 의존성 설치
Write-Host "[4/8] NPM 의존성 설치 중..." -ForegroundColor Yellow
try {
    npm install
    if ($LASTEXITCODE -ne 0) {
        throw "NPM install failed"
    }
    Write-Host "✅ NPM 의존성 설치 완료" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] NPM 설치 실패" -ForegroundColor Red
    $response = Read-Host "대안 설치 방법을 시도하시겠습니까? (y/n)"
    if ($response -eq "y" -or $response -eq "Y") {
        Write-Host "NPM 글로벌 prefix 설정 중..." -ForegroundColor Yellow
        npm config set prefix "$env:USERPROFILE\AppData\Roaming\npm"
        Write-Host "재시도 중..." -ForegroundColor Yellow
        npm install
        if ($LASTEXITCODE -ne 0) {
            Handle-Error "대안 설치도 실패했습니다."
        }
        Write-Host "✅ 대안 설치 완료" -ForegroundColor Green
    } else {
        Handle-Error "NPM 설치가 필요합니다."
    }
}
Write-Host ""

# 5. Python 의존성 설치
Write-Host "[5/8] Python 의존성 설치 중..." -ForegroundColor Yellow
try {
    if (Test-Path "requirements.txt") {
        & $pythonCmd -m pip install -r requirements.txt
    } else {
        Write-Host "[WARNING] requirements.txt 파일이 없습니다." -ForegroundColor Yellow
        Write-Host "기본 의존성을 설치합니다..." -ForegroundColor Yellow
        & $pythonCmd -m pip install markitdown pdfminer.six python-docx openpyxl beautifulsoup4 requests
    }
    
    if ($LASTEXITCODE -ne 0) {
        throw "Python dependencies installation failed"
    }
    Write-Host "✅ Python 의존성 설치 완료" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python 의존성 설치 실패" -ForegroundColor Red
    $response = Read-Host "가상환경을 사용하여 재시도하시겠습니까? (y/n)"
    if ($response -eq "y" -or $response -eq "Y") {
        Write-Host "가상환경 생성 중..." -ForegroundColor Yellow
        & $pythonCmd -m venv venv
        
        # 가상환경 활성화
        if (Test-Path "venv\Scripts\Activate.ps1") {
            & "venv\Scripts\Activate.ps1"
        } else {
            Handle-Error "가상환경 활성화 실패"
        }
        
        Write-Host "가상환경에서 의존성 설치 중..." -ForegroundColor Yellow
        python -m pip install --upgrade pip
        
        if (Test-Path "requirements.txt") {
            python -m pip install -r requirements.txt
        } else {
            python -m pip install markitdown pdfminer.six python-docx openpyxl beautifulsoup4 requests
        }
        
        if ($LASTEXITCODE -ne 0) {
            Handle-Error "가상환경에서도 설치 실패"
        }
        Write-Host "✅ 가상환경에서 Python 의존성 설치 완료" -ForegroundColor Green
    } else {
        Handle-Error "Python 의존성 설치가 필요합니다."
    }
}
Write-Host ""

# 6. MCP 서버 설치
Write-Host "[6/8] MCP 서버 설치 중..." -ForegroundColor Yellow
if (Test-Path "setup.py") {
    try {
        & $pythonCmd -m pip install -e .
        if ($LASTEXITCODE -ne 0) {
            throw "MCP server installation failed"
        }
        Write-Host "✅ MCP 서버 설치 완료" -ForegroundColor Green
    } catch {
        Write-Host "[WARNING] MCP 서버 설치 실패, 직접 실행으로 대체합니다." -ForegroundColor Yellow
    }
} else {
    Write-Host "[WARNING] setup.py 파일이 없습니다. 직접 실행 모드로 설정합니다." -ForegroundColor Yellow
}
Write-Host ""

# 7. 설치 테스트
Write-Host "[7/8] 설치 테스트 중..." -ForegroundColor Yellow
Write-Host "Testing basic functionality..." -ForegroundColor Gray

# Python 모듈 테스트
if (Test-Path "src\markitdown_mcp_enhanced\server.py") {
    Write-Host "Testing Python module..." -ForegroundColor Gray
    try {
        $testResult = & $pythonCmd -c "import sys; sys.path.insert(0, 'src'); from markitdown_mcp_enhanced import server; print('✅ Python module test passed')"
        Write-Host $testResult -ForegroundColor Green
    } catch {
        Write-Host "[WARNING] Python 모듈 테스트 실패" -ForegroundColor Yellow
    }
} else {
    Write-Host "[WARNING] MCP 서버 소스 파일이 없습니다." -ForegroundColor Yellow
}

# NPX 테스트
if (Test-Path "bin\markitdown-mcp-enhanced.js") {
    Write-Host "Testing NPX execution..." -ForegroundColor Gray
    try {
        node bin\markitdown-mcp-enhanced.js --help 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ NPX 실행 테스트 통과" -ForegroundColor Green
        } else {
            Write-Host "[WARNING] NPX 실행 테스트 실패" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "[WARNING] NPX 실행 테스트 실패" -ForegroundColor Yellow
    }
}
Write-Host ""

# 8. Claude Desktop 설정
Write-Host "[8/8] Claude Desktop 설정 안내..." -ForegroundColor Yellow
Write-Host ""

$claudeConfigPath = "$env:APPDATA\Claude\claude_desktop_config.json"
$currentPath = Get-Location

if (Test-Path $claudeConfigPath) {
    Write-Host "Claude Desktop 설정 파일 발견: $claudeConfigPath" -ForegroundColor Green
    Write-Host ""
    Write-Host "설정 파일에 다음 내용을 추가하세요:" -ForegroundColor Yellow
    Write-Host ""
    
    $configContent = @"
{
  "mcpServers": {
    "markitdown-mcp-enhanced": {
      "command": "npx",
      "args": ["markitdown-mcp-enhanced"],
      "cwd": "$currentPath",
      "env": {
        "KOREAN_SUPPORT": "true",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
"@
    
    Write-Host $configContent -ForegroundColor Cyan
    Write-Host ""
    
    $response = Read-Host "설정 파일을 지금 여시겠습니까? (y/n)"
    if ($response -eq "y" -or $response -eq "Y") {
        notepad $claudeConfigPath
    }
    
    Write-Host ""
    $response = Read-Host "설정을 자동으로 추가하시겠습니까? (기존 설정을 백업합니다) (y/n)"
    if ($response -eq "y" -or $response -eq "Y") {
        try {
            # 기존 설정 백업
            Copy-Item $claudeConfigPath "$claudeConfigPath.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')"
            
            # 기존 설정 읽기
            $existingConfig = Get-Content $claudeConfigPath -Raw | ConvertFrom-Json
            
            # mcpServers 섹션이 없으면 생성
            if (-not $existingConfig.mcpServers) {
                $existingConfig | Add-Member -NotePropertyName "mcpServers" -NotePropertyValue @{}
            }
            
            # 새 MCP 서버 추가
            $newServer = @{
                command = "npx"
                args = @("markitdown-mcp-enhanced")
                cwd = $currentPath.Path
                env = @{
                    KOREAN_SUPPORT = "true"
                    LOG_LEVEL = "INFO"
                }
            }
            
            $existingConfig.mcpServers | Add-Member -NotePropertyName "markitdown-mcp-enhanced" -NotePropertyValue $newServer -Force
            
            # 설정 파일 저장
            $existingConfig | ConvertTo-Json -Depth 10 | Set-Content $claudeConfigPath
            
            Write-Host "✅ 설정이 자동으로 추가되었습니다." -ForegroundColor Green
            Write-Host "백업 파일: $claudeConfigPath.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')" -ForegroundColor Blue
        } catch {
            Write-Host "[ERROR] 자동 설정 추가 실패: $($_.Exception.Message)" -ForegroundColor Red
            Write-Host "수동으로 설정을 추가해주세요." -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "[WARNING] Claude Desktop 설정 파일이 없습니다." -ForegroundColor Yellow
    Write-Host "Claude Desktop이 설치되어 있고 한 번 실행되었는지 확인하세요." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "설정 파일 경로: $claudeConfigPath" -ForegroundColor Blue
}

# 9. 완료 및 정리
Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "     설치 완료!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "다음 단계:" -ForegroundColor Yellow
Write-Host "1. Claude Desktop 설정 파일 편집" -ForegroundColor White
Write-Host "2. Claude Desktop 재시작" -ForegroundColor White
Write-Host "3. '파일을 마크다운으로 변환해주세요' 테스트" -ForegroundColor White
Write-Host ""
Write-Host "문제가 발생하면 다음 파일을 참조하세요:" -ForegroundColor Yellow
Write-Host "- TROUBLESHOOTING.md" -ForegroundColor White
Write-Host "- WINDOWS_INSTALL_FIX.md" -ForegroundColor White
Write-Host "- WINDOWS_SETUP.md" -ForegroundColor White
Write-Host ""
Write-Host "로그 파일: $env:APPDATA\Claude\logs\mcp.log" -ForegroundColor Blue
Write-Host ""

# 진단 정보 생성
$response = Read-Host "진단 정보를 생성하시겠습니까? (문제 해결 시 유용) (y/n)"
if ($response -eq "y" -or $response -eq "Y") {
    Write-Host ""
    Write-Host "=== 진단 정보 ===" -ForegroundColor Cyan
    
    $diagnosticInfo = @{
        OS = "$env:OS $env:PROCESSOR_ARCHITECTURE"
        PowerShell = $PSVersionTable.PSVersion
        NodeJS = $nodeVersion
        Python = "$pythonVersion ($pythonCmd)"
        CurrentDirectory = $currentPath.Path
        ClaudeConfig = $claudeConfigPath
        InstallationDate = Get-Date
        ExecutionPolicy = Get-ExecutionPolicy
        IsAdmin = $isAdmin
    }
    
    $diagnosticInfo | Format-Table -AutoSize
    
    $response = Read-Host "이 정보를 diagnostic_info.json 파일로 저장하시겠습니까? (y/n)"
    if ($response -eq "y" -or $response -eq "Y") {
        $diagnosticInfo | ConvertTo-Json -Depth 10 | Set-Content "diagnostic_info.json"
        Write-Host "✅ 진단 정보가 diagnostic_info.json에 저장되었습니다." -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "설치 스크립트를 종료합니다." -ForegroundColor Yellow
Read-Host "Press Enter to exit"
exit 0