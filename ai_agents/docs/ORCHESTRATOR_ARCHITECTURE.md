# GRC Task Orchestrator - Architecture Diagram

## System Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          USER REQUEST                                    │
│         "Set up SOC 2 compliance program with risk assessment"          │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         GRC TASK ORCHESTRATOR                            │
│                    (LangGraph Supervisor Pattern)                        │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
              ┌────────────────────────────────────┐
              │      PLANNER NODE (LLM-Powered)    │
              │  • Analyze task complexity         │
              │  • Decompose into subtasks         │
              │  • Assign agents to subtasks       │
              │  • Identify dependencies           │
              └────────────────────────────────────┘
                                    │
                                    ▼
                          TASK PLAN (JSON):
                    ┌─────────────────────────┐
                    │ Subtask 1: Search SOC 2 │
                    │   Agent: GeneralRes     │
                    │   Deps: []              │
                    ├─────────────────────────┤
                    │ Subtask 2: Create Proj  │
                    │   Agent: ProjectMgmt    │
                    │   Deps: [1]             │
                    ├─────────────────────────┤
                    │ Subtask 3: Risk Assess  │
                    │   Agent: ProjectMgmt    │
                    │   Deps: [2]             │
                    └─────────────────────────┘
                                    │
                                    ▼
              ┌────────────────────────────────────┐
              │     ROUTER (Conditional Edges)     │
              │  Routes based on:                  │
              │  • state['active_agent']           │
              │  • Subtask completion status       │
              └────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
    ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
    │  TENANT ADMIN    │ │ GENERAL          │ │  PROJECT         │
    │     AGENT        │ │ RESOURCES AGENT  │ │ MANAGEMENT AGENT │
    ├──────────────────┤ ├──────────────────┤ ├──────────────────┤
    │ 55 TOOLS         │ │ 108 TOOLS        │ │ 69 TOOLS         │
    ├──────────────────┤ ├──────────────────┤ ├──────────────────┤
    │ • Users          │ │ • Frameworks     │ │ • Projects       │
    │ • Roles          │ │ • Controls       │ │ • Assessments    │
    │ • Teams          │ │ • Policies       │ │ • Tasks          │
    │ • Sessions       │ │ • Vendors        │ │ • Risks          │
    │ • Tokens         │ │ • Evidence       │ │ • Reports        │
    │ • Auth           │ │ • Applications   │ │ • Team Mgmt      │
    └──────────────────┘ └──────────────────┘ └──────────────────┘
            │                     │                     │
            └─────────────────────┼─────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │  RESULTS COLLECTION     │
                    │                         │
                    │  Subtask 1: ✅ Done     │
                    │    Result: Framework    │
                    │    found with 80        │
                    │    controls             │
                    │                         │
                    │  Subtask 2: ✅ Done     │
                    │    Result: Project      │
                    │    created ID: 123      │
                    │                         │
                    │  Subtask 3: ✅ Done     │
                    │    Result: 15 risks     │
                    │    identified           │
                    └─────────────────────────┘
                                  │
                                  ▼
              ┌────────────────────────────────────┐
              │    AGGREGATOR NODE (LLM-Powered)   │
              │  • Synthesize all results          │
              │  • Create coherent response        │
              │  • Format for user consumption     │
              └────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       COMPREHENSIVE RESPONSE                             │
│                                                                          │
│  "Successfully set up SOC 2 compliance program:                         │
│   1. Found SOC 2 framework with 80 controls                            │
│   2. Created project 'SOC 2 Compliance 2024' (ID: 123)                 │
│   3. Identified 15 key risks across 5 categories                       │
│   4. Assigned 20 critical controls to project                          │
│   Next steps: Review risk register, assign control owners..."          │
└─────────────────────────────────────────────────────────────────────────┘
```

## State Management Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    GRCOrchestratorState                         │
├─────────────────────────────────────────────────────────────────┤
│  messages: List[BaseMessage]                                    │
│    → Conversation history                                       │
│                                                                 │
│  active_agent: str                                             │
│    → "tenant_admin" | "general_resources" |                    │
│      "project_management" | "aggregator"                       │
│                                                                 │
│  task_plan: str (JSON)                                         │
│    → Full execution plan with subtasks                         │
│                                                                 │
│  subtasks: List[dict]                                          │
│    → [{                                                        │
│         "id": 1,                                               │
│         "description": "Search SOC 2",                         │
│         "agent": "general_resources",                          │
│         "status": "completed",                                 │
│         "result": "Found framework...",                        │
│         "dependencies": []                                     │
│       }]                                                       │
│                                                                 │
│  results: dict                                                 │
│    → {"general_resources": "...",                              │
│       "project_management": "..."}                             │
└─────────────────────────────────────────────────────────────────┘
```

## Graph Structure

```
                    START
                      │
                      ▼
              ┌──────────────┐
              │   planner    │
              └──────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
  ┌──────────┐ ┌──────────┐ ┌──────────┐
  │  tenant  │ │ general  │ │ project  │
  │  _admin  │ │_resources│ │_mgmt     │
  └──────────┘ └──────────┘ └──────────┘
        │             │             │
        └─────────────┼─────────────┘
                      │
                      ▼
              ┌──────────────┐
              │  aggregator  │
              └──────────────┘
                      │
                      ▼
                     END

Routing Logic:
• Planner → Agent (based on next subtask)
• Agent → Planner (loop for next subtask)
• Planner → Aggregator (all subtasks done)
• Aggregator → END
```

