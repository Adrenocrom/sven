# Sven Project Specification

## Overview
Sven is a Python package that provides an interactive language‑model driven assistant capable of performing on‑the‑fly file operations and simple code editing tasks through tool calls. It is designed to be used from the command line or imported as a library.

## Key Features
- **Interactive chat** using Ollama models with tool‑call support.
- **Built‑in tools** for:
  - Getting current datetime
  - Web searching via DuckDuckGo
  - Retrieving manual pages of Unix utilities
  - Auto‑formatting Python files (via `autopep8`/`black`)
  - Basic Vim‑style file editing (read, search & replace, line replacement, full file replacement).
  - Listing directory contents.
  - Touching files.
- **Prompt sequences** for running multiple tasks in one go.
- **Extensible architecture** – add new tools by adding a function to `available_functions`.

## Architecture
```
├─ sven/
│   ├─ chat.py            # Interactive Chat loop & tool registry
│   ├─ task.py            # Prompt‑sequence runner
│   └─ __init__.py
└─ sven/tools/
    ├─ getdatetime.py
    ├─ websearch.py
    ├─ manpage.py
    ├─ touch.py
    ├─ listfiles.py
    ├─ vim/
    │   ├─ read.py
    │   ├─ edit.py      # searchandreplace, replacefile, replaceline
    │   └─ autoformat.py
```
The *chat* module sends user messages to an Ollama model and processes any tool calls the model requests. Results from tools are appended as a `tool` role in the conversation history.

## Installation
```bash
pip install sven‑0.1.0   # or from source: pip install .
```
Make sure you have an Ollama instance running locally and the required models downloaded (`gpt-oss`, `gemma4`, etc.).

## Usage
### Interactive Mode
```bash
python -m sven.app.main      # runs interactive_chat with default model
```
The assistant will prompt for user input. When it needs a tool, it will automatically call the corresponding function.

### Prompt Sequence
```python
from sven.task import run_prompt_sequence
run_prompt_sequence(
    prompts=[
        "create a spec.md file",
        "list all files in current directory"
    ],
    model="gpt-oss:20b"
)
```
### Custom Model / Options
Both `interactive_chat` and `run_prompt_sequence` accept an `Options` object (from Ollama) to tweak temperature, max tokens, etc.

## Testing
The test suite is located in the `tests/` directory. Run with:
```bash
pytest tests/
```
All tests are currently focused on tool utilities and ensure they return expected results.

---
**Author:** Sven Developer Team

