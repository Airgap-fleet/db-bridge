#!/usr/bin/env python3
"""
Vault Reindex Script for Obsidian Vault at C:\the force
Rebuilds full-text search index and vector embeddings.
"""

import os
import json
import hashlib
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import re

VAULT_PATH = Path(r"C:\the force")
SEARCH_INDEX_PATH = VAULT_PATH / "05_Skills" / "search-index.json"
DAILY_LOG_DIR = VAULT_PATH / "04_Daily_Logs" / datetime.now().strftime("%Y-%m-%d")
VAULT_HEALTH_LOG = DAILY_LOG_DIR / "vault-health.md"

# Ollama configuration
OLLAMA_HOST = "http://localhost:11434"
EMBEDDING_MODEL = "qwen2.5:14b"  # Using available model for embeddings


def get_all_markdown_files(vault_path: Path) -> List[Path]:
    """Recursively find all .md files in the vault."""
    md_files = []
    for root, dirs, files in os.walk(vault_path):
        # Skip hidden directories and .git
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '.git']
        for file in files:
            if file.endswith('.md'):
                full_path = Path(root) / file
                md_files.append(full_path)
    return md_files


def read_file_content(filepath: Path) -> str:
    """Read file content with error handling."""
    try:
        return filepath.read_text(encoding='utf-8')
    except Exception as e:
        print(f"Warning: Could not read {filepath}: {e}")
        return ""


def extract_frontmatter(content: str) -> tuple[Dict[str, Any], str]:
    """Extract YAML frontmatter from markdown content."""
    frontmatter = {}
    body = content
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            try:
                import yaml
                frontmatter = yaml.safe_load(parts[1]) or {}
                body = parts[2]
            except Exception:
                pass
    return frontmatter, body


def extract_headings(content: str) -> List[Dict[str, Any]]:
    """Extract all headings from markdown content."""
    headings = []
    for match in re.finditer(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE):
        level = len(match.group(1))
        text = match.group(2).strip()
        headings.append({"level": level, "text": text})
    return headings


def extract_wikilinks(content: str) -> List[str]:
    """Extract all Obsidian wikilinks [[...]] from content."""
    return re.findall(r'\[\[([^\]]+)\]\]', content)


def extract_tags(content: str) -> List[str]:
    """Extract all #tags from content."""
    return re.findall(r'(?<!\w)#([a-zA-Z0-9_\-/]+)', content)


def compute_content_hash(content: str) -> str:
    """Compute SHA256 hash of content (first 12 chars)."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()[:12]


def get_file_stats(filepath: Path) -> Dict[str, Any]:
    """Get file statistics."""
    stat = filepath.stat()
    return {
        "size": stat.st_size,
        "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
    }


def generate_embedding(text: str, model: str = EMBEDDING_MODEL) -> Optional[List[float]]:
    """Generate embedding using Ollama API."""
    try:
        import requests
        # Truncate text to avoid token limits
        truncated_text = text[:8000]
        response = requests.post(
            f"{OLLAMA_HOST}/api/embeddings",
            json={"model": model, "prompt": truncated_text},
            timeout=30
        )
        if response.status_code == 200:
            return response.json().get("embedding", [])
        else:
            print(f"Embedding API error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Warning: Could not generate embedding: {e}")
        return None


def build_search_index(vault_path: Path) -> Dict[str, Any]:
    """Build the complete search index for the vault."""
    print(f"Scanning vault: {vault_path}")
    md_files = get_all_markdown_files(vault_path)
    print(f"Found {len(md_files)} markdown files")

    index = {
        "version": "1.0.0",
        "created_at": datetime.now().isoformat(),
        "vault_path": str(vault_path),
        "total_files": len(md_files),
        "files": []
    }

    for i, filepath in enumerate(md_files, 1):
        try:
            relative_path = filepath.relative_to(vault_path)
        except ValueError:
            relative_path = filepath

        print(f"  [{i}/{len(md_files)}] Processing: {relative_path}")

        content = read_file_content(filepath)
        if not content:
            continue

        frontmatter, body = extract_frontmatter(content)
        headings = extract_headings(content)
        wikilinks = extract_wikilinks(content)
        tags = extract_tags(content)
        content_hash = compute_content_hash(content)
        stats = get_file_stats(filepath)

        # Generate embedding for semantic search
        # Use title + first 2000 chars of body for embedding
        title = frontmatter.get('title', relative_path.stem)
        embedding_text = f"{title}\n\n{body[:2000]}"
        embedding = generate_embedding(embedding_text)

        # Word count
        words = len(re.findall(r'\b\w+\b', body))

        file_entry = {
            "path": str(relative_path).replace('/', '\\\\'),
            "absolute_path": str(filepath).replace('/', '\\\\'),
            "title": title,
            "frontmatter": frontmatter,
            "headings": headings,
            "wikilinks": wikilinks,
            "tags": tags,
            "word_count": words,
            "char_count": len(content),
            "content_hash": content_hash,
            "modified_at": stats["modified_at"],
            "preview": body[:500].replace('\n', ' ').strip(),
        }

        if embedding:
            file_entry["embedding"] = embedding
            file_entry["embedding_model"] = EMBEDDING_MODEL

        index["files"].append(file_entry)

    return index


def write_search_index(index: Dict[str, Any], output_path: Path):
    """Write search index to JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    print(f"Search index written to: {output_path}")


