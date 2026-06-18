# Sven

Sven is an autonomous AI agent designed to assist with software development tasks by leveraging a tool-calling architecture. Unlike standard chat interfaces, Sven can manage its own goals through a structured task system, allowing it to break down complex requests into actionable steps and track progress autonomously.

## Features

- **Agentic Task Management**: Automatically decomposes complex goals into sub-tasks, manages state transitions, and tracks success criteria.
- **Tool Integration**: Equipped with a suite of built-in tools:
    - **Web Search**: Real-time information retrieval from the internet.
    - **File System Operations**: Read, write, and modify files directly.
    - **System Utilities**: Access to `man` pages, `git` commands, and more.
- **Advanced Context Management**: Intelligent conversation summarization to maintain context over long interactions while staying within model token limits.
- **Configurable Environment**: Support for multiple profiles (e.g., 'dev', 'prod') via `config.json` and environment variables.

## Configuration

Sven's behavior can be customized via `config.json` or environment variables:
- `SVEN_MODEL`: The Ollama model to use (default: `gemma4:12b`).
- `SVEN_PROFILE`: Select a specific configuration profile.
- `SVEN_TEMPERATURE`: Adjust the creativity of the responses.

## Installation

To install Sven using Poetry:

```bash
poetry install
```

## Usage

Start the interactive agent:

```bash
poetry run sven
```

## Development

If you want to contribute or develop features, follow these steps:

1. Clone the repository.
2. Install dependencies with `poetry install`.
3. Run tests using `pytest` (if applicable).
4. Submit your changes via a pull request.
