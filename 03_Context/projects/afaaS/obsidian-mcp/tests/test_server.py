"""Tests for Obsidian MCP Server."""

import asyncio
import tempfile
from pathlib import Path

import pytest

from obsidian_mcp.server import ObsidianMCPServer, VaultConfig


@pytest.fixture
def temp_vault():
    """Create a temporary vault with test notes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_path = Path(tmpdir)

        # Create test notes
        (vault_path / "note1.md").write_text(
            """---
tags: [project, active]
aliases: ["Note One"]
---

# Note One

This is the first note with [[Note Two]] and #inline-tag.

Some content here.
""",
            encoding="utf-8",
        )

        (vault_path / "note2.md").write_text(
            """---
tags: [reference]
---

# Note Two

This note links back to [[Note One]].

More content with #another-tag.
""",
            encoding="utf-8",
        )

        (vault_path / "subfolder").mkdir(parents=True, exist_ok=True)
        (vault_path / "subfolder" / "note3.md").write_text(
            """---
tags: [project, archive]
---

# Note Three

No links here.
""",
            encoding="utf-8",
        )

        yield vault_path


@pytest.mark.asyncio
async def test_parse_note(temp_vault):
    config = VaultConfig(vault_path=str(temp_vault))
    server = ObsidianMCPServer(config)

    # Wait for index to build
    await asyncio.sleep(0.1)

    note = await server.read_note("note1")
    assert note.name == "note1"  # Name is derived from filename
    assert "project" in note.tags
    assert "active" in note.tags
    assert "inline-tag" in note.tags
    assert "Note Two" in note.wikilinks


@pytest.mark.asyncio
async def test_search_vault(temp_vault):
    config = VaultConfig(vault_path=str(temp_vault))
    server = ObsidianMCPServer(config)

    await asyncio.sleep(0.1)

    results = await server.search_vault("first")
    assert len(results) == 1
    assert results[0].name == "note1"  # Name is derived from filename

    results = await server.search_vault("content")
    assert len(results) >= 2


@pytest.mark.asyncio
async def test_search_with_tag_filter(temp_vault):
    config = VaultConfig(vault_path=str(temp_vault))
    server = ObsidianMCPServer(config)

    await asyncio.sleep(0.1)

    results = await server.search_vault("note", tags=["project"])
    assert len(results) == 2
    for r in results:
        assert "project" in r.tags


@pytest.mark.asyncio
async def test_list_tags(temp_vault):
    config = VaultConfig(vault_path=str(temp_vault))
    server = ObsidianMCPServer(config)

    await asyncio.sleep(0.1)

    tags = await server.list_tags()
    assert "project" in tags
    assert tags["project"] == 2
    assert "active" in tags
    assert "reference" in tags


@pytest.mark.asyncio
async def test_write_note(temp_vault):
    config = VaultConfig(vault_path=str(temp_vault))
    server = ObsidianMCPServer(config)

    await asyncio.sleep(0.1)

    note = await server.write_note(
        "new_note.md", "This is a new note.", {"tags": ["new", "test"], "custom_field": "value"}
    )

    assert note.name == "new_note"
    assert "new" in note.tags
    assert "test" in note.tags

    # Verify it's readable
    read_note = await server.read_note("new_note")
    assert read_note.content.strip() == "This is a new note."


@pytest.mark.asyncio
async def test_get_graph(temp_vault):
    config = VaultConfig(vault_path=str(temp_vault))
    server = ObsidianMCPServer(config)

    await asyncio.sleep(0.1)

    graph = await server.get_graph("note1", depth=1)
    assert graph.center is not None
    assert graph.center.name == "note1"  # Name is derived from filename
    assert len(graph.nodes) >= 1  # At least center node
    assert len(graph.edges) >= 1  # At least one wikilink edge


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
