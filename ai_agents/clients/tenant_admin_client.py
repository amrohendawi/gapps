#!/usr/bin/env python3
"""
FastMCP Client for Tenant & User Administration Agent

This client provides a simplified interface to interact with the Gapps administrative
endpoints through the FastMCP server. It filters the available tools to only those related
to tenant and user administration operations.

Agent Scope: AI Agent - Tenant & User Administration
- Manages tenants, users, roles, sessions, and authentication
- Endpoints: /admin/*, /session/*, /tenants/*, /token, /users/*

Usage:
    python tenant_admin_client.py
    
Or import as a module:
    from tenant_admin_client import TenantAdminClient
    
    async with TenantAdminClient() as admin_client:
        tools = admin_client.list_available_tools()
"""

import asyncio
from ai_agents.base.base_client import BaseClient


class TenantAdminClient(BaseClient):
    """
    A specialized FastMCP client for Tenant & User Administration operations.
    
    This client connects to the Gapps MCP server and provides a focused interface
    for administrative operations, filtering out non-administrative tools.
    
    Inherits from BaseClient and provides:
    - Tool filtering for admin, session, tenant, user, and token endpoints
    - Specialized display name for logging
    """
    
    # Define the tool patterns we're interested in for administration
    # FastMCP OpenAPI creates tool names like: GET_adminusers, POST_sessionlogin
    # We filter for tools that contain these keywords in their name
    TOOL_PATTERNS = [
        "admin",      # Matches /admin/* endpoints
        "session",    # Matches /session/* endpoints  
        "tenant",     # Matches /tenants/* endpoints
        "user",       # Matches /users/* endpoints
        "token",      # Matches /token endpoint
    ]
    
    def get_client_name(self) -> str:
        """Return the client name for logging."""
        return "Tenant & User Administration"


async def main():
    """Example usage of the Tenant Admin Client."""
    print("🔧 Tenant & User Administration Client - Example Usage\n")
    
    # Create and connect the client
    async with TenantAdminClient() as admin_client:
        # List available tools
        tools = admin_client.list_available_tools()
        print(f"Found {len(tools)} administrative tools\n")
        
        # Print detailed tool information
        admin_client.print_available_tools()
        
        # Example: Call a specific tool (if needed)
        # result = await admin_client.call_tool("GET_adminusers")
        # print(f"Result: {result}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
