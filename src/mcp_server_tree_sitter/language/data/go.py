"""Go language data."""

from ..schema import LanguageDataBase
from ..templates import go as _t

_qt = dict(_t.TEMPLATES)


class Go(LanguageDataBase):
    id = "go"
    extensions = ["go"]
    scope_node_types = {
        "function": ["function_declaration", "method_declaration"],
        "class": ["type_declaration"],
        "module": ["source_file"],
    }
    query_templates = _qt
    node_type_descriptions = {}
