# GRC AI Agents System

A comprehensive LangGraph-based multi-agent system for GRC (Governance, Risk, and Compliance) automation, with full **LangGraph Studio** support for visual development and debugging.

## 🚀 Quick Start with LangGraph Studio

### Visual Development (Recommended)

```bash
# From project root - starts Studio with visual interface
./ai_agents/start_langgraph_studio.sh
```

This opens **LangGraph Studio** where you can:
- 🎨 Visually see graph execution in real-time
- 🔍 Set breakpoints and inspect state at each node  
- 📊 Monitor all 232 tool calls across agents
- ⏱️ Debug with time-travel capabilities
- 📈 View performance metrics

**See:** [LANGGRAPH_STUDIO_README.md](./LANGGRAPH_STUDIO_README.md) for complete Studio guide.

### Programmatic Usage

**⚠️ IMPORTANT: Authentication with User-Provided Token**

The system now uses a **simplified token-based authentication flow**. Instead of environment variables, you must obtain a token and pass it to the orchestrator.

```bash
# Step 1: Get API token (one-time)
TOKEN=$(curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"your_password"}' \
  | jq -r '.token')

# Step 2: Use the orchestrator with token
python -c "
from ai_agents.orchestrator import GRCTaskOrchestrator
orchestrator = GRCTaskOrchestrator()
result = orchestrator.run(
    'Set up SOC 2 compliance program',
    api_token='$TOKEN'  # ← USER-PROVIDED TOKEN
)
print(result)
"
```

**See:** [SIMPLIFIED_TOKEN_FLOW.md](./docs/SIMPLIFIED_TOKEN_FLOW.md) for complete details on the new authentication architecture.

## 📁 Package Structure

```
ai_agents/
├── README.md                          # This file
├── LANGGRAPH_STUDIO_README.md        # Quick start guide for Studio
├── STUDIO_IS_RUNNING.md              # Success confirmation
├── langgraph.json                     # LangGraph Studio configuration
├── start_langgraph_studio.sh         # Automated launcher script
│
├── base/                              # Base classes & abstractions
│   ├── base_agent.py                  # Abstract agent class
│   └── base_client.py                 # Abstract MCP client class
│
├── agents/                            # Specialized AI agents
│   ├── tenant_admin_agent.py         # User/tenant management (55 tools)
│   ├── general_resources_agent.py    # Frameworks/controls/policies (108 tools)
│   └── project_management_agent.py   # Projects/assessments/tasks (69 tools)
│
├── clients/                           # Specialized MCP clients
│   ├── tenant_admin_client.py
│   ├── general_resources_client.py
│   └── project_management_client.py
│
├── orchestrator/                      # Multi-agent coordination
│   ├── grc_orchestrator.py           # Main orchestrator (supervisor pattern)
│   └── langgraph_app.py              # Studio entry point
│
├── docs/                              # Comprehensive documentation
│   ├── README.md                      # Main documentation
│   ├── SIMPLIFIED_TOKEN_FLOW.md      # New authentication architecture
│   ├── LANGGRAPH_STUDIO_INTEGRATION.md
│   ├── GETTING_STARTED_STUDIO.md
│   └── STUDIO_QUICK_REFERENCE.md
│
├── examples/                          # Usage examples
│   ├── tenant_admin_examples.py
│   ├── general_resources_examples.py
│   ├── project_management_examples.py
│   └── orchestrator_examples.py
│
└── tests/                             # Test suite
    ├── test_tenant_admin_agent.py
    ├── test_general_resources_agent.py
    ├── test_project_management_agent.py
    └── test_grc_orchestrator.py
```

## 🤖 Available Agents & Orchestrator

### GRC Orchestrator (Main Entry Point) 🎯
**Intelligent multi-agent coordinator** - 232 total tools across all agents

```python
from ai_agents.orchestrator import GRCTaskOrchestrator
orchestrator = GRCTaskOrchestrator()
result = orchestrator.run("Set up SOC 2 program with risk assessment")
```

**Capabilities:**
- Task planning and decomposition
- Intelligent agent selection  
- Parallel execution coordination
- Result aggregation and synthesis

### Specialized Agents

**1. Tenant Admin Agent** 👥 - 55 tools
- User CRUD, tenant management, roles/permissions

**2. General Resources Agent** 📊 - 108 tools  
- Frameworks, controls, policies, evidence, mapping

**3. Project Management Agent** 📁 - 69 tools
- Projects, assessments, tasks, workflows, reporting

## 📚 Documentation

- **[Main Documentation](docs/README.md)** - Complete system docs
- **[Simplified Token Flow](docs/SIMPLIFIED_TOKEN_FLOW.md)** - New authentication architecture ⭐ NEW
- **[LangGraph Studio Guide](LANGGRAPH_STUDIO_README.md)** - Quick start with Studio
- **[Integration Guide](docs/LANGGRAPH_STUDIO_INTEGRATION.md)** - Studio integration
- **[Examples](examples/)** - Usage examples for all agents

## Key Features

✅ **LangGraph Studio Integration** - Visual development & debugging
✅ **Multi-Agent Orchestration** - Intelligent task delegation
✅ **232 Tools** - Comprehensive GRC automation capabilities  
✅ **Abstract Base Classes** - 70% code reduction
✅ **Automatic Authentication** - MCP protocol handling
✅ **LangGraph ReAct Pattern** - With memory & tool calling
✅ **Multiple LLM Providers** - Anthropic, OpenAI, Local
✅ **Production Ready** - Full test coverage

## Examples

See `examples/` directory for:
- `orchestrator_examples.py` - Multi-agent workflows
- `tenant_admin_examples.py` - Admin operations
- `general_resources_examples.py` - Framework/control management
- `project_management_examples.py` - Project workflows

---

**Version:** 2.0.0 | **Status:** Production Ready with Studio Support ✅  
**Get Started:** `./ai_agents/start_langgraph_studio.sh`
