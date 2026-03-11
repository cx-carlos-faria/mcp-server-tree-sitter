"""Dependency injection container for MCP Tree-sitter Server.

This module provides a central container for managing all application dependencies.
Singleton pattern: we use a single mechanism throughout the codebase — the __new__-based
singleton (see ProjectRegistry in models/project.py). The container itself is also a
__new__ singleton so that get_container() always returns the same instance.
"""

import threading
from typing import Dict, Optional

# Import logging from bootstrap package
from .bootstrap import get_logger
from .cache.parser_cache import TreeCache
from .config import ConfigurationManager, ServerConfig
from .language.registry import LanguageRegistry
from .models.project import ProjectRegistry

logger = get_logger(__name__)


class DependencyContainer:
    """Container for all application dependencies.

    Implemented as a __new__-based singleton: only one instance exists per process.
    Thread-safe; use DependencyContainer() or get_container() to obtain the instance.
    """

    _instance: Optional["DependencyContainer"] = None
    _lock = threading.RLock()

    def __new__(cls) -> "DependencyContainer":
        """Return the single container instance (thread-safe __new__ singleton)."""
        with cls._lock:
            if cls._instance is None:
                inst = super().__new__(cls)
                cls._instance = inst
            return cls._instance

    def __init__(self) -> None:
        """Initialize container with all core dependencies (runs only once)."""
        if getattr(self, "_container_initialized", False):
            return
        # Guard re-entrant init (e.g. LanguageRegistry() may call get_container().get_config())
        if getattr(self, "_container_initializing", False):
            return
        self._container_initializing = True
        logger.debug("Initializing dependency container")

        # Create core dependencies (ProjectRegistry() returns the __new__ singleton)
        self.config_manager = ConfigurationManager()
        self._config = self.config_manager.get_config()
        self.project_registry = ProjectRegistry()
        # Load language data once at startup so derived structures (scope types, extensions,
        # query templates, etc.) are built and cached before any tool runs.
        from .language.loader import load_all_language_data

        load_all_language_data()
        self.language_registry = LanguageRegistry()
        self.tree_cache = TreeCache(
            max_size_mb=self._config.cache.max_size_mb, ttl_seconds=self._config.cache.ttl_seconds
        )

        # Storage for additional dependencies (callers must narrow after get_dependency)
        self._additional: Dict[str, object] = {}
        self._container_initializing = False
        self._container_initialized = True

    def get_config(self) -> ServerConfig:
        """Get the current configuration."""
        # Always get the latest from the config manager
        config = self.config_manager.get_config()
        return config

    def register_dependency(self, name: str, instance: object) -> None:
        """Register an additional dependency. Callers should narrow after get_dependency."""
        self._additional[name] = instance

    def get_dependency(self, name: str) -> Optional[object]:
        """Get a registered dependency. Callers must narrow the return type."""
        return self._additional.get(name)


def get_container() -> DependencyContainer:
    """Get the dependency container (__new__ singleton; same instance every time)."""
    return DependencyContainer()
