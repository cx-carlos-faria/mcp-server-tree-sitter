"""Tools for building and manipulating tree-sitter queries."""

from typing import Dict, List

from ..language.query_templates import get_query_template


def get_template(language: str, pattern: str) -> str:
    """
    Get a query template with optional parameter replacement.

    Args:
        language: Language identifier
        pattern: Template name or custom pattern

    Returns:
        Query string
    """
    # Check if this is a template name
    template = get_query_template(language, pattern)
    if template:
        return template

    # Otherwise return as-is
    return pattern


def build_compound_query(language: str, patterns: List[str], combine: str = "or") -> str:
    """
    Build a compound query from multiple patterns.

    Args:
        language: Language identifier
        patterns: List of pattern names or custom patterns
        combine: How to combine patterns ("or" or "and")

    Returns:
        Combined query string
    """
    queries = []

    for pattern in patterns:
        template = get_template(language, pattern)
        if template:
            queries.append(template)

    # For 'or' we can just concatenate
    if combine.lower() == "or":
        return "\n".join(queries)

    # For 'and' we need to add predicates
    # This is a simplified implementation
    combined = "\n".join(queries)
    combined += "\n\n;; Add your #match predicates here to require combinations"

    return combined


def adapt_query(query: str, from_language: str, to_language: str) -> Dict[str, str]:
    """
    Adapt a query from one language to another.

    Args:
        query: Original query string
        from_language: Source language
        to_language: Target language

    Returns:
        Dictionary with adapted query and metadata
    """
    adapted = adapt_query_for_language(query, from_language, to_language)
    return {
        "original_language": from_language,
        "target_language": to_language,
        "original_query": query,
        "adapted_query": adapted,
    }


def adapt_query_for_language(query: str, from_language: str, to_language: str) -> str:
    """
    Try to adapt a query from one language to another.

    Args:
        query: Original query
        from_language: Source language
        to_language: Target language

    Returns:
        Adapted query string

    Note:
        This is a simplified implementation that assumes similar node types.
        A real implementation would need language-specific translations.
    """
    translations = {
        # Python -> JavaScript
        ("python", "javascript"): {
            "function_definition": "function_declaration",
            "class_definition": "class_declaration",
            "block": "statement_block",
            "parameters": "formal_parameters",
            "argument_list": "arguments",
            "import_statement": "import_statement",
            "call": "call_expression",
        },
        # JavaScript -> Python
        ("javascript", "python"): {
            "function_declaration": "function_definition",
            "class_declaration": "class_definition",
            "statement_block": "block",
            "formal_parameters": "parameters",
            "arguments": "argument_list",
            "call_expression": "call",
        },
        # Add more language pairs...
    }

    pair = (from_language, to_language)
    if pair in translations:
        trans_dict = translations[pair]
        for src, dst in trans_dict.items():
            # Simple string replacement
            query = query.replace(f"({src}", f"({dst}")

    return query


def describe_node_types(language: str) -> Dict[str, str]:
    """
    Get descriptions of common node types for a language.

    Data is loaded from per-language data (language/data/) via the loader.

    Args:
        language: Language identifier

    Returns:
        Dictionary of node type -> description
    """
    from ..language.loader import get_node_type_descriptions

    descriptions = get_node_type_descriptions()
    return descriptions.get(language, {})
