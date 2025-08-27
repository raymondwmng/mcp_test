#!/bin/bash

# Brave Search MCP Server Startup Script

echo "🚀 Starting Brave Search MCP Server..."

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed or not in PATH"
    exit 1
fi

# Check if BRAVE_API_KEY is set
if [ -z "$BRAVE_API_KEY" ]; then
    echo "❌ BRAVE_API_KEY environment variable is not set"
    echo "Please set it with: export BRAVE_API_KEY='your_api_key_here'"
    echo ""
    echo "You can also create a .env file with:"
    echo "BRAVE_API_KEY=your_api_key_here"
    echo ""
    echo "Then source it with: source .env"
    exit 1
fi

echo "✅ BRAVE_API_KEY is set"
echo "🔍 Starting MCP server..."

# Start the server
python brave_search_mcp_server.py
