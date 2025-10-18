#!/usr/bin/env python3
"""
Usage Examples for General Resources Agent

This file demonstrates various ways to use the General Resources Agent
for managing applications, assessments, controls, frameworks, policies,
risks, vendors, and other core resources.
"""

import asyncio
from ai_agents.agents.general_resources_agent import GeneralResourcesAgent


async def example_1_list_frameworks():
    """Example 1: List available compliance frameworks."""
    print("\n" + "="*80)
    print("Example 1: List Available Frameworks")
    print("="*80 + "\n")
    
    async with GeneralResourcesAgent() as agent:
        response = await agent.run("List all available compliance frameworks")
        print(response)


async def example_2_manage_applications():
    """Example 2: Work with applications."""
    print("\n" + "="*80)
    print("Example 2: Application Management")
    print("="*80 + "\n")
    
    async with GeneralResourcesAgent() as agent:
        response = await agent.run("Show me information about managing applications")
        print(response)


async def example_3_list_controls():
    """Example 3: View security controls."""
    print("\n" + "="*80)
    print("Example 3: Security Controls")
    print("="*80 + "\n")
    
    async with GeneralResourcesAgent() as agent:
        response = await agent.run("What security controls are available?")
        print(response)


async def example_4_vendor_management():
    """Example 4: Vendor operations."""
    print("\n" + "="*80)
    print("Example 4: Vendor Management")
    print("="*80 + "\n")
    
    async with GeneralResourcesAgent() as agent:
        response = await agent.run("How can I manage vendors in the system?")
        print(response)


async def example_5_risk_management():
    """Example 5: Risk tracking."""
    print("\n" + "="*80)
    print("Example 5: Risk Management")
    print("="*80 + "\n")
    
    async with GeneralResourcesAgent() as agent:
        response = await agent.run("Explain how to work with risks")
        print(response)


async def example_6_policy_operations():
    """Example 6: Policy management."""
    print("\n" + "="*80)
    print("Example 6: Policy Management")
    print("="*80 + "\n")
    
    async with GeneralResourcesAgent() as agent:
        response = await agent.run("What can I do with policies?")
        print(response)


async def example_7_evidence_handling():
    """Example 7: Evidence management."""
    print("\n" + "="*80)
    print("Example 7: Evidence Management")
    print("="*80 + "\n")
    
    async with GeneralResourcesAgent() as agent:
        response = await agent.run("How do I manage evidence in the system?")
        print(response)


async def example_8_assessments():
    """Example 8: Security assessments."""
    print("\n" + "="*80)
    print("Example 8: Security Assessments")
    print("="*80 + "\n")
    
    async with GeneralResourcesAgent() as agent:
        response = await agent.run("Tell me about managing assessments")
        print(response)


async def example_9_streaming_response():
    """Example 9: Stream responses in real-time."""
    print("\n" + "="*80)
    print("Example 9: Streaming Response")
    print("="*80 + "\n")
    
    async with GeneralResourcesAgent() as agent:
        print("Streaming response: ", end="", flush=True)
        async for chunk in agent.stream("What resources can you help me with?"):
            print(chunk, end="", flush=True)
        print("\n")


async def example_10_multi_turn_conversation():
    """Example 10: Multi-turn conversation with memory."""
    print("\n" + "="*80)
    print("Example 10: Multi-Turn Conversation")
    print("="*80 + "\n")
    
    async with GeneralResourcesAgent() as agent:
        # First query
        print("User: Tell me about frameworks\n")
        response1 = await agent.run("Tell me about frameworks", thread_id="conversation-1")
        print(f"Agent: {response1}\n")
        
        # Follow-up query (uses memory from previous turn)
        print("User: Which one is most comprehensive?\n")
        response2 = await agent.run("Which one is most comprehensive?", thread_id="conversation-1")
        print(f"Agent: {response2}\n")


async def interactive_menu():
    """Interactive menu for running examples."""
    examples = {
        "1": ("List Frameworks", example_1_list_frameworks),
        "2": ("Application Management", example_2_manage_applications),
        "3": ("Security Controls", example_3_list_controls),
        "4": ("Vendor Management", example_4_vendor_management),
        "5": ("Risk Management", example_5_risk_management),
        "6": ("Policy Management", example_6_policy_operations),
        "7": ("Evidence Management", example_7_evidence_handling),
        "8": ("Security Assessments", example_8_assessments),
        "9": ("Streaming Response", example_9_streaming_response),
        "10": ("Multi-Turn Conversation", example_10_multi_turn_conversation),
    }
    
    print("\n" + "="*80)
    print("GENERAL RESOURCES AGENT - Examples Menu")
    print("="*80)
    print("\nAvailable Examples:")
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    print("  0. Run all examples")
    print("  q. Quit")
    print("="*80)
    
    choice = input("\nSelect an example (0-10, q): ").strip()
    
    if choice == "q":
        print("Goodbye!")
        return
    elif choice == "0":
        print("\nRunning all examples...\n")
        for name, func in examples.values():
            try:
                await func()
                await asyncio.sleep(1)  # Brief pause between examples
            except KeyboardInterrupt:
                print("\n\nExamples interrupted by user")
                return
            except Exception as e:
                print(f"\n❌ Error in {name}: {e}\n")
    elif choice in examples:
        name, func = examples[choice]
        try:
            await func()
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
    else:
        print("Invalid choice. Please try again.")


async def main():
    """Main entry point."""
    await interactive_menu()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
