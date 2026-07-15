# Sven — Project Specification

## 1. Overview

Sven is an autonomous, terminal-based AI agent for software development. It combines a local large language model (LLM) with a tool-calling architecture so that it can plan, execute, and track multi-step tasks on its own. Unlike a simple chatbot, Sven can read and write files, run commands, search the web, manage a task queue, remember skills across sessions, and summarize long conversations to stay within model context limits.

## 2. Goals

- **Autonomous task execution:** Decompose user requests into sub-tasks, track their state, and evaluate success criteria.
- **Developer productivity:** Automate common software engineering workflows such as reading code, editing files, running builds, and searching documentation.
- **Context preservation:** Keep conversations useful even as they grow long, through summarization and persistent memory.
- **Extensibility:** Make it easy to add new tools, agents, and stored knowledge.
- **Local-first operation:** Run against a local Ollama instance by default, keeping data on the user's machine.

## 3. Target Audience

- **Software developers** who want an AI assistant that can work directly with code, files, and repositories.
- **Technical power users** who prefer terminal-based workflows and local LLMs.
- **Teams and individuals** building or maintaining Python, Rust, Java, or general-purpose projects.

## 4. Functional Requirements

### 4.1 Interactive Chat
- Provide a REPL-style terminal interface.
- Load and persist conversation history across sessions.
- Support readline-style command history.

### 4.2 Tool Use
- Expose a set of callable tools to the LLM, including:
  - Filesystem: `read`, `listfiles`, `touch`, `replacefile`, `replaceline`, `searchandreplace`.
  - Search: `websearch`, `webfetch`, `grep`, `find`, `manpage`.
  - Build and validation: `compilefile`, `compilefiles`, `cargo_build`, `maven_clean_install`.
  - Git: `diff`.
  - Utilities: `getdatetime`.
- Execute tool calls returned by the model and feed results back into the conversation.

### 4.3 Task Management
- Maintain a FIFO task queue persisted to JSON.
- Allow adding, listing, canceling, completing, and retrieving the current task.
- Represent tasks with `id`, `description`, `success_definition`, `state`, `plan`, and `raw_data`.

### 4.4 Memory and Skills
- Store reusable knowledge as "skills" with name, description, content, and tags.
- Persist skills as markdown files with YAML frontmatter.
- Support adding, listing, retrieving, updating, deleting, and searching skills.
- Let the agent discover and apply relevant skills during task execution.

### 4.5 Agent Orchestration
- Support multiple agents with distinct system prompts and tool sets.
- Provide keyword-based or LLM-based routing to select the best agent for a task.
- Include a built-in prompt-optimization agent ("Greg") that rewrites user prompts before execution.

### 4.6 Context Management
- Summarize older conversation turns when the message count exceeds a configurable threshold.
- Preserve the most recent messages and a compact summary of earlier context.

### 4.7 Configuration
- Load configuration from a JSON file with profile-specific overrides.
- Allow environment variables to override key settings (`SVEN_MODEL`, `SVEN_PROFILE`, `SVEN_TEMPERATURE`, `SVEN_WORKDIR`, etc.).

## 5. Non-Functional Requirements

- **Local execution:** Primary LLM inference runs through a local Ollama server.
- **Low latency feedback:** Stream model output to the terminal in real time.
- **Persistence:** Task queues, chat history, token usage, configuration, and skills survive restarts.
- **Sandboxing:** Filesystem operations are scoped to a configurable working directory.
- **Observability:** Display token counts per turn and cumulative usage.
- **Maintainability:** Modular Python package with clear separation between core, tools, agents, memory, and configuration.
- **Python version:** Requires Python 3.14 or newer.

## 6. Architecture and Key Components

```
sven/
├── chat.py              # Interactive REPL and prompt preprocessing
├── core.py              # LLM communication, streaming, tool-call processing, summarization
├── agent.py             # Reusable agent abstraction
├── orchestrator.py      # Multi-agent routing
├── config.py            # Configuration loading, profiles, env overrides
├── task.py              # Task data model and JSON serialization
├── tools/task.py        # Task queue operations
├── memory.py            # Skill storage backend (markdown + YAML frontmatter)
├── tools/memory_tools.py# Skill tool wrappers
├── skills.py            # Skill registry and LLM tool definitions (legacy/placeholder)
├── history.py           # Chat history persistence
├── token_counter.py     # Token usage tracking
└── tools/               # Individual tool implementations
```

### Key components

- **`Config`**: Central configuration object loaded from JSON and environment variables.
- **`send()` in `core.py`**: Main LLM loop. Streams responses, handles tool calls, and triggers summarization.
- **`Agent`**: Wraps a system prompt, tool set, and message history for reusable agents.
- **`AgentOrchestrator`**: Routes tasks to registered agents by keyword or via a router agent.
- **`MemoryStore`**: Persists skills as `SKILL.md` files under `~/.local/share/sven/skills/`.
- **Tool modules**: Each tool is a plain Python function returning a standardized `{"success", "message", "data"}` dictionary.

## 7. Data Models and Interfaces

### 7.1 Task
```python
@dataclass
class Task:
    id: str
    description: str
    success_defintion: str   # note: intentional typo preserved from source
    state: str
    plan: str
    raw_data: str
```

### 7.2 Skill
```python
@dataclass
class Skill:
    id: str
    name: str
    description: str
    content: str
    tags: list[str]
    created_at: str
```

### 7.3 Config
```python
@dataclass
class Config:
    data_dir: str            # default: ~/.local/share/sven
    config_dir: str          # default: ~/.config/sven
    token_stats_file: str
    model: str
    host: str
    keep_alive: str
    system_prompt: str
    options: Options         # temperature, num_ctx, repeat_penalty
    keep_recent_count: int
    max_messages: int
```

### 7.4 Tool Result
All tools return a dictionary of the form:
```python
{
    "success": bool,
    "message": str,
    "data": Any | None
}
```

### 7.5 Conversation Message
Messages follow the Ollama chat format:
```python
{"role": "system" | "user" | "assistant" | "tool", "content": str}
```
Assistant messages with tool calls include an additional `tool_calls` field; tool result messages include `tool_name`.

## 8. Assumptions and Constraints

- An Ollama server is available at the configured host (default `localhost`).
- The user has a Python 3.14+ environment and uses Poetry for dependency management.
- Filesystem tools operate relative to `SVEN_WORKDIR` or the current directory.
- The agent has permission to run shell commands for build tools (`cargo`, `maven`, `python -m py_compile`, `git`).
- Skill names are filesystem-safe after sanitization.
- The task queue is stored in a single JSON file (`tasks.json`) in the working directory.
- Token usage is tracked globally and persisted to `tokens.json` in the data directory.

## 9. Open Questions and Next Steps

- Should the task queue support priorities, deadlines, or dependencies between tasks?
- Should skills be versioned or support provenance (e.g., source URL, confidence score)?
- Is the legacy `skills.py` registry still needed, or should it be merged with the `MemoryStore` backend?
- Should tool results be richer (e.g., structured schemas, streaming output, progress updates)?
- Should Sven support remote LLM providers as a fallback or alternative to Ollama?
- Should there be a plugin or manifest system for registering custom tools without editing source code?
- Add comprehensive tests for tools, agents, orchestrator, and memory store.
- Improve error handling and recovery when the Ollama server is unreachable.
- Add a CLI flag parser so options like `--workdir` and `--profile` can be passed directly.
