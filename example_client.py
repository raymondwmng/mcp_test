#!/usr/bin/env python3
"""
Example client for the Brave Search MCP Server.

This script demonstrates how to use the MCP server programmatically.
"""

import asyncio
import json
from pathlib import Path
from brave_search_mcp_server import BraveSearchMCPServer


async def example_workflow():
    """Demonstrate a complete workflow with the MCP server."""
    
    print("🚀 Starting Brave Search MCP Server example workflow...")
    
    # Create server instance
    server = BraveSearchMCPServer()
    
    try:
        # Step 1: Perform a web search
        print("\n🔍 Step 1: Performing web search...")
        search_query = "latest AI developments 2024"
        search_result = await server._search_brave(search_query, 5)
        
        if not search_result:
            print("❌ No search results found")
            return
        
        # Create a session
        session_id = f"example_session_{hash(search_query) % 10000}"
        server.search_sessions[session_id] = search_result
        
        print(f"✅ Found {len(search_result)} results for '{search_query}'")
        print(f"📝 Session ID: {session_id}")
        
        # Step 2: Display results and get user ratings
        print("\n📋 Step 2: Displaying search results...")
        for i, result in enumerate(search_result):
            print(f"\n{i+1}. {result.title}")
            print(f"   URL: {result.url}")
            print(f"   Description: {result.description[:150]}...")
            
            # Simulate user rating (in real usage, this would be user input)
            rating = 5 if i == 0 else 4 if i == 1 else 3
            print(f"   Rating: {rating}/5")
            
            # Apply rating
            await server.rate_search_result(i, rating, session_id)
        
        # Step 3: Save results
        print("\n💾 Step 3: Saving search results...")
        save_result = await server.save_search_results(session_id, "ai_developments_2024")
        
        if save_result.get("success"):
            print(f"✅ {save_result['message']}")
            print(f"   File: {save_result['filename']}")
            print(f"   Results saved: {save_result['results_saved']}")
            print(f"   Rated results: {save_result['rated_results']}")
        else:
            print(f"❌ Save failed: {save_result.get('error')}")
        
        # Step 4: List saved results
        print("\n📋 Step 4: Listing saved results...")
        list_result = await server.list_saved_results()
        
        if list_result.get("success"):
            print(f"✅ Found {list_result['total_files']} saved files:")
            for file_info in list_result['files']:
                print(f"   - {file_info['filename']}")
                print(f"     Session: {file_info['session_id']}")
                print(f"     Results: {file_info['total_results']}")
                print(f"     Rated: {file_info['rated_results']}")
                print(f"     Avg Rating: {file_info['average_rating']}")
                print()
        else:
            print(f"❌ List failed: {list_result.get('error')}")
        
        # Step 5: Show the saved file content
        print("\n📄 Step 5: Displaying saved file content...")
        if save_result.get("success"):
            filepath = Path(save_result['filepath'])
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                
                print("📊 File metadata:")
                metadata = content['metadata']
                for key, value in metadata.items():
                    print(f"   {key}: {value}")
                
                print(f"\n📝 Sample results (showing first 2):")
                for i, result in enumerate(content['results'][:2]):
                    print(f"   {i+1}. {result['title']}")
                    print(f"      Rating: {result.get('rating', 'Not rated')}")
                    print(f"      URL: {result['url']}")
                    print()
            else:
                print("❌ Saved file not found")
        
        print("\n🎉 Example workflow completed successfully!")
        
    except Exception as e:
        print(f"❌ Example failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


async def interactive_workflow():
    """Interactive workflow where user can input search queries and ratings."""
    
    print("\n🎯 Interactive Workflow Mode")
    print("==========================")
    
    server = BraveSearchMCPServer()
    
    try:
        # Get search query from user
        query = input("\n🔍 Enter your search query: ").strip()
        if not query:
            print("❌ No query provided")
            return
        
        # Perform search
        print(f"\n🔍 Searching for: {query}")
        search_result = await server._search_brave(query, 10)
        
        if not search_result:
            print("❌ No search results found")
            return
        
        # Create session
        session_id = f"interactive_{hash(query) % 10000}"
        server.search_sessions[session_id] = search_result
        
        print(f"✅ Found {len(search_result)} results")
        print(f"📝 Session ID: {session_id}")
        
        # Display results
        print("\n📋 Search Results:")
        for i, result in enumerate(search_result):
            print(f"\n{i+1}. {result.title}")
            print(f"   URL: {result.url}")
            print(f"   Description: {result.description[:150]}...")
        
        # Get ratings from user
        print("\n⭐ Rate the results (1-5, where 1=worst, 5=best)")
        print("Press Enter to skip rating a result")
        
        for i in range(len(search_result)):
            while True:
                rating_input = input(f"Rating for result {i+1} (1-5 or Enter to skip): ").strip()
                
                if not rating_input:
                    print(f"   Skipped rating for result {i+1}")
                    break
                
                try:
                    rating = int(rating_input)
                    if 1 <= rating <= 5:
                        await server.rate_search_result(i, rating, session_id)
                        print(f"   ✅ Rated result {i+1} with {rating}/5")
                        break
                    else:
                        print("   ❌ Rating must be between 1 and 5")
                except ValueError:
                    print("   ❌ Please enter a valid number (1-5) or press Enter to skip")
        
        # Ask if user wants to save
        save_choice = input("\n💾 Save these results? (y/n): ").strip().lower()
        
        if save_choice in ['y', 'yes']:
            filename = input("Enter filename (or press Enter for default): ").strip()
            if not filename:
                filename = None
            
            save_result = await server.save_search_results(session_id, filename)
            
            if save_result.get("success"):
                print(f"✅ {save_result['message']}")
                print(f"   File: {save_result['filename']}")
            else:
                print(f"❌ Save failed: {save_result.get('error')}")
        else:
            print("   Results not saved")
        
        print("\n🎉 Interactive workflow completed!")
        
    except Exception as e:
        print(f"❌ Interactive workflow failed: {str(e)}")
        import traceback
        traceback.print_exc()


async def main():
    """Main entry point with menu selection."""
    
    print("🌟 Brave Search MCP Server - Example Client")
    print("==========================================")
    print("1. Run example workflow")
    print("2. Interactive workflow")
    print("3. Exit")
    
    while True:
        choice = input("\nSelect an option (1-3): ").strip()
        
        if choice == "1":
            await example_workflow()
            break
        elif choice == "2":
            await interactive_workflow()
            break
        elif choice == "3":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please select 1, 2, or 3.")


if __name__ == "__main__":
    asyncio.run(main())
