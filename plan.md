# Sven Implementation Plan

## 1. Goal
Implement the improvements outlined in *improv.md* while keeping the existing functionality of **Sven** intact. The plan focuses on:
- Unified tool response format.
- Robust error handling and logging.
- Advanced file‑editing capabilities (streaming, regex, multi‑line support).
- Argument validation for tool calls.
- CLI enhancements (model selection, temperature, dry‑run). 
- Expanded unit tests and documentation.

## 2. Current Architecture Recap
```
├─ sven/
│   ├─ chat.py          # interactive loop & tool registry
│   ├─ task.py          # prompt‑sequence runner
│   └─ __init__.py
└─ sven/tools/
    ├─ getdatetime.py
    ├─ websearch.py
    ├─ manpage.py
    ├─ touch.py
    ├─ listfiles.py
    └─ vim/
        ├─ read.py
        ├─ edit.py      # searchandreplace, replacefile, replaceline
        └─ autoformat.py
```
Each tool currently returns a raw value (`str`, `dict`, etc.). The chat loop simply forwards this back to the model as part of the conversation.

## 3. Proposed Architecture Enhancements
1. **Unified Tool Response Schema**
   ```python
   {
       "success": bool,
       "message": str,          # human readable description
       "data": any | None
   }
   ```
   All tools will wrap their output in this JSON‑serialisable dict.
2. **Centralized Error Handling** – A decorator `@tool_handler` that catches exceptions and converts them into a failure response with a clear error message.
3. **Logging Layer** – Use the standard `logging` module to write INFO/ERROR logs to `sven.log`. Log tool invocations, parameters, and failures.
4. **Editing Enhancements**
   * Implement streaming I/O for large files in `vim/edit.py` using memory‑mapped files or temporary buffers.
   * Add optional regex flag (`use_regex: bool`) and multi‑line support for `searchandreplace`.
   * Provide a `--dry-run` flag that returns the would‑be changes without writing.
5. **Argument Validation** – Create a schema validator (simple type checks) per tool; if validation fails, return an error response instead of raising.
6. **CLI Options** – Extend `app/main.py` to accept:
   * `--model <name>`
   * `--temperature <float>`
   * `--dry-run`
   * `--log-level {debug,info,warn,error}`
7. **Caching Layer** – Simple in‑memory LRU cache for websearch results within a session.
8. **Encoding Support** – File read/write helpers that auto‑detect or allow specifying encoding.

## 4. Implementation Roadmap (High Level)
| Phase | Milestone | Tasks | Deliverable |
|-------|-----------|-------|-------------|
| 1 | Response Wrapper & Decorator | - Define `ToolResponse` dataclass.<br>- Implement `tool_handler` decorator.<br>- Update all existing tool modules to use the wrapper. | Updated tool API, tests for response schema. |
| 2 | Logging & Error Handling | - Configure global logger.<br>- Add logging statements in each tool and chat loop.<br>- Verify error logs. | `sven.log` with detailed trace. |
| 3 | Editing Enhancements | - Refactor `vim/edit.py`: streaming, regex flag, dry‑run support.<br>- Update docs & tests. | Robust file editing tools. |
| 4 | Validation Layer | - Create a simple schema validation helper.<br>- Apply to all tools. | Safer tool calls, user friendly error messages. |
| 5 | CLI Enhancements | - Modify `app/main.py` argument parser.<br>- Wire options into chat and task runner. | User can configure model/temperature/log‑level/dry‑run from CLI. |
| 6 | Caching & Performance | - Implement LRU cache for websearch.<br>- Benchmark impact. | Faster repeated searches, reduced latency. |
| 7 | Encoding & Internationalization | - Update file read/write helpers to detect encoding or accept parameter.<br>- Add tests for non‑UTF8 files. | Support for diverse encodings. |
| 8 | Tests & Documentation | - Expand `tests/` covering new features and edge cases.<br>- Update README, help output, docstrings. | Comprehensive test suite, user documentation. |

## 5. Dependency Management & Tooling
- **Python 3.10+** (type hints, dataclasses).
- **Pydantic** or simple custom validators for schema enforcement.
- **Cachetools** for LRU caching (optional, can be lightweight implementation).<br>
- **Black** for code formatting and `autopep8` integration remains unchanged.<br>
- Ensure all dependencies are listed in `setup.cfg` / `pyproject.toml`.

## 6. Potential Risks & Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| Changing tool signature may break existing users. | Medium | Provide a backward‑compatible wrapper or deprecation period in the release notes. |
| Logging could flood disk space with large volumes of data. | Low | Rotate logs after size threshold; provide `--log-level` to reduce verbosity. |
| Performance hit when streaming large files. | High | Benchmark and profile; offer a `--stream` flag toggle. |

## 7. Success Criteria
- All existing tests pass and new tests cover the added features.
- The interactive chat can successfully call tools with the new schema without crashes.
- CLI options work as documented; dry‑run mode correctly shows changes.
- Log file contains detailed trace for debugging failures.
- Websearch results are cached within a session, reducing latency on repeated queries.

---
## 8. Next Steps
1. Commit this plan to `plan.md` (done).
2. Create a new Git branch `feature/improvement-plan`.
3. Start Phase 1 implementation in the order outlined above.
4. Continuously integrate and test after each phase.
5. Once all phases are complete, create a pull request for review.

