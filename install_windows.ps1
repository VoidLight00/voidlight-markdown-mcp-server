#!/usr/bin/env powershell

<#
.SYNOPSIS
    Windows용 Voidlight 마크다운 MCP 서버 자동 설치 스크립트

.DESCRIPTION
    이 스크립트는 Windows에서 필요한 모든 의존성을 확인하고 
    Voidlight 마크다운 MCP 서버를 자동으로 설치합니다.

.EXAMPLE
    .\install_windows.ps1
    기본 설치 실행

.EXAMPLE
    .\install_windows.ps1 -SkipDependencies
    의존성 검사 없이 MCP 서버만 설치
#>

param(
    [switch]$SkipDependencies,
    [switch]$Verbose
)

# 색상 함수들
function Write-Success($message) {
    Write-Host "✅ $message" -ForegroundColor Green
}

function Write-Warning($message) {
    Write-Host "⚠️  $message" -ForegroundColor Yellow
}

function Write-Error($message) {
    Write-Host "❌ $message" -ForegroundColor Red
}

function Write-Info($message) {
    Write-Host "ℹ️  $message" -ForegroundColor Cyan
}

function Write-Step($step, $message) {
    Write-Host "`n🔧 Step $step`: $message" -ForegroundColor Magenta
}

# 관리자 권한 확인
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Node.js 설치 확인
function Test-NodeJS {
    try {
        $nodeVersion = node --version 2>$null
        if ($nodeVersion) {
            Write-Success "Node.js 발견: $nodeVersion"
            return $true
        }
    }
    catch {
        Write-Warning "Node.js가 설치되지 않았습니다."
        return $false
    }
    return $false
}

# Python 설치 확인
function Test-Python {
    $pythonCommands = @("python", "py", "python3")
    
    foreach ($cmd in $pythonCommands) {
        try {
            $pythonVersion = & $cmd --version 2>$null
            if ($pythonVersion -match "Python 3\.[8-9]|Python 3\.1[0-9]") {
                Write-Success "Python 발견: $pythonVersion"
                return $true
            }
        }
        catch {
            continue
        }
    }
    
    Write-Warning "Python 3.8+ 가 설치되지 않았습니다."
    return $false
}

# Claude Desktop 설치 확인
function Test-ClaudeDesktop {
    $claudePath = "$env:APPDATA\Claude"
    if (Test-Path $claudePath) {
        Write-Success "Claude Desktop 설치 폴더 발견"
        return $true
    } else {
        Write-Warning "Claude Desktop이 설치되지 않았습니다."
        return $false
    }
}

# Node.js 자동 설치
function Install-NodeJS {
    Write-Info "Node.js 다운로드 및 설치를 시작합니다..."
    
    try {
        # Chocolatey가 있으면 사용
        if (Get-Command choco -ErrorAction SilentlyContinue) {
            Write-Info "Chocolatey를 사용하여 Node.js를 설치합니다..."
            choco install nodejs -y
        }
        # winget 사용
        elseif (Get-Command winget -ErrorAction SilentlyContinue) {
            Write-Info "winget을 사용하여 Node.js를 설치합니다..."
            winget install OpenJS.NodeJS
        }
        else {
            Write-Warning "자동 설치를 위해 수동으로 Node.js를 설치해주세요:"
            Write-Info "https://nodejs.org/ 에서 LTS 버전을 다운로드하세요."
            return $false
        }
        
        Write-Success "Node.js 설치 완료"
        return $true
    }
    catch {
        Write-Error "Node.js 자동 설치 실패: $($_.Exception.Message)"
        return $false
    }
}

# Python 자동 설치
function Install-Python {
    Write-Info "Python 다운로드 및 설치를 시작합니다..."
    
    try {
        # winget 사용
        if (Get-Command winget -ErrorAction SilentlyContinue) {
            Write-Info "winget을 사용하여 Python을 설치합니다..."
            winget install Python.Python.3.11
        }
        # Chocolatey 사용
        elseif (Get-Command choco -ErrorAction SilentlyContinue) {
            Write-Info "Chocolatey를 사용하여 Python을 설치합니다..."
            choco install python -y
        }
        else {
            Write-Warning "자동 설치를 위해 수동으로 Python을 설치해주세요:"
            Write-Info "https://www.python.org/downloads/ 에서 Python 3.8+ 를 다운로드하세요."
            Write-Info "설치 시 'Add Python to PATH' 옵션을 체크해주세요."
            return $false
        }
        
        Write-Success "Python 설치 완료"
        return $true
    }
    catch {
        Write-Error "Python 자동 설치 실패: $($_.Exception.Message)"
        return $false
    }
}

# MCP 서버 설치
function Install-MCPServer {
    Write-Info "Voidlight 마크다운 MCP 서버를 설치합니다..."
    
    try {
        # NPX로 설치
        $output = npx markitdown-mcp-enhanced --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "MCP 서버 설치 및 테스트 완료"
            Write-Info "버전: $output"
            return $true
        } else {
            Write-Error "MCP 서버 설치 실패"
            return $false
        }
    }
    catch {
        Write-Error "MCP 서버 설치 중 오류: $($_.Exception.Message)"
        return $false
    }
}

