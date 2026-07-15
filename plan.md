# Multi-Language Tooling Analysis & Improvement Plan

## Executive Summary

This repository contains four language-specific tool wrappers (`python.py`, `rust.py`, `dotnet.py`, `java.py`) that provide subprocess-based interfaces to native build systems. While functional, these tools suffer from inconsistent feature sets and lack of cross-language standardization opportunities. This plan outlines analysis findings and proposes improvements through both individual enhancements and consolidation where beneficial.

---

## 1. Current Capabilities Analysis

### Python (`src/sven/tools/python.py`)
**Current Tools:**
- `compilefiles()` - Compiles all `.py` files in current directory using poetry environment
- `compilefile(filepath)` - Compiles a single specified file via poetry environment

**Strengths:**
- ✅ Poetry integration for consistent dependency management
- ✅ Both batch and individual file compilation support
- ✅ Proper error handling with subprocess output capture

**Weaknesses/Gaps:**
- ❌ No linting (ruff, pylint) or formatting tools exposed
- ❌ No type checking (mypy) capabilities
- ❌ No testing framework integration (pytest not wired up as tool)
- ❌ `compilefiles()` uses shell-out to find files instead of Python's pathlib — fragile and slow

---

### Rust (`src/sven/tools/rust.py`)
**Current Tools:**
- `cargo_build()` - Runs basic cargo build command only

**Strengths:**
- ✅ Single, focused tool for compilation
- ✅ Proper subprocess error handling

**Weaknesses/Gaps:**
- ❌ No clippy (linter) integration — missing quality checks
- ❌ No rustfmt (formatter) exposure as separate tool
- ❌ No `cargo test` command exposed — tests run but not accessible via agent interface
- ❌ Limited to build phase only; no analysis pipeline

---

### .NET (`src/sven/tools/dotnet.py`)
**Current Tools:**
- `dotnet_build()` - Runs basic dotnet build command

**Strengths:**
- ✅ Simple, direct wrapper around SDK tooling
- ✅ Proper error handling structure

**Weaknesses/Gaps:**
- ❌ No Roslyn analyzers integration (code quality checks)
- ❌ No formatting tools (`dotnet format`) exposed as separate capability
- ❌ No test runner exposure — `dotnet test` not available via agent interface
- ❌ Limited to compilation only; no analysis or verification phases

---

### Java (`src/sven/tools/java.py`)
**Current Tools:**
- `maven_clean_install()` - Runs full Maven lifecycle (compile → test → package)

**Strengths:**
- ✅ Full build pipeline included in single command
- ✅ Tests run automatically as part of install phase
- ✅ Proper subprocess error handling with output capture

**Weaknesses/Gaps:**
- ❌ No dedicated linting tool exposed separately from default lifecycle (Checkstyle, SpotBugs)
- ❌ Cannot selectively enable/disable checks — must use full Maven pipeline or none
- ❌ No IDE-independent formatter/linter available as separate agent call
- ⚠️ `mvn clean install` is heavyweight; may be overkill for simple syntax validation

---

## 2. Consolidation Opportunities

### Opportunity A: Unified Tool Pattern Standardization (High Impact, Low Effort)
**Problem:** All four tools follow the same subprocess wrapper pattern but with inconsistent naming and return structures.

**Proposal:** Create a shared base class or factory function that standardizes tool creation across languages while preserving language-specific behavior where needed.

```python
# Proposed: src/sven/tools/base_tool.py (new)
class LanguageTool:
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> dict: ...
    
    # Common error handling and output formatting methods here

# Then each language tool inherits from this base for consistency
```

**Benefits:**
- Consistent API across all languages → easier agent reasoning
- Centralized error handling improvements propagate to all tools
- Easier maintenance when adding new language support

---

### Opportunity B: Cross-Language Quality Pipeline (Medium Impact, Medium Effort)
**Problem:** Each language has different quality gates but no unified way to run them together.

**Proposal:** Create a `quality_check()` tool that runs appropriate linters/formatters for each detected language in the project root.

