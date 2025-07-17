@echo off
REM Windows batch file wrapper for MarkItDown MCP Enhanced Server

setlocal enabledelayedexpansion

REM Check if Node.js is available
where node >nul 2>&1
if errorlevel 1 (
    echo Error: Node.js is required but not found.
    echo Please install Node.js from https://nodejs.org/
    exit /b 1
)

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."

REM Run the Node.js wrapper
node "%SCRIPT_DIR%markitdown-mcp-enhanced.js" %*