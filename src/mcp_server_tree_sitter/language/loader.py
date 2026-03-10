"""Load and validate per-language data from language/data/ modules.

Subclasses of LanguageDataBase register themselves when defined. LanguageDataLoader
imports all modules in the data package (so classes are created), then builds
LanguageData from the registry. Derived structures are built from the cached load.
"""

import importlib
import logging
import pkgutil
from types import ModuleType
from typing import ClassVar, Dict

from .schema import LanguageData, LanguageDataBase

logger: logging.Logger = logging.getLogger(__name__)

_DATA_PACKAGE: str = "mcp_server_tree_sitter.language.data"


class LanguageDataLoader:
    """Loads language data from language/data/ and builds derived structures. Cache is on the class."""

    _loaded: ClassVar[Dict[str, LanguageData] | None] = None

    @classmethod
    def _get_loaded(cls) -> Dict[str, LanguageData]:
        """Return loaded language data, loading and caching once."""
        if cls._loaded is None:
            cls.load_all_language_data()
        assert cls._loaded is not None  # set by load_all_language_data()
        return cls._loaded

    @classmethod
    def load_all_language_data(cls) -> Dict[str, LanguageData]:
        """
        Import all language/data modules (so LanguageDataBase subclasses register),
        then build and return a dict mapping language id -> LanguageData. Caches on the class.
        """
        try:
            pkg: ModuleType = importlib.import_module(_DATA_PACKAGE)
        except ImportError as e:
            logger.warning("Language data package %s not importable: %s", _DATA_PACKAGE, e)
            cls._loaded = {}
            return {}

        path: list[str] | None = getattr(pkg, "__path__", None)
        if path is None:
            cls._loaded = {}
            return {}

        prefix: str = pkg.__name__ + "."
        for _importer, modname, _is_pkg in pkgutil.iter_modules(path, prefix):
            try:
                importlib.import_module(modname)
            except Exception as e:
                logger.warning("Skipping language data module %s: %s", modname, e)

        result: Dict[str, LanguageData] = {}
        for reg_cls in LanguageDataBase.registered_subclasses():
            try:
                data: LanguageData = reg_cls.to_language_data()
                result[data.id] = data
            except Exception as e:
                logger.warning(
                    "Invalid language data in %s: %s",
                    f"{reg_cls.__module__}.{reg_cls.__qualname__}",
                    e,
                )
        cls._loaded = result
        return result

    @classmethod
    def get_scope_node_types(cls) -> dict[str, dict[str, list[str]]]:
        """
        Build scope kind -> language id -> list of node type names (same shape as SCOPE_NODE_TYPES).
        """
        loaded: Dict[str, LanguageData] = cls._get_loaded()
        result: dict[str, dict[str, list[str]]] = {"function": {}, "class": {}, "module": {}}
        for lang_id, data in loaded.items():
            for kind, node_types in data.scope_node_types.items():
                result[kind][lang_id] = list(node_types)
        return result

    @classmethod
    def get_extension_map(cls) -> dict[str, str]:
        """Build file extension -> language id (for registry language_for_file)."""
        loaded: Dict[str, LanguageData] = cls._get_loaded()
        result: dict[str, str] = {}
        for data in loaded.values():
            for ext in data.extensions:
                result[ext] = data.id
        return result

    @classmethod
    def get_query_templates(cls) -> dict[str, dict[str, str]]:
        """Build language id -> template name -> query string (same shape as QUERY_TEMPLATES)."""
        loaded: Dict[str, LanguageData] = cls._get_loaded()
        return {lang_id: dict(data.query_templates) for lang_id, data in loaded.items()}

    @classmethod
    def get_node_type_descriptions(cls) -> dict[str, dict[str, str]]:
        """Build language id -> node type -> description (for describe_node_types)."""
        loaded: Dict[str, LanguageData] = cls._get_loaded()
        return {lang_id: dict(data.node_type_descriptions) for lang_id, data in loaded.items()}


# Public API: keep the same names so callers can import functions unchanged.
def load_all_language_data() -> Dict[str, LanguageData]:
    """Load all language data (cached). See LanguageDataLoader.load_all_language_data."""
    return LanguageDataLoader.load_all_language_data()


def get_scope_node_types() -> dict[str, dict[str, list[str]]]:
    """Build scope node types from loaded data. See LanguageDataLoader.get_scope_node_types."""
    return LanguageDataLoader.get_scope_node_types()


def get_extension_map() -> dict[str, str]:
    """Build extension -> language id map. See LanguageDataLoader.get_extension_map."""
    return LanguageDataLoader.get_extension_map()


def get_query_templates() -> dict[str, dict[str, str]]:
    """Build query templates by language. See LanguageDataLoader.get_query_templates."""
    return LanguageDataLoader.get_query_templates()


def get_node_type_descriptions() -> dict[str, dict[str, str]]:
    """Build node type descriptions by language. See LanguageDataLoader.get_node_type_descriptions."""
    return LanguageDataLoader.get_node_type_descriptions()