# Claude Desktop 설정
function Set-ClaudeDesktopConfig {
    $configPath = "$env:APPDATA\Claude\claude_desktop_config.json"
    $configDir = Split-Path $configPath
    
    # 디렉토리 생성
    if (-not (Test-Path $configDir)) {
        New-Item -ItemType Directory -Path $configDir -Force | Out-Null
        Write-Info "Claude 설정 디렉토리를 생성했습니다."
    }
    
    # 기존 설정 백업
    if (Test-Path $configPath) {
        $backupPath = "$configPath.backup.$(Get-Date -Format 'yyyyMMdd-HHmmss')"
        Copy-Item $configPath $backupPath
        Write-Info "기존 설정을 백업했습니다: $backupPath"
    }
    
    # 새 설정 생성
    $config = @{
        mcpServers = @{
            "markitdown-mcp-enhanced" = @{
                command = "npx"
                args = @("markitdown-mcp-enhanced")
                env = @{
                    KOREAN_SUPPORT = "true"
                    LOG_LEVEL = "INFO"
                }
            }
        }
    }
    
    try {
        $configJson = $config | ConvertTo-Json -Depth 4
        $configJson | Out-File -FilePath $configPath -Encoding UTF8
        Write-Success "Claude Desktop 설정이 완료되었습니다."
        Write-Info "설정 파일: $configPath"
        return $true
    }
    catch {
        Write-Error "Claude Desktop 설정 실패: $($_.Exception.Message)"
        return $false
    }
}

# PowerShell 실행 정책 확인 및 설정
function Set-ExecutionPolicyIfNeeded {
    $currentPolicy = Get-ExecutionPolicy -Scope CurrentUser
    
    if ($currentPolicy -eq "Restricted") {
        Write-Warning "PowerShell 실행 정책이 제한적입니다."
        
        $response = Read-Host "실행 정책을 RemoteSigned로 변경하시겠습니까? (y/N)"
        if ($response -match "^[Yy]") {
            try {
                Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
                Write-Success "PowerShell 실행 정책을 변경했습니다."
            }
            catch {
                Write-Error "실행 정책 변경 실패: $($_.Exception.Message)"
                return $false
            }
        }
    } else {
        Write-Success "PowerShell 실행 정책: $currentPolicy"
    }
    return $true
}

# 메인 설치 함수
function Start-Installation {
    Write-Host @"
🚀 Voidlight 마크다운 MCP 서버 설치 스크립트
================================================
이 스크립트는 Windows에서 필요한 모든 구성 요소를 설치합니다.

"@ -ForegroundColor Cyan

    $isAdmin = Test-Administrator
    if (-not $isAdmin) {
        Write-Warning "일부 기능을 위해 관리자 권한이 필요할 수 있습니다."
    }

    # Step 1: PowerShell 실행 정책 확인
    Write-Step 1 "PowerShell 실행 정책 확인"
    if (-not (Set-ExecutionPolicyIfNeeded)) {
        Write-Error "PowerShell 설정에 실패했습니다."
        return $false
    }

    if (-not $SkipDependencies) {
        # Step 2: Node.js 확인 및 설치
        Write-Step 2 "Node.js 확인 및 설치"
        if (-not (Test-NodeJS)) {
            if (-not (Install-NodeJS)) {
                Write-Error "Node.js 설치에 실패했습니다. 수동으로 설치해주세요."
                return $false
            }
        }

        # Step 3: Python 확인 및 설치  
        Write-Step 3 "Python 확인 및 설치"
        if (-not (Test-Python)) {
            if (-not (Install-Python)) {
                Write-Error "Python 설치에 실패했습니다. 수동으로 설치해주세요."
                return $false
            }
        }

        # 환경 변수 새로고침
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    }

    # Step 4: MCP 서버 설치
    Write-Step 4 "MCP 서버 설치"
    if (-not (Install-MCPServer)) {
        Write-Error "MCP 서버 설치에 실패했습니다."
        return $false
    }

    # Step 5: Claude Desktop 설정
    Write-Step 5 "Claude Desktop 설정"
    if (Test-ClaudeDesktop) {
        if (-not (Set-ClaudeDesktopConfig)) {
            Write-Error "Claude Desktop 설정에 실패했습니다."
            return $false
        }
    } else {
        Write-Warning "Claude Desktop이 설치되지 않았습니다."
        Write-Info "Claude Desktop을 설치한 후 다음 설정을 수동으로 추가해주세요:"
        Write-Info "$env:APPDATA\Claude\claude_desktop_config.json"
    }

    return $true
}

# 설치 완료 메시지
function Show-CompletionMessage {
    Write-Host @"

🎉 설치 완료!
==========================================

✅ Voidlight 마크다운 MCP 서버가 성공적으로 설치되었습니다.

📋 다음 단계:
1. Claude Desktop을 재시작하세요
2. Claude Desktop에서 다음과 같이 테스트해보세요:
   "지원되는 파일 형식을 알려주세요"

🔧 수동 테스트:
   npx markitdown-mcp-enhanced --version

📁 설정 파일 위치:
   $env:APPDATA\Claude\claude_desktop_config.json

📖 자세한 사용법:
   WINDOWS_SERVER_GUIDE.md 파일을 참조하세요

🆘 문제 발생 시:
   GitHub Issues: https://github.com/VoidLight00/voidlight-markdown-mcp-server/issues

"@ -ForegroundColor Green
}

# 메인 실행
try {
    if (Start-Installation) {
        Show-CompletionMessage
        exit 0
    } else {
        Write-Error "설치에 실패했습니다. 위의 오류 메시지를 확인해주세요."
        exit 1
    }
}
catch {
    Write-Error "예상치 못한 오류가 발생했습니다: $($_.Exception.Message)"
    Write-Info "수동 설치를 위해 WINDOWS_SERVER_GUIDE.md 파일을 참조해주세요."
    exit 1
}