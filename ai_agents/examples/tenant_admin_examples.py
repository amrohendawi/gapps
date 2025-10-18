#!/usr/bin/env python3
"""
Tenant & User Administration Agent - Usage Examples

This script demonstrates various ways to use the Tenant Admin Agent
for different administrative tasks and integration patterns.

Examples:
1. Basic queries
2. Tenant operations
3. User management
4. Multi-step workflows
5. Error handling
6. Custom configuration
7. Streaming responses
8. Interactive mode
"""

import asyncio
import os
from tenant_admin_agent import TenantAdminAgent


async def example_basic_queries():
    """Example 1: Basic information queries."""
    print("\n" + "="*80)
    print("EXAMPLE 1: Basic Queries")
    print("="*80 + "\n")
    
    async with TenantAdminAgent() as agent:
        queries = [
            "What administrative capabilities do you have?",
            "How many tools do you have access to?",
            "What endpoints can you work with?",
        ]
        
        for query in queries:
            print(f"Query: {query}")
            response = await agent.run(query)
            print(f"Response: {response}\n")


async def example_tenant_operations():
    """Example 2: Tenant management operations."""
    print("\n" + "="*80)
    print("EXAMPLE 2: Tenant Operations")
    print("="*80 + "\n")
    
    async with TenantAdminAgent() as agent:
        # List existing tenants
        print("📋 Listing existing tenants...")
        response = await agent.run("List all tenants in the system")
        print(f"Response: {response}\n")
        
        # Get tenant count
        print("📊 Getting tenant count...")
        response = await agent.run("How many tenants are there?")
        print(f"Response: {response}\n")


async def example_user_management():
    """Example 3: User management operations."""
    print("\n" + "="*80)
    print("EXAMPLE 3: User Management")
    print("="*80 + "\n")
    
    async with TenantAdminAgent() as agent:
        # List users
        print("👥 Listing users...")
        response = await agent.run("Show me all users")
        print(f"Response: {response}\n")
        
        # User information
        print("ℹ️  Getting user info...")
        response = await agent.run("Tell me about the users in the system")
        print(f"Response: {response}\n")


async def example_multi_step_workflow():
    """Example 4: Multi-step workflow."""
    print("\n" + "="*80)
    print("EXAMPLE 4: Multi-Step Workflow")
    print("="*80 + "\n")
    
    async with TenantAdminAgent() as agent:
        # Complex request requiring multiple tools
        print("🔄 Executing multi-step workflow...")
        response = await agent.run(
            "First check if a tenant called 'Example Corp' exists. "
            "If not, tell me what tenants are available."
        )
        print(f"Response: {response}\n")


async def example_error_handling():
    """Example 5: Error handling and recovery."""
    print("\n" + "="*80)
    print("EXAMPLE 5: Error Handling")
    print("="*80 + "\n")
    
    async with TenantAdminAgent() as agent:
        try:
            # Intentional invalid request
            print("❌ Attempting invalid operation...")
            response = await agent.run("Delete tenant with ID 'nonexistent-123'")
            print(f"Response: {response}\n")
        except Exception as e:
            print(f"Caught exception: {e}\n")


async def example_custom_configuration():
    """Example 6: Custom agent configuration."""
    print("\n" + "="*80)
    print("EXAMPLE 6: Custom Configuration")
    print("="*80 + "\n")
    
    custom_prompt = """You are a strict administrative agent.
    
    Rules:
    1. Always list available options before performing actions
    2. Confirm destructive operations twice
    3. Provide detailed explanations for each step
    4. Use formal language
    """
    
    async with TenantAdminAgent(
        model_provider="anthropic",
        temperature=0,  # Completely deterministic
        custom_prompt=custom_prompt,
        thread_id="custom_thread"
    ) as agent:
        print("🔧 Using custom-configured agent...")
        response = await agent.run("What tenants exist?")
        print(f"Response: {response}\n")


async def example_streaming_responses():
    """Example 7: Streaming responses for real-time output."""
    print("\n" + "="*80)
    print("EXAMPLE 7: Streaming Responses")
    print("="*80 + "\n")
    
    async with TenantAdminAgent() as agent:
        print("📡 Streaming response...\n")
        print("Agent: ", end="", flush=True)
        
        response_text = ""
        async for token in agent.stream("List the first 3 tenants"):
            if token and token != response_text:
                new_text = token[len(response_text):]
                print(new_text, end="", flush=True)
                response_text = token
        
        print("\n")


async def example_session_management():
    """Example 8: Session and authentication queries."""
    print("\n" + "="*80)
    print("EXAMPLE 8: Session Management")
    print("="*80 + "\n")
    
    async with TenantAdminAgent() as agent:
        # Check active sessions
        print("🔐 Checking active sessions...")
        response = await agent.run("How many active sessions are there?")
        print(f"Response: {response}\n")


