# MCP Tree-Sitter Server — Enhancement Task List

## P2 — Architecture

### TASK-06: Remove runtime imports used to break circular dependencies
- **Files**: `cache/parser_cache.py:56–61`, `config.py:337–340`, `language/registry.py:70–80`
- Resolve the root cause by refactoring module dependencies
- Move shared types/interfaces to a `core.py` or `types.py` module that nothing else depends on
- Verify no circular imports remain using `pydeps` or `importlib` trace

### TASK-07: Unify singleton patterns
- **Files**: `models/project.py:104–119`, `di.py`
- Pick one singleton mechanism: either the `__new__`-based pattern or the DI container pattern — not both
- Document the chosen pattern in code comments
- Add tests confirming only one instance is created across threads

### TASK-08: Simplify configuration precedence
- **File**: `src/mcp_server_tree_sitter/config.py:369–407`
- Env vars should be applied exactly once, at load time
- Remove the duplicate `update_config_from_env()` call inside `update_value()`
- Write a clear docstring documenting the final precedence order
- Add unit tests covering each precedence level

### TASK-09: Fix path containment check
- **File**: `src/mcp_server_tree_sitter/models/project.py:98`
- Replace `str(norm_path).startswith(str(self.root_path))` with `norm_path.is_relative_to(self.root_path)` (Python 3.9+)
- Add tests for symlinks, relative paths, and path traversal attempts

### TASK-10: Remove deprecated `auto_install` config field ✅
- **File**: `src/mcp_server_tree_sitter/config.py:75`
- Delete the field from `ServerConfig`
- Add a migration note in `CHANGELOG.md` or `README.md`
- Search codebase for all usages and remove them
- **Done**: Removed from `config_schema.py`, `config_loader.py`; updated tests and docs; added CHANGELOG.md and README migration note; added `.github/workflows/tests.yml`.

---

## P3 — Testing Gaps

### TASK-11: Add cache unit tests
- **File**: `src/mcp_server_tree_sitter/cache/parser_cache.py`
- Write `tests/test_parser_cache.py`
- Cover: LRU eviction, TTL expiration, max-size enforcement, concurrent access (use `threading`), cache-miss/hit ratio

### TASK-12: Add security module tests
- **File**: `src/mcp_server_tree_sitter/utils/security.py`
- Write `tests/test_security.py`
- Cover: path traversal (`../../etc/passwd`), symlink bypass, files with no extension, allowed extension filtering, file size limit enforcement

### TASK-13: Add tool-level integration tests
- **Files**: `tools/registration.py` (all tool handlers)
- Write `tests/test_tools.py`
- Cover at minimum: happy path, missing project, invalid language, parse error
- Use the existing DI test helpers to inject mock dependencies

### TASK-14: Add concurrent access tests
- **Files**: `tools/search.py`, `cache/parser_cache.py`, `models/project.py`
- Write `tests/test_concurrency.py`
- Use `concurrent.futures.ThreadPoolExecutor` to simulate concurrent calls
- Assert no data corruption or deadlock

### TASK-15: Add configuration edge-case tests
- **File**: `src/mcp_server_tree_sitter/config.py`
- Cover: malformed YAML, unknown keys, env var overrides, runtime `update_value()` calls, precedence order verification

---

## P4 — Feature Completeness

### TASK-16: Fix `find_similar_code` returning no results
- **File**: `src/mcp_server_tree_sitter/tools/analysis.py`
- Trace the execution path; likely the similarity threshold or result formatting is broken
- Add a failing test first, then fix the implementation
- Document expected input/output format

### TASK-17: Add UTF-16 file encoding support
- **File**: `src/mcp_server_tree_sitter/utils/file_io.py`
- Detect encoding using `chardet` or `charset-normalizer` before reading
- Fall back gracefully to UTF-8 if detection fails
- Add tests with UTF-16 encoded fixture files

### TASK-18: Add example `config.yaml`
- Create `docs/config.example.yaml` with all fields and their defaults
- Reference it from `README.md` and installation guide
- Auto-generate from `ServerConfig` Pydantic schema if possible

---

## P5 — Documentation

### TASK-19: Write architecture documentation
- Create `docs/architecture.md`
- Explain: DI container lifecycle, module dependency graph, thread-safety guarantees, config precedence, language data loading pipeline
- Include a diagram (ASCII or Mermaid) of module dependencies

### TASK-20: Write troubleshooting guide
- Create `docs/troubleshooting.md`
- Cover: common errors, query debugging, performance tuning, environment variable reference, how to add a new language

---

## Quick Wins

| #    | Task                                        | File                   | Effort  |
|------|---------------------------------------------|------------------------|---------|
| QW-1 | Use `is_relative_to()` for path containment | `models/project.py:98` | 10 min  |
| QW-2 | Remove deprecated `auto_install` field      | `config.py:75`         | 15 min  |
| QW-3 | Add example config YAML                     | `docs/`                | 20 min  |
| QW-4 | Replace `Dict`/`List` with built-in types   | all tools              | 30 min  |
| QW-5 | Add `disallow_untyped_defs` to mypy config  | `pyproject.toml`       | 5 min   |
