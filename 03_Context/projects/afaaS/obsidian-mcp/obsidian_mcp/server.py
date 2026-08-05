"""Obsidian Vault MCP Server — read, write, search, and navigate notes via MCP."""

import asyncio
import os
import re
from pathlib import Path

import aiofiles
import yaml
from fastmcp import FastMCP
from pydantic import BaseModel, Field


class VaultConfig(BaseModel):
    """Configuration for Obsidian vault access."""

    vault_path: str = Field(description="Absolute path to Obsidian vault root")
    max_file_size: int = Field(default=1024 * 1024, description="Max file size in bytes (1MB)")
    max_search_results: int = Field(default=50, description="Max search results to return")
    follow_wikilinks: bool = Field(default=True, description="Resolve [[wikilinks]] in content")


class NoteFrontmatter(BaseModel):
    """Parsed frontmatter from a note."""

    tags: list[str] = []
    aliases: list[str] = []
    cssclass: str | None = None

    model_config = {"extra": "allow"}  # Allow arbitrary frontmatter fields


class Note(BaseModel):
    """Represents a vault note with parsed frontmatter."""

    path: str
    name: str
    content: str
    frontmatter: NoteFrontmatter
    wikilinks: list[str] = []
    tags: list[str] = []


class SearchResult(BaseModel):
    """Single search result."""

    path: str
    name: str
    snippet: str
    score: float
    tags: list[str] = []


class GraphNode(BaseModel):
    """Node in the wikilink graph."""

    path: str
    name: str
    tags: list[str] = []
    connections: int = 0


class GraphEdge(BaseModel):
    """Edge in the wikilink graph."""

    source: str
    target: str
    type: str = "wikilink"


class VaultGraph(BaseModel):
    """Wikilink graph centered on a note."""

    center: GraphNode | None = None
    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []


