#!/usr/bin/env python3
"""
Simple demo script for the Brave Search MCP Server.

This script demonstrates the basic functionality in a non-interactive way.
"""

import asyncio
import os
from brave_search_mcp_server import BraveSearchMCPServer


async def demo():
    """Run a simple demonstration of the MCP server."""
    
    print("🌟 Brave Search MCP Server Demo")
    print("===============================")
    
    # Check if API key is set
    if not os.getenv("BRAVE_API_KEY"):
        print("❌ BRAVE_API_KEY environment variable not set!")
        print("Please set it with: export BRAVE_API_KEY='your_api_key_here'")
        print("Or run: source env.example")
        return
    
    print("✅ API key configured")
    
    # Create server instance
    server = BraveSearchMCPServer()
    
    try:
        # Demo search
        print("\n🔍 Demo: Searching for 'Python MCP server'...")
        search_results = await server._search_brave("Python MCP server", 3)
        
        if not search_results:
            print("❌ No results found")
            return
        
        print(f"✅ Found {len(search_results)} results")
        
        # Create session
        session_id = "demo_session_123"
        server.search_sessions[session_id] = search_results
        
        # Show results
        print("\n📋 Search Results:")
        for i, result in enumerate(search_results):
            print(f"\n{i+1}. {result.title}")
            print(f"   URL: {result.url}")
            print(f"   Description: {result.description[:100]}...")
        
        # Demo rating
        print("\n⭐ Demo: Rating results...")
        ratings = [5, 4, 3]  # Demo ratings
        
        for i, rating in enumerate(ratings):
            result = await server.rate_search_result(i, rating, session_id)
            if result.get("success"):
                print(f"   ✅ Rated result {i+1} with {rating}/5")
            else:
                print(f"   ❌ Failed to rate result {i+1}: {result.get('error')}")
        
        # Demo saving
        print("\n💾 Demo: Saving results...")
        save_result = await server.save_search_results(session_id, "demo_python_mcp")
        
        if save_result.get("success"):
            print(f"✅ {save_result['message']}")
            print(f"   File: {save_result['filename']}")
            print(f"   Results saved: {save_result['results_saved']}")
            print(f"   Rated results: {save_result['rated_results']}")
        else:
            print(f"❌ Save failed: {save_result.get('error')}")
        
        # Demo listing
        print("\n📋 Demo: Listing saved results...")
        list_result = await server.list_saved_results()
        
        if list_result.get("success"):
            print(f"✅ Found {list_result['total_files']} saved files")
            for file_info in list_result['files']:
                print(f"   - {file_info['filename']}")
                print(f"     Results: {file_info['total_results']}")
                print(f"     Rated: {file_info['rated_results']}")
                print(f"     Avg Rating: {file_info['average_rating']}")
        else:
            print(f"❌ List failed: {list_result.get('error')}")
        
        print("\n🎉 Demo completed successfully!")
        print("\n💡 Next steps:")
        print("   1. Try the interactive client: python example_client.py")
        print("   2. Run tests: python test_server.py")
        print("   3. Start the MCP server: python brave_search_mcp_server.py")
        
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(demo())
