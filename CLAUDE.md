# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

This project uses `uv` for dependency management (Python 3.12).

```bash
# Install dependencies
uv sync

# Run the agent
uv run buildcomputer

# Or install in editable mode and run directly
pip install -e .
buildcomputer
```

The `CLAUDE_API_KEY` environment variable must be set to your Anthropic API key.

## Architecture

This is a CLI-based DIY PC build assistant powered by the Anthropic Claude API. The project uses a composable multi-agent architecture where each agent is a self-contained unit that can be nested inside a parent agent as a callable tool.

**Entry point** (`app.py:DIYComputer`): A simple REPL loop that reads user input and calls `agent.ProcessNewUserInput()`. Currently wired directly to `MainUnitAgent`.

**Base agent** (`agents/agent.py:Agent`): The core abstraction. Key behaviors:
- `Run()` drives the tool-use loop (up to `maxIter`): calls Claude, processes `tool_use` blocks, appends results, repeats until no tool calls remain.
- `GetTools()` merges `GetAgentTools()` (the agent's own tools) + `GetSubAgentAsTools()` (registered sub-agents exposed as tools).
- `AddSubAgent()` / `__CallSubAgent()`: sub-agents are registered on a parent and callable from the parent's tool-use loop; invocation calls `ConfigureInput()` then `Run()`.
- `GetToolDescripiton()`: lets any agent expose itself as a tool to a parent orchestrator.
- `__PrintContextWindow()`: prints full message history and tool schemas to stdout before each API call, formatted with grey background ANSI codes.
- Tool dispatch via `__CallTool()` → `getattr(self, toolName)` first, then falls back to `__CallSubAgent()`.

**Concrete agents** (`agents/`):
- `mainUnitAgent.py:MainUnitAgent` — recommends core PC components: CPU, GPU, motherboard, RAM, case, storage, PSU. Tools support optional filters (e.g. socket, price range).
- `monitorAgent.py:MonitorAgent` — recommends monitors filtered by resolution, use case (`gaming`/`creative`/`office`), and price.
- `computerBuilderAgent.py:ComputerBuilderAgent` — top-level orchestrator. Registers `MainUnitAgent` and `MonitorAgent` as sub-agents, and adds its own tools for mouse (`GetAvailableMice`) and keyboard (`GetAvailableKeyboards`) with filters for wireless, use case, layout, and price. `app.py` should use this agent as the entry point for full-setup recommendations.

All component data is hardcoded as in-memory dictionaries (no external DB or API calls).

## Adding a new agent

1. Create a new file in `agents/` subclassing `Agent`.
2. Override `GetAgentTools()` to return tool schemas.
3. Override `CallTool()` using `getattr` dispatch.
4. Implement tool methods that return component data dicts.
5. Register it on a parent via `parent.AddSubAgent(new_agent)` to expose it as a tool.
