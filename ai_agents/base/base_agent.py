#!/usr/bin/env python3
"""
Base Agent Class for LangGraph-powered MCP Agents

This module provides a reusable base class for creating specialized agents
that use LangGraph's ReAct pattern with MCP tools from the Gapps API.

The base class handles:
- LLM initialization (Anthropic, OpenAI, or local models)
- MCP tool conversion to LangChain format
- ReAct agent creation with checkpointing
- Conversation management and memory
- Streaming and interactive modes

To create a new specialized agent:
1. Subclass BaseAgent
2. Implement get_mcp_client() to return your specialized MCP client
3. Override get_default_prompt() to provide your agent's system prompt
4. Optionally override get_agent_name() for logging

Example:
    class MyCustomAgent(BaseAgent):
        def get_mcp_client(self):
            return MyCustomMCPClient(
                server_url=self.server_url,
                auth_token=self.auth_token
            )

        def get_default_prompt(self) -> str:
            return "You are a helpful assistant for..."
"""

import asyncio
import os
from abc import ABC, abstractmethod
from typing import Optional, AsyncIterator, Any
from pydantic import SecretStr
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import StructuredTool


class BaseAgent(ABC):
    """
    Abstract base class for LangGraph-powered MCP agents.

    This class provides the common infrastructure for creating specialized agents
    that work with different MCP tool sets. Subclasses must implement methods
    to provide their specific MCP client and system prompt.

    Attributes:
        client: MCP client instance (provided by subclass)
        agent: LangGraph ReAct agent instance
        config (RunnableConfig): Configuration for agent execution
        llm: Language model instance (ChatAnthropic, ChatOpenAI, or local)
        checkpointer: MemorySaver for conversation continuity
    """

    def __init__(
        self,
        model_provider: str = "local",
        model_name: Optional[str] = None,
        temperature: float = 0,
        max_tokens: int = 4000,
        server_url: Optional[str] = None,
        auth_token: Optional[str] = None,
        custom_prompt: Optional[str] = None,
        thread_id: str = "default",
        recursion_limit: int = 30,
    ):
        """
        Initialize the Base Agent.

        Args:
            model_provider: LLM provider ("anthropic", "openai", or "local")
            model_name: Specific model name (defaults based on provider)
            temperature: Model temperature (0 for deterministic)
            max_tokens: Maximum tokens in response
            server_url: MCP server URL or script path
            auth_token: API authentication token (REQUIRED for API access)
            custom_prompt: Custom system prompt (overrides get_default_prompt())
            thread_id: Thread ID for conversation continuity
            recursion_limit: Maximum tool call depth
        """
        self.client: Optional[Any] = None
        self.agent = None
        self.checkpointer = MemorySaver()

        # Store configuration
        self.model_provider = model_provider
        self.model_name = model_name or self._get_default_model(model_provider)
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.server_url = server_url
        self.auth_token = auth_token  # Token is now required and passed from orchestrator
        self.prompt = custom_prompt or self.get_default_prompt()
        self.base_url = os.getenv("LOCALAI_API_URL", "http://localhost:1234/v1")

        # Agent configuration
        self.config = RunnableConfig(
            recursion_limit=recursion_limit, configurable={"thread_id": thread_id}
        )

        # LLM instance (will be initialized in __aenter__)
        self.llm = None

    @abstractmethod
    def get_mcp_client(self):
        """
        Create and return the MCP client instance for this agent.

        This method must be implemented by subclasses to provide their
        specialized MCP client (e.g., TenantAdminClient, ProjectManagementClient).

        Returns:
            MCP client instance with server_url and auth_token configured

        Example:
            def get_mcp_client(self):
                return TenantAdminClient(
                    server_url=self.server_url,
                    auth_token=self.auth_token
                )
        """
        pass

    @abstractmethod
    def get_default_prompt(self) -> str:
        """
        Return the default system prompt for this agent.

        This method must be implemented by subclasses to provide their
        agent-specific instructions and guidelines.

        Returns:
            System prompt string with agent instructions

        Example:
            def get_default_prompt(self) -> str:
                return "You are a Project Management Agent..."
        """
        pass

    def get_agent_name(self) -> str:
        """
        Return the agent name for logging and display.

        Subclasses can override this to provide a custom name.

        Returns:
            Agent name string
        """
        return self.__class__.__name__

    def _get_default_model(self, provider: str) -> str:
        """Get default model name for provider"""
        defaults = {
            "local": "openai/gpt-oss-20b",  # Compatible with LocalAI
            "openai": "gpt-4",
        }
        return defaults.get(provider, "openai/gpt-oss-20b")

    def _convert_mcp_tools_to_langchain(self, mcp_tools: list) -> list:
        """
        Convert MCP tools to LangChain StructuredTool objects.

        Args:
            mcp_tools: List of MCP Tool objects

        Returns:
            List of LangChain StructuredTool objects
        """
        langchain_tools = []

        for mcp_tool in mcp_tools:
            # Create a closure to capture the tool name
            def make_tool_func(tool_name: str):
                async def tool_func(**kwargs) -> str:
                    """Execute the MCP tool with given arguments."""
                    try:
                        result = await self.client.call_tool(tool_name, kwargs)
                        # Convert result to string for LangChain
                        if isinstance(result, dict):
                            import json

                            return json.dumps(result, indent=2)
                        return str(result)
                    except Exception as e:
                        return f"Error calling tool {tool_name}: {str(e)}"

                return tool_func

            # Create LangChain StructuredTool
            langchain_tool = StructuredTool.from_function(
                func=make_tool_func(mcp_tool.name),
                name=mcp_tool.name,
                description=mcp_tool.description or f"MCP tool: {mcp_tool.name}",
                coroutine=make_tool_func(mcp_tool.name),
            )

            langchain_tools.append(langchain_tool)

        return langchain_tools

    async def __aenter__(self):
        """Async context manager entry - initializes client and agent."""
        # Initialize MCP client (provided by subclass)
        self.client = self.get_mcp_client()
        await self.client.__aenter__()

        # Initialize LLM
        if self.model_provider == "openai":
            self.llm = ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature,
                max_completion_tokens=self.max_tokens,
            )
        elif self.model_provider == "local":
            self.llm = ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature,
                max_completion_tokens=self.max_tokens,
                base_url=self.base_url,
                api_key=SecretStr("not-needed"),
            )
        else:
            raise ValueError(f"Unsupported model provider: {self.model_provider}. Use 'openai' or 'local'")

        # Get MCP tools from client
        mcp_tools = self.client.list_available_tools()

        # Convert MCP tools to LangChain tools
        tools = self._convert_mcp_tools_to_langchain(mcp_tools)

        agent_name = self.get_agent_name()
        print(f"🤖 Initializing {agent_name} with {len(tools)} tools...")

        # Create ReAct agent
        self.agent = create_react_agent(
            model=self.llm,
            tools=tools,
            prompt=self.prompt,
            checkpointer=self.checkpointer,
        )

        print(f"✅ Agent ready! Using {self.model_provider}:{self.model_name}")

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - cleanup resources."""
        if self.client:
            await self.client.__aexit__(exc_type, exc_val, exc_tb)

    async def run(self, message: str) -> str:
        """
        Run the agent with a single message and return the response.

        Args:
            message: User message/query

        Returns:
            Agent's text response
        """
        if not self.agent:
            raise RuntimeError(
                "Agent not initialized. Use 'async with' context manager."
            )

        # Invoke agent
        result = await self.agent.ainvoke(
            {"messages": [{"role": "user", "content": message}]}, config=self.config
        )

        # Extract final response
        if result and "messages" in result:
            last_message = result["messages"][-1]
            if hasattr(last_message, "content"):
                return last_message.content
            return str(last_message)

        return "No response generated."

    async def stream(self, message: str) -> AsyncIterator[str]:
        """
        Stream the agent's response token by token.

        Args:
            message: User message/query

        Yields:
            Response tokens as they're generated
        """
        if not self.agent:
            raise RuntimeError(
                "Agent not initialized. Use 'async with' context manager."
            )

        # Stream agent responses
        async for chunk in self.agent.astream(
            {"messages": [{"role": "user", "content": message}]},
            config=self.config,
            stream_mode="values",
        ):
            if chunk and "messages" in chunk:
                last_message = chunk["messages"][-1]
                if hasattr(last_message, "content"):
                    yield last_message.content

    async def run_interactive(self):
        """Run an interactive chat session with the agent."""
        agent_name = self.get_agent_name()

        print("\n" + "=" * 80)
        print(f"🤖 {agent_name.upper()} - Interactive Mode")
        print("=" * 80)
        print("\nType your questions or commands. Type 'exit' or 'quit' to end.\n")

        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ["exit", "quit", "q"]:
                    print("\n👋 Goodbye!\n")
                    break

                # Get agent response
                print("\nAgent: ", end="", flush=True)

                response_text = ""
                async for token in self.stream(user_input):
                    if token and token != response_text:
                        print(token[len(response_text) :], end="", flush=True)
                        response_text = token

                print("\n")

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!\n")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")

    def get_conversation_history(self) -> list:
        """
        Get the conversation history for the current thread.

        Returns:
            List of messages in the conversation
        """
        if not self.agent or not self.checkpointer:
            return []

        # Get state from checkpointer
        try:
            state = self.checkpointer.get(self.config)
            if state and "messages" in state:
                return state["messages"]
        except Exception:
            pass

        return []
