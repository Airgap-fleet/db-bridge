import json
import os
import re
from datetime import datetime
from pathlib import Path

vault_path = Path(r"C:/the force")
md_files = list(vault_path.rglob("*.md"))

index = {
    "version": 1,
    "updated": datetime.now().isoformat(),
    "total_files": len(md_files),
    "files": []
}

for md_file in md_files:
    try:
        content = md_file.read_text(encoding="utf-8")
        rel_path = md_file.relative_to(vault_path)
        
        # Extract headings
        headings = re.findall(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE)
        
        # Extract wikilinks
        wikilinks = re.findall(r'\[\[([^\]]+)\]\]', content)
        
        # Extract tags
        tags = re.findall(r'#([a-zA-Z0-9_-]+)', content)
        
        # Word count
        words = len(content.split())
        
        index["files"].append({
            "path": str(rel_path),
            "title": md_file.stem,
            "headings": [h[1] for h in headings],
            "heading_levels": [len(h[0]) for h in headings],
            "wikilinks": wikilinks,
            "tags": list(set(tags)),
            "word_count": words,
            "size_bytes": md_file.stat().st_size,
            "modified": datetime.fromtimestamp(md_file.stat().st_mtime).isoformat()
        })
    except Exception as e:
        print(f"Error reading {md_file}: {e}")

# Write search index
index_path = vault_path / "05_Skills" / "search-index.json"
index_path.parent.mkdir(parents=True, exist_ok=True)
index_path.write_text(json.dumps(index, indent=2), encoding="utf-8")

print(f"Indexed {len(md_files)} files")
print(f"Written to {index_path}")
print(f"Total words: {sum(f['word_count'] for f in index['files'])}")