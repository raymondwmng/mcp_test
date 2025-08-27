#!/usr/bin/env python3
"""
Test script for the Brave Search MCP Server.

This script demonstrates the basic functionality of the server.
Note: Requires BRAVE_API_KEY environment variable to be set.
"""

import asyncio
import os
from brave_search_mcp_server import BraveSearchMCPServer


async def test_server():
    """Test the MCP server functionality."""
    
    # Check if API key is set
    if not os.getenv("BRAVE_API_KEY"):
        print("❌ BRAVE_API_KEY environment variable not set!")
        print("Please set it with: export BRAVE_API_KEY='your_api_key_here'")
        return
    
    print("🚀 Starting Brave Search MCP Server test...")
    
    # Create server instance
    server = BraveSearchMCPServer()
    
    try:
        # Test web search
        print("\n🔍 Testing web search...")
        search_result = await server._search_brave("Python programming", 3)
        
        if search_result:
            print(f"✅ Found {len(search_result)} results")
            for i, result in enumerate(search_result):
                print(f"  {i+1}. {result.title}")
                print(f"     URL: {result.url}")
                print(f"     Description: {result.description[:100]}...")
                print()
        else:
            print("❌ No search results found")
            return
        
        # Test session management
        print("📝 Testing session management...")
        session_id = f"test_session_{hash('Python programming') % 10000}"
        server.search_sessions[session_id] = search_result
        
        # Test rating
        print("⭐ Testing result rating...")
        rating_result = await server.rate_search_result(0, 5, session_id)
        if rating_result.get("success"):
            print(f"✅ {rating_result['message']}")
        else:
            print(f"❌ Rating failed: {rating_result.get('error')}")
        
        # Test saving results
        print("💾 Testing result saving...")
        save_result = await server.save_search_results(session_id, "test_python_programming")
        if save_result.get("success"):
            print(f"✅ {save_result['message']}")
            print(f"   File saved as: {save_result['filename']}")
        else:
            print(f"❌ Save failed: {save_result.get('error')}")
        
        # Test listing saved results
        print("📋 Testing saved results listing...")
        list_result = await server.list_saved_results()
        if list_result.get("success"):
            print(f"✅ Found {list_result['total_files']} saved files")
            for file_info in list_result['files']:
                print(f"   - {file_info['filename']} ({file_info['total_results']} results)")
        else:
            print(f"❌ List failed: {list_result.get('error')}")
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_server())
