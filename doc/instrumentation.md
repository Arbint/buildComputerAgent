# Instrumentation with OpenTelemetry and Langfuse

This document walks through adding observability to the buildcomputer agent using
OpenTelemetry (OTel) as the instrumentation layer and Langfuse as the backend and
web UI.

## Architecture

```
Agent code
    │
    ▼
OpenTelemetry SDK          ← vendor-neutral instrumentation standard
(spans, attributes, events)
    │
    ▼
OTLP HTTP Exporter         ← ships spans over HTTP/protobuf
    │
    ▼
Langfuse OTLP endpoint     ← /api/public/otel/v1/traces
    │
    ▼
Langfuse Web UI            ← trace tree, generation viewer, token counts, cost
```

The key benefit of this approach over using the Langfuse SDK directly is
vendor neutrality: if you later want to switch to Jaeger, Grafana Tempo, or
Honeycomb, you change the exporter endpoint — not the instrumentation code.

---

## Prerequisites

- Python 3.12+
- `uv` for dependency management
- Docker (only if self-hosting Langfuse)
- A Langfuse account (cloud) or a running Langfuse instance (self-hosted)

---

## Step 1 — Get Langfuse running

### Option A: Langfuse Cloud (recommended for getting started)

1. Go to [cloud.langfuse.com](https://cloud.langfuse.com) and create a free account.
2. Create a new project.
3. Go to **Settings → API Keys** and create a new key pair. Copy the
   **Public Key** and **Secret Key** — you will need them in Step 3.

The host for cloud is `https://cloud.langfuse.com`.

### Option B: Self-hosted with Docker

Langfuse v2 can be run locally with a single Docker Compose command:

```bash
git clone https://github.com/langfuse/langfuse.git
cd langfuse
docker compose up -d
```

The UI will be available at `http://localhost:3000`.

On first launch, Langfuse shows a registration form — create your admin account
there. There are no hardcoded default credentials. Once logged in, create a
project and copy the API keys from **Settings → API Keys**.

The host for self-hosted is `http://localhost:3000`.

---

## Step 2 — Add the OTLP exporter dependency

The project already has `opentelemetry-api` and `opentelemetry-sdk`. Add the
HTTP exporter package to `pyproject.toml`:

```toml
dependencies = [
    "anthropic>=0.96.0",
    "opentelemetry-api>=1.41.1",
    "opentelemetry-sdk>=1.41.1",
    "opentelemetry-exporter-otlp-proto-http>=1.41.1",
]
```

Then install:

```bash
uv sync
```

---

## Step 3 — Set environment variables

Langfuse authenticates OTLP requests using HTTP Basic Auth. Set these three
variables in your shell or in a `.env` file before running the agent:

```bash
export LANGFUSE_PUBLIC_KEY="pk-lf-..."
export LANGFUSE_SECRET_KEY="sk-lf-..."
export LANGFUSE_HOST="https://cloud.langfuse.com"   # or http://localhost:3000
```

The `CLAUDE_API_KEY` variable (already required) stays the same.

---

## Step 4 — Update `instrumentation.py`

Replace the contents of
`src/buildcomputer/instrumentation/instrumentation.py` with the following.
This replaces the `ConsoleSpanExporter` placeholder with the real Langfuse
OTLP exporter:

```python
import base64
import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter


def setup_tracing() -> trace.Tracer:
    public_key = os.environ["LANGFUSE_PUBLIC_KEY"]
    secret_key = os.environ["LANGFUSE_SECRET_KEY"]
    host = os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com")

    credentials = base64.b64encode(f"{public_key}:{secret_key}".encode()).decode()

    exporter = OTLPSpanExporter(
        endpoint=f"{host}/api/public/otel/v1/traces",
        headers={"Authorization": f"Basic {credentials}"},
    )

    provider = TracerProvider()
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    return trace.get_tracer("buildcomputer")
```

### Why `BatchSpanProcessor`?

`BatchSpanProcessor` buffers finished spans in memory and flushes them to the
exporter in the background. This is non-blocking — your agent code does not
wait for the HTTP call to Langfuse before continuing. Never use
`SimpleSpanProcessor` in production: it makes a synchronous HTTP request on
every span end, which adds latency to every tool call.

---

## Step 5 — Initialize tracing in `app.py`

Call `setup_tracing()` once at startup, before any agent code runs. The
returned tracer is stored globally by the OTel SDK so all subsequent
`trace.get_tracer(...)` calls resolve to the same configured provider.

```python
from buildcomputer.instrumentation.instrumentation import setup_tracing
from buildcomputer.agents.computerBuilderAgent import ComputerBuilderAgent


def DIYComputer():
    setup_tracing()   # must be called before agents are created

    agent = ComputerBuilderAgent()
    agent.ProcessNewUserInput("hi")

    maxIter = 10
    iter = 0
    while iter < maxIter:
        userInput = input("\n>>> ")
        if userInput.lower() == "exit":
            break
        agent.ProcessNewUserInput(userInput)
        iter += 1


def main():
    DIYComputer()
```

---

## Step 6 — Instrument `agent.py`

This is where all the instrumentation lives. Four changes are needed.

### 6a — Add the tracer at the top of the file

After the existing imports, add:

```python
from opentelemetry import trace

_tracer = trace.get_tracer("buildcomputer.agent")
```

`_tracer` is a module-level singleton. Because `setup_tracing()` runs first
in `app.py`, the global OTel provider is already configured by the time this
module is imported and the tracer resolves to the right exporter.

### 6b — `ProcessNewUserInput` — trace root

This creates the top-level trace entry in Langfuse. One trace appears per user
message. Wrap the method body in a span:

```python
def ProcessNewUserInput(self, userInput):
    with _tracer.start_as_current_span(self.name) as span:
        span.set_attribute("agent.name", self.name)
        self.messages.append({"role": "user", "content": userInput})
        self.Run()
```

### 6c — `Run` — per-agent execution span

This span covers all iterations (LLM calls + tool calls) for one agent
invocation. Replace the method with:

```python
def Run(self):
    with _tracer.start_as_current_span(f"{self.name}.run") as span:
        client = Anthropic(api_key=GetAPIKey())

        iter = 0
        response = None
        while iter < self.maxIter:
            iter += 1

            print(f"\n------- Iteration {iter} -------")
            self.__PrintContextWindow()

            response = self._CreateMessage(client, self.messages, self.GetTools())

            toolUseBlocks = [block for block in response.content if block.type == "tool_use"]
            textBlocks = [block for block in response.content if block.type == "text"]

            for textBlock in textBlocks:
                print(f"assistant: {textBlock.text}")

            self.messages.append({"role": "assistant", "content": response.content})

            if toolUseBlocks:
                toolResults = self.__ProcessToolUse(toolUseBlocks)
                self.messages.append({"role": "user", "content": toolResults})
            else:
                break

        finalResponse = "".join(
            block.text for block in response.content if block.type == "text"
        ) or "no response"

        span.set_attribute("agent.iterations", iter)
        return finalResponse
```

### 6d — `_CreateMessage` (new method) — LLM generation span

Extract the `client.messages.create(...)` call out of `Run` into this new
private method. This is the most important span: the `gen_ai.*` attributes
tell Langfuse to render it as a generation with token counts and cost, and
the two `add_event` calls attach the full prompt and completion text so they
appear in the generation detail view.

```python
def _CreateMessage(self, client, messages, tools):
    with _tracer.start_as_current_span("claude", kind=trace.SpanKind.CLIENT) as span:
        span.set_attribute("gen_ai.system", "anthropic")
        span.set_attribute("gen_ai.request.model", "claude-sonnet-4-6")
        span.set_attribute("gen_ai.request.max_tokens", 1024)

        # Attach the full prompt so it appears in the Langfuse generation viewer.
        # OTel semantic conventions use events (not attributes) for large payloads.
        span.add_event("gen_ai.prompt", {"content": json.dumps(messages, default=str)})

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=self.system,
            messages=messages,
            tools=tools,
        )

        span.set_attribute("gen_ai.usage.input_tokens", response.usage.input_tokens)
        span.set_attribute("gen_ai.usage.output_tokens", response.usage.output_tokens)
        span.set_attribute("gen_ai.response.model", response.model)

        # Attach the completion text.
        completion = " ".join(b.text for b in response.content if b.type == "text")
        span.add_event("gen_ai.completion", {"content": completion})

        return response
```

`default=str` in `json.dumps` is a safety net: some message blocks in the
conversation history are Anthropic SDK objects (not plain dicts) after tool
calls, and `str()` prevents a serialization error without losing information.

### 6e — `__ProcessToolUse` — one child span per tool call

Replace the existing `__ProcessToolUse` with this version, which wraps each
tool call in its own span. Sub-agent calls are also caught here — when
`__CallTool` falls through to `__CallSubAgent`, the sub-agent's `Run()` span
(from 6c) automatically nests underneath because OTel propagates context via
Python's `contextvars`:

```python
def __ProcessToolUse(self, toolUseBlocks):
    toolResults = []
    for toolUseBlock in toolUseBlocks:
        print(f"----> Calling: {toolUseBlock.name}")
        print(f"args: {toolUseBlock.input}")

        with _tracer.start_as_current_span(f"tool.{toolUseBlock.name}") as span:
            span.set_attribute("tool.name", toolUseBlock.name)
            span.set_attribute("tool.input", json.dumps(toolUseBlock.input))

            result = self.__CallTool(toolName=toolUseBlock.name, **toolUseBlock.input)

            span.set_attribute("tool.output", json.dumps(result, default=str) if result else "")
            toolResults.append({
                "type": "tool_result",
                "tool_use_id": toolUseBlock.id,
                "content": json.dumps(result),
            })

    return toolResults
```

---

## What the trace tree looks like in Langfuse

After running the agent and asking a question, open the Langfuse UI and go to
**Traces**. Each user message appears as one trace. Expanding it shows:

```
ComputerBuilderAgent                      ← ProcessNewUserInput span (trace root)
  ComputerBuilderAgent.run                ← Run span
    claude  [generation]                  ← _CreateMessage: model, tokens, cost,
    |                                       prompt text, completion text
    tool.GetAvailableMice                 ← __ProcessToolUse span
    tool.GetAvailableKeyboards
    tool.MainUnitAgent                    ← sub-agent call
      MainUnitAgent.run
        claude  [generation]
        tool.CPUAgent
          CPUAgent.run
            claude  [generation]
    tool.MonitorAgent
      MonitorAgent.run
        claude  [generation]
```

Clicking any `[generation]` node shows the full prompt messages and completion
text from the `add_event` calls, along with token counts and the cost
Langfuse calculates from the model name and token usage.

---

## Troubleshooting

**No traces appearing in the UI**

- Confirm env vars are set: `echo $LANGFUSE_PUBLIC_KEY`
- The `BatchSpanProcessor` flushes on a timer (default 5 seconds) or when the
  process exits cleanly. If you kill the process with `Ctrl+C` mid-run, spans
  buffered in memory may not flush. Call `provider.force_flush()` before exit,
  or wait a few seconds after the agent finishes before closing.
- Check the Langfuse project matches the key pair you configured.

**`KeyError: LANGFUSE_PUBLIC_KEY`**

The `setup_tracing()` function reads env vars at call time. Make sure they are
exported before running `uv run buildcomputer`, not just defined in a file
that isn't sourced.

**Generation nodes show empty prompt/completion**

The `add_event` calls in `_CreateMessage` must happen inside the
`start_as_current_span` context manager. If the span is ended before the
events are added, they are dropped.

**`json.dumps` serialization errors on messages**

Some entries in `self.messages` after a tool-use round-trip contain Anthropic
SDK objects (`ToolUseBlock`, etc.) rather than plain dicts. The `default=str`
argument in `json.dumps(messages, default=str)` handles this — if you see
serialization errors, check that argument is present.
