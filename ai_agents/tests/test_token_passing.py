#!/usr/bin/env python3
"""
Test script to verify API token is being passed correctly through the agent system.
This will help debug why agents are not receiving authentication tokens.
"""

import asyncio
import os
import sys
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Add ai_agents to path
sys.path.insert(0, str(Path(__file__).parent / "ai_agents"))

from ai_agents.agents.tenant_admin_agent import TenantAdminAgent


async def test_token_passing():
    """Test if token is passed correctly to agent and MCP client"""
    
    print("=" * 80)
    print("🧪 Testing API Token Passing Through Agent System")
    print("=" * 80)
    print()
    
    # Step 1: Check environment
    print("📋 Step 1: Check Environment Variables")
    print("-" * 80)
    api_token = os.getenv("GAPPS_API_TOKEN")
    api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")
    
    print(f"   GAPPS_API_TOKEN: {'✅ Set' if api_token else '❌ Not set'}")
    if api_token:
        print(f"   Token preview: {api_token[:30]}...")
        print(f"   Token length: {len(api_token)} characters")
    print(f"   API_BASE_URL: {api_base_url}")
    print()
    
    if not api_token:
        print("❌ ERROR: GAPPS_API_TOKEN environment variable is not set")
        print()
        print("💡 To fix this:")
        print("   1. Get a token:")
        print("      curl -X POST http://localhost:8000/login \\")
        print("           -H 'Content-Type: application/json' \\")
        print("           -d '{\"email\":\"admin@example.com\",\"password\":\"admin1234567\"}'")
        print()
        print("   2. Set the token:")
        print("      export GAPPS_API_TOKEN='your-token-here'")
        print()
        return False
    
    # Step 2: Create agent with explicit token
    print("📋 Step 2: Create Agent with Explicit Token")
    print("-" * 80)
    
    try:
        agent = TenantAdminAgent(
            model_provider="local",
            model_name="gpt-3.5-turbo",
            auth_token=api_token  # Explicitly pass token
        )
        print("   ✅ Agent created successfully")
        print(f"   Agent auth_token set: {'✅ Yes' if agent.auth_token else '❌ No'}")
        if agent.auth_token:
            print(f"   Agent token preview: {agent.auth_token[:30]}...")
        print()
    except Exception as e:
        print(f"   ❌ Failed to create agent: {e}")
        return False
    
    # Step 3: Test agent context manager (initializes MCP client)
    print("📋 Step 3: Initialize MCP Client via Agent Context")
    print("-" * 80)
    
    try:
        async with agent as initialized_agent:
            print("   ✅ Agent context manager entered successfully")
            print(f"   Client initialized: {'✅ Yes' if initialized_agent.client else '❌ No'}")
            
            if initialized_agent.client:
                print(f"   Client type: {type(initialized_agent.client).__name__}")
                print(f"   Client auth_token set: {'✅ Yes' if initialized_agent.client.auth_token else '❌ No'}")
                if initialized_agent.client.auth_token:
                    print(f"   Client token preview: {initialized_agent.client.auth_token[:30]}...")
                
                # Check if client is connected
                if hasattr(initialized_agent.client, 'session'):
                    print(f"   Client session: {'✅ Connected' if initialized_agent.client.session else '❌ Not connected'}")
            print()
            
            # Step 4: Try to list available tools
            print("📋 Step 4: Check Available Tools")
            print("-" * 80)
            
            if initialized_agent.client and hasattr(initialized_agent.client, 'list_tools'):
                try:
                    tools = await initialized_agent.client.list_tools()
                    print(f"   ✅ Successfully retrieved {len(tools)} tools")
                    print(f"   Sample tools: {[t.name for t in tools[:3]]}")
                    print()
                except Exception as e:
                    print(f"   ❌ Failed to list tools: {e}")
                    print()
            
            # Step 5: Try a simple operation
            print("📋 Step 5: Test Simple Operation (List Users)")
            print("-" * 80)
            
            try:
                result = await initialized_agent.run("List all users in the system")
                print("   ✅ Operation completed!")
                print(f"   Result preview: {str(result)[:200]}...")
                print()
                return True
            except Exception as e:
                print(f"   ❌ Operation failed: {e}")
                print()
                
                # Check if it's an authentication error
                if "401" in str(e) or "unauthorized" in str(e).lower():
                    print("   🔍 This appears to be an AUTHENTICATION ERROR")
                    print("   The token may be:")
                    print("      - Expired (tokens last ~10 minutes)")
                    print("      - Invalid")
                    print("      - Not being passed to the MCP server correctly")
                    print()
                elif "415" in str(e) or "unsupported media type" in str(e).lower():
                    print("   🔍 This appears to be a CONTENT-TYPE ERROR")
                    print("   The MCP server may not be setting Content-Type header")
                    print()
                
                return False
                
    except Exception as e:
        print(f"   ❌ Failed to initialize agent: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_orchestrator_token_passing():
    """Test if token is passed correctly through the orchestrator"""
    
    print("\n")
    print("=" * 80)
    print("🧪 Testing API Token Passing Through Orchestrator")
    print("=" * 80)
    print()
    
    from ai_agents.orchestrator.grc_orchestrator import GRCTaskOrchestrator
    
    api_token = os.getenv("GAPPS_API_TOKEN")
    
    if not api_token:
        print("❌ Skipping orchestrator test - no token available")
        return False
    
    print("📋 Step 1: Create Orchestrator")
    print("-" * 80)
    
    try:
        orchestrator = GRCTaskOrchestrator(
            model_provider="local",
            model_name="gpt-3.5-turbo"
        )
        print("   ✅ Orchestrator created successfully")
        print()
    except Exception as e:
        print(f"   ❌ Failed to create orchestrator: {e}")
        return False
    
    print("📋 Step 2: Test Graph Invocation with Token")
    print("-" * 80)
    print(f"   Passing token: {api_token[:30]}...")
    print()
    
    try:
        # Use the compiled app (graph with checkpointer)
        result = await orchestrator.app.ainvoke(
            {
                "messages": [{"role": "user", "content": "List all users"}],
                "api_token": api_token  # Pass token in state
            },
            config={"configurable": {"thread_id": "test-thread"}}
        )
        
        print("   ✅ Graph invocation completed!")
        print(f"   Result keys: {list(result.keys())}")
        
        # Check messages for token-related errors
        messages = result.get('messages', [])
        print(f"   Total messages: {len(messages)}")
        
        for i, msg in enumerate(messages):
            content = str(msg.content) if hasattr(msg, 'content') else str(msg)
            preview = content[:100] + "..." if len(content) > 100 else content
            print(f"   Message {i+1}: {preview}")
            
            if "token" in content.lower() and ("required" in content.lower() or "error" in content.lower()):
                print(f"   ⚠️  Found token-related error in message {i+1}")
                print(f"   Full error: {content}")
                return False
        
        print()
        return True
        
    except Exception as e:
        print(f"   ❌ Orchestrator failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print()
    print("🚀 Starting Token Passing Tests")
    print()
    
    # Test 1: Direct agent
    success1 = asyncio.run(test_token_passing())
    
    # Test 2: Through orchestrator
    success2 = asyncio.run(test_orchestrator_token_passing())
    
    print()
    print("=" * 80)
    print("📊 Test Results Summary")
    print("=" * 80)
    print(f"   Direct Agent Test: {'✅ PASSED' if success1 else '❌ FAILED'}")
    print(f"   Orchestrator Test: {'✅ PASSED' if success2 else '❌ FAILED'}")
    print()
    
    if not (success1 or success2):
        print("❌ All tests failed - token is NOT being passed correctly")
        sys.exit(1)
    elif success1 and success2:
        print("✅ All tests passed - token IS being passed correctly")
        sys.exit(0)
    else:
        print("⚠️  Some tests passed, some failed - partial success")
        sys.exit(1)
