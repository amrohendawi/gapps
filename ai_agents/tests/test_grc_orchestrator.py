"""
Test suite for GRC Task Orchestrator

Tests the multi-agent orchestration system.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from ai_agents.orchestrator.grc_orchestrator import GRCTaskOrchestrator


async def test_simple_task():
    """Test orchestrator with a simple single-agent task"""
    print("\n" + "="*80)
    print("TEST 1: Simple Single-Agent Task")
    print("="*80 + "\n")
    
    orchestrator = GRCTaskOrchestrator()
    
    task = "List all available compliance frameworks"
    print(f"📝 Task: {task}\n")
    
    try:
        result = await orchestrator.run(task)
        print(f"\n✅ Result:\n{result}\n")
        return True
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
        return False


async def test_multi_agent_task():
    """Test orchestrator with a complex multi-agent task"""
    print("\n" + "="*80)
    print("TEST 2: Complex Multi-Agent Task")
    print("="*80 + "\n")
    
    orchestrator = GRCTaskOrchestrator()
    
    task = """
    Help me set up compliance tracking:
    1. List available frameworks
    2. Create a project for ISO 27001 compliance
    3. Show me controls for access management
    """
    
    print(f"📝 Task: {task}\n")
    print("🔄 Streaming execution...\n")
    
    try:
        async for chunk in orchestrator.stream(task):
            for node_name, node_output in chunk.items():
                if node_name not in ["__start__", "__end__"]:
                    print(f"\n[{node_name}] Processing...")
                    
                    if "messages" in node_output:
                        for msg in node_output["messages"]:
                            if hasattr(msg, 'content') and msg.content:
                                print(f"  {msg.content[:200]}...")
        
        print("\n✅ Multi-agent orchestration completed!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
        return False


async def test_orchestrator_planning():
    """Test the orchestrator's planning capabilities"""
    print("\n" + "="*80)
    print("TEST 3: Orchestrator Planning")
    print("="*80 + "\n")
    
    orchestrator = GRCTaskOrchestrator()
    
    task = "I need to audit our vendor risk management process"
    print(f"📝 Task: {task}\n")
    print("📋 Testing task decomposition and agent selection...\n")
    
    try:
        result = await orchestrator.run(task)
        print(f"\n✅ Result:\n{result}\n")
        return True
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("="*80)
    print("GRC TASK ORCHESTRATOR - TEST SUITE")
    print("="*80)
    
    # Check environment
    print("\n📋 Environment Check:")
    print(f"   GAPPS_API_TOKEN: {'✅ Set' if os.getenv('GAPPS_API_TOKEN') else '⚠️  Not set'}")
    print(f"   LLM Provider: {os.getenv('AGENT_LLM_PROVIDER', 'local')}")
    
    results = []
    
    # Run tests
    print("\n" + "="*80)
    print("RUNNING TESTS")
    print("="*80)
    
    results.append(("Simple Task", await test_simple_task()))
    results.append(("Multi-Agent Task", await test_multi_agent_task()))
    results.append(("Planning Test", await test_orchestrator_planning()))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80 + "\n")
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    all_passed = all(passed for _, passed in results)
    
    print("\n" + "="*80)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED")
    print("="*80 + "\n")
    
    print("💡 Next steps:")
    print("   - Try the orchestrator: python -m ai_agents.orchestrator.grc_orchestrator")
    print("   - Use in your code:")
    print("     from ai_agents.orchestrator import GRCTaskOrchestrator")
    print("     orchestrator = GRCTaskOrchestrator()")
    print("     result = await orchestrator.run('your GRC task')")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user\n")
