# Sven – Autonomous AI Software‑Development Agent

Sven is an autonomous AI agent designed to assist with software development tasks by leveraging a tool‑calling architecture. Unlike standard chat interfaces, Sven can manage its own goals through a structured task system, allowing it to break down complex requests into actionable steps and track progress autonomously.

## Features

- **Agentic Task Management** – automatically decomposes goals into sub‑tasks, tracks state, and evaluates success criteria.
- **Tool Integration** – built‑in tools for web search, filesystem I/O, git, man pages, etc.
- **Advanced Context Management** – conversation summarisation to stay within model token limits.
- **Configurable Environment** – profiles (`dev`, `prod`, …) via `config.json` and environment variables.

## Configuration

Sven’s behaviour can be customised via `config.json` **or** environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `SVEN_MODEL` | Ollama model to use | `gemma4:12b` |
| `SVEN_PROFILE` | Configuration profile name (`dev`, `prod`, …) | `dev` |
| `SVEN_TEMPERATURE` | Sampling temperature for the LLM | `0.0` |
| `SVEN_WORKDIR` | **Custom working directory** (see below) | Project root (`.`) |

### Example `config.json`

```json
{
  "model": "gemma4:12b",
  "system_prompt": "You are a Senior software developer called Sven.",
  "keep_recent_count": 5,
  "max_messages": 20,
  "profiles": {
    "dev": { "model": "gemma4:12b" },
    "prod": { "model": "gemma4:7b", "temperature": 0.2 }
  }
}
```

## Installation

```bash
poetry install
```

## Usage

Start the interactive agent:

```bash
poetry run sven
```

### Running with a Custom Working Directory

Sven reads and writes files relative to its **working directory**. By default this is the directory where you launch the command (`.`). If you need Sven to operate on a different directory (e.g., a cloned repo located elsewhere), you can override the working directory in two ways:

#### 1. Environment Variable (recommended)

```bash
export SVEN_WORKDIR=/path/to/your/project
poetry run sven
```

or in a single command:

```bash
SVEN_WORKDIR=/path/to/your/project poetry run sven
```

#### 2. Command‑line flag (if the entry‑point supports it)

If the `sven` entry‑point has been extended to accept `--workdir` (future‑proof), you can run:

```bash
poetry run sven --workdir /path/to/your/project
```

> **Note:** At the moment the project only honours the `SVEN_WORKDIR` environment variable. The flag is documented here for possible future versions.

#### How it works internally

The `Config` class loads the value of `SVEN_WORKDIR` (if set) and stores it as `config.work_dir`. Every tool that accesses the filesystem (`read`, `write`, `touch`, `listfiles`, etc.) prefixes paths with this base directory, ensuring all file operations stay sandboxed to the chosen folder.

### Example workflow

```bash
# Suppose you have a repository at ~/my‑app
SVEN_WORKDIR=~/my‑app poetry run sven
# Inside the interactive session you can now do:
> read src/sven/core.py
> write src/sven/new_module.py "print('Hello from Sven')"
```

## Development

1. Clone the repository.
2. Install dependencies: `poetry install`.
3. Run the test suite (if present): `pytest`.
4. Make your changes, commit, and open a PR.

---

*Happy coding with Sven!*

---

### Implementation notes (for maintainers)

The addition only required modifying `README.md`. No source‑code changes were needed because the agent already reads the `SVEN_WORKDIR` variable (see `src/sven/config.py`). If you ever add a CLI flag for the workdir, update the entry‑point accordingly.