## Execution Timeline

```
Time →

T0: User submits complex task
    "Set up SOC 2 with risk assessment"
    
T1: Planner analyzes and creates plan
    [Planning with LLM: 2-3 seconds]
    
T2: Route to GeneralResourcesAgent
    Subtask 1: "Search SOC 2 framework"
    [Execution: 2-4 seconds]
    
T3: Return to Planner, update state
    Mark subtask 1 complete
    
T4: Route to ProjectManagementAgent  
    Subtask 2: "Create compliance project"
    [Execution: 2-4 seconds]
    
T5: Return to Planner, update state
    Mark subtask 2 complete
    
T6: Route to ProjectManagementAgent
    Subtask 3: "Generate risk assessment"
    [Execution: 3-5 seconds]
    
T7: All subtasks complete, route to Aggregator
    [Synthesis with LLM: 2-3 seconds]
    
T8: Final response delivered to user
    Total time: ~15-20 seconds
```

## Agent Initialization Strategy

```
┌────────────────────────────────────────────┐
│     Orchestrator __init__()                │
│                                            │
│  ✓ Initialize LLM (Anthropic/OpenAI)      │
│  ✓ Build StateGraph                       │
│  ✓ Create MemorySaver checkpointer        │
│  ✗ DON'T initialize agents yet            │
└────────────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────┐
│     First Agent Node Execution             │
│                                            │
│  if not hasattr(self, '_tenant_admin'):   │
│      self._tenant_admin =                 │
│          TenantAdminAgent()               │
│                                            │
│  → Lazy initialization on demand          │
│  → Saves ~150MB memory if agent unused    │
│  → Faster orchestrator startup            │
└────────────────────────────────────────────┘
```

## Error Handling Flow

```
┌────────────────────────────────────────────┐
│         Task Execution Error               │
└────────────────────────────────────────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │  Caught in agent node │
        └───────────────────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │  Update subtask:      │
        │  status = "failed"    │
        │  result = error msg   │
        └───────────────────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │  Return to planner    │
        └───────────────────────┘
                    │
    ┌───────────────┴───────────────┐
    │                               │
    ▼                               ▼
┌─────────┐                   ┌─────────┐
│ Retry   │                   │ Skip &  │
│ with    │                   │ Continue│
│ context │                   │         │
└─────────┘                   └─────────┘
```

## Conversation Memory

```
Thread ID: "user123-session1"
├── Checkpoint 0: Initial state
│   └── messages: ["Create SOC 2 project"]
│
├── Checkpoint 1: After planning
│   └── task_plan: {...}
│   └── subtasks: [...]
│
├── Checkpoint 2: After subtask 1
│   └── subtasks[0].status: "completed"
│   └── results["general_resources"]: "..."
│
├── Checkpoint 3: After subtask 2
│   └── subtasks[1].status: "completed"
│   └── results["project_management"]: "..."
│
└── Checkpoint 4: Final state
    └── Aggregated response ready
    
Benefits:
• Can resume from any checkpoint
• Audit trail of all operations
• Debug failed executions
• Multi-turn conversations
```

## Comparison: Sequential vs Orchestrated

### Without Orchestrator (Manual)
```python
# User must coordinate manually
async with GeneralResourcesAgent() as gr:
    framework = await gr.run("Find SOC 2")
    
async with ProjectManagementAgent() as pm:
    project = await pm.run(f"Create project for {framework}")
    risks = await pm.run(f"Risk assessment for {project}")
    
# User synthesizes results
final = combine(framework, project, risks)
```

### With Orchestrator (Automatic)
```python
# Single call, automatic coordination
orchestrator = GRCTaskOrchestrator()
final = await orchestrator.run(
    "Set up SOC 2 with risk assessment"
)
```

**Advantages:**
- ✅ 10x less code
- ✅ Automatic agent selection
- ✅ Built-in error handling
- ✅ Conversation memory
- ✅ Result synthesis
- ✅ Audit trail

## Performance Characteristics

### Memory Usage
```
Component                    Memory
─────────────────────────   ────────
Orchestrator (base)         ~5 MB
  - LLM client              ~3 MB
  - StateGraph              ~1 MB
  - MemorySaver             ~1 MB

Per Agent (when loaded):
  - TenantAdmin             ~50 MB
  - GeneralResources        ~50 MB
  - ProjectManagement       ~50 MB

Total (all agents loaded):  ~155 MB
```

### Execution Times
```
Operation                   Time
─────────────────────────   ──────
Orchestrator init           <1s
Task planning               2-3s
Agent initialization        1-2s
Tool call (average)         0.5-2s
Result aggregation          2-3s

Simple task (1 agent):      3-5s
Medium task (2 agents):     8-12s
Complex task (3 agents):    15-25s
```

## Scaling Considerations

### Current Architecture
- ✅ Handles 1-10 concurrent tasks
- ✅ Linear scaling with task complexity
- ✅ Memory efficient (lazy loading)

### Future Optimizations
- [ ] Parallel subtask execution
- [ ] Agent pooling for high load
- [ ] Result caching
- [ ] Distributed execution

---

**Version:** 1.0.0  
**Last Updated:** 2024  
**Pattern:** LangGraph Supervisor  
**Total System Capacity:** 232 tools across 3 specialized agents
