# Sven Project Improvement Plan

## Overview
Sven is a lightweight AI‑assistant framework that exposes a set of tools (web search, file manipulation, task queue, etc.) and runs an interactive chat loop. The current code base works but has several areas where maintainability, reliability, and extensibility can be improved.

The goal of this plan is to:
1. **Make the project production‑ready** – robust error handling, logging, type safety.
2. **Improve developer experience** – clear documentation, tests, CI/CD, packaging.
3. **Add missing features** – configuration management, graceful shutdown, plugin architecture.
4. **Prepare for scaling** – async support, better state persistence, performance profiling.

---

## Current State Snapshot
| Area | Status |
|------|--------|
| Code quality | Mostly functional but lacks type hints and linting |
| Tests | Very few unit tests; integration tests missing |
| Documentation | README covers basics; no API docs or contribution guide |
| Packaging | Poetry used, wheel built, but no CI pipeline |
| Logging | Uses `print`; no structured logging |
| Error handling | Exceptions bubble up; no graceful recovery |
| State persistence | Basic JSON file in `storage_manager.py` – works but not robust |
| Extensibility | Tools are hard‑coded; adding a new tool requires editing core logic |

---

## High‑Level Goals
1. **Add static typing** (PEP 484) and run `mypy`.
2. **Introduce linting & formatting** – `ruff`, `black`.
3. **Write comprehensive tests** – unit, integration, end‑to‑end.
4. **Implement structured logging** with `loguru` or Python’s `logging` module.
5. **Create a plugin system** for tools so new functionality can be added without touching core.
6. **Add graceful shutdown & signal handling**.
7. **Improve configuration management** – load from `.env`, support overrides.
8. **Set up CI/CD** with GitHub Actions: lint, test, build wheel, publish to TestPyPI.
9. **Document public API** using Sphinx or MkDocs.
10. **Add async support** for I/O‑bound tools (web search, file ops) to keep the chat responsive.

---

## Detailed Improvement Plan
### 1. Static Typing & Linting
- Add `typing` annotations throughout the codebase.
- Create a `pyproject.toml` section for `mypy` configuration.
- Run `ruff check --fix` to auto‑format and lint.
- Enforce type checks in CI.

### 2. Logging
- Replace all `print` statements with `logging.getLogger(__name__)` calls.
- Configure a default logger that outputs JSON for easier parsing.
- Add log levels: DEBUG, INFO, WARNING, ERROR.
- Expose a CLI flag to set the log level.

### 3. Configuration Management
- Introduce a `Config` dataclass in `src/sven/config.py` with defaults.
- Load from `config.json`, `.env`, or command‑line arguments.
- Provide validation (e.g., required keys, type checks).

### 4. State Persistence Enhancements
- Refactor `storage_manager.py` to use a context manager and handle concurrent writes.
- Add schema validation using `pydantic` or `jsonschema`.
- Store state in a dedicated directory (`~/.sven/`).
- Implement versioning of the state file.

### 5. Plugin Architecture for Tools
- Define an abstract base class `BaseTool` with `name`, `description`, and `execute()`.
- Create a registry that automatically discovers tools via entry points or a simple discovery function.
- Update core loop to iterate over registered tools instead of hard‑coded imports.
- Provide documentation on how to add a new tool.

### 6. Graceful Shutdown & Signal Handling
- Catch `SIGINT` and `SIGTERM` in the main loop.
- Flush pending tasks, save state, close resources.
- Ensure that long‑running tools can be cancelled via a timeout or cancellation token.

### 7. Async Support
- Convert I/O‑bound tool implementations to async functions.
- Use `asyncio.run()` for the main event loop.
- Update core logic to await tool execution.
- Provide backward compatibility for synchronous tools.

### 8. Testing Strategy
- **Unit tests**: each tool, storage manager, config loader.
- **Integration tests**: simulate a full chat session with mocked external services (web search, git).
- **End‑to‑end**: run the CLI and verify that tasks are queued and executed correctly.
- Use `pytest` fixtures for setup/teardown.
- Add coverage thresholds in CI.

### 9. Documentation & Contribution Guide
- Generate API docs with Sphinx (autodoc) or MkDocs.
- Write a `CONTRIBUTING.md` explaining the development workflow, linting rules, and testing.
- Update README to include installation, usage, and example workflows.

### 10. CI/CD Pipeline
- GitHub Actions workflow:
  - Checkout code.
  - Set up Python (3.11+).
  - Install dependencies via Poetry.
  - Run `ruff`, `mypy`, `pytest`.
  - Build wheel and source distribution.
  - Publish to TestPyPI on every push to `main`.
- Optionally, create a release workflow that publishes to PyPI when a tag is pushed.

---

## Implementation Roadmap (Sprint‑Based)
| Sprint | Milestone |
|--------|-----------|
| 1 | Add typing, linting, and basic tests. |
| 2 | Implement logging, config loader, and state persistence improvements. |
| 3 | Build plugin system for tools; refactor core loop. |
| 4 | Add async support and graceful shutdown. |
| 5 | Write comprehensive integration tests and CI pipeline. |
| 6 | Documentation, contribution guide, and release process. |

---

## Deliverables
- Updated codebase with type hints, linting, logging.
- New `Config` dataclass and environment support.
- Refactored `storage_manager.py` with schema validation.
- Plugin architecture for tools.
- Async-enabled core loop.
- Full test suite (≥80 % coverage).
- CI workflow files (`.github/workflows/ci.yml`).
- Documentation site built with MkDocs or Sphinx.
- Release notes and changelog template.

---

## Next Steps
1. Create a new branch `improve-project`.
2. Implement typing and linting first.
3. Commit incremental changes and push to GitHub.
4. Open a PR for review.

Happy coding!
