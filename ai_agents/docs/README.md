# AI Agents System Documentation

A Python package for building LangGraph AI agents that use Model Context Protocol (MCP) to access Gapps API, with **multi-agent orchestration** for complex GRC tasks.

## 🎨 LangGraph Studio Support

This project is fully compatible with **LangGraph Studio** for visual development and debugging!

```bash
# Quick start with launcher script
cd /Users/a.hendawi/Desktop/gapps
./ai_agents/start_langgraph_studio.sh

# Or run directly
langgraph dev --config ai_agents/langgraph.json
```

**Available Graph:**
- 🎯 `grc_orchestrator` - Multi-agent coordinator with access to all 232 tools across 3 specialized agents

**See:** 
- [Quick Start Guide](../LANGGRAPH_STUDIO_README.md) - Get started in 5 minutes
- [LangGraph Studio Integration](./LANGGRAPH_STUDIO_INTEGRATION.md) - Detailed integration guide

## Quick Start

### Prerequisites

```bash
# Activate virtual environment
source .venv_uv/bin/activate

# Optional: LLM provider (defaults to local)
export AGENT_LLM_PROVIDER="local"  # or "anthropic" or "openai"
```

### Running Tests

```bash
# From project root
cd /Users/a.hendawi/Desktop/gapps

# Run authentication test
.venv_uv/bin/python -m ai_agents.tests.test_mcp_auth

# Run agent test
.venv_uv/bin/python -m ai_agents.tests.test_tenant_admin_agent

# Run orchestrator test
.venv_uv/bin/python -m ai_agents.tests.test_grc_orchestrator

# Run all tests
.venv_uv/bin/python -m ai_agents.tests
```

### Using an Agent

```python
import asyncio
from ai_agents.agents.tenant_admin_agent import TenantAdminAgent

async def main():
    async with TenantAdminAgent() as agent:
        response = await agent.run("List all tenants")
        print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

### Using the Orchestrator (Recommended!)

```python
import asyncio
from ai_agents.orchestrator import GRCTaskOrchestrator

async def main():
    orchestrator = GRCTaskOrchestrator()
    
    # Complex task spanning multiple agents
    task = """
    Set up SOC 2 compliance:
    1. List available frameworks
    2. Create a new project for SOC 2
    3. Add access controls to the project
    """
    
    result = await orchestrator.run(task)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

## Package Structure

```
ai_agents/
├── __init__.py
├── README.md                      # Package overview (points to docs/)
│
├── base/                          # Base classes for all agents
│   ├── __init__.py
│   ├── base_agent.py             # Abstract base agent class
│   └── base_client.py            # Abstract base MCP client
│
├── agents/                        # Specialized agent implementations
│   ├── __init__.py
│   ├── tenant_admin_agent.py     # Tenant & User Administration
│   ├── general_resources_agent.py # General & Supporting Resources
│   └── project_management_agent.py # Project Management
│
├── clients/                       # MCP client implementations
│   ├── __init__.py
│   ├── tenant_admin_client.py    # 55 tools (admin, session, tenant, user, token)
│   ├── general_resources_client.py # 108 tools (application, assessment, control, etc.)
│   └── project_management_client.py # 69 tools (project, project-control, etc.)
│
├── orchestrator/                  # Multi-agent orchestration (NEW!)
│   ├── __init__.py
│   └── grc_orchestrator.py       # LangGraph supervisor for GRC tasks
│
├── examples/                      # Usage examples for each agent
│   ├── __init__.py
│   ├── tenant_admin_examples.py
│   ├── general_resources_examples.py
│   ├── project_management_examples.py
│   └── orchestrator_examples.py  # Multi-agent orchestration examples
│
├── tests/                         # Test suites
│   ├── __init__.py
│   ├── __main__.py               # Test runner
│   ├── conftest.py               # Pytest configuration
│   ├── test_authentication.py    # MCP connection tests
│   ├── test_tenant_admin_agent.py
│   ├── test_general_resources_agent.py
│   ├── test_project_management_agent.py
│   └── test_grc_orchestrator.py  # Orchestrator tests
│
└── docs/                          # Documentation
    └── README.md                 # This file - comprehensive guide
```

## Architecture

### Base Classes

**BaseClient** (`base/base_client.py`):
- Connects to MCP server (STDIO or HTTP)
- Filters tools by pattern matching
- Handles authentication
- Provides `call_tool()` interface

