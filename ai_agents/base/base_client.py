#!/usr/bin/env python3
"""
Base Client Class for Specialized MCP Clients

This module provides a reusable base class for creating specialized MCP clients
that filter tools from the Gapps OpenAPI MCP server.

The base class handles:
- STDIO and HTTP transport configuration
- Authentication via environment variables
- Subprocess environment variable passing
- Tool filtering based on patterns
- Connection management (async context manager)

To create a new specialized client:
1. Subclass BaseClient
2. Define TOOL_PATTERNS class variable
3. Override get_client_name() (optional)

Example:
    class ProjectManagementClient(BaseClient):
        TOOL_PATTERNS = ["project", "control"]
        
        def get_client_name(self) -> str:
            return "Project Management"
"""

import asyncio
import os
import sys
from abc import ABC
from typing import Any, Optional, List
from fastmcp import Client
from fastmcp.client.transports import StdioTransport


class BaseClient(ABC):
    """
    Abstract base class for specialized MCP clients.
    
    This class provides the common infrastructure for creating specialized clients
    that filter MCP tools based on domain-specific patterns. Subclasses must define
    TOOL_PATTERNS to specify which tools to include.
    
    Attributes:
        TOOL_PATTERNS: List of string patterns to match tool names (case-insensitive)
        server_url: MCP server URL or script path
        auth_token: API authentication token
        client: FastMCP Client instance
        _available_tools: Filtered list of tools
    """
    
    # Subclasses must define this
    TOOL_PATTERNS: List[str] = []
    
    def __init__(
        self,
        server_url: Optional[str] = None,
        auth_token: Optional[str] = None,
    ):
        """
        Initialize the Base Client.
        
        Args:
            server_url: URL or path to the MCP server. Can be:
                       - HTTP URL: "http://localhost:8000/mcp"
                       - Python script: "mcp_server_openapi.py" (for STDIO)
                       - Or from GAPPS_MCP_SERVER env var
                       Defaults to "mcp_server_openapi.py" for STDIO connection
            auth_token: Authentication token. If not provided, will use GAPPS_API_TOKEN env var
        """
        if not self.TOOL_PATTERNS:
            raise ValueError(
                f"{self.__class__.__name__} must define TOOL_PATTERNS class variable"
            )
        
        # Default to STDIO connection using the script path
        # MCP server is at project root, so we need to get the absolute path
        default_server = os.getenv("GAPPS_MCP_SERVER")
        if not default_server:
            # Find mcp_server_openapi.py - check current dir, then parent dir
            if os.path.exists("mcp_server_openapi.py"):
                default_server = "mcp_server_openapi.py"
            else:
                # We're likely in a subdirectory, try parent
                parent_path = os.path.join(os.path.dirname(__file__), "..", "..", "mcp_server_openapi.py")
                if os.path.exists(parent_path):
                    default_server = os.path.abspath(parent_path)
                else:
                    default_server = "mcp_server_openapi.py"  # Fallback
        
        self.server_url = server_url or default_server
        self.auth_token = auth_token or os.getenv("GAPPS_API_TOKEN")
        
        # Store the client but don't connect yet (use async context manager)
        self.client: Optional[Client] = None
        self._available_tools = []
    
    def get_client_name(self) -> str:
        """
        Return the client name for logging and display.
        
        Subclasses can override this to provide a custom name.
        
        Returns:
            Client name string
        """
        return self.__class__.__name__.replace("Client", "")
    
    async def __aenter__(self):
        """
        Async context manager entry - connects to the MCP server.
        
        Supports two connection modes:
        1. STDIO: server_url is a Python script path (e.g., "mcp_server_openapi.py")
        2. HTTP: server_url is a URL (e.g., "http://localhost:8000/mcp")
        """
        # Determine connection type
        is_http = self.server_url.startswith("http://") or self.server_url.startswith("https://")
        
        if is_http:
            # HTTP connection - FastMCP Client supports URL directly
            self.client = Client(self.server_url)
        else:
            # STDIO connection - Build environment dict to pass to subprocess
            # Servers run in isolation and don't inherit shell environment
            env = self._build_environment()
            
            # Create StdioTransport with explicit environment variables
            transport = StdioTransport(
                command=sys.executable,  # Use current Python interpreter
                args=[self.server_url],
                env=env
            )
            
            # Create Client with the configured transport
            self.client = Client(transport)
        
        # Connect to the server
        await self.client.__aenter__()
        
        # Load and filter tools
        await self._load_tools()
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - disconnects from the MCP server."""
        if self.client:
            await self.client.__aexit__(exc_type, exc_val, exc_tb)
    
    def _build_environment(self) -> dict:
        """
        Build environment dictionary for STDIO subprocess.
        
        The MCP server subprocess needs:
        1. Authentication: GAPPS_API_TOKEN (provided by user)
        2. API Configuration: API_BASE_URL, OPENAPI_SPEC_URL
        3. Python path: PYTHONPATH for imports
        
        Returns:
            Dictionary of environment variables to pass to MCP server subprocess
        """
        env = {}
        
        # ============================================================
        # AUTHENTICATION - Token is now REQUIRED and provided by user
        # ============================================================
        if not self.auth_token:
            raise ValueError(
                "API token is required. Please provide auth_token when creating the client.\n"
                "The token should be obtained from the Gapps API and passed through the orchestrator state."
            )
        
        env["GAPPS_API_TOKEN"] = self.auth_token
        
        # ============================================================
        # API CONFIGURATION - CRITICAL for MCP server connection
        # ============================================================
        # The MCP server needs to know where the Gapps API is running
        api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")
        env["API_BASE_URL"] = api_base_url
        
        # OpenAPI spec URL (for fetching the schema)
        openapi_spec_url = os.getenv("OPENAPI_SPEC_URL", "http://localhost:8000/api/v1/swagger.json")
        env["OPENAPI_SPEC_URL"] = openapi_spec_url
        
        # ============================================================
        # PYTHON ENVIRONMENT - Ensure imports work
        # ============================================================
        # Pass through PYTHONPATH so MCP server can find its modules
        pythonpath = os.getenv("PYTHONPATH")
        if pythonpath:
            env["PYTHONPATH"] = pythonpath
        
        # ============================================================
        # PATH - Ensure subprocess can find system commands
        # ============================================================
        # Pass through PATH for httpx and other system dependencies
        path = os.getenv("PATH")
        if path:
            env["PATH"] = path
        
        return env
    
    async def _load_tools(self):
        """Load and filter tools based on TOOL_PATTERNS."""
        if not self.client:
            raise RuntimeError("Client not connected. Use 'async with' context manager.")
        
        all_tools = await self.client.list_tools()
        
        # Filter tools based on patterns (case-insensitive substring matching)
        self._available_tools = [
            tool for tool in all_tools
            if any(pattern in tool.name.lower() for pattern in self.TOOL_PATTERNS)
        ]
        
        client_name = self.get_client_name()
        print(f"✅ Loaded {len(self._available_tools)} {client_name} tools")
    
    def list_available_tools(self) -> list:
        """
        Get a list of all available filtered tools.
        
        Returns:
            List of tool objects with name, description, and input schema
        """
        return self._available_tools
    
    def print_available_tools(self):
        """Print a formatted list of all available tools."""
        if not self._available_tools:
            print("⚠️  No tools loaded. Make sure you're using 'async with' context manager.")
            return
        
        client_name = self.get_client_name()
        
        print("\n" + "="*80)
        print(f"{client_name.upper()} TOOLS")
        print("="*80 + "\n")
        
        for tool in self._available_tools:
            print(f"📌 {tool.name}")
            
            # Parse the description if available
            if hasattr(tool, 'description') and tool.description:
                print(f"   {tool.description}\n")
    
    async def call_tool(self, tool_name: str, arguments: Optional[dict] = None) -> Any:
        """
        Call a specific tool by name.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Dictionary of arguments to pass to the tool
            
        Returns:
            Result from the tool execution
        """
        if not self.client:
            raise RuntimeError("Client not connected. Use 'async with' context manager.")
        
        # Verify tool exists in our filtered list
        if not any(tool.name == tool_name for tool in self._available_tools):
            available_names = [tool.name for tool in self._available_tools]
            client_name = self.get_client_name()
            raise ValueError(
                f"Tool '{tool_name}' not found in {client_name} tools. "
                f"Available tools: {available_names}"
            )
        
        return await self.client.call_tool(tool_name, arguments or {})
