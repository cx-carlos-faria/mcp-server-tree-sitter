"""Rust language data."""

from ..schema import LanguageDataBase
from ..templates import rust as _t

_qt = dict(_t.TEMPLATES)


class Rust(LanguageDataBase):
    id = "rust"
    extensions = ["rs"]
    scope_node_types = {
        "function": ["function_item"],
        "class": ["struct_item", "impl_item", "trait_item"],
        "module": ["source_file"],
    }
    query_templates = _qt
    node_type_descriptions = {}
