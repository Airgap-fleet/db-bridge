import os
import json
import hashlib
from datetime import datetime
from pathlib import Path

VAULT_PATH = r"C:\the force"
INDEX_PATH = r"C:\the force\05_Skills\search-index.json"

# Collect all markdown files
md_files = []
for root, dirs, files in os.walk(VAULT_PATH):
    # Skip .git, .obsidian, Chat Logs (too verbose for index)
    if any(skip in root for skip in ['.git', '.obsidian', 'Chat Logs']):
        continue
    for f in files:
        if f.endswith('.md'):
            full_path = os.path.join(root, f)
            md_files.append(full_path)

print(f"Found {len(md_files)} markdown files to index")

# Build index
index = {
    "version": "1.0.0",
    "created_at": datetime.now().isoformat(),
    "vault_path": VAULT_PATH,
    "total_files": len(md_files),
    "files": []
}

for filepath in md_files:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Get relative path
        rel_path = os.path.relpath(filepath, VAULT_PATH)
        
        # Extract frontmatter if present
        frontmatter = {}
        body = content
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                import yaml
                try:
                    frontmatter = yaml.safe_load(parts[1]) or {}
                    body = parts[2]
                except:
                    pass
        
        # Extract headings
        import re
        headings = re.findall(r'^(#{1,6})\s+(.+)$', body, re.MULTILINE)
        
        # Extract wikilinks
        wikilinks = re.findall(r'\[\[([^\]]+)\]\]', content)
        
        # Extract tags from frontmatter or inline
        tags = frontmatter.get('tags', [])
        if isinstance(tags, str):
            tags = [tags]
        
        # Calculate content hash
        content_hash = hashlib.md5(content.encode()).hexdigest()[:12]
        
        # File stats
        stat = os.stat(filepath)
        
        index["files"].append({
            "path": rel_path,
            "absolute_path": filepath,
            "title": frontmatter.get('title', os.path.splitext(os.path.basename(filepath))[0]),
            "frontmatter": frontmatter,
            "headings": [{"level": len(h[0]), "text": h[1]} for h in headings],
            "wikilinks": wikilinks,
            "tags": tags,
            "word_count": len(body.split()),
            "char_count": len(content),
            "content_hash": content_hash,
            "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "preview": body[:500].replace('\n', ' ')
        })
        print(f"  Indexed: {rel_path} ({len(body)} chars)")
    except Exception as e:
        print(f"  Error indexing {filepath}: {e}")

# Write index
os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
with open(INDEX_PATH, 'w', encoding='utf-8') as f:
    json.dump(index, f, indent=2, ensure_ascii=False)

print(f"\nIndex written to {INDEX_PATH}")
print(f"Total files: {index['total_files']}")
print(f"Total words: {sum(f['word_count'] for f in index['files'])}")
print(f"Total chars: {sum(f['char_count'] for f in index['files'])}")