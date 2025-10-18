"""
AI Agents Package for Gapps

A template-based system for creating LangGraph ReAct agents that use the 
Model Context Protocol (MCP) to access Gapps API tools.

Package Structure:
    base/       - Abstract base classes (BaseAgent, BaseClient)
    agents/     - Specialized agent implementations
    clients/    - Specialized MCP client implementations
    templates/  - Copy-paste templates for creating new agents
    examples/   - Usage examples and demonstrations
    tests/      - Test suite
    docs/       - Comprehensive documentation
"""

__version__ = "1.0.0"
__author__ = "Gapps Team"

from ai_agents.base.base_agent import BaseAgent
from ai_agents.base.base_client import BaseClient

__all__ = ["BaseAgent", "BaseClient"]
