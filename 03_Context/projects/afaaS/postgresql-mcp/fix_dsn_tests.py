#!/usr/bin/env python3
"""Fix all PostgreSQL MCP Server DSN patterns in test files."""

import os
import re

# Files to fix
target_files = [
    "/c/the force/03_Context/projects/afaaS/postgresql-mcp/tests/test_core.py",
    "/c/the force/03_Context/projects/afaaS/postgresql-mcp/tests/conftest.py",
    "/c/the force/03_Context/projects/afaaS/postgresql-mcp/tests/test_models.py",
    "/c/the force/03_Context/projects/afaaS/postgresql-mcp/tests/test_tools.py",
]

for file_path in target_files:
    if not os.path.exists(file_path):
        print(f"✗ File not found: {file_path}")
        continue
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace the pattern
    original = content
    new_content = re.sub(
        r'postgres:\*\*@localhost:5432/postgres',
        r'postgres:postgres@localhost:5432/postgres',
        content
    )
    
    if new_content != original:
        with open(file_path, 'w') as f:
            f.write(new_content)
        print(f"✓ Fixed: {os.path.basename(file_path)}")
    else:
        print(f"  No change needed: {os.path.basename(file_path)}")

print("\nAll DSN patterns fixed!")