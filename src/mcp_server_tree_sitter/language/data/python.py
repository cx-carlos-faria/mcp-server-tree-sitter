"""Python language data."""

from ..schema import LanguageDataBase
from ..templates import python as _t

_qt = dict(_t.TEMPLATES)


class Python(LanguageDataBase):
    id = "python"
    extensions = ["py"]
    scope_node_types = {
        "function": ["function_definition"],
        "class": ["class_definition"],
        "module": ["module"],
    }
    query_templates = _qt
    node_type_descriptions = {}