def update_vault_health_log(index: Dict[str, Any]):
    """Append reindex completion to vault-health.md."""
    DAILY_LOG_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%H:%M:%S")
    total_files = index["total_files"]
    total_words = sum(f.get("word_count", 0) for f in index["files"])
    files_with_embeddings = sum(1 for f in index["files"] if "embedding" in f)

    log_entry = f"""

## Vault Reindex — {timestamp}

- **Files indexed:** {total_files}
- **Total words:** {total_words:,}
- **Files with embeddings:** {files_with_embeddings}/{total_files}
- **Index file:** `05_Skills/search-index.json`
- **Embedding model:** {EMBEDDING_MODEL}
"""

    if VAULT_HEALTH_LOG.exists():
        content = VAULT_HEALTH_LOG.read_text(encoding='utf-8')
        # Append before any trailing whitespace
        content = content.rstrip() + log_entry + "\n"
    else:
        content = f"# Vault Health Log — {datetime.now().strftime('%Y-%m-%d')}\n{log_entry}\n"

    VAULT_HEALTH_LOG.write_text(content, encoding='utf-8')
    print(f"Vault health log updated: {VAULT_HEALTH_LOG}")


def git_commit(message: str):
    """Commit changes to git."""
    try:
        # Check if we're in a git repo
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=VAULT_PATH,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print("Not a git repository or git not available")
            return

        # Add the changed files
        subprocess.run(["git", "add", "05_Skills/search-index.json"], cwd=VAULT_PATH, check=False)
        subprocess.run(["git", "add", f"04_Daily_Logs/{datetime.now().strftime('%Y-%m-%d')}/vault-health.md"], cwd=VAULT_PATH, check=False)

        # Commit
        result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=VAULT_PATH,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"Git commit successful: {message}")
            print(result.stdout)
        else:
            print(f"Git commit failed (may be no changes): {result.stderr}")
    except Exception as e:
        print(f"Git commit error: {e}")


def main():
    print("=" * 60)
    print("VAULT REINDEX STARTED")
    print("=" * 60)

    # Build the search index
    index = build_search_index(VAULT_PATH)

    # Write the index
    write_search_index(index, SEARCH_INDEX_PATH)

    # Update vault health log
    update_vault_health_log(index)

    # Git commit
    commit_msg = f"chore: vault reindex {datetime.now().strftime('%Y-%m-%d')}"
    git_commit(commit_msg)

    print("=" * 60)
    print("VAULT REINDEX COMPLETED")
    print("=" * 60)
    print(f"Indexed {index['total_files']} files")
    print(f"Search index: {SEARCH_INDEX_PATH}")
    print(f"Health log: {VAULT_HEALTH_LOG}")


if __name__ == "__main__":
    main()