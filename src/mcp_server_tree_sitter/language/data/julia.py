"""Julia language data."""

from ..schema import LanguageDataBase
from ..templates import julia as _t

_qt = dict(_t.TEMPLATES)


class Julia(LanguageDataBase):
    id = "julia"
    extensions = ["jl"]
    scope_node_types = {
        "function": ["function_definition"],
        "class": ["struct_definition", "mutable_struct_definition"],
        "module": ["source_file"],
    }
    query_templates = _qt
    node_type_descriptions = {}
