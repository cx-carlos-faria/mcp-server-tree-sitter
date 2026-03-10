"""Python language data."""

from ..schema import LanguageDataBase


class Python(LanguageDataBase):
    id = "python"
    extensions = ["py"]
    scope_node_types = {
        "function": ["function_definition"],
        "class": ["class_definition"],
        "module": ["module"],
    }
    query_templates = {
        "functions": """
        (function_definition
            name: (identifier) @function.name
            parameters: (parameters) @function.params
            body: (block) @function.body) @function.def
    """,
        "classes": """
        (class_definition
            name: (identifier) @class.name
            body: (block) @class.body) @class.def
    """,
        "imports": """
        (import_statement
            name: (dotted_name) @import.module) @import

        (import_from_statement
            module_name: (dotted_name) @import.from
            name: (dotted_name) @import.item) @import

        ;; Handle aliased imports with 'as' keyword
        (import_from_statement
            module_name: (dotted_name) @import.from
            name: (aliased_import
                name: (dotted_name) @import.item
                alias: (identifier) @import.alias)) @import
    """,
        "function_calls": """
        (call
            function: (identifier) @call.function
            arguments: (argument_list) @call.args) @call
    """,
        "assignments": """
        (assignment
            left: (_) @assign.target
            right: (_) @assign.value) @assign
    """,
    }
    node_type_descriptions = {}
