# DIY PC Build Assistant

A CLI-based DIY PC build assistant powered by the Anthropic Claude API. Uses a composable multi-agent architecture where each agent is a self-contained unit that can be nested inside a parent agent as a callable tool.

## Setup

```bash
# Install dependencies
uv sync

# Run the agent
uv run buildcomputer
```

Requires the `CLAUDE_API_KEY` environment variable set to your Anthropic API key.

### One-command launch scripts

Platform-specific scripts handle Python 3.12+ and `uv` installation automatically, then launch the agent:

| Platform | Script |
|----------|--------|
| Linux | `./launch.sh` |
| macOS | `./launch_macos.sh` |
| Windows | `launch.bat` |

Each script will prompt for `CLAUDE_API_KEY` if it is not already set.

## Architecture

### Overview

The system is built around a base `Agent` class with a tool-use loop. Agents can register other agents as sub-agents, which get exposed to Claude as callable tools. This allows building deep hierarchies where orchestrator agents delegate specialized queries to leaf agents.

```
app.py (REPL)
└── ComputerBuilderAgent          ← top-level orchestrator
    ├── tools: GetAvailableMice, GetAvailableKeyboards
    ├── MainUnitAgent             ← sub-agent (core PC components)
    │   ├── tools: GetAvailableGPUs, GetAvailableMotherBoard,
    │   │          GetAvailableMemory, GetAvailableCase,
    │   │          GetAvailableHardDrive, GetAvailablePowerSupply
    │   └── CPUAgent              ← sub-agent (CPU lookup with filters)
    │       └── tools: GetAvailableCPUs
    └── MonitorAgent              ← sub-agent (monitor lookup with filters)
        └── tools: GetAvailableMonitors
```

### Base Agent (`agents/agent.py:Agent`)

The core abstraction all agents inherit from. Constructor parameters:

| Parameter | Purpose |
|-----------|---------|
| `name` | Identifies the agent; used as the tool name when exposed to a parent |
| `description` | Tool description shown to the parent's Claude context |
| `properties` | JSON Schema properties for the tool's input when called by a parent |
| `system` | System prompt for this agent's own Claude calls |
| `maxIter` | Maximum tool-use iterations before the loop exits (default 10) |

**Tool-use loop — `Run()`**

Each call to `Run()` enters a loop (wrapped in an OTel span):

1. Prints the full context window to stdout (grey ANSI background) for debugging.
2. Calls `_SendRequestToAgent()`, which wraps `client.messages.create` in an OTel `claude` generation span that records model, token counts, and the prompt/completion text.
3. Appends any text blocks to stdout.
4. If the response contains `tool_use` blocks, dispatches each via `__CallTool()` (each wrapped in its own `tool.*` span) and appends the results as a `tool_result` user message, then loops.
5. If no tool calls are present, exits and returns the final text response.

**Tool dispatch — `__CallTool()`**

Tries `getattr(self, toolName)` first (own methods). If not found, falls back to `__CallSubAgent(agentName)`, which looks up the agent in `self.subAgents`, calls `ConfigureInput(**inputs)` on it, then calls `Run()`.

**Sub-agent registration**

```python
parent.AddSubAgent(child_agent)
```

`GetSubAgentAsTools()` iterates `self.subAgents` and calls `GetToolDescription()` on each, producing the JSON Schema tool definition that gets merged into `GetTools()` alongside the agent's own tools.

**`ConfigureInput(**inputs)`**

Override in concrete agents to translate the parent's tool call inputs into an initial message appended to `self.messages` before `Run()` is called. The base implementation is a no-op.

**`__PrintContextWindow()`**

Prints all registered tool schemas and the full message history before each API call. Tool parameters are shown as `param*` (required) or `param?` (optional).

---

### Concrete Agents

#### `ComputerBuilderAgent` — top-level orchestrator

Entry point used by `app.py`. Registers `MainUnitAgent` and `MonitorAgent` as sub-agents. Also owns two direct tool methods:

- **`GetAvailableMice(wireless, use_case, priceMax)`** — filters by connectivity, use case (`gaming`/`productivity`), and price.
- **`GetAvailableKeyboards(wireless, layout, priceMax)`** — filters by connectivity, layout (`full`/`tenkeyless`/`75%`/`65%`), and price.

System prompt instructs Claude to coordinate a complete setup: main unit + monitor + mouse + keyboard.

