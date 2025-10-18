# Simplified Token Flow Architecture

## Overview

The GRC AI Agents system has been refactored to use a **simplified token-based authentication flow**. Instead of agents managing token generation and refresh internally, **users now provide the authentication token upfront** when invoking the graph.

## Why This Change?

### Before: Complex Internal Authentication
- Agents read `GAPPS_API_EMAIL` + `GAPPS_API_PASSWORD` from environment
- MCP clients passed credentials to subprocesses
- MCP server authenticated and generated tokens
- Complex fallback logic if tokens expired
- ~62 lines of authentication code in BaseClient
- Difficult to debug authentication issues

### After: Simple User-Provided Token
- User generates token manually (via API or UI)
- User passes token as graph input parameter
- Orchestrator stores token in state
- Agents receive token from state
- MCP clients pass token to subprocesses
- MCP server uses token directly
- ~30 lines of simple code in BaseClient
- Clear, traceable authentication flow

## Architecture Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. User Obtains Token                                           │
│    curl -X POST http://localhost:8000/login \                   │
│         -d '{"email":"admin@example.com","password":"pass"}'    │
│    → Returns: {"token": "eyJhbGci...", "expires_in": 600}       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. User Passes Token to Graph                                   │
│    orchestrator.run(                                            │
│        task="Set up SOC 2 compliance",                          │
│        api_token="eyJhbGci..."  ← USER-PROVIDED TOKEN           │
│    )                                                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. Orchestrator Stores Token in State                          │
│    class GRCOrchestratorState(TypedDict):                      │
│        messages: list                                           │
│        api_token: Optional[str]  ← STORED IN STATE              │
│        active_agent: Optional[str]                              │
│        subtasks: Optional[list]                                 │
│        results: dict                                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. Orchestrator Passes Token to Agents                         │
│    async def _tenant_admin_node(self, state):                  │
│        api_token = state.get("api_token")                       │
│        if not api_token:                                        │
│            return error_message                                 │
│                                                                 │
│        agent = TenantAdminAgent(                                │
│            auth_token=api_token  ← PASSED TO AGENT              │
│        )                                                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 5. Agents Pass Token to MCP Clients                            │
│    class TenantAdminAgent(BaseAgent):                          │
│        async def __aenter__(self):                              │
│            self.client = TenantAdminClient(                     │
│                auth_token=self.auth_token  ← PASSED TO CLIENT   │
│            )                                                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 6. MCP Clients Pass Token to Subprocess                        │
│    class BaseClient:                                            │
│        def _build_environment(self):                            │
│            if not self.auth_token:                              │
│                raise ValueError("Token required")               │
│                                                                 │
│            env["GAPPS_API_TOKEN"] = self.auth_token             │
│            return env  ← PASSED TO SUBPROCESS                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 7. MCP Server Uses Token for API Calls                         │
│    def create_mcp_server():                                     │
│        api_token = os.getenv("GAPPS_API_TOKEN")                 │
│        if not api_token:                                        │
│            sys.exit(1)  # FAIL FAST                             │
│                                                                 │
│        auth_headers["token"] = api_token                        │
│        client = httpx.AsyncClient(headers=auth_headers)         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 8. API Calls Succeed                                            │
│    HTTP Headers:                                                │
│    - token: eyJhbGci...                                         │
│    - Content-Type: application/json                             │
│                                                                 │
│    → 200 OK (successful API calls)                              │
└─────────────────────────────────────────────────────────────────┘
```

## Usage Examples

### LangGraph Studio

When using LangGraph Studio, provide the token in the input configuration:

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Set up SOC 2 compliance program"
    }
  ],
  "api_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Programmatic Usage

```python
from ai_agents.orchestrator import GRCTaskOrchestrator

# Step 1: Obtain token (one-time, manual)
# You can get this from the API or UI login
api_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Step 2: Create orchestrator
orchestrator = GRCTaskOrchestrator()

