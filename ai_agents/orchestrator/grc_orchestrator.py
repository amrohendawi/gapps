"""
GRC Task Orchestrator using LangGraph Supervisor Pattern

This orchestrator manages three specialized agents:
1. Tenant Admin Agent - User, tenant, session, token management
2. General Resources Agent - Frameworks, controls, policies, risks, vendors, etc.
3. Project Management Agent - Project-specific operations

The orchestrator analyzes GRC tasks, decomposes them into subtasks,
and delegates each subtask to the appropriate specialized agent.
"""

import asyncio
import os
from typing import Annotated, Optional, Literal
from typing_extensions import TypedDict

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END, add_messages
from langgraph.types import Command
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import InjectedState

from ai_agents.agents.tenant_admin_agent import TenantAdminAgent
from ai_agents.agents.general_resources_agent import GeneralResourcesAgent
from ai_agents.agents.project_management_agent import ProjectManagementAgent


# State schema for the orchestrator
class GRCOrchestratorState(TypedDict):
    """State for GRC Task Orchestrator"""

    messages: Annotated[list, add_messages]
    active_agent: Optional[str]
    task_plan: Optional[str]
    subtasks: Optional[list[dict]]
    results: dict[str, any]
    api_token: Optional[str]  # User-provided API authentication token


class GRCTaskOrchestrator:
    """
    LangGraph orchestrator for GRC (Governance, Risk, Compliance) tasks.

    This orchestrator coordinates three specialized agents:
    - TenantAdminAgent: Handles tenant, user, session, and administrative operations
    - GeneralResourcesAgent: Manages frameworks, controls, policies, risks, vendors
    - ProjectManagementAgent: Manages project-specific operations

    The orchestrator:
    1. Analyzes incoming GRC tasks
    2. Creates a task plan and decomposes into subtasks
    3. Delegates each subtask to the appropriate agent
    4. Aggregates results and provides comprehensive responses
    """

    def __init__(
        self,
        model_provider: str = "local",
        model_name: Optional[str] = None,
        temperature: float = 0.7,
    ):
        """
        Initialize the GRC Task Orchestrator.

        Args:
            model_provider: LLM provider ("anthropic", "openai", or "local")
            model_name: Specific model name
            temperature: Model temperature for supervisor decisions
        """
        self.model_provider = model_provider
        self.model_name = model_name or self._get_default_model(model_provider)
        self.temperature = temperature

        # Initialize LLM for supervisor
        self.llm = self._initialize_llm()

        # Initialize agents (will be created on demand)
        self.tenant_admin_agent: Optional[TenantAdminAgent] = None
        self.general_resources_agent: Optional[GeneralResourcesAgent] = None
        self.project_management_agent: Optional[ProjectManagementAgent] = None

        # Build the orchestrator graph
        self.graph = self._build_graph()
        self.checkpointer = MemorySaver()
        self.app = self.graph.compile(checkpointer=self.checkpointer)

    def _get_default_model(self, provider: str) -> str:
        """Get default model name for provider"""
        defaults = {
            "openai": "gpt-4o",
            "local": " openai/gpt-oss-20b",
        }
        return defaults.get(provider, defaults["local"])

    def _initialize_llm(self):
        """Initialize the LLM based on provider"""
        if self.model_provider == "openai":
            return ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature,
            )
        else:  # local
            from pydantic import SecretStr
            base_url = os.getenv("LOCALAI_API_URL", "http://localhost:1234/v1")
            return ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature,
                base_url=base_url,
                api_key=SecretStr("not-needed"),
            )

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph supervisor graph"""
        graph = StateGraph(GRCOrchestratorState)

        # Add nodes
        graph.add_node("planner", self._planner_node)
        graph.add_node("tenant_admin", self._tenant_admin_node)
        graph.add_node("general_resources", self._general_resources_node)
        graph.add_node("project_management", self._project_management_node)
        graph.add_node("aggregator", self._aggregator_node)

        # Add edges
        graph.add_edge(START, "planner")

        # Planner can route to any agent
        graph.add_conditional_edges(
            "planner",
            self._route_task,
            {
                "tenant_admin": "tenant_admin",
                "general_resources": "general_resources",
                "project_management": "project_management",
                "aggregator": "aggregator",
                "end": END,
            },
        )

        # All agents return to planner for next task
        graph.add_edge("tenant_admin", "planner")
        graph.add_edge("general_resources", "planner")
        graph.add_edge("project_management", "planner")

        # Aggregator returns final result
        graph.add_edge("aggregator", END)

        return graph

    async def _planner_node(self, state: GRCOrchestratorState) -> dict:
        """
        Planning node: Analyzes the task and creates a plan with subtasks.

        This node:
        1. Analyzes the user's GRC task
        2. Determines which agents are needed
        3. Breaks down the task into subtasks
        4. Delegates to appropriate agents
        """
        messages = state["messages"]
        last_message = messages[-1].content if messages else ""

        # If we already have subtasks, don't re-plan - just continue execution
        # (This happens when agents return to planner after completing a subtask)
        subtasks = state.get("subtasks", [])
        if subtasks:
            # Just return current state, routing logic will handle next agent
            return {}

        # Create initial plan
        planning_prompt = f"""You are a GRC (Governance, Risk, Compliance) task orchestrator.

