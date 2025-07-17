#!/usr/bin/env node

/**
 * Local test script for MarkItDown MCP Enhanced
 * This helps test the MCP server locally before using with Claude Desktop
 */

const { spawn } = require('child_process');
const path = require('path');

console.log('🧪 Testing MarkItDown MCP Enhanced locally...\n');

// Test the Node.js wrapper
console.log('1. Testing Node.js wrapper...');
const testProcess = spawn('node', ['bin/markitdown-mcp-enhanced.js', '--version'], {
  cwd: __dirname,
  stdio: 'inherit'
});

testProcess.on('close', (code) => {
  if (code === 0) {
    console.log('✅ Node.js wrapper works correctly!\n');
    
    console.log('2. Testing MCP server startup...');
    console.log('Press Ctrl+C to stop the server and continue...\n');
    
    // Test the actual server
    const serverProcess = spawn('node', ['bin/markitdown-mcp-enhanced.js'], {
      cwd: __dirname,
      stdio: 'inherit'
    });
    
    serverProcess.on('close', (serverCode) => {
      console.log('\n✅ MCP server test completed!');
      console.log('\n📋 Next steps:');
      console.log('1. Copy the configuration to Claude Desktop:');
      console.log('   macOS: ~/Library/Application Support/Claude/claude_desktop_config.json');
      console.log('   Windows: %APPDATA%\\Claude\\claude_desktop_config.json');
      console.log('\n2. Add this configuration:');
      console.log(JSON.stringify({
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
      }, null, 2));
      console.log('\n3. Restart Claude Desktop');
      console.log('\n🎉 You can now use the MCP server in Claude Desktop!');
    });
    
  } else {
    console.error('❌ Node.js wrapper test failed');
    process.exit(1);
  }
});

testProcess.on('error', (error) => {
  console.error('❌ Error testing wrapper:', error.message);
  process.exit(1);
});