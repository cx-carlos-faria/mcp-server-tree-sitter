"""C language data."""

from ..schema import LanguageDataBase
from ..templates import c as _t

_qt = dict(_t.TEMPLATES)


class C(LanguageDataBase):
    id = "c"
    extensions = ["c", "h"]
    scope_node_types = {
        "function": ["function_definition"],
        "class": ["struct_specifier"],
        "module": ["translation_unit"],
    }
    query_templates = _qt
    node_type_descriptions = {}
