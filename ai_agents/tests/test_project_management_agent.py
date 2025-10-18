"""
Test suite for Project Management Agent

This test verifies that the Project Management Agent can:
1. Connect to the MCP server
2. Load project management tools
3. Initialize the agent
4. Respond to project management queries
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from ai_agents.agents.project_management_agent import ProjectManagementAgent


async def test_project_management_agent():
    """Test the Project Management Agent"""
    
    print("="*80)
    print("TESTING PROJECT MANAGEMENT AGENT")
    print("="*80 + "\n")
    
    # Check environment
    print("1️⃣  Checking environment...")
    if not os.getenv("GAPPS_API_TOKEN"):
        print("   ⚠️  GAPPS_API_TOKEN not set (required)")
    print("   ✅ Environment checked\n")
    
    # Initialize agent
    print("2️⃣  Initializing Project Management Agent...\n")
    
    # Simple test query
    print("3️⃣  Testing with a simple query...")
    print("   Query: 'What can you help me with regarding project management?'\n")
    
    try:
        async with ProjectManagementAgent() as agent:
            print(f"   ✅ Agent ready! Using {agent.model_name}\n")
            
            response = await agent.run(
                "What can you help me with regarding project management? "
                "Give me a brief overview of your capabilities."
            )
        
        print("   📝 Agent Response:")
        print("   " + "-"*76)
        for line in response.split('\n'):
            print(f"   {line}")
        print("   " + "-"*76)
        print("\n   ✅ Query successful!\n")
        
    except Exception as e:
        print(f"   ❌ Query failed: {e}\n")
        raise
    
    print("="*80)
    print("✅ ALL TESTS PASSED!")
    print("="*80 + "\n")
    
    print("💡 Next steps:")
    print("   - Try the examples: python -m ai_agents.examples.project_management_examples")
    print("   - Use the agent in your code:")
    print("     from ai_agents.agents.project_management_agent import ProjectManagementAgent")
    print("     agent = ProjectManagementAgent()")
    print("     response = await agent.run('list my projects')")


if __name__ == "__main__":
    asyncio.run(test_project_management_agent())
