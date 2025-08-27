#!/usr/bin/env python3
"""
MCP Server for Brave Search with Result Rating and Storage

This server provides three main capabilities:
1. Web search using Brave Search API
2. Result rating functionality
3. Saving search results with ratings to JSON files

The server uses Fast MCP for efficient communication and provides comprehensive
tool descriptions for effective LLM integration.
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiofiles
import httpx
from fastmcp import FastMCP
from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    """Model for individual search results."""
    title: str = Field(..., description="Title of the search result")
    url: str = Field(..., description="URL of the search result")
    description: str = Field(..., description="Description/snippet of the search result")
    rating: Optional[int] = Field(None, description="User rating from 1-5 (1=worst, 5=best)")
    rated_at: Optional[str] = Field(None, description="Timestamp when result was rated")


class SearchQuery(BaseModel):
    """Model for search query requests."""
    query: str = Field(..., description="Search query string")
    count: int = Field(default=10, ge=1, le=20, description="Number of results to return (1-20)")


class RatingRequest(BaseModel):
    """Model for rating requests."""
    result_index: int = Field(..., ge=0, description="Index of the result to rate (0-based)")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1-5 (1=worst, 5=best)")
    search_session_id: str = Field(..., description="Unique identifier for the search session")


class SaveResultsRequest(BaseModel):
    """Model for saving results requests."""
    search_session_id: str = Field(..., description="Unique identifier for the search session")
    filename: Optional[str] = Field(None, description="Custom filename (without extension)")


class BraveSearchMCPServer:
    """MCP Server for Brave Search with rating and storage capabilities."""
    
    def __init__(self):
        self.fast_mcp = FastMCP()
        self.search_sessions: Dict[str, List[SearchResult]] = {}
        self.brave_api_key = os.getenv("BRAVE_API_KEY")
        self.results_dir = Path("search_results")
        self.results_dir.mkdir(exist_ok=True)
        
        # Register tools
        self._register_tools()
    
    def _register_tools(self):
        """Register all MCP tools with comprehensive descriptions."""
        
        @self.fast_mcp.tool()
        async def perform_web_search(query: str, count: int = 10) -> Dict[str, Any]:
            """
            Perform a web search using Brave Search API and return the top results.
            
            This tool is essential when you need to find current information, news, 
            or factual data from the web. Use it for:
            - Researching current events or topics
            - Finding recent information that may not be in your training data
            - Getting up-to-date news or developments
            - Fact-checking or gathering multiple sources
            
            The tool returns structured search results that can then be rated and saved.
            
            Args:
                query: The search query string (e.g., "latest AI developments 2024")
                count: Number of results to return (1-20, default 10)
            
            Returns:
                Dictionary containing search results, session ID, and metadata
            """
            if not self.brave_api_key:
                return {
                    "error": "Brave API key not configured. Please set BRAVE_API_KEY environment variable.",
                    "results": [],
                    "session_id": None
                }
            
            try:
                # Perform search using Brave API
                search_results = await self._search_brave(query, count)
                
                # Create session ID and store results
                session_id = f"search_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(query) % 10000}"
                self.search_sessions[session_id] = search_results
                
                return {
                    "session_id": session_id,
                    "query": query,
                    "results_count": len(search_results),
                    "results": [result.dict() for result in search_results],
                    "message": f"Found {len(search_results)} results for '{query}'. Use the session_id to rate results or save them."
                }
                
            except Exception as e:
                return {
                    "error": f"Search failed: {str(e)}",
                    "results": [],
                    "session_id": None
                }
        
        @self.fast_mcp.tool()
        async def rate_search_result(result_index: int, rating: int, search_session_id: str) -> Dict[str, Any]:
            """
            Rate a specific search result from a previous search session.
            
            This tool allows users to provide feedback on search result quality and relevance.
            Use it after performing a web search to:
            - Evaluate result relevance and quality
            - Provide feedback for improving future searches
            - Mark results as useful or not useful
            - Create a curated list of high-quality sources
            
            Ratings help improve search quality and can be used to filter or sort results.
            
            Args:
                result_index: Index of the result to rate (0-based, first result is 0)
                rating: Rating from 1-5 where 1=worst/poor quality, 5=excellent/perfect match
                search_session_id: Session ID from the previous search operation
            
            Returns:
                Dictionary confirming the rating was applied
            """
            if search_session_id not in self.search_sessions:
                return {
                    "error": f"Session ID '{search_session_id}' not found. Please perform a search first.",
                    "success": False
                }
            
            if not (0 <= result_index < len(self.search_sessions[search_session_id])):
                return {
                    "error": f"Result index {result_index} is out of range. Available indices: 0-{len(self.search_sessions[search_session_id])-1}",
                    "success": False
                }
            
            if not (1 <= rating <= 5):
                return {
                    "error": "Rating must be between 1 and 5 (1=worst, 5=best)",
                    "success": False
                }
            
            # Apply rating
            result = self.search_sessions[search_session_id][result_index]
            result.rating = rating
            result.rated_at = datetime.now().isoformat()
            
            return {
                "success": True,
                "message": f"Rated result '{result.title}' with rating {rating}/5",
                "result_title": result.title,
                "rating": rating,
                "rated_at": result.rated_at
            }
        
        @self.fast_mcp.tool()
        async def save_search_results(search_session_id: str, filename: Optional[str] = None) -> Dict[str, Any]:
            """
            Save search results with ratings to a JSON file for future reference.
            
            This tool persists search results and user ratings to disk, allowing you to:
            - Keep a record of research sessions
            - Build a database of rated sources
            - Share results with others
            - Reference previous searches and ratings
            - Track research progress over time
            
            Results are saved in a structured JSON format with metadata including
            timestamps, ratings, and full result details.
            
            Args:
                search_session_id: Session ID from the previous search operation
                filename: Optional custom filename (without extension). If not provided,
                         a default name based on query and timestamp will be used.
            
            Returns:
                Dictionary confirming the save operation and file location
            """
            if search_session_id not in self.search_sessions:
                return {
                    "error": f"Session ID '{search_session_id}' not found. Please perform a search first.",
                    "success": False
                }
            
            results = self.search_sessions[search_session_id]
            
            # Generate filename if not provided
            if not filename:
                query = results[0].title[:30] if results else "unknown"
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"search_results_{query}_{timestamp}"
            
            # Clean filename
            filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = filename.replace(' ', '_')
            
            filepath = self.results_dir / f"{filename}.json"
            
            # Prepare data for saving
            save_data = {
                "metadata": {
                    "session_id": search_session_id,
                    "saved_at": datetime.now().isoformat(),
                    "total_results": len(results),
                    "rated_results": len([r for r in results if r.rating is not None]),
                    "average_rating": self._calculate_average_rating(results)
                },
                "results": [result.dict() for result in results]
            }
            
            try:
                async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
                    await f.write(json.dumps(save_data, indent=2, ensure_ascii=False))
                
                return {
                    "success": True,
                    "message": f"Search results saved successfully",
                    "filepath": str(filepath),
                    "filename": f"{filename}.json",
                    "results_saved": len(results),
                    "rated_results": len([r for r in results if r.rating is not None])
                }
                
            except Exception as e:
                return {
                    "error": f"Failed to save results: {str(e)}",
                    "success": False
                }
        
        @self.fast_mcp.tool()
        async def list_saved_results() -> Dict[str, Any]:
            """
            List all previously saved search result files.
            
            This tool provides an overview of your research history and saved sessions.
            Use it to:
            - See what research sessions you've saved
            - Find previous search results
            - Manage your research database
            - Track your research progress over time
            
            Returns:
                Dictionary containing list of saved files with metadata
            """
            try:
                saved_files = []
                for filepath in self.results_dir.glob("*.json"):
                    try:
                        async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
                            content = await f.read()
                            data = json.loads(content)
                            
                            saved_files.append({
                                "filename": filepath.name,
                                "filepath": str(filepath),
                                "session_id": data.get("metadata", {}).get("session_id", "unknown"),
                                "saved_at": data.get("metadata", {}).get("saved_at", "unknown"),
                                "total_results": data.get("metadata", {}).get("total_results", 0),
                                "rated_results": data.get("metadata", {}).get("rated_results", 0),
                                "average_rating": data.get("metadata", {}).get("average_rating", 0)
                            })
                    except Exception as e:
                        # Skip corrupted files
                        continue
                
                # Sort by saved date (newest first)
                saved_files.sort(key=lambda x: x.get("saved_at", ""), reverse=True)
                
                return {
                    "success": True,
                    "total_files": len(saved_files),
                    "files": saved_files
                }
                
            except Exception as e:
                return {
                    "error": f"Failed to list saved results: {str(e)}",
                    "success": False
                }
    
    async def _search_brave(self, query: str, count: int) -> List[SearchResult]:
        """Perform search using Brave Search API."""
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.brave_api_key
        }
        
        params = {
            "q": query,
            "count": count,
            "safesearch": "moderate"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers=headers,
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get("web", {}).get("results", []):
                result = SearchResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    description=item.get("description", "")
                )
                results.append(result)
            
            return results
    
    def _calculate_average_rating(self, results: List[SearchResult]) -> Optional[float]:
        """Calculate average rating from rated results."""
        rated_results = [r.rating for r in results if r.rating is not None]
        if not rated_results:
            return None
        return round(sum(rated_results) / len(rated_results), 2)
    
    async def run(self):
        """Run the MCP server."""
        await self.fast_mcp.run()


async def main():
    """Main entry point."""
    server = BraveSearchMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
