"""C# language data."""

from ..schema import LanguageDataBase
from ..templates import csharp as _t

_qt = dict(_t.TEMPLATES)


class Csharp(LanguageDataBase):
    id = "csharp"
    extensions = ["cs"]
    scope_node_types = {
        "function": [
            "method_declaration",
            "constructor_declaration",
            "local_function_statement",
        ],
        "class": ["class_declaration", "struct_declaration", "interface_declaration"],
        "module": ["compilation_unit"],
    }
    query_templates = _qt
    node_type_descriptions = {}
