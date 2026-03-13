"""Tests for search_text context_before / context_after behaviour."""

import contextlib
from pathlib import Path

from tests.test_helpers import find_text, register_project_tool, remove_project_tool

PROJECT_NAME = "search_text_context_project"

# A fixed 9-line file used by most tests.
# Line numbers:   1        2          3        4        5          6       7         8         9
NINE_LINES = "alpha\nbeta\ngamma\nMATCH\nepsilon\nzeta\neta\nMATCH\ntheta\n"


def _setup(tmp_path: Path, content: str = NINE_LINES) -> str:
    (tmp_path / "sample.txt").write_text(content)
    register_project_tool(path=str(tmp_path), name=PROJECT_NAME)
    return PROJECT_NAME


def _teardown() -> None:
    with contextlib.suppress(Exception):
        remove_project_tool(PROJECT_NAME)


# ---------------------------------------------------------------------------
# context_lines=0  →  empty before/after lists
# ---------------------------------------------------------------------------

def test_no_context_gives_empty_lists(tmp_path: Path) -> None:
    name = _setup(tmp_path)
    try:
        results = find_text(project=name, pattern="MATCH", context_lines=0)
        assert len(results) == 2
        for r in results:
            assert r["context_before"] == []
            assert r["context_after"] == []
    finally:
        _teardown()


# ---------------------------------------------------------------------------
# Basic before / after content
# ---------------------------------------------------------------------------

def test_context_before_and_after(tmp_path: Path) -> None:
    """Match in the middle: verify correct before and after lines."""
    name = _setup(tmp_path)
    try:
        results = find_text(project=name, pattern="MATCH", context_lines=2, file_pattern="**/*.txt")
        # First match is on line 4 ("MATCH")
        first = next(r for r in results if r["line"] == 4)
        assert set(first["context_before"]) == {"beta", "gamma"}
        assert set(first["context_after"]) == {"epsilon", "zeta"}
    finally:
        _teardown()


def test_context_before_order_is_oldest_first(tmp_path: Path) -> None:
    """context_before lists lines in ascending (oldest-first) order."""
    name = _setup(tmp_path)
    try:
        results = find_text(project=name, pattern="MATCH", context_lines=2, file_pattern="**/*.txt")
        first = next(r for r in results if r["line"] == 4)
        # pre_ctx deque holds (line_no, text) in insertion order → oldest first
        assert first["context_before"] == ["beta", "gamma"]   # lines 2, 3
        assert first["context_after"] == ["epsilon", "zeta"]  # lines 5, 6
    finally:
        _teardown()


# ---------------------------------------------------------------------------
# Match at the very start of the file
# ---------------------------------------------------------------------------

def test_match_at_start_has_no_before_context(tmp_path: Path) -> None:
    content = "MATCH\nline2\nline3\nline4\n"
    name = _setup(tmp_path, content)
    try:
        results = find_text(project=name, pattern="MATCH", context_lines=2, file_pattern="**/*.txt")
        assert len(results) == 1
        assert results[0]["line"] == 1
        assert results[0]["context_before"] == []
        assert results[0]["context_after"] == ["line2", "line3"]
    finally:
        _teardown()


# ---------------------------------------------------------------------------
# Match at the very end of the file
# ---------------------------------------------------------------------------

def test_match_at_end_has_no_after_context(tmp_path: Path) -> None:
    content = "line1\nline2\nMATCH\n"
    name = _setup(tmp_path, content)
    try:
        results = find_text(project=name, pattern="MATCH", context_lines=2, file_pattern="**/*.txt")
        assert len(results) == 1
        assert results[0]["context_before"] == ["line1", "line2"]
        assert results[0]["context_after"] == []
    finally:
        _teardown()


# ---------------------------------------------------------------------------
# Context is clipped when the window extends past the file boundary
# ---------------------------------------------------------------------------

def test_context_clipped_at_file_start(tmp_path: Path) -> None:
    """context_lines=3 but only 1 line exists before the match."""
    content = "only_before\nMATCH\nafter1\nafter2\nafter3\n"
    name = _setup(tmp_path, content)
    try:
        results = find_text(project=name, pattern="MATCH", context_lines=3, file_pattern="**/*.txt")
        assert results[0]["context_before"] == ["only_before"]
        assert results[0]["context_after"] == ["after1", "after2", "after3"]
    finally:
        _teardown()


def test_context_clipped_at_file_end(tmp_path: Path) -> None:
    """context_lines=3 but only 1 line exists after the match."""
    content = "before1\nbefore2\nbefore3\nMATCH\nonly_after\n"
    name = _setup(tmp_path, content)
    try:
        results = find_text(project=name, pattern="MATCH", context_lines=3, file_pattern="**/*.txt")
        assert results[0]["context_before"] == ["before1", "before2", "before3"]
        assert results[0]["context_after"] == ["only_after"]
    finally:
        _teardown()


# ---------------------------------------------------------------------------
# Two matches far apart: independent context windows
# ---------------------------------------------------------------------------

def test_two_distant_matches_have_independent_context(tmp_path: Path) -> None:
    name = _setup(tmp_path)  # uses NINE_LINES; matches at lines 4 and 8
    try:
        results = find_text(project=name, pattern="MATCH", context_lines=2, file_pattern="**/*.txt")
        results_by_line = {r["line"]: r for r in results}
        assert set(results_by_line.keys()) == {4, 8}

        r4 = results_by_line[4]
        assert r4["context_before"] == ["beta", "gamma"]      # lines 2–3
        assert r4["context_after"] == ["epsilon", "zeta"]     # lines 5–6

        r8 = results_by_line[8]
        assert r8["context_before"] == ["zeta", "eta"]        # lines 6–7
        assert r8["context_after"] == ["theta"]               # line 9 (only 1 line after)
    finally:
        _teardown()


# ---------------------------------------------------------------------------
# Two matches whose context windows overlap
# ---------------------------------------------------------------------------

def test_overlapping_context_windows(tmp_path: Path) -> None:
    """Matches on lines 2 and 4 with context_lines=2: windows overlap but each result is independent."""
    content = "line1\nMATCH\nline3\nMATCH\nline5\n"
    name = _setup(tmp_path, content)
    try:
        results = find_text(project=name, pattern="MATCH", context_lines=2, file_pattern="**/*.txt")
        results_by_line = {r["line"]: r for r in results}
        assert set(results_by_line.keys()) == {2, 4}

        r2 = results_by_line[2]
        assert r2["context_before"] == ["line1"]
        assert r2["context_after"] == ["line3", "MATCH"]  # lines 3–4 (line 4 is the second match)

        r4 = results_by_line[4]
        assert r4["context_before"] == ["MATCH", "line3"]  # lines 2–3
        assert r4["context_after"] == ["line5"]
    finally:
        _teardown()


# ---------------------------------------------------------------------------
# max_results stops collection even with pending after-context
# ---------------------------------------------------------------------------

def test_max_results_respected_with_pending_context(tmp_path: Path) -> None:
    """max_results=1 must return exactly 1 result even when after-context is still pending."""
    name = _setup(tmp_path)  # two matches in file
    try:
        results = find_text(project=name, pattern="MATCH", context_lines=2, max_results=1, file_pattern="**/*.txt")
        assert len(results) == 1
    finally:
        _teardown()