#### `MainUnitAgent` — core PC components

Sub-agent of `ComputerBuilderAgent`. Registers `CPUAgent` as its own sub-agent. `ConfigureInput` seeds the conversation with a budget-aware prompt. Owns six tool methods (no filters — returns full catalogues):

- `GetAvailableGPUs` — NVIDIA Ada Lovelace and AMD RDNA 3 cards
- `GetAvailableMotherBoard` — Intel Z790/B760 and AMD B650/X670E boards
- `GetAvailableMemory` — DDR4 and DDR5 kits
- `GetAvailableCase` — mid and mini tower cases with clearance specs
- `GetAvailableHardDrive` — NVMe SSDs, SATA SSDs, and HDDs
- `GetAvailablePowerSupply` — ATX PSUs from 550 W to 1000 W

#### `CPUAgent` — CPU lookup

Leaf sub-agent of `MainUnitAgent`. Exposes one tool:

- **`GetAvailableCPUs(socket, priceMin, priceMax)`** — filters the catalogue by socket (`LGA1700`/`AM5`) and price range. Covers Intel Raptor Lake Refresh (i5/i7/i9) and AMD Zen 4 (Ryzen 5/7/9) CPUs.

`ConfigureInput` converts the parent's tool call inputs into a natural-language message so CPUAgent's own Claude call knows what filters to apply.

#### `MonitorAgent` — monitor recommendations

Sub-agent of `ComputerBuilderAgent`. Exposes one tool:

- **`GetAvailableMonitors(resolution, use_case, priceMax)`** — filters by resolution (`1080p`/`1440p`/`4K`), use case (`gaming`/`creative`/`office`), and price. Catalogue covers IPS, VA, and Nano IPS panels from 24" to 34".

---

### Entry Point (`app.py`)

`DIYComputer()` is a simple REPL:

1. Instantiates `ComputerBuilderAgent`.
2. Sends an initial `"hi"` to start the conversation.
3. Loops reading user input from stdin, passing each line to `agent.ProcessNewUserInput()`.
4. Exits on `"exit"`.

---

### Observability — OpenTelemetry + Langfuse

The agent is instrumented with [OpenTelemetry](https://opentelemetry.io/) and ships traces to [Langfuse](https://langfuse.com/) for LLM observability. Every user message produces one trace in Langfuse containing:

- A root span per agent (`ProcessNewUserInput`)
- A `Run` span covering all tool-use iterations for that agent
- A `claude` generation span per API call, with model name, token counts, and full prompt/completion text
- A `tool.*` child span per tool or sub-agent call

```
ComputerBuilderAgent                  ← trace root
  ComputerBuilderAgent.Run
    claude  [generation]              ← tokens, cost, prompt, completion
    tool.GetAvailableMice
    tool.MainUnitAgent                ← sub-agent call
      MainUnitAgent.Run
        claude  [generation]
        tool.CPUAgent
          CPUAgent.Run
            claude  [generation]
    tool.MonitorAgent
      MonitorAgent.Run
        claude  [generation]
```

#### Setup

Set these environment variables before running the agent:

```bash
export LANGFUSE_PUBLIC_KEY="pk-lf-..."
export LANGFUSE_SECRET_KEY="sk-lf-..."
export LANGFUSE_HOST="https://cloud.langfuse.com"   # or http://localhost:3000 for self-hosted
```

Tracing is initialized once at startup in `app.py` via `SetupTracing()` in `src/buildcomputer/instrumentation/instrumentation.py`. The instrumentation uses `BatchSpanProcessor` so HTTP exports to Langfuse are non-blocking. See [`doc/instrumentation.md`](doc/instrumentation.md) for a full step-by-step walkthrough including self-hosted Langfuse setup.

---

### Adding a New Agent

1. Create `agents/myAgent.py` subclassing `Agent`.
2. Override `GetAgentTools()` to return tool schemas (list of Anthropic tool dicts).
3. Override `CallTool()` if you need custom dispatch; otherwise rely on `getattr` — just name your methods to match the tool `name` fields.
4. Implement tool methods returning plain dicts (serialized to JSON by the base class).
5. Override `ConfigureInput(**inputs)` to translate parent-supplied parameters into an initial message.
6. Register on a parent: `parent.AddSubAgent(MyAgent())`.

---

### Data

All component catalogues are hardcoded in-memory dicts inside each agent's tool methods. There is no external database or API.
