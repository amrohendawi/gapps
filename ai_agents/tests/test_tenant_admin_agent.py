#!/usr/bin/env python3
"""
Test script for Tenant Admin Agent

Verifies that the agent can:
1. Connect to MCP server
2. Load administrative tools
3. Initialize LangGraph agent
4. Respond to basic queries
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


async def test_agent():
    """Test the Tenant Admin Agent."""
    print("=" * 80)
    print("TENANT ADMIN AGENT - Connection Test")
    print("=" * 80 + "\n")

    # Check environment
    print("📋 Environment Check:")
    print(
        f"   MCP Server: {os.getenv('GAPPS_MCP_SERVER', 'mcp_server_openapi.py (default)')}"
    )
    print(f"   API Token: {'✅ Set' if os.getenv('GAPPS_API_TOKEN') else '❌ Not set'}")

    # Check LLM API key
    provider = os.getenv("AGENT_LLM_PROVIDER", "local")
    if provider == "openai":
        api_key_set = bool(os.getenv("OPENAI_API_KEY"))
        print(f"   OpenAI API Key: {'✅ Set' if api_key_set else '❌ Not set'}")
        if not api_key_set:
            print("\n❌ Error: OPENAI_API_KEY not set")
            print("   Set it with: export OPENAI_API_KEY='your-key-here'")
            return False
    elif provider == "local":
        print("   Using local LLM provider - no API key needed")
    else:
        print(f"   ❌ Unknown LLM provider: {provider}")
        return False

    print()

    # Import here to show any import errors clearly
    try:
        from ai_agents.agents.tenant_admin_agent import TenantAdminAgent
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("\n💡 Make sure all dependencies are installed:")
        print("   pip install langgraph langchain langchain-core")
        return False

    # Try to create and connect the agent
    try:
        print("🔌 Connecting to MCP server and initializing agent...")
        async with TenantAdminAgent(model_provider=provider) as agent:
            print()

            # Test a simple query
            print("🧪 Testing simple query...\n")
            query = "What tools do you have access to? List just the first 5."
            print(f"Query: {query}\n")

            response = await agent.run(query)
            print(f"Agent Response:\n{response}\n")

            print("✅ Agent test passed!")
            return True

    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Make sure the Gapps API is running:")
        print("      docker compose up -d")
        print("   2. Check your authentication credentials")
        print("   3. Verify the LLM API key is valid")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Run the test."""
    print("\n🧪 Starting Tenant Admin Agent Tests...\n")

    success = await test_agent()

    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    if success:
        print("✅ PASS - Agent is working correctly")
        print("\n🎉 You can now use the agent!")
        print("\nNext steps:")
        print("  1. Run the agent: python tenant_admin_agent.py")
        print("  2. Or import it: from tenant_admin_agent import TenantAdminAgent")
        sys.exit(0)
    else:
        print("❌ FAIL - Agent test failed")
        print("\nSee error details above for troubleshooting.")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
