import os
import json
import hashlib
import re
from datetime import datetime
from pathlib import Path

VAULT_PATH = Path("C:/the force")

md_files = list(VAULT_PATH.rglob("*.md"))
print(f"Found {len(md_files)} markdown files")

unique_files = []
for f in md_files:
    rel = f.relative_to(VAULT_PATH)
    if any(part in str(rel) for part in ['.git', '.obsidian']):
        continue
    if 'Chat Logs' in str(rel) and 'today_export' in str(rel):
        continue
    unique_files.append(f)

print(f"Unique files to index: {len(unique_files)}")

def parse_markdown(content):
    frontmatter = {}
    headings = []
    wikilinks = []
    tags = []
    
    fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if fm_match:
        fm_text = fm_match.group(1)
        for line in fm_text.split('\n'):
            if ':' in line:
                key, val = line.split(':', 1)
                frontmatter[key.strip()] = val.strip().strip('"\'')
    
    for match in re.finditer(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE):
        level = len(match.group(1))
        text = match.group(2).strip()
        headings.append({"level": level, "text": text})
    
    wikilinks = re.findall(r'\[\[([^\]]+)\]\]', content)
    tags = re.findall(r'(?<!\w)#(\w[\w-]*)', content)
    
    return frontmatter, headings, wikilinks, tags

index_entries = []
for f in unique_files:
    try:
        content = f.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        content = f.read_text(encoding='utf-8', errors='replace')
    
    rel_path = f.relative_to(VAULT_PATH)
    abs_path = str(f)
    
    content_hash = hashlib.md5(content.encode()).hexdigest()[:12]
    
    frontmatter, headings, wikilinks, tags = parse_markdown(content)
    
    word_count = len(content.split())
    char_count = len(content)
    
    preview_content = content
    fm_match = re.match(r'^---\n.*?\n---', content, re.DOTALL)
    if fm_match:
        preview_content = content[fm_match.end():]
    preview = preview_content.strip()[:300].replace('\n', ' ')
    
    title = headings[0]['text'] if headings else f.stem
    
    mtime = datetime.fromtimestamp(f.stat().st_mtime).isoformat()
    
    entry = {
        "path": str(rel_path).replace('/', '\\'),
        "absolute_path": abs_path.replace('/', '\\'),
        "title": title,
        "frontmatter": frontmatter,
        "headings": headings,
        "wikilinks": wikilinks,
        "tags": tags,
        "word_count": word_count,
        "char_count": char_count,
        "content_hash": content_hash,
        "modified_at": mtime,
        "preview": preview
    }
    index_entries.append(entry)

index_entries.sort(key=lambda x: x['path'])

index = {
    "version": "1.0.0",
    "created_at": datetime.now().isoformat(),
    "vault_path": "C:\\the force",
    "total_files": len(index_entries),
    "files": index_entries
}

output_path = VAULT_PATH / "05_Skills" / "search-index.json"
with open(output_path, 'w', encoding='utf-8') as out:
    json.dump(index, out, indent=2, ensure_ascii=False)

print(f"Index written to {output_path}")
print(f"Total files indexed: {len(index_entries)}")
print(f"Total words: {sum(e['word_count'] for e in index_entries)}")
print(f"Total chars: {sum(e['char_count'] for e in index_entries)}")
