#!/usr/bin/env python3
"""
LangGraph Agent for Tenant & User Administration

This agent uses LangGraph's ReAct pattern to intelligently manage tenants, users,
sessions, and administrative tasks using MCP tools from the Gapps API.

Features:
- Natural language interface for admin tasks
- Intelligent tool selection and orchestration
- Conversation memory for multi-turn interactions
- Safe execution with confirmation for destructive actions

Usage:
    from tenant_admin_agent import TenantAdminAgent

    async with TenantAdminAgent() as agent:
        response = await agent.run("Create a new tenant called 'Acme Corp'")
        print(response)
"""

import asyncio
import os
from ai_agents.base.base_agent import BaseAgent
from ai_agents.clients.tenant_admin_client import TenantAdminClient


class TenantAdminAgent(BaseAgent):
    """
    LangGraph-powered agent for Tenant & User Administration.

    This agent uses the ReAct (Reasoning + Acting) pattern to handle administrative
    tasks through natural language interactions. It automatically selects and calls
    the appropriate MCP tools based on user requests.

    Inherits from BaseAgent and provides:
    - TenantAdminClient for MCP tool access
    - Specialized system prompt for tenant/user administration
    """

    def get_mcp_client(self):
        """Create and return the TenantAdminClient instance."""
        return TenantAdminClient(
            server_url=self.server_url,
            auth_token=self.auth_token
        )

    def get_default_prompt(self) -> str:
        """Return the default system prompt for tenant administration."""
        return """You are a Tenant & User Administration Agent for the Gapps governance platform.

**Your Responsibilities:**
- Manage tenants (create, view, update, delete organizations)
- Manage users (create, view, update, delete, assign roles)  
- Handle authentication, sessions, and access tokens
- Perform administrative tasks and system configuration

**Guidelines:**
1. Always confirm before performing destructive operations (delete, major updates)
2. Provide clear, structured responses with relevant details
3. Use appropriate tools to gather information before making decisions
4. If you're unsure about a parameter or action, ask for clarification
5. Present information in a user-friendly format (tables, lists, etc.)
6. Handle errors gracefully and provide helpful error messages

**Tool Usage:**
- GET tools: Retrieve information (safe, no side effects)
- POST tools: Create new resources (requires data validation)
- PUT tools: Update existing resources (verify resource exists first)
- DELETE tools: Remove resources (always confirm with user first)

**Response Format:**
- Use clear headings and bullet points
- Show IDs and key details when creating/updating resources
- Summarize actions taken and results
- Suggest next steps when appropriate

Remember: You're managing critical business data. Be accurate, cautious, and helpful!
"""

    def get_agent_name(self) -> str:
        """Return the agent name for logging."""
        return "Tenant & User Administration Agent"


async def main():
    """Example usage of the Tenant Admin Agent."""
    print("\n🚀 Tenant & User Administration Agent - Demo\n")

    # Check for required API keys
    provider = os.getenv("AGENT_LLM_PROVIDER", "local")

    if provider == "openai" and not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("Set it with: export OPENAI_API_KEY='your-key-here'")
        return

    # Create and run agent
    async with TenantAdminAgent(model_provider=provider) as agent:
        # Example interactions
        examples = [
            "List all available administrative tools you have access to",
            "What tenants exist in the system?",
            "How many users are there?",
        ]

        print("Running example queries:\n")

        for i, query in enumerate(examples, 1):
            print(f"\n{'='*80}")
            print(f"Example {i}: {query}")
            print("=" * 80 + "\n")

            response = await agent.run(query)
            print(f"Agent: {response}\n")

        # Optional: Start interactive mode
        start_interactive = (
            input("\nWould you like to start interactive mode? (y/n): ")
            .strip()
            .lower()
        )
        if start_interactive == "y":
            await agent.run_interactive()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
