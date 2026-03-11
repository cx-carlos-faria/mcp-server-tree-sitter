"""Shared types and interfaces with no dependency on app, config, or cache.

This module is at the bottom of the dependency graph. Place here any types or
protocols that would otherwise cause circular imports between app, config,
cache, and language modules. Currently no shared types are required; config
and cache settings are passed via constructor arguments and callbacks (e.g.
ConfigurationManager.set_on_config_loaded).
"""

__all__: list[str] = []
