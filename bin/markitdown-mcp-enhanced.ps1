#!/usr/bin/env powershell

<#
.SYNOPSIS
    PowerShell wrapper for MarkItDown MCP Enhanced Server

.DESCRIPTION
    This script runs the MarkItDown MCP Enhanced Server on Windows systems.
    It automatically handles Python dependency installation and server startup.

.PARAMETER Help
    Show help information

.PARAMETER Version
    Show version information

.EXAMPLE
    .\markitdown-mcp-enhanced.ps1
    Start the MCP server

.EXAMPLE
    .\markitdown-mcp-enhanced.ps1 -Version
    Show version information
#>

param(
    [switch]$Help,
    [switch]$Version
)

# Function to find Python executable
function Find-Python {
    $pythonCommands = @("python", "python3", "py")
    
    foreach ($cmd in $pythonCommands) {
        try {
            $result = & $cmd --version 2>&1
            if ($result -match "Python 3\.") {
                return $cmd
            }
        }
        catch {
            # Command not found, try next
        }
    }
    
    Write-Error "Error: Python 3.8+ is required but not found."
    Write-Error "Please install Python 3.8 or higher from https://www.python.org/downloads/"
    exit 1
}

# Function to ensure dependencies are installed
function Install-Dependencies {
    param($PythonCmd, $ProjectRoot)
    
    Write-Host "Checking Python dependencies..." -ForegroundColor Yellow
    
    try {
        $process = Start-Process -FilePath $PythonCmd -ArgumentList @("-m", "pip", "install", "-r", "requirements.txt") -WorkingDirectory $ProjectRoot -Wait -PassThru -NoNewWindow
        
        if ($process.ExitCode -eq 0) {
            Write-Host "Dependencies installed successfully." -ForegroundColor Green
        } else {
            Write-Error "Failed to install dependencies."
            exit $process.ExitCode
        }
    }
    catch {
        Write-Error "Error installing dependencies: $($_.Exception.Message)"
        exit 1
    }
}

# Function to run the MCP server
function Start-Server {
    param($PythonCmd, $ProjectRoot)
    
    Write-Host "Starting MarkItDown MCP Enhanced Server..." -ForegroundColor Green
    
    try {
        # Set PYTHONPATH
        $env:PYTHONPATH = Join-Path $ProjectRoot "src"
        
        # Run the Python MCP server
        & $PythonCmd -m markitdown_mcp_enhanced.server
    }
    catch {
        Write-Error "Error starting server: $($_.Exception.Message)"
        exit 1
    }
}

# Main execution
function Main {
    # Get script directory and project root
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    $projectRoot = Split-Path -Parent $scriptDir
    
    # Handle command line arguments
    if ($Help) {
        Write-Host @"
MarkItDown MCP Enhanced Server

Usage: .\markitdown-mcp-enhanced.ps1 [options]

Options:
  -Help           Show this help message
  -Version        Show version information

Environment Variables:
  OPENAI_API_KEY                     OpenAI API key for image descriptions
  AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT  Azure Document Intelligence endpoint
  AZURE_DOCUMENT_INTELLIGENCE_KEY       Azure Document Intelligence key
  LOG_LEVEL                         Log level (DEBUG, INFO, WARNING, ERROR)
  KOREAN_SUPPORT                    Enable Korean support (true/false)

Examples:
  .\markitdown-mcp-enhanced.ps1
  `$env:OPENAI_API_KEY="your-key"; .\markitdown-mcp-enhanced.ps1
  `$env:LOG_LEVEL="DEBUG"; .\markitdown-mcp-enhanced.ps1

For more information, visit:
https://github.com/VoidLight00/voidlight-markdown-mcp-server
"@
        return
    }
    
    if ($Version) {
        $packageJsonPath = Join-Path $projectRoot "package.json"
        if (Test-Path $packageJsonPath) {
            $packageJson = Get-Content $packageJsonPath | ConvertFrom-Json
            Write-Host "markitdown-mcp-enhanced v$($packageJson.version)"
        } else {
            Write-Host "markitdown-mcp-enhanced v1.0.0"
        }
        return
    }
    
    try {
        # Find Python
        $pythonCmd = Find-Python
        
        # Check if we're in development mode (package.json exists)
        $packageJsonPath = Join-Path $projectRoot "package.json"
        if (Test-Path $packageJsonPath) {
            # Development mode - ensure dependencies are installed
            Install-Dependencies -PythonCmd $pythonCmd -ProjectRoot $projectRoot
        }
        
        # Run the server
        Start-Server -PythonCmd $pythonCmd -ProjectRoot $projectRoot
    }
    catch {
        Write-Error "Failed to start MarkItDown MCP Enhanced Server: $($_.Exception.Message)"
        exit 1
    }
}

# Execute main function
Main