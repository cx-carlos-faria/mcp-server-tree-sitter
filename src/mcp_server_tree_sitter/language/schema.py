"""Pydantic schema for per-language data files.

Each supported language is defined in a single data file under language/data/.
All such files must conform to LanguageData so that loading and validation
are consistent. Scope kinds match ScopeKind enum in scope_node_types.py.
"""

from typing import Literal

from pydantic import BaseModel, Field, model_validator

# Canonical scope kinds; must match ScopeKind in scope_node_types.py
ScopeKindKey = Literal["function", "class", "module"]

_REQUIRED_SCOPE_KINDS: tuple[ScopeKindKey, ...] = ("function", "class", "module")


class LanguageData(BaseModel):
    """Schema for one language's data (one file per language under language/data/)."""

    id: str = Field(..., description="Language identifier, e.g. 'python', 'javascript'")
    extensions: list[str] = Field(
        ...,
        min_length=1,
        description="File extensions that map to this language (e.g. ['py'] for Python)",
    )
    scope_node_types: dict[ScopeKindKey, list[str]] = Field(
        ...,
        description="Canonical scope kind -> tree-sitter node type names for enclosure resolution",
    )
    query_templates: dict[str, str] = Field(
        ...,
        description="Named query template -> tree-sitter query string",
    )
    node_type_descriptions: dict[str, str] = Field(
        default_factory=dict,
        description="Optional: node type name -> short description for tooling/docs",
    )

    @model_validator(mode="after")
    def _check_scope_kinds(self) -> "LanguageData":
        """Ensure scope_node_types has exactly the three required keys."""
        for key in _REQUIRED_SCOPE_KINDS:
            if key not in self.scope_node_types:
                raise ValueError(f"scope_node_types must contain key {key!r}")
        for key in self.scope_node_types:
            if key not in _REQUIRED_SCOPE_KINDS:
                raise ValueError(f"scope_node_types has unknown key {key!r}; allowed: {_REQUIRED_SCOPE_KINDS}")
        return self