**BaseAgent** (`base/base_agent.py`):
- LangGraph ReAct pattern
- Converts MCP tools to LangChain format
- Manages conversation memory
- Supports multiple LLM providers

### GRC Task Orchestrator (Multi-Agent Coordination)

**GRCTaskOrchestrator** (`orchestrator/grc_orchestrator.py`):
- **Purpose:** Coordinates multiple specialized agents to handle complex GRC tasks
- **Pattern:** LangGraph Supervisor architecture
- **Capabilities:**
  - Analyzes complex GRC tasks
  - Decomposes tasks into subtasks
  - Routes each subtask to the appropriate specialized agent
  - Aggregates results into comprehensive responses
  - Maintains conversation context across agents

**How it works:**
1. **Planning Node:** Analyzes incoming task and creates execution plan
2. **Routing:** Determines which agent(s) should handle each subtask
3. **Execution:** Delegates subtasks to specialized agents
4. **Aggregation:** Synthesizes results into cohesive response

**Benefits:**
- ✅ Handles complex multi-step GRC workflows automatically
- ✅ Intelligent agent selection based on task requirements
- ✅ Parallel execution of independent subtasks
- ✅ Maintains full audit trail of all operations
- ✅ Simplifies client code - one interface for all GRC operations

**Example:**
```python
from ai_agents.orchestrator import GRCTaskOrchestrator

orchestrator = GRCTaskOrchestrator()

# Single call handles: framework lookup + project creation + control assignment
result = await orchestrator.run("""
    Create a SOC 2 compliance project with access controls
""")
```

### Creating New Agents

1. **Create a Client** (inherits from `BaseClient`):

```python
from ai_agents.base.base_client import BaseClient

class MyDomainClient(BaseClient):
    """Client for my domain operations."""
    
    TOOL_PATTERNS = [
        "my_domain",    # Tools matching these patterns
        "related_tool",
    ]
    
    def get_client_name(self) -> str:
        return "My Domain"
```

2. **Create an Agent** (inherits from `BaseAgent`):

```python
from ai_agents.base.base_agent import BaseAgent
from ai_agents.clients.my_domain_client import MyDomainClient

class MyDomainAgent(BaseAgent):
    """AI agent for my domain."""
    
    def get_mcp_client(self):
        return MyDomainClient()
    
    def get_default_prompt(self) -> str:
        return """You are a helpful assistant for [domain].
        
        You can help with:
        - Task 1
        - Task 2
        """
    
    def get_agent_name(self) -> str:
        return "My Domain Agent"
```

3. **Use the Agent**:

```python
async with MyDomainAgent() as agent:
    response = await agent.run("What can you do?")
    print(response)
```

## Tool Pattern Examples

### Tenant & User Administration
```python
TOOL_PATTERNS = ["admin", "session", "tenant", "user", "token"]
# Result: 55 tools
```

### General & Supporting Resources
```python
TOOL_PATTERNS = [
    "application", "assessment", "control", "deployment", "evidence",
    "form", "framework", "policy", "policies", "risk", "subcontrol", "vendor"
]
# Result: 108 tools
```

### Project Management
```python
TOOL_PATTERNS = ["project", "project-control", "project_control"]
# Result: 69 tools
```

### Vendor Management
```python
TOOL_PATTERNS = ["vendor", "supplier", "questionnaire"]
# Result: ~40 tools
```

### Risk Management
```python
TOOL_PATTERNS = ["risk", "register", "assessment"]
# Result: ~50 tools
```

## API Reference

### BaseClient

```python
class BaseClient(ABC):
    """Abstract base class for MCP clients."""
    
    TOOL_PATTERNS: List[str] = []  # Define in subclass
    
    def __init__(
        self,
        server_url: Optional[str] = None,
        auth_token: Optional[str] = None,
    )
    
    async def call_tool(
        self,
        tool_name: str,
        arguments: Optional[dict] = None
    ) -> Any
    
    def list_available_tools(self) -> List[str]
    def print_available_tools(self)
    def get_client_name(self) -> str  # Override for custom name
```

### BaseAgent

```python
class BaseAgent(ABC):
    """Abstract base class for LangGraph agents."""
    
    def __init__(
        self,
        model_provider: str = "local",  # "anthropic", "openai", or "local"
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        custom_prompt: Optional[str] = None,
    )
    
    @abstractmethod
    def get_mcp_client(self) -> BaseClient
    
    @abstractmethod
    def get_default_prompt(self) -> str
    
    @abstractmethod
    def get_agent_name(self) -> str
    
    async def run(self, query: str, thread_id: str = "default") -> str
    
    async def stream(
        self,
        query: str,
        thread_id: str = "default"
    ) -> AsyncIterator[str]
    
    async def run_interactive(self, thread_id: str = "default")
```

