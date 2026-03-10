"""C++ language data."""

from ..schema import LanguageDataBase
from ..templates import cpp as _t

_qt = dict(_t.TEMPLATES)


class Cpp(LanguageDataBase):
    id = "cpp"
    extensions = ["cpp", "cc", "hpp"]
    scope_node_types = {
        "function": ["function_definition", "method_definition"],
        "class": ["class_specifier", "struct_specifier"],
        "module": ["translation_unit"],
    }
    query_templates = _qt
    node_type_descriptions = {}
