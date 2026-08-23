#!/usr/bin/env python3
"""Fix PostgreSQL MCP Server DSN patterns across all relevant files."""

import os

files_to_fix = [
    "/c/the force/03_Context/projects/afaaS/postgresql-mcp/src/postgresql_mcp/models.py",
    "/c/the force/03_Context/projects/afaaS/postgresql-mcp/tests/conftest.py",
    "/c/the force/03_Context/projects/afaaS/postgresql-mcp/tests/test_core.py",
    "/c/the force/03_Context/projects/afaaS/postgresql-mcp/tests/test_models.py",
    "/c/the force/03_Context/projects/afaaS/postgresql-mcp/tests/test_tools.py",
]

print("Fixing PostgreSQL MCP Server DSN patterns...")
print("=" * 60)

for file_path in files_to_fix:
    if not os.path.exists(file_path):
        print(f"✗ File not found: {os.path.basename(file_path)}")
        continue
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    original = content
    # Replace postgres:***@ with postgres:postgres@
    new_content = content.replace('postgres:***@', 'postgres:postgres@')
    
    if new_content != original:
        with open(file_path, 'w') as f:
            f.write(new_content)
        print(f"✓ Fixed: {os.path.basename(file_path)}")
    else:
        print(f"  No changes needed: {os.path.basename(file_path)}")

print("\n" + "=" * 60)
print("DSN fix process complete!")
print("\nChecking for remaining patterns...")
print("-" * 60)

for file_path in files_to_fix:
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            content = f.read()
        if 'postgres:***@' in content:
            print(f"✗ Still has postgres:***@: {os.path.basename(file_path)}")
        else:
            print(f"✓ Clean: {os.path.basename(file_path)}")