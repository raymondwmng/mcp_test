# Configuration Guide

This guide explains how to configure and use the Brave Search MCP Server.

## Prerequisites

1. **Python 3.12+**: Ensure you have Python 3.12 or higher installed
2. **Brave Search API Key**: Get your API key from [Brave Search API](https://api.search.brave.com/)

## Installation

### 1. Install Dependencies

```bash
# Using pip
pip install -r requirements.txt

# Or using uv (if you have it installed)
uv sync
```

### 2. Set Environment Variables

#### Option A: Export directly
```bash
export BRAVE_API_KEY="your_actual_api_key_here"
```

#### Option B: Create .env file
```bash
# Copy the example file
cp env.example .env

# Edit .env and add your actual API key
nano .env
```

Then source it:
```bash
source .env
```

#### Option C: Use the startup script
```bash
# Make sure the script is executable
chmod +x start_server.sh

# Run the startup script (it will check for the API key)
./start_server.sh
```

## Usage

### Starting the MCP Server

#### Method 1: Direct Python execution
```bash
python brave_search_mcp_server.py
```

#### Method 2: Using the startup script
```bash
./start_server.sh
```

#### Method 3: As an MCP server
Add to your MCP client configuration:
```json
{
  "mcpServers": {
    "brave-search": {
      "command": "python",
      "args": ["brave_search_mcp_server.py"],
      "env": {
        "BRAVE_API_KEY": "${BRAVE_API_KEY}"
      }
    }
  }
}
```

### Testing the Server

#### Run the demo
```bash
python demo.py
```

#### Run tests
```bash
python test_server.py
```

#### Interactive example
```bash
python example_client.py
```

## API Key Management

### Getting a Brave Search API Key

1. Visit [Brave Search API](https://api.search.brave.com/)
2. Sign up for an account
3. Generate an API key
4. Copy the key to your environment

### Security Best Practices

- **Never commit API keys** to version control
- **Use environment variables** instead of hardcoding
- **Rotate keys regularly** for production use
- **Limit key permissions** to only what's needed

## Configuration Options

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `BRAVE_API_KEY` | Your Brave Search API key | Yes | None |
| `PYTHONPATH` | Python path for imports | No | Current directory |

### Server Configuration

The server creates a `search_results/` directory by default for storing JSON files. You can modify this in the `BraveSearchMCPServer` class.

### MCP Configuration

The `mcp-config.json` file contains the server configuration for MCP clients. Modify this file to change server behavior or add additional configuration options.

## Troubleshooting

### Common Issues

#### 1. "BRAVE_API_KEY not set" error
```bash
# Solution: Set the environment variable
export BRAVE_API_KEY="your_key_here"
```

#### 2. "Module not found" errors
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

#### 3. "Permission denied" on startup script
```bash
# Solution: Make script executable
chmod +x start_server.sh
```

#### 4. API rate limiting
- Brave Search API has rate limits
- Implement exponential backoff for production use
- Monitor API usage in your Brave dashboard

### Debug Mode

To enable debug logging, modify the server code to add logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Testing API Connectivity

Test your API key directly:

```bash
curl -H "X-Subscription-Token: YOUR_API_KEY" \
     "https://api.search.brave.com/res/v1/web/search?q=test&count=1"
```

## Production Deployment

### Docker (Recommended)

Create a `Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "brave_search_mcp_server.py"]
```

### Systemd Service

Create `/etc/systemd/system/brave-search-mcp.service`:

```ini
[Unit]
Description=Brave Search MCP Server
After=network.target

[Service]
Type=simple
User=mcp
WorkingDirectory=/path/to/your/app
Environment=BRAVE_API_KEY=your_key_here
ExecStart=/usr/bin/python3 brave_search_mcp_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### Environment Management

For production, use a proper environment management tool:

```bash
# Using direnv
echo "export BRAVE_API_KEY=your_key" > .envrc
direnv allow

# Using python-dotenv
# The server already supports this via the .env file
```

## Monitoring and Logging

### Health Checks

The server provides health check endpoints when running as an MCP server. Monitor these for uptime.

### Log Rotation

Implement log rotation for production deployments:

```bash
# Using logrotate
/path/to/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

## Support

For additional help:

1. Check the [README.md](README.md) for usage examples
2. Review the [example files](example_client.py) for implementation details
3. Open an issue on the repository for bugs or feature requests
4. Check the [Brave Search API documentation](https://api.search.brave.com/) for API-specific issues
