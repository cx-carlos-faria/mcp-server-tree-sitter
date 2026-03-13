"""File operation tools for MCP server."""

import itertools
import logging
from pathlib import Path
from typing import Any

from ..exceptions import FileAccessError, ProjectError
from ..models.project import Project
from ..utils.security import validate_file_access

logger = logging.getLogger(__name__)


def list_project_files(
    project: Project,
    pattern: str | None = None,
    max_depth: int | None = None,
    filter_extensions: list[str] | None = None,
) -> list[str]:
    """
    List files in a project, optionally filtered by pattern.

    Args:
        project: Project object
        pattern: Glob pattern for files (e.g., "**/*.py")
        max_depth: Maximum directory depth to traverse
        filter_extensions: List of file extensions to include (without dot)

    Returns:
        List of relative file paths
    """
    root = project.root_path
    pattern = pattern or "**/*"
    files = []

    # Normalize once: lowercase + frozenset for O(1) lookup in both branches below
    ext_filter: frozenset[str] | None = (
        frozenset(e.lower() for e in filter_extensions) if filter_extensions else None
    )

    # Handle max_depth=0 specially to avoid glob patterns with /*
    if max_depth == 0:
        # For max_depth=0, only list files directly in root directory
        for path in root.iterdir():
            if path.is_file():
                if ext_filter and path.suffix[1:].lower() not in ext_filter:
                    continue
                files.append(str(path.relative_to(root)))

        return sorted(files)

    # Handle max depth for glob pattern for max_depth > 0
    if max_depth is not None and max_depth > 0 and "**" in pattern:
        parts = pattern.split("**")
        if len(parts) == 2:
            pattern = f"{parts[0]}{'*/' * max_depth}{parts[1]}"

    # Ensure pattern doesn't start with / to avoid NotImplementedError
    pattern = pattern.removeprefix("/")

    for path in root.glob(pattern):
        if path.is_file():
            if ext_filter and path.suffix[1:].lower() not in ext_filter:
                continue
            files.append(str(path.relative_to(root)))

    return sorted(files)


def get_file_content(
    project: Project,
    path: str,
    as_bytes: bool = False,
    max_lines: int | None = 1000,
    start_line: int = 0,
) -> str | bytes:
    """
    Get content of a file in a project.

    Args:
        project: Project object
        path: Path to the file, relative to project root
        as_bytes: Whether to return raw bytes instead of string
        max_lines: Maximum number of lines to return (default 1000)
        start_line: First line to include (0-based)

    Returns:
        File content

    Raises:
        ProjectError: If project not found
        FileAccessError: If file access fails
    """
    try:
        file_path = project.get_file_path(path)
    except ProjectError as e:
        raise FileAccessError(str(e)) from e

    try:
        validate_file_access(file_path, project.root_path)
    except Exception as e:
        raise FileAccessError(f"Access denied: {e}") from e

    try:
        need_slice = start_line > 0 or max_lines is not None

        if as_bytes:
            with open(file_path, "rb") as f:
                if not need_slice:
                    return f.read()
                stop = start_line + max_lines if max_lines is not None else None
                return b"".join(itertools.islice(f, start_line, stop))
        else:
            with open(file_path, encoding="utf-8", errors="replace") as f:
                if not need_slice:
                    return f.read()
                stop = start_line + max_lines if max_lines is not None else None
                return "".join(itertools.islice(f, start_line, stop))

    except FileNotFoundError as e:
        raise FileAccessError(f"File not found: {path}") from e
    except PermissionError as e:
        raise FileAccessError(f"Permission denied: {path}") from e
    except Exception as e:
        raise FileAccessError(f"Error reading file: {e}") from e


def get_file_info(project: Project, path: str) -> dict[str, Any]:
    """
    Get metadata about a file.

    Args:
        project: Project object
        path: Path to the file, relative to project root

    Returns:
        Dictionary with file information

    Raises:
        ProjectError: If project not found
        FileAccessError: If file access fails
    """
    try:
        file_path = project.get_file_path(path)
    except ProjectError as e:
        raise FileAccessError(str(e)) from e

    try:
        validate_file_access(file_path, project.root_path)
    except Exception as e:
        raise FileAccessError(f"Access denied: {e}") from e

    try:
        stat = file_path.stat()
        return {
            "path": str(path),
            "size": stat.st_size,
            "last_modified": stat.st_mtime,
            "created": stat.st_ctime,
            "is_directory": file_path.is_dir(),
            "extension": file_path.suffix[1:] if file_path.suffix else None,
            "line_count": count_lines(file_path) if file_path.is_file() else None,
        }
    except FileNotFoundError as e:
        raise FileAccessError(f"File not found: {path}") from e
    except PermissionError as e:
        raise FileAccessError(f"Permission denied: {path}") from e
    except Exception as e:
        raise FileAccessError(f"Error getting file info: {e}") from e


def count_lines(file_path: Path) -> int:
    """
    Count lines in a file efficiently.

    Args:
        file_path: Path to the file

    Returns:
        Number of lines
    """
    try:
        with open(file_path, "rb") as f:
            return sum(1 for _ in f)
    except OSError:
        return 0
