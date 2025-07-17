#!/usr/bin/env node

/**
 * Node.js wrapper for MarkItDown MCP Enhanced Server
 * This script runs the Python MCP server from Node.js/npx
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// Check if Python is available
function findPython() {
  const pythonCommands = ['python3', 'python'];
  
  for (const cmd of pythonCommands) {
    try {
      const result = require('child_process').execSync(`${cmd} --version`, { 
        encoding: 'utf8', 
        stdio: 'pipe' 
      });
      if (result.includes('Python 3.')) {
        return cmd;
      }
    } catch (error) {
      // Command not found, try next
    }
  }
  
  console.error('Error: Python 3.8+ is required but not found.');
  console.error('Please install Python 3.8 or higher and ensure it\'s in your PATH.');
  process.exit(1);
}

// Install Python dependencies if needed
async function ensureDependencies() {
  const pythonCmd = findPython();
  const projectRoot = path.dirname(__dirname);
  
  console.log('Checking Python dependencies...');
  
  return new Promise((resolve, reject) => {
    // Install required dependencies only
    const installProcess = spawn(pythonCmd, ['-m', 'pip', 'install', '-r', 'requirements.txt'], {
      cwd: projectRoot,
      stdio: 'inherit'
    });
    
    installProcess.on('close', (code) => {
      if (code === 0) {
        console.log('Dependencies installed successfully.');
        resolve();
      } else {
        console.error('Failed to install dependencies.');
        reject(new Error(`pip install failed with code ${code}`));
      }
    });
    
    installProcess.on('error', (error) => {
      console.error('Error installing dependencies:', error.message);
      reject(error);
    });
  });
}

// Run the MCP server
async function runServer() {
  const pythonCmd = findPython();
  const projectRoot = path.dirname(__dirname);
  
  console.log('Starting MarkItDown MCP Enhanced Server...');
  
  // Run the Python MCP server
  const serverProcess = spawn(pythonCmd, ['-m', 'markitdown_mcp_enhanced.server'], {
    cwd: projectRoot,
    stdio: 'inherit',
    env: {
      ...process.env,
      PYTHONPATH: path.join(projectRoot, 'src')
    }
  });
  
  serverProcess.on('close', (code) => {
    if (code !== 0) {
      console.error(`Server exited with code ${code}`);
      process.exit(code);
    }
  });
  
  serverProcess.on('error', (error) => {
    console.error('Error starting server:', error.message);
    process.exit(1);
  });
  
  // Handle graceful shutdown
  process.on('SIGINT', () => {
    console.log('\nShutting down server...');
    serverProcess.kill('SIGINT');
  });
  
  process.on('SIGTERM', () => {
    console.log('\nShutting down server...');
    serverProcess.kill('SIGTERM');
  });
}

// Main execution
async function main() {
  try {
    // Check if we're in development mode (package.json exists)
    const projectRoot = path.dirname(__dirname);
    const packageJsonPath = path.join(projectRoot, 'package.json');
    
    if (fs.existsSync(packageJsonPath)) {
      // Development mode - ensure dependencies are installed
      await ensureDependencies();
    }
    
    // Run the server
    await runServer();
    
  } catch (error) {
    console.error('Failed to start MarkItDown MCP Enhanced Server:', error.message);
    process.exit(1);
  }
}

// Parse command line arguments
const args = process.argv.slice(2);

if (args.includes('--help') || args.includes('-h')) {
  console.log(`
MarkItDown MCP Enhanced Server

Usage: npx markitdown-mcp-enhanced [options]

Options:
  --help, -h          Show this help message
  --version, -v       Show version information

Environment Variables:
  OPENAI_API_KEY                     OpenAI API key for image descriptions
  AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT  Azure Document Intelligence endpoint
  AZURE_DOCUMENT_INTELLIGENCE_KEY       Azure Document Intelligence key
  LOG_LEVEL                         Log level (DEBUG, INFO, WARNING, ERROR)
  KOREAN_SUPPORT                    Enable Korean support (true/false)

Examples:
  npx markitdown-mcp-enhanced
  OPENAI_API_KEY="your-key" npx markitdown-mcp-enhanced
  LOG_LEVEL=DEBUG npx markitdown-mcp-enhanced

For more information, visit:
https://github.com/VoidLight00/voidlight-markdown-mcp-server
`);
  process.exit(0);
}

if (args.includes('--version') || args.includes('-v')) {
  const packageJson = require('../package.json');
  console.log(`markitdown-mcp-enhanced v${packageJson.version}`);
  process.exit(0);
}

// Start the main process
main().catch((error) => {
  console.error('Unhandled error:', error);
  process.exit(1);
});