## Configuration

### Environment Variables

**Optional:**
```bash
# LLM Provider
export AGENT_LLM_PROVIDER="local"  # or "anthropic" or "openai"

# API Keys (only if using cloud providers)
export OPENAI_API_KEY="sk-..."

# MCP Server path (auto-detected by default)
export GAPPS_MCP_SERVER="/path/to/mcp_server_openapi.py"
```

### LLM Providers

**Local (Ollama):**
```python
agent = MyAgent(model_provider="local")
# Uses ollama or LM Studio
```

**OpenAI GPT:**
```python
agent = MyAgent(
    model_provider="openai",
    model_name="gpt-4"
)
```

## Examples

### Interactive Agent Session

```python
from ai_agents.agents.tenant_admin_agent import TenantAdminAgent
import asyncio

async def main():
    async with TenantAdminAgent() as agent:
        await agent.run_interactive()

if __name__ == "__main__":
    asyncio.run(main())
```

### Streaming Responses

```python
async def streaming_example():
    async with TenantAdminAgent() as agent:
        async for chunk in agent.stream("List all tenants"):
            print(chunk, end="", flush=True)
```

### Calling Tools Directly

```python
from ai_agents.clients.tenant_admin_client import TenantAdminClient

async def direct_tool_call():
    async with TenantAdminClient() as client:
        # List available tools
        client.print_available_tools()
        
        # Call a specific tool
        result = await client.call_tool("GET_session")
        print(result)
```

## Troubleshooting

### HTTP 302 Errors

**Problem:** All tool calls return HTTP 302 redirects

**Solution:** Ensure authentication environment variables are set:
```bash
export GAPPS_API_EMAIL="admin@example.com"
export GAPPS_API_PASSWORD="your_password"
```

### No Tools Found

**Problem:** Client reports "0 tools found"

**Solution:** Check your `TOOL_PATTERNS` match actual tool names:
```python
async with YourClient() as client:
    # List all available tools
    all_tools = await client.client.list_tools()
    for tool in all_tools:
        print(tool.name)
```

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'ai_agents'`

**Solution:** Run from project root:
```bash
cd /Users/a.hendawi/Desktop/gapps
.venv_uv/bin/python -m ai_agents.tests
```

Or add to PYTHONPATH:
```bash
export PYTHONPATH=/Users/a.hendawi/Desktop/gapps:$PYTHONPATH
```

## Testing

### Running Tests

```bash
# Authentication test
.venv_uv/bin/python -m ai_agents.tests.test_mcp_auth

# Agent functionality test
.venv_uv/bin/python -m ai_agents.tests.test_tenant_admin_agent

# All tests
.venv_uv/bin/python -m ai_agents.tests
```

### Writing New Tests

```python
import asyncio
from ai_agents.agents.my_agent import MyAgent

async def test_my_agent():
    """Test my agent functionality."""
    async with MyAgent() as agent:
        response = await agent.run("Test query")
        assert "expected" in response.lower()
        print("✅ Test passed!")
        return True

if __name__ == "__main__":
    result = asyncio.run(test_my_agent())
    exit(0 if result else 1)
```

## Code Metrics

- **Base abstractions:** ~600 lines (reusable)
- **Specialized implementations:** ~750 lines
- **Tests:** ~400 lines
- **Code reduction:** 64-70% vs without base classes

## Key Features

✅ **Template-based architecture** - BaseAgent & BaseClient abstractions
✅ **70% code reduction** - Clients: 267→80 lines, Agents: 405→145 lines
✅ **Automatic authentication** - STDIO/HTTP transport with env var passing
✅ **Tool filtering** - Pattern-based tool selection by domain
✅ **ReAct pattern** - Intelligent reasoning and action loops
✅ **3 LLM providers** - Anthropic, OpenAI, Local (Ollama)
✅ **Conversation memory** - Multi-turn interactions with context
✅ **Production ready** - Full test coverage, comprehensive error handling

## License

Part of the Gapps project. See main repository LICENSE.

---

**Version:** 1.0.0  
**Last Updated:** October 2025  
**Status:** Production Ready ✅