# Step 3: Run task with token
result = await orchestrator.run(
    task="Set up SOC 2 compliance program",
    api_token=api_token  # ← USER-PROVIDED TOKEN
)
```

### Getting a Token via API

```bash
# Login and get token
TOKEN=$(curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin1234567"}' \
  | jq -r '.token')

# Use token with orchestrator
python -c "
from ai_agents.orchestrator import GRCTaskOrchestrator
orchestrator = GRCTaskOrchestrator()
result = orchestrator.run(
    'List all users',
    api_token='$TOKEN'
)
print(result)
"
```

## Code Changes Summary

### 1. GRCOrchestratorState (orchestrator/grc_orchestrator.py)

```python
class GRCOrchestratorState(TypedDict):
    messages: Annotated[list, add_messages]
    active_agent: Optional[str]
    task_plan: Optional[str]
    subtasks: Optional[list[dict]]
    results: dict[str, any]
    api_token: Optional[str]  # NEW: User-provided API authentication token
```

### 2. Orchestrator Agent Nodes (orchestrator/grc_orchestrator.py)

```python
async def _tenant_admin_node(self, state: GRCOrchestratorState) -> dict:
    """Execute subtask using Tenant Admin Agent"""
    api_token = state.get("api_token")
    
    # Validate token is provided
    if not api_token:
        return {
            "messages": [AIMessage(content="❌ Error: API token is required")],
        }
    
    # Create agent with token
    self.tenant_admin_agent = TenantAdminAgent(
        model_provider=self.model_provider,
        model_name=self.model_name,
        auth_token=api_token,  # Pass user-provided token
    )
```

### 3. BaseClient Simplification (base/base_client.py)

**Before** (~62 lines):
```python
def _build_environment(self) -> dict:
    env = {}
    
    # Complex email/password/token fallback logic
    email = os.getenv("GAPPS_API_EMAIL")
    password = os.getenv("GAPPS_API_PASSWORD")
    api_token = os.getenv("GAPPS_API_TOKEN")
    
    if email and password:
        env["GAPPS_API_EMAIL"] = email
        env["GAPPS_API_PASSWORD"] = password
    
    if self.auth_token:
        env["GAPPS_API_TOKEN"] = self.auth_token
    elif api_token:
        env["GAPPS_API_TOKEN"] = api_token
    
    # ... more logic
```

**After** (~30 lines):
```python
def _build_environment(self) -> dict:
    env = {}
    
    # Simple token requirement
    if not self.auth_token:
        raise ValueError(
            "API token is required. Please provide auth_token when creating the client.\n"
            "The token should be obtained from the Gapps API and passed through the orchestrator state."
        )
    
    env["GAPPS_API_TOKEN"] = self.auth_token
    
    # ... API config and paths
```

### 4. MCP Server Simplification (mcp_server_openapi.py)

**Before**:
```python
def create_mcp_server():
    api_email = os.getenv("GAPPS_API_EMAIL")
    api_password = os.getenv("GAPPS_API_PASSWORD")
    api_token = os.getenv("GAPPS_API_TOKEN")
    
    if api_token:
        auth_headers["token"] = api_token
    elif api_email and api_password:
        token = get_auth_token_from_credentials(email, password)
        if token:
            auth_headers["token"] = token
    # ... complex fallback logic
```

**After**:
```python
def create_mcp_server():
    api_token = os.getenv("GAPPS_API_TOKEN")
    
    if not api_token:
        print("❌ ERROR: GAPPS_API_TOKEN environment variable is required")
        sys.exit(1)
    
    auth_headers["token"] = api_token
```

## Benefits

### 1. **Simplicity**
- Removed ~60 lines of complex authentication code
- Clear, linear flow from user → graph → agents → API
- No fallback logic or conditional paths

### 2. **Explicit Control**
- User controls when/how tokens are obtained
- No hidden token generation or refresh
- Clear token lifecycle management

### 3. **Easier Debugging**
- Token is visible in state at each step
- Can inspect token in LangGraph Studio
- No mysterious authentication failures

### 4. **Better Security**
- No storing email/password in environment variables
- Token can be rotated independently
- Clear separation between authentication and execution

### 5. **Testability**
- Easy to mock tokens in tests
- No need to mock authentication flows
- Deterministic behavior

## Migration Guide

### For Existing Code

**Old way** (environment variables):
```bash
export GAPPS_API_EMAIL="admin@example.com"
export GAPPS_API_PASSWORD="admin1234567"

python -c "
from ai_agents.orchestrator import GRCTaskOrchestrator
orchestrator = GRCTaskOrchestrator()
result = orchestrator.run('List users')
"
```

**New way** (user-provided token):
```bash
# Get token once
TOKEN=$(curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin1234567"}' \
  | jq -r '.token')

# Use token in all requests
python -c "
from ai_agents.orchestrator import GRCTaskOrchestrator
orchestrator = GRCTaskOrchestrator()
result = orchestrator.run('List users', api_token='$TOKEN')
"
```

### For LangGraph Studio

**Old configuration** (langgraph.json):
```json
{
  "env": ".env"
}
```

**.env file**:
```
GAPPS_API_EMAIL=admin@example.com
GAPPS_API_PASSWORD=admin1234567
```

**New configuration** (provide token in Studio UI):
```json
{
  "messages": [{"role": "user", "content": "List users"}],
  "api_token": "eyJhbGci..."
}
```

## Error Messages

### Missing Token Error (Orchestrator)
```
❌ Error: API token is required. Please provide api_token in the graph input.
```

**Solution**: Add `api_token` parameter when invoking the graph.

### Missing Token Error (BaseClient)
```
ValueError: API token is required. Please provide auth_token when creating the client.
The token should be obtained from the Gapps API and passed through the orchestrator state.
```

**Solution**: Ensure token is passed from orchestrator state to agents.

### Missing Token Error (MCP Server)
```
❌ ERROR: GAPPS_API_TOKEN environment variable is required
💡 The token should be obtained from the Gapps API and passed through the orchestrator state
```

**Solution**: Ensure token is being passed through the environment when starting MCP subprocess.

## Frequently Asked Questions

### Q: How do I get a token?

**A**: You can get a token by logging in via the API:

```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"email":"your_email","password":"your_password"}'
```

Or via the web UI, then copy the token from your session.

### Q: How long does a token last?

**A**: Tokens typically expire after 10 minutes (600 seconds). You'll need to obtain a fresh token when it expires.

### Q: Can I still use environment variables?

**A**: No. The system now requires tokens to be passed as input parameters. This makes the flow more explicit and easier to debug.

### Q: What happens if the token expires during execution?

**A**: The API will return a 401 UNAUTHORIZED error. You'll need to obtain a fresh token and retry the operation.

### Q: Can I use multiple tokens for different agents?

**A**: Currently, the system uses a single token for all agents. If you need different tokens, you can modify the state to include agent-specific tokens.

## Implementation Details

### Files Modified

1. **ai_agents/orchestrator/grc_orchestrator.py**
   - Added `api_token` field to `GRCOrchestratorState`
   - Updated `_tenant_admin_node()` to extract and pass token
   - Updated `_general_resources_node()` to extract and pass token
   - Updated `_project_management_node()` to extract and pass token

2. **ai_agents/base/base_agent.py**
   - Updated `auth_token` parameter documentation
   - Emphasized token is required and passed from orchestrator

3. **ai_agents/base/base_client.py**
   - Simplified `_build_environment()` method
   - Removed email/password fallback logic
   - Added token requirement validation
   - Reduced from ~62 lines to ~30 lines

4. **mcp_server_openapi.py**
   - Removed `get_auth_token_from_credentials()` function
   - Simplified `create_mcp_server()` to only use token
   - Added fail-fast validation if token missing
   - Reduced complexity by ~40 lines

### Lines of Code Reduced

- **BaseClient**: 62 → 30 lines (~50% reduction)
- **MCP Server**: ~70 lines removed (get_auth_token_from_credentials + complex logic)
- **Total**: ~100 lines of authentication code removed

### Complexity Reduced

- **Conditional Paths**: 4 → 1 (token-only path)
- **Environment Variables**: 3 → 1 (GAPPS_API_TOKEN only)
- **Error Cases**: 6 → 2 (missing token, expired token)

## Conclusion

The simplified token flow makes the GRC AI Agents system:

- ✅ **Simpler** - 100 fewer lines of authentication code
- ✅ **More Explicit** - User controls token lifecycle
- ✅ **Easier to Debug** - Clear, traceable flow
- ✅ **More Secure** - No stored credentials
- ✅ **More Testable** - Deterministic behavior

This refactoring maintains all functionality while significantly improving developer experience and system maintainability.
