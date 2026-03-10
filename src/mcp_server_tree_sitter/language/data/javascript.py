"""JavaScript language data."""

from ..schema import LanguageDataBase
from ..templates import javascript as _t

_qt = dict(_t.TEMPLATES)


class JavaScript(LanguageDataBase):
    id = "javascript"
    extensions = ["js", "jsx"]
    scope_node_types = {
        "function": ["function_declaration", "method_definition"],
        "class": ["class_declaration"],
        "module": ["program"],
    }
    query_templates = _qt
    node_type_descriptions = {}
