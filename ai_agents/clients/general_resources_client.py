#!/usr/bin/env python3
"""
FastMCP Client for General & Supporting Resources Agent

This client provides access to core resources that are not specific to projects or
tenant administration. It handles global-level management of applications, assessments,
controls, deployments, evidence, vendors, policies, and risks.

Agent Scope: AI Agent - General & Supporting Resources
- Manages applications, assessments, controls, deployments, evidence, vendors, policies, risks
- Endpoints: /applications/*, /assessments/*, /controls/*, /deployments/*, /evidence/*,
  /forms/*, /frameworks/*, /policies/*, /risks/*, /subcontrols/*, /vendors/*, utilities

Usage:
    from ai_agents.clients.general_resources_client import GeneralResourcesClient
    
    async with GeneralResourcesClient() as client:
        tools = client.list_available_tools()
        result = await client.call_tool("GET_applications")
"""

import asyncio
from ai_agents.base.base_client import BaseClient


class GeneralResourcesClient(BaseClient):
    """
    A specialized FastMCP client for General & Supporting Resources operations.
    
    This client filters the MCP tools to only include those related to:
    - Applications management
    - Assessments and frameworks
    - Controls and subcontrols
    - Deployments
    - Evidence management
    - Forms and templates
    - Policies
    - Risks
    - Vendors
    - System utilities
    
    Tool Patterns:
        - application: Application CRUD and management
        - assessment: Assessment operations
        - control: Controls and subcontrols
        - deployment: Deployment management
        - evidence: Evidence handling
        - form: Form templates
        - framework: Framework operations
        - policy/policies: Policy management
        - risk: Risk management
        - vendor: Vendor operations
        - subcontrol: Subcontrol management
    
    Example:
        async with GeneralResourcesClient() as client:
            # List all applications
            apps = await client.call_tool("GET_applications")
            
            # Get frameworks
            frameworks = await client.call_tool("GET_frameworks")
            
            # List available tools
            client.print_available_tools()
    """
    
    # Tool patterns for filtering (case-insensitive substring matching)
    TOOL_PATTERNS = [
        "application",   # /applications/*
        "assessment",    # /assessments/*
        "control",       # /controls/*
        "deployment",    # /deployments/*
        "evidence",      # /evidence/*
        "form",          # /forms/*
        "framework",     # /frameworks/*
        "policy",        # /policies/*
        "policies",      # Alternative policy endpoints
        "risk",          # /risks/*
        "subcontrol",    # /subcontrols/*
        "vendor",        # /vendors/*
    ]
    
    def get_client_name(self) -> str:
        """Return descriptive name for this client."""
        return "General & Supporting Resources"


async def main():
    """Example usage of the GeneralResourcesClient."""
    print("\n" + "="*80)
    print("GENERAL & SUPPORTING RESOURCES CLIENT - Example Usage")
    print("="*80 + "\n")
    
    async with GeneralResourcesClient() as client:
        print(f"✅ Connected to MCP server")
        print(f"📋 Loaded {len(client._available_tools)} general resource tools\n")
        
        # Display available tools
        print("Available Tools:")
        print("-" * 80)
        client.print_available_tools()
        
        # Example: Call a tool
        print("\n" + "="*80)
        print("Example: Calling GET_frameworks")
        print("="*80)
        try:
            result = await client.call_tool("GET_frameworks")
            print(f"✅ Success: {result}")
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
