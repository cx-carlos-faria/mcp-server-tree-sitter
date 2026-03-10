"""Java language data."""

from ..schema import LanguageDataBase
from ..templates import java as _t

_qt = dict(_t.TEMPLATES)


class Java(LanguageDataBase):
    id = "java"
    extensions = ["java"]
    scope_node_types = {
        "function": ["method_declaration", "constructor_declaration"],
        "class": ["class_declaration", "interface_declaration"],
        "module": ["program"],
    }
    query_templates = _qt
    node_type_descriptions = {}
