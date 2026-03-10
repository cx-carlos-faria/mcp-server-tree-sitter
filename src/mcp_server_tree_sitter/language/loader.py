"""Load and validate per-language data from language/data/ modules.

Subclasses of LanguageDataBase register themselves when defined. The loader
imports all modules in the data package (so classes are created), then builds
LanguageData from the registry.
"""

import importlib
import logging
import pkgutil
from types import ModuleType
from typing import Dict

from .schema import LanguageData, LanguageDataBase

logger: logging.Logger = logging.getLogger(__name__)

_DATA_PACKAGE: str = "mcp_server_tree_sitter.language.data"


def load_all_language_data() -> Dict[str, LanguageData]:
    """
    Import all language/data modules (so LanguageDataBase subclasses register),
    then build and return a dict mapping language id -> LanguageData.
    """
    try:
        pkg: ModuleType = importlib.import_module(_DATA_PACKAGE)
    except ImportError as e:
        logger.warning("Language data package %s not importable: %s", _DATA_PACKAGE, e)
        return {}

    path: list[str] | None = getattr(pkg, "__path__", None)
    if path is None:
        return {}

    prefix: str = pkg.__name__ + "."
    for _importer, modname, _is_pkg in pkgutil.iter_modules(path, prefix):
        try:
            importlib.import_module(modname)
        except Exception as e:
            logger.warning("Skipping language data module %s: %s", modname, e)

    result: Dict[str, LanguageData] = {}
    for cls in LanguageDataBase.registered_subclasses():
        try:
            data: LanguageData = cls.to_language_data()
            result[data.id] = data
        except Exception as e:
            logger.warning("Invalid language data in %s: %s", f"{cls.__module__}.{cls.__qualname__}", e)
    return result