Analyze this task and create a plan with subtasks:
Task: {last_message}

Available agents:
1. **tenant_admin**: Manages tenants, users, sessions, authentication, tokens
   - Use for: Creating tenants, managing users, generating tokens, admin operations
   
2. **general_resources**: Manages frameworks, controls, policies, risks, vendors, assessments
   - Use for: Listing frameworks, managing controls, policies, risk assessments, vendor operations
   
3. **project_management**: Manages projects and project-specific operations
   - Use for: Creating projects, adding controls to projects, project evidence, project teams

Create a plan with subtasks. For each subtask, specify:
- agent: which agent should handle it (tenant_admin, general_resources, or project_management)
- description: clear description of what needs to be done
- dependencies: which previous subtasks must complete first (if any)

Response format (JSON):
{{
  "plan_summary": "Brief overview of the plan",
  "subtasks": [
    {{"agent": "agent_name", "description": "Task description", "dependencies": []}},
    ...
  ]
}}

If the task is simple and needs only one agent, create a single subtask.
If no agents are needed (e.g., just informational question), return empty subtasks list.
"""

        response = await self.llm.ainvoke([HumanMessage(content=planning_prompt)])

        # Parse response (in production, use structured output)
        try:
            import json

            # Try to extract JSON from response
            content = response.content
            json_start = content.find("{")
            json_end = content.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                plan_data = json.loads(content[json_start:json_end])
            else:
                # Fallback: create simple plan
                plan_data = {
                    "plan_summary": "Process the request",
                    "subtasks": [
                        {
                            "agent": "general_resources",
                            "description": last_message,
                            "dependencies": [],
                        }
                    ],
                }
        except:
            # Fallback plan
            plan_data = {
                "plan_summary": "Process the request",
                "subtasks": [
                    {
                        "agent": "general_resources",
                        "description": last_message,
                        "dependencies": [],
                    }
                ],
            }

        # Add status to subtasks
        subtasks_with_status = []
        for subtask in plan_data.get("subtasks", []):
            subtasks_with_status.append(
                {
                    **subtask,
                    "status": "pending",
                    "result": None,
                }
            )

        return {
            "task_plan": plan_data.get("plan_summary", ""),
            "subtasks": subtasks_with_status,
            "messages": [
                AIMessage(content=f"📋 Plan: {plan_data.get('plan_summary', '')}")
            ],
        }

    async def _tenant_admin_node(self, state: GRCOrchestratorState) -> dict:
        """Execute subtask using Tenant Admin Agent"""
        subtasks = state.get("subtasks", [])
        api_token = state.get("api_token")

        # Validate token is provided
        if not api_token:
            return {
                "messages": [AIMessage(content="❌ Error: API token is required. Please provide api_token in the graph input.")],
            }

        # Find current pending subtask
        current_task = None
        for i, subtask in enumerate(subtasks):
            if (
                subtask.get("status") == "pending"
                and subtask.get("agent") == "tenant_admin"
            ):
                current_task = subtask
                task_index = i
                break

        if not current_task:
            return {}

        # Execute with Tenant Admin Agent (passing token from state)
        if not self.tenant_admin_agent:
            self.tenant_admin_agent = TenantAdminAgent(
                model_provider=self.model_provider,
                model_name=self.model_name,
                auth_token=api_token,  # Pass user-provided token
            )

        async with self.tenant_admin_agent as agent:
            result = await agent.run(current_task["description"])

        # Update subtask status
        subtasks[task_index]["status"] = "completed"
        subtasks[task_index]["result"] = result

        return {
            "subtasks": subtasks,
            "messages": [AIMessage(content=f"✅ Tenant Admin: {result}")],
            "results": {f"subtask_{task_index}": result},
        }

    async def _general_resources_node(self, state: GRCOrchestratorState) -> dict:
        """Execute subtask using General Resources Agent"""
        subtasks = state.get("subtasks", [])
        api_token = state.get("api_token")

        # Validate token is provided
        if not api_token:
            return {
                "messages": [AIMessage(content="❌ Error: API token is required. Please provide api_token in the graph input.")],
            }

        # Find current pending subtask
        current_task = None
        for i, subtask in enumerate(subtasks):
            if (
                subtask.get("status") == "pending"
                and subtask.get("agent") == "general_resources"
            ):
                current_task = subtask
                task_index = i
                break

        if not current_task:
            return {}

        # Execute with General Resources Agent (passing token from state)
        if not self.general_resources_agent:
            self.general_resources_agent = GeneralResourcesAgent(
                model_provider=self.model_provider,
                model_name=self.model_name,
                auth_token=api_token,  # Pass user-provided token
            )

        async with self.general_resources_agent as agent:
            result = await agent.run(current_task["description"])

        # Update subtask status
        subtasks[task_index]["status"] = "completed"
        subtasks[task_index]["result"] = result

        return {
            "subtasks": subtasks,
            "messages": [AIMessage(content=f"✅ General Resources: {result}")],
            "results": {f"subtask_{task_index}": result},
        }

    async def _project_management_node(self, state: GRCOrchestratorState) -> dict:
        """Execute subtask using Project Management Agent"""
        subtasks = state.get("subtasks", [])
        api_token = state.get("api_token")

        # Validate token is provided
        if not api_token:
            return {
                "messages": [AIMessage(content="❌ Error: API token is required. Please provide api_token in the graph input.")],
            }

        # Find current pending subtask
        current_task = None
        for i, subtask in enumerate(subtasks):
            if (
                subtask.get("status") == "pending"
                and subtask.get("agent") == "project_management"
            ):
                current_task = subtask
                task_index = i
                break

        if not current_task:
            return {}

        # Execute with Project Management Agent (passing token from state)
        if not self.project_management_agent:
            self.project_management_agent = ProjectManagementAgent(
                model_provider=self.model_provider,
                model_name=self.model_name,
                auth_token=api_token,  # Pass user-provided token
            )

        async with self.project_management_agent as agent:
            result = await agent.run(current_task["description"])

        # Update subtask status
        subtasks[task_index]["status"] = "completed"
        subtasks[task_index]["result"] = result

        return {
            "subtasks": subtasks,
            "messages": [AIMessage(content=f"✅ Project Management: {result}")],
            "results": {f"subtask_{task_index}": result},
        }

    async def _aggregator_node(self, state: GRCOrchestratorState) -> dict:
        """Aggregate results from all subtasks and provide final response"""
        subtasks = state.get("subtasks", [])
        plan = state.get("task_plan", "")

        # Collect all results
        results = []
        for i, subtask in enumerate(subtasks):
            if subtask.get("status") == "completed":
                results.append(
                    {
                        "task": subtask["description"],
                        "agent": subtask["agent"],
                        "result": subtask.get("result", ""),
                    }
                )

        # Generate final summary
        summary_prompt = f"""Synthesize the results from multiple GRC agents into a cohesive response.