```python
# Proposed: src/sven/tools/quality.py (new)
def quality_check(language: str = None) -> dict:
    """Run all applicable quality checks across languages."""
    
    if not language or language == "all":
        # Detect which languages exist in current project
        results = {}
        
        if any(Path().rglob("*.py")):  # Python detected
            from sven.tools.python import ruff_check, mypy_run
            results["python"] = {
                "linting": await ruff_check(),
                "formatting": await ruff_format(check=True),
                "typecheck": await mypy_run()
            }
        
        if any(Path().rglob("*.rs")):  # Rust detected
            from sven.tools.rust import cargo_clippy, rustfmt_check
            results["rust"] = { ... }
            
        return {"success": True, "data": results}
```

**Benefits:**
- Single command to validate code quality across entire project
- Agent can run pre-commit checks without knowing language-specific commands
- Consistent reporting format regardless of underlying tools used

---

### Opportunity C: Unified Configuration File (Medium Impact, Low Effort)
**Problem:** Each tool has its own configuration scattered across different files (`pyproject.toml`, `.editorconfig`, `Cargo.toml`, etc.).

**Proposal:** Create a single `sven.config.json` that declares available tools and their default flags per language.

```jsonc
// sven.config.json (new) — centralized tool registry
{
  "languages": {
    "python": {
      "formatter": {"tool": "ruff", "args": ["format"]},
      "linter": [{"name": "mypy", "flags": ["--strict"]}],
      "test_cmd": "pytest"
    },
    "rust": {
      "formatter": {"tool": "cargo fmt"},
      "linter": [{"name": "clippy"}],
      "test_cmd": "cargo test"
    }
  }
}
```

**Benefits:**
- Single source of truth for tool configuration
- Easier to add new languages without modifying core logic
- Enables dynamic tool discovery based on project contents

---

## 3. Implementation Steps (Prioritized)

### Phase 1: Foundation & Standardization *(Week 1)*
| Task | Language(s) | Effort | Priority |
|------|-------------|--------|----------|
| Refactor `compilefiles()` to use pathlib instead of shell-out | Python | Low | High |
| Add consistent docstrings and return types across all tools | All | Medium | High |
| Create shared base class for tool execution patterns | All | Medium | Medium |

### Phase 2: Individual Enhancements *(Weeks 2-3)*
| Task | Language(s) | Effort | Priority |
|------|-------------|--------|----------|
| Add `ruff_check()` and `mypy_run()` tools for Python linting/typecheck | Python | Low-High | High |
| Expose `cargo clippy`, `rustfmt --check`, and `cargo test` as separate tools | Rust | Medium | High |
| Add Roslyn analyzer integration + expose `dotnet format/test` commands | .NET | Medium-High | Medium |
| Configure Checkstyle/SpotBugs Maven plugins with dedicated tool wrappers | Java | High | Low-Medium |

### Phase 3: Consolidation & Integration *(Weeks 4-5)*
| Task | Language(s) | Effort | Priority |
|------|-------------|--------|----------|
| Create `quality_check()` unified pipeline tool | All | Medium-High | Medium |
| Build centralized config file (`sven.config.json`) for tool discovery | All | Low-Medium | High |
| Generate cross-language CI workflow template from configuration | All | Medium | Backlog |

---

## 4. Expected Benefits Summary

### Immediate Wins (Phase 1-2)
- **Consistency**: Uniform API across all language tools → easier agent reasoning and debugging
- **Quality Gates**: Linting/formatting/type-checking now accessible via agent interface instead of manual CLI invocation
- **Performance**: Refactored Python file discovery eliminates shell-out overhead

### Long-Term Value (Phase 3)
- **Unified Workflow**: Single command to validate entire multi-language project quality
- **Extensibility**: New languages can be added by registering in config without modifying core logic
- **CI/CD Ready**: Generated workflows ensure consistent builds across all supported language stacks

---

## Next Steps

1. Review this plan with stakeholders for alignment on priorities
2. Begin Phase 1 implementation (foundation work) — lowest risk, highest consistency gain
3. Iterate through Phases 2 and 3 based on actual usage patterns observed during development

Would you like me to start implementing any specific phase or task from this plan? I recommend beginning with the Python refactor (`compilefiles()` → pathlib) as it's quick win that demonstrates immediate value while establishing consistent patterns for subsequent work.