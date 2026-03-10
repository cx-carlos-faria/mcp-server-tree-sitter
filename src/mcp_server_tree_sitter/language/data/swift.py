"""Swift language data."""

from ..schema import LanguageDataBase
from ..templates import swift as _t

_qt = dict(_t.TEMPLATES)


class Swift(LanguageDataBase):
    id = "swift"
    extensions = ["swift"]
    scope_node_types = {
        "function": ["function_declaration", "computed_getter", "computed_setter"],
        "class": ["class_declaration", "struct_declaration"],
        "module": ["source_file"],
    }
    query_templates = _qt
    node_type_descriptions = {}