Original Plan: {plan}

Results from agents:
{chr(10).join([f"{i+1}. {r['agent']}: {r['task']}\n   Result: {r['result']}" for i, r in enumerate(results)])}

Provide a clear, comprehensive summary that:
1. Confirms what was accomplished
2. Highlights key results from each agent
3. Provides any next steps or recommendations
4. Maintains professional GRC terminology
"""

        response = await self.llm.ainvoke([HumanMessage(content=summary_prompt)])

        return {
            "messages": [
                AIMessage(content=f"\n🎯 **Final Summary**\n\n{response.content}")
            ],
        }

    def _route_task(self, state: GRCOrchestratorState) -> str:
        """Route to next agent or aggregator based on subtask status"""
        subtasks = state.get("subtasks", [])
        
        # If no subtasks, end the graph
        if not subtasks:
            return "end"

        # Check if all subtasks are completed
        all_complete = all(t.get("status") == "completed" for t in subtasks)
        if all_complete:
            return "aggregator"

        # Find the next pending subtask and route to its agent
        for subtask in subtasks:
            if subtask.get("status") == "pending":
                agent = subtask.get("agent")
                if agent in ["tenant_admin", "general_resources", "project_management"]:
                    return agent
        
        # If we get here, something went wrong - fallback to end
        return "end"

    async def run(self, task: str, thread_id: str = "default") -> str:
        """
        Execute a GRC task using the orchestrator.

        Args:
            task: The GRC task description
            thread_id: Thread ID for conversation continuity

        Returns:
            str: The final aggregated response
        """
        config = {"configurable": {"thread_id": thread_id}}

        result = await self.app.ainvoke(
            {"messages": [HumanMessage(content=task)]},
            config=config,
        )

        # Return the last message content
        messages = result.get("messages", [])
        if messages:
            return messages[-1].content
        return "No response generated"

    async def stream(self, task: str, thread_id: str = "default"):
        """
        Stream the execution of a GRC task.

        Args:
            task: The GRC task description
            thread_id: Thread ID for conversation continuity

        Yields:
            dict: Chunks of the execution process
        """
        config = {"configurable": {"thread_id": thread_id}}

        async for chunk in self.app.astream(
            {"messages": [HumanMessage(content=task)]},
            config=config,
        ):
            yield chunk


async def demo():
    """Demonstration of the GRC Task Orchestrator"""
    print("=" * 80)
    print("GRC TASK ORCHESTRATOR DEMO")
    print("=" * 80 + "\n")

    orchestrator = GRCTaskOrchestrator()

    # Example complex task that needs multiple agents
    complex_task = """
    I need to set up a new SOC 2 compliance project:
    1. First, list available compliance frameworks to choose the right one
    2. Then create a new project called "SOC 2 Type II Audit Q1 2024"
    3. Add key access control requirements to the project
    4. Show me the project status
    """

    print(f"📝 Task: {complex_task}\n")
    print("🤖 Orchestrator processing...\n")

    try:
        # Stream the execution
        async for chunk in orchestrator.stream(complex_task):
            for node_name, node_output in chunk.items():
                if "messages" in node_output:
                    for msg in node_output["messages"]:
                        if hasattr(msg, "content"):
                            print(f"\n[{node_name}] {msg.content}")

        print("\n" + "=" * 80)
        print("✅ ORCHESTRATION COMPLETE!")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(demo())
