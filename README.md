# Brave Search MCP Server

A Model Context Protocol (MCP) server that integrates with Brave Search API to provide web search capabilities, result rating, and persistent storage of search results.

## Features

- **Web Search**: Perform web searches using Brave Search API
- **Result Rating**: Rate search results on a 1-5 scale for quality assessment
- **Persistent Storage**: Save search results with ratings to JSON files
- **Session Management**: Track search sessions and maintain state
- **Comprehensive Tool Descriptions**: Detailed descriptions for effective LLM integration

## Prerequisites

- Python 3.12 or higher
- Brave Search API key ([Get one here](https://api.search.brave.com/))

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd mcp_test
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set your Brave API key:
```bash
export BRAVE_API_KEY="your_api_key_here"
```

## Usage

### Starting the Server

```bash
python brave_search_mcp_server.py
```

### MCP Configuration

Add this to your MCP client configuration:

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

## Available Tools

### 1. `perform_web_search`

Performs a web search using Brave Search API and returns structured results.

**When to use:**
- Researching current events or topics
- Finding recent information not in training data
- Getting up-to-date news or developments
- Fact-checking or gathering multiple sources

**Parameters:**
- `query` (string): Search query string
- `count` (int, optional): Number of results (1-20, default: 10)

**Returns:**
- Search results with session ID for subsequent operations
- Structured data including title, URL, and description

### 2. `rate_search_result`

Rate a specific search result from a previous search session.

**When to use:**
- After performing a web search to evaluate result quality
- Providing feedback for improving future searches
- Marking results as useful or not useful
- Creating curated lists of high-quality sources

**Parameters:**
- `result_index` (int): Index of result to rate (0-based)
- `rating` (int): Rating from 1-5 (1=worst, 5=best)
- `search_session_id` (string): Session ID from search operation

**Returns:**
- Confirmation of rating application
- Updated result metadata

### 3. `save_search_results`

Save search results with ratings to a JSON file for future reference.

**When to use:**
- Keeping records of research sessions
- Building databases of rated sources
- Sharing results with others
- Referencing previous searches and ratings
- Tracking research progress over time

**Parameters:**
- `search_session_id` (string): Session ID from search operation
- `filename` (string, optional): Custom filename (without extension)

**Returns:**
- Confirmation of save operation
- File location and metadata

### 4. `list_saved_results`

List all previously saved search result files.

**When to use:**
- Seeing research history and saved sessions
- Finding previous search results
- Managing research database
- Tracking research progress over time

**Returns:**
- List of saved files with metadata
- File statistics and ratings summary

## Data Models

### SearchResult
```python
{
    "title": "Result title",
    "url": "https://example.com",
    "description": "Result description/snippet",
    "rating": 5,  # Optional: 1-5 rating
    "rated_at": "2024-01-01T12:00:00"  # Optional: rating timestamp
}
```

### Saved File Structure
```json
{
    "metadata": {
        "session_id": "search_20240101_120000_1234",
        "saved_at": "2024-01-01T12:00:00",
        "total_results": 10,
        "rated_results": 5,
        "average_rating": 4.2
    },
    "results": [...]
}
```

## Example Workflow

1. **Perform Search:**
   ```python
   # Search for "latest AI developments 2024"
   result = await perform_web_search("latest AI developments 2024", count=10)
   session_id = result["session_id"]
   ```

2. **Rate Results:**
   ```python
   # Rate the first result as excellent
   await rate_search_result(0, 5, session_id)
   
   # Rate the second result as good
   await rate_search_result(1, 4, session_id)
   ```

3. **Save Results:**
   ```python
   # Save with custom filename
   await save_search_results(session_id, "ai_developments_2024")
   ```

4. **List Saved Results:**
   ```python
   # View all saved research sessions
   await list_saved_results()
   ```

## File Structure

```
mcp_test/
├── brave_search_mcp_server.py    # Main MCP server
├── mcp-config.json              # MCP configuration
├── search_results/               # Directory for saved results
├── pyproject.toml               # Project dependencies
└── README.md                    # This file
```

## Error Handling

The server includes comprehensive error handling for:
- Missing API keys
- Invalid session IDs
- Out-of-range result indices
- File I/O errors
- API request failures

## Security Considerations

- API keys are read from environment variables
- Input validation for all parameters
- Safe file operations with proper error handling
- No sensitive data logging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Add your license here]

## Support

For issues and questions, please open an issue on the repository.