async def example_conversation_context():
    """Example 9: Multi-turn conversation with context."""
    print("\n" + "="*80)
    print("EXAMPLE 9: Conversation Context")
    print("="*80 + "\n")
    
    async with TenantAdminAgent(thread_id="conversation_example") as agent:
        # First turn
        print("Turn 1:")
        print("You: List all tenants")
        response1 = await agent.run("List all tenants")
        print(f"Agent: {response1}\n")
        
        # Second turn - agent remembers previous context
        print("Turn 2:")
        print("You: How many were there?")  # Refers to previous question
        response2 = await agent.run("How many were there?")
        print(f"Agent: {response2}\n")


async def example_openai_provider():
    """Example 10: Using OpenAI instead of Anthropic."""
    print("\n" + "="*80)
    print("EXAMPLE 10: OpenAI Provider")
    print("="*80 + "\n")
    
    # Check if OpenAI key is available
    if not os.getenv("OPENAI_API_KEY"):
        print("⏭️  Skipping - OPENAI_API_KEY not set\n")
        return
    
    async with TenantAdminAgent(
        model_provider="openai",
        model_name="gpt-4o-mini"
    ) as agent:
        print("🤖 Using OpenAI GPT-4...")
        response = await agent.run("What tenants exist?")
        print(f"Response: {response}\n")


async def run_all_examples():
    """Run all examples in sequence."""
    examples = [
        ("Basic Queries", example_basic_queries),
        ("Tenant Operations", example_tenant_operations),
        ("User Management", example_user_management),
        ("Multi-Step Workflow", example_multi_step_workflow),
        ("Error Handling", example_error_handling),
        ("Custom Configuration", example_custom_configuration),
        ("Streaming Responses", example_streaming_responses),
        ("Session Management", example_session_management),
        ("Conversation Context", example_conversation_context),
        ("OpenAI Provider", example_openai_provider),
    ]
    
    print("\n🚀 Tenant Admin Agent - Usage Examples")
    print(f"\nRunning {len(examples)} examples...\n")
    
    for i, (name, example_func) in enumerate(examples, 1):
        try:
            print(f"\n{'='*80}")
            print(f"Running Example {i}/{len(examples)}: {name}")
            print(f"{'='*80}")
            await example_func()
        except Exception as e:
            print(f"\n❌ Error in {name}: {e}")
            import traceback
            traceback.print_exc()
        
        # Pause between examples
        if i < len(examples):
            await asyncio.sleep(1)
    
    print("\n" + "="*80)
    print("✅ All examples completed!")
    print("="*80 + "\n")


async def interactive_menu():
    """Interactive menu to run specific examples."""
    examples = {
        "1": ("Basic Queries", example_basic_queries),
        "2": ("Tenant Operations", example_tenant_operations),
        "3": ("User Management", example_user_management),
        "4": ("Multi-Step Workflow", example_multi_step_workflow),
        "5": ("Error Handling", example_error_handling),
        "6": ("Custom Configuration", example_custom_configuration),
        "7": ("Streaming Responses", example_streaming_responses),
        "8": ("Session Management", example_session_management),
        "9": ("Conversation Context", example_conversation_context),
        "10": ("OpenAI Provider", example_openai_provider),
        "all": ("Run All Examples", run_all_examples),
    }
    
    print("\n" + "="*80)
    print("TENANT ADMIN AGENT - EXAMPLE MENU")
    print("="*80 + "\n")
    
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    
    print("\n  q. Quit\n")
    
    while True:
        choice = input("Select an example (or 'q' to quit): ").strip().lower()
        
        if choice == 'q':
            print("\n👋 Goodbye!\n")
            break
        
        if choice in examples:
            name, func = examples[choice]
            try:
                await func()
            except Exception as e:
                print(f"\n❌ Error: {e}\n")
                import traceback
                traceback.print_exc()
        else:
            print("\n❌ Invalid choice. Please try again.\n")


async def main():
    """Main entry point."""
    import sys
    
    # Check environment
    if not os.getenv("GAPPS_API_TOKEN"):
        print("❌ Error: GAPPS_API_TOKEN not set")
        print("Get token via: curl -X POST http://localhost:8000/login -H 'Content-Type: application/json' -d '{\"email\":\"admin@example.com\",\"password\":\"your_password\"}'")
        print("Then set it with: export GAPPS_API_TOKEN='your-token-here'")
        return
    
    provider = os.getenv("AGENT_LLM_PROVIDER", "local")
    if provider == "openai" and not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not set")
        print("Set it with: export OPENAI_API_KEY='your-key'")
        return
    
    # Determine mode
    if len(sys.argv) > 1:
        if sys.argv[1] == "--all":
            await run_all_examples()
        elif sys.argv[1] == "--interactive":
            await interactive_menu()
        else:
            print(f"Unknown argument: {sys.argv[1]}")
            print("Usage: python tenant_admin_examples.py [--all|--interactive]")
    else:
        # Default: show menu
        await interactive_menu()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  Interrupted by user\n")
    except Exception as e:
        print(f"\n\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
