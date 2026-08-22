#!/usr/bin/env python3
"""
Fix the PostgreSQL MCP Server DSN in models.py by replacing postgres:***@localhost with postgres:postgres@localhost
"""

import re

file_path = "/c/the force/03_Context/projects/afaaS/postgresql-mcp/src/postgresql_mcp/models.py"

# Read the file
with open(file_path, 'r') as f:
    content = f.read()

print(f"Original DSN in file: {content[content.find('postgresql://postgres:***@localhost:5432/postgres'):content.find('postgresql://postgres:***@localhost:5432/postgres')+80]}")

# Fix the DSN pattern
old_pattern = 'postgresql://postgres:***@localhost:5432/postgres'
new_pattern = 'postgresql://postgres:postgres@localhost:5432/postgres'

if old_pattern in content:
    content = content.replace(old_pattern, new_pattern)
    print(f"✓ DSN pattern replaced: {old_pattern} → {new_pattern}")
else:
    # Try regex approach
    content = re.sub(
        r'postgresql://postgres:\*\*@localhost:5432/postgres',
        'postgresql://postgres:postgres@localhost:5432/postgres',
        content
    )
    print(f"✓ DSN pattern replaced using regex")

# Write back to file
with open(file_path, 'w') as f:
    f.write(content)

# Verify the fix
with open(file_path, 'r') as f:
    fixed_content = f.read()
    
if new_pattern in fixed_content:
    print("✅ SUCCESS: DSN pattern fixed in models.py")
    print(f"   Fixed pattern: {new_pattern}")
else:
    print("❌ FAILURE: Could not fix DSN pattern")
    print(f"   Content snippet: {fixed_content[fixed_content.find('default='):fixed_content.find('default=') + 200]}")