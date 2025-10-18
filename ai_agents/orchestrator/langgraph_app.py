"""
LangGraph Studio Entry Point for GRC Task Orchestrator

This file exposes the orchestrator graph for LangGraph Studio.
"""

from ai_agents.orchestrator.grc_orchestrator import GRCTaskOrchestrator

# Create orchestrator instance (Studio will provide its own checkpointer)
orchestrator = GRCTaskOrchestrator()

# Build the graph without running initialization
orchestrator._build_graph()

# Export the compiled graph for LangGraph Studio  
graph = orchestrator.graph
