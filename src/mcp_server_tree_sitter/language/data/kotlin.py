"""Kotlin language data."""

from ..schema import LanguageDataBase
from ..templates import kotlin as _t

_qt = dict(_t.TEMPLATES)


class Kotlin(LanguageDataBase):
    id = "kotlin"
    extensions = ["kt"]
    scope_node_types = {
        "function": ["function_declaration", "getter", "setter"],
        "class": ["class_declaration", "interface_declaration"],
        "module": ["kotlin_file"],
    }
    query_templates = _qt
    node_type_descriptions = {}