class ObsidianMCPServer:
    """MCP Server for Obsidian Vault operations."""

    def __init__(self, config: VaultConfig) -> None:
            """Initialize the server with vault configuration."""
            self.config = config
            self.vault_root = Path(config.vault_path).resolve()
            if not self.vault_root.exists():
                raise ValueError(f"Vault path does not exist: {self.vault_root}")
            if not self.vault_root.is_dir():
                raise ValueError(f"Vault path is not a directory: {self.vault_root}")

            # Build index on startup (synchronous)
            self._note_index: dict[str, Note] = {}
            self._tag_index: dict[str, set[str]] = {}
            self._wikilink_index: dict[str, set[str]] = {}
            self._reverse_wikilink_index: dict[str, set[str]] = {}
            self._build_index_sync()

    async def _build_index(self) -> None:
        """Build in-memory index of all notes (async version for future use)."""
        self._build_index_sync()

    def _build_index_sync(self) -> None:
        """Build in-memory index of all notes (synchronous)."""
        self._note_index.clear()
        self._tag_index.clear()
        self._wikilink_index.clear()
        self._reverse_wikilink_index.clear()

        for md_file in self.vault_root.rglob("*.md"):
            if md_file.is_file():
                try:
                    note = self._parse_note_sync(md_file)
                    rel_path = str(md_file.relative_to(self.vault_root))
                    self._note_index[rel_path] = note

                    # Index tags
                    for tag in note.tags:
                        self._tag_index.setdefault(tag, set()).add(rel_path)

                    # Index wikilinks
                    for link in note.wikilinks:
                        self._wikilink_index.setdefault(rel_path, set()).add(link)
                        self._reverse_wikilink_index.setdefault(link, set()).add(rel_path)

                except Exception:
                    # Skip unreadable files
                    continue

    def _parse_note_sync(self, file_path: Path) -> Note:
        """Parse a markdown file into a Note with frontmatter (synchronous)."""
        content = file_path.read_text(encoding="utf-8")

        # Parse frontmatter
        frontmatter = NoteFrontmatter()
        body = content
        wikilinks = []
        tags = []

        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                try:
                    fm_data = yaml.safe_load(parts[1]) or {}
                    frontmatter = NoteFrontmatter(**fm_data)
                    body = parts[2].lstrip("\n")
                except yaml.YAMLError:
                    pass

        # Extract tags from frontmatter
        tags.extend(frontmatter.tags)

        # Extract inline tags (#tag)
        inline_tags = re.findall(r"(?<!\w)#([\w/-]+)", body)
        tags.extend(inline_tags)

        # Extract wikilinks [[link]] or [[link|alias]]
        wikilink_pattern = r"\[\[([^\]]+)\]\]"
        for match in re.finditer(wikilink_pattern, body):
            link = match.group(1).split("|")[0].strip()
            wikilinks.append(link)

        return Note(
            path=str(file_path.relative_to(self.vault_root)),
            name=file_path.stem,
            content=body,
            frontmatter=frontmatter,
            wikilinks=wikilinks,
            tags=list(set(tags)),
        )

    async def _read_file_safe(self, file_path: Path) -> str:
        """Read file with size limit."""
        stat = file_path.stat()
        if stat.st_size > self.config.max_file_size:
            raise ValueError(
                f"File too large: {stat.st_size} bytes (max {self.config.max_file_size})"
            )
        async with aiofiles.open(file_path, encoding="utf-8") as f:
            return await f.read()

    def _resolve_note_path(self, path: str) -> Path:
        """Resolve a note path to absolute path within vault."""
        # Handle both relative paths and wikilink-style names
        candidate = self.vault_root / path
        if candidate.exists():
            return candidate

        # Try with .md extension
        candidate = self.vault_root / f"{path}.md"
        if candidate.exists():
            return candidate

        # Search by name
        for note in self._note_index.values():
            if note.name == path or note.path == path:
                return self.vault_root / note.path

        raise FileNotFoundError(f"Note not found: {path}")

    # --- MCP Tools ---

    async def read_note(self, path: str) -> Note:
        """Read a note from the vault by path or name."""
        note_path = self._resolve_note_path(path)
        return self._parse_note_sync(note_path)

    async def write_note(
        self,
        path: str,
        content: str,
        frontmatter: dict | None = None,
    ) -> Note:
        """Create or update a note in the vault."""
        note_path = self.vault_root / path
        if not note_path.suffix:
            note_path = note_path.with_suffix(".md")

        # Ensure parent directory exists
        note_path.parent.mkdir(parents=True, exist_ok=True)

        # Build frontmatter
        fm = frontmatter or {}
        fm_yaml = yaml.dump(fm, sort_keys=False, allow_unicode=True) if fm else ""

        # Write file
        full_content = f"---\n{fm_yaml}---\n\n{content}" if fm else content
        note_path.write_text(full_content, encoding="utf-8")

        # Re-index this note
        note = self._parse_note_sync(note_path)
        rel_path = str(note_path.relative_to(self.vault_root))
        self._note_index[rel_path] = note

        return note

    async def search_vault(
        self,
        query: str,
        tags: list[str] | None = None,
        folder: str | None = None,
        limit: int | None = None,
    ) -> list[SearchResult]:
        """Search vault by full-text query with optional tag/folder filters."""
        limit = limit or self.config.max_search_results
        results = []

        # Build candidate set
        candidates = set(self._note_index.keys())

        if tags:
            tag_candidates = set()
            for tag in tags:
                tag_candidates.update(self._tag_index.get(tag, set()))
            candidates &= tag_candidates

        if folder:
            folder_path = folder.rstrip("/") + "/"
            candidates = {c for c in candidates if c.startswith(folder_path)}

        # Score matches
        query_lower = query.lower()
        query_terms = query_lower.split()

        for path in candidates:
            note = self._note_index[path]
            score = 0.0

            # Score title
            if query_lower in note.name.lower():
                score += 10.0

            # Score content
            content_lower = note.content.lower()
            for term in query_terms:
                count = content_lower.count(term)
                score += count * 2.0

            # Score tags
            for tag in note.tags:
                if query_lower in tag.lower():
                    score += 5.0

            if score > 0:
                # Generate snippet
                snippet = self._generate_snippet(note.content, query_terms)
                results.append(
                    SearchResult(
                        path=note.path,
                        name=note.name,
                        snippet=snippet,
                        score=score,
                        tags=note.tags,
                    )
                )

        # Sort by score descending
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:limit]

    def _generate_snippet(self, content: str, terms: list[str], radius: int = 100) -> str:
        """Generate a snippet around the first match."""
        content_lower = content.lower()
        for term in terms:
            idx = content_lower.find(term)
            if idx >= 0:
                start = max(0, idx - radius)
                end = min(len(content), idx + radius)
                snippet = content[start:end]
                if start > 0:
                    snippet = "..." + snippet
                if end < len(content):
                    snippet = snippet + "..."
                return snippet
        return content[:200] + ("..." if len(content) > 200 else "")

    async def list_tags(self) -> dict[str, int]:
        """List all tags with their note counts."""
        return {tag: len(notes) for tag, notes in sorted(self._tag_index.items())}

    async def list_files(self, folder: str = "") -> list[str]:
        """List all markdown files in a folder (relative paths)."""
        folder_path = folder.rstrip("/") + "/" if folder else ""
        return sorted(
            path
            for path in self._note_index.keys()
            if path.startswith(folder_path) and "/" not in path[len(folder_path) :]
        )

    async def get_graph(self, center: str | None = None, depth: int = 1) -> VaultGraph:
        """Get wikilink graph centered on a note (or full graph if no center)."""
        nodes: dict[str, GraphNode] = {}
        edges: list[GraphEdge] = []

        if center:
            # Build subgraph around center
            center_path = center
            if center_path not in self._note_index:
                # Try to resolve
                try:
                    center_path = str(self._resolve_note_path(center).relative_to(self.vault_root))
                except FileNotFoundError:
                    center_path = None

            if center_path:
                visited = {center_path}
                frontier = {center_path}

                for _ in range(depth):
                    next_frontier = set()
                    for node_path in frontier:
                        # Outgoing links
                        for target in self._wikilink_index.get(node_path, set()):
                            edges.append(GraphEdge(source=node_path, target=target))
                            if target not in visited:
                                next_frontier.add(target)
                        # Incoming links (backlinks)
                        for source in self._reverse_wikilink_index.get(node_path, set()):
                            edges.append(GraphEdge(source=source, target=node_path))
                            if source not in visited:
                                next_frontier.add(source)
                    visited.update(next_frontier)
                    frontier = next_frontier

                # Build nodes for visited
                for path in visited:
                    note = self._note_index.get(path)
                    if note:
                        connections = len(self._wikilink_index.get(path, set())) + len(
                            self._reverse_wikilink_index.get(path, set())
                        )
                        nodes[path] = GraphNode(
                            path=path,
                            name=note.name,
                            tags=note.tags,
                            connections=connections,
                        )

                center_node = nodes.get(center_path)
                return VaultGraph(center=center_node, nodes=list(nodes.values()), edges=edges)

        # Full graph
        for path, note in self._note_index.items():
            connections = len(self._wikilink_index.get(path, set())) + len(
                self._reverse_wikilink_index.get(path, set())
            )
            nodes[path] = GraphNode(
                path=path,
                name=note.name,
                tags=note.tags,
                connections=connections,
            )

        for source, targets in self._wikilink_index.items():
            for target in targets:
                edges.append(GraphEdge(source=source, target=target))

        return VaultGraph(nodes=list(nodes.values()), edges=edges)


