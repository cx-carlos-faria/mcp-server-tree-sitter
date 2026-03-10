# Per-language data directory

One **Python module per supported language** lives here. Each module is loaded at startup and must conform to the `LanguageData` Pydantic model in `language/schema.py`.

## Layout

- **One file per language**, named by language id: `python.py`, `javascript.py`, `csharp.py`, etc.
- Each module must expose a **single instance** that validates as `LanguageData`:
  - Either a variable named `LANG_DATA` (a dict that will be validated with `LanguageData.model_validate(...)`), or
  - A variable named `DATA` of type `LanguageData` (already instantiated).

## Required structure (LanguageData)

| Field                    | Type           | Required  | Description                                                                                            |
|--------------------------|----------------|-----------|--------------------------------------------------------------------------------------------------------|
| `id`                     | str            | Yes       | Language identifier (e.g. `"python"`, `"javascript"`).                                                 |
| `extensions`             | list[str]      | Yes       | At least one file extension mapping to this language (e.g. `["py"]`).                                  |
| `scope_node_types`       | dict           | Yes       | Keys exactly `"function"`, `"class"`, `"module"`. Each value is a list of tree-sitter node type names. |
| `query_templates`        | dict[str, str] | Yes       | Template name → tree-sitter query string (multi-line allowed).                                         |
| `node_type_descriptions` | dict[str, str] | No        | Node type name → short description; default `{}`.                                                      |

## Convention

- **File name** must match `id` (e.g. `id: "python"` → `python.py`). The loader will discover modules in this package and validate each.
- **Scope kinds** must be exactly `function`, `class`, `module` (see `ScopeKind` in `scope_node_types.py`).
- **No executable logic** in these files; they are data only. Keep them as pure dicts or a single `LanguageData` instance.

## Adding a new language

1. Add a new module `language/data/<lang_id>.py`.
2. Define data that conforms to `LanguageData` (e.g. a dict assigned to `LANG_DATA`).
3. Ensure the loader is updated to import the new module (or use discovery so no change is needed).
4. Run tests and linting.
