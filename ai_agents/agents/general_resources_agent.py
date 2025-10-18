#!/usr/bin/env python3
"""
LangGraph Agent for General & Supporting Resources

This agent manages core resources that are not specific to projects or tenant administration.
It handles Applications, Assessments, Controls, Deployments, Evidence, Vendors, Policies,
and Risks at a global level.

Features:
- Natural language interface for resource management
- Intelligent tool selection and orchestration
- Conversation memory for multi-turn interactions
- Safe execution with confirmation for destructive actions

Usage:
    from ai_agents.agents.general_resources_agent import GeneralResourcesAgent

    async with GeneralResourcesAgent() as agent:
        response = await agent.run("List all frameworks")
        print(response)
"""

import asyncio
import os
from ai_agents.base.base_agent import BaseAgent
from ai_agents.clients.general_resources_client import GeneralResourcesClient


class GeneralResourcesAgent(BaseAgent):
    """
    LangGraph-powered agent for General & Supporting Resources.
    
    This agent provides intelligent access to core system resources including:
    - Applications: Manage application inventory and metadata
    - Assessments: Handle security assessments and evaluations
    - Controls: Manage security controls and subcontrols
    - Deployments: Track system deployments
    - Evidence: Manage evidence and documentation
    - Forms: Work with form templates
    - Frameworks: Access compliance frameworks
    - Policies: Manage organizational policies
    - Risks: Track and manage risks
    - Vendors: Manage vendor information
    
    The agent uses LangGraph's ReAct pattern to intelligently select and use
    the appropriate tools based on user queries.
    
    Example:
        async with GeneralResourcesAgent() as agent:
            # Interactive mode
            await agent.run_interactive()
            
            # Single query
            response = await agent.run("Show me all available frameworks")
            
            # Streaming response
            async for chunk in agent.stream("List applications"):
                print(chunk, end="", flush=True)
    """
    
    def get_mcp_client(self):
        """Return the specialized MCP client for this agent."""
        return GeneralResourcesClient()
    
    def get_default_prompt(self) -> str:
        """Return the default system prompt for this agent."""
        return """You are a helpful AI assistant for managing General & Supporting Resources in the Gapps system.

You have access to tools for managing:

**Applications:**
- List, create, update, and delete applications
- Manage application metadata and configurations
- Track application security posture

**Assessments:**
- Create and manage security assessments
- Track assessment progress and results
- Generate assessment reports

**Controls & Subcontrols:**
- Manage security controls and control families
- Work with control implementations
- Track control effectiveness

**Deployments:**
- Monitor system deployments
- Track deployment status and history
- Manage deployment configurations

**Evidence:**
- Upload and organize evidence
- Link evidence to controls and assessments
- Manage evidence lifecycle

**Forms:**
- Work with form templates
- Create and manage custom forms
- Process form submissions

**Frameworks:**
- Access compliance frameworks (ISO 27001, NIST, SOC2, etc.)
- Map controls to framework requirements
- Track framework compliance

**Policies:**
- Manage organizational policies
- Track policy versions and approvals
- Link policies to controls

**Risks:**
- Identify and track risks
- Assess risk severity and impact
- Manage risk mitigation strategies

**Vendors:**
- Manage vendor relationships
- Track vendor security posture
- Handle vendor assessments

**Guidelines:**
1. Always confirm before performing destructive operations (delete, update)
2. Provide clear, concise responses with relevant details
3. When listing items, organize them logically and include key information
4. For complex queries, break down the steps and explain your approach
5. If you're unsure about something, ask for clarification
6. Suggest related actions when appropriate

**Response Format:**
- Use clear headings and bullet points
- Include relevant IDs and names
- Highlight important information
- Provide actionable next steps when applicable

Remember: You're managing critical security and compliance resources. Be accurate and thorough.
"""
    
    def get_agent_name(self) -> str:
        """Return the name of this agent."""
        return "General & Supporting Resources Agent"


async def main():
    """Example usage of the GeneralResourcesAgent."""
    print("\n" + "="*80)
    print("GENERAL & SUPPORTING RESOURCES AGENT - Interactive Mode")
    print("="*80 + "\n")
    
    print("Starting agent...")
    print("Type 'quit' or 'exit' to end the session.\n")
    
    async with GeneralResourcesAgent() as agent:
        await agent.run_interactive()


if __name__ == "__main__":
    asyncio.run(main())