# --- FastMCP App Setup ---


def create_server(config: VaultConfig | None = None) -> FastMCP:
    """Create and configure the FastMCP server."""
    if config is None:
        # Default to environment variable or current vault
        vault_path = os.environ.get("OBSIDIAN_VAULT_PATH", "C:\\the force")
        config = VaultConfig(vault_path=vault_path)

    server_instance = ObsidianMCPServer(config)
    mcp = FastMCP("Obsidian Vault")

    @mcp.tool()
    async def read_note(path: str) -> dict:
        """Read a note from the vault by path or name."""
        note = await server_instance.read_note(path)
        return note.model_dump()

    @mcp.tool()
    async def write_note(path: str, content: str, frontmatter: dict | None = None) -> dict:
        """Create or update a note in the vault."""
        note = await server_instance.write_note(path, content, frontmatter)
        return note.model_dump()

    @mcp.tool()
    async def search_vault(
        query: str,
        tags: list[str] | None = None,
        folder: str | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        """Search vault by full-text query with optional tag/folder filters."""
        results = await server_instance.search_vault(query, tags, folder, limit)
        return [r.model_dump() for r in results]

    @mcp.tool()
    async def list_tags() -> dict[str, int]:
        """List all tags with their note counts."""
        return await server_instance.list_tags()

    @mcp.tool()
    async def list_files(folder: str = "") -> list[str]:
        """List all markdown files in a folder (relative paths)."""
        return await server_instance.list_files(folder)

    @mcp.tool()
    async def get_graph(center: str | None = None, depth: int = 1) -> dict:
        """Get wikilink graph centered on a note (or full graph if no center)."""
        graph = await server_instance.get_graph(center, depth)
        return graph.model_dump()

    return mcp


def main() -> None:
    """Entry point for stdio transport."""
    import sys

    vault_path = "C:\\the force"
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    elif "OBSIDIAN_VAULT_PATH" in os.environ:
        vault_path = os.environ["OBSIDIAN_VAULT_PATH"]

    config = VaultConfig(vault_path=vault_path)
    mcp = create_server(config)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
