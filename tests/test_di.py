"""Tests for the dependency injection container and __new__ singleton pattern."""

import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from mcp_server_tree_sitter.di import DependencyContainer, get_container
from mcp_server_tree_sitter.models.project import ProjectRegistry


def test_container_singleton() -> None:
    """Test that get_container returns the same instance each time."""
    container1 = get_container()
    container2 = get_container()
    assert container1 is container2


def test_register_custom_dependency() -> None:
    """Test registering and retrieving a custom dependency."""
    container = get_container()

    # Register a custom dependency
    test_value = {"test": "value"}
    container.register_dependency("test_dependency", test_value)

    # Retrieve it
    retrieved = container.get_dependency("test_dependency")
    assert retrieved is test_value


def test_core_dependencies_initialized() -> None:
    """Test that core dependencies are automatically initialized."""
    container = get_container()

    assert container.config_manager is not None
    assert container.project_registry is not None
    assert container.language_registry is not None
    assert container.tree_cache is not None


def test_container_singleton_across_threads() -> None:
    """Confirm only one DependencyContainer instance is created across threads."""
    instances: list[DependencyContainer] = []
    lock = threading.Lock()

    def get_one() -> None:
        c = get_container()
        with lock:
            instances.append(c)

    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = [executor.submit(get_one) for _ in range(32)]
        for f in as_completed(futures):
            f.result()
    assert len(instances) == 32
    unique = {id(i) for i in instances}
    assert len(unique) == 1, "all threads must see the same container instance"


def test_project_registry_singleton_across_threads() -> None:
    """Confirm only one ProjectRegistry instance is created across threads."""
    instances: list[ProjectRegistry] = []
    lock = threading.Lock()

    def get_one() -> None:
        r = ProjectRegistry()
        with lock:
            instances.append(r)

    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = [executor.submit(get_one) for _ in range(32)]
        for f in as_completed(futures):
            f.result()
    assert len(instances) == 32
    unique = {id(i) for i in instances}
    assert len(unique) == 1, "all threads must see the same ProjectRegistry instance"
