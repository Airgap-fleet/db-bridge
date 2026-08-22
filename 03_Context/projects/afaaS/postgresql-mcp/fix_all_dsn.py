import os
from pathlib import Path

# Fix all PostgreSQL MCP Server DSN patterns

def fix_dsn_in_file(file_path):
    """Replace postgres:***@localhost with postgres:postgres@localhost"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        original = content
        new_content = content.replace('postgres:***@localhost:5432/postgres', 'postgres:postgres@localhost:5432/postgres')
        
        if new_content != original:
            with open(file_path, 'w') as f:
                f.write(new_content)
            print(f"✓ Fixed: {file_path}")
            return True
        else:
            print(f"  No change needed: {file_path}")
            return False
    except Exception as e:
        print(f"✗ Error fixing {file_path}: {e}")
        return False

# Target files based on the search results
target_files = [
    # Core files
    '/c/the force/03_Context/projects/afaaS/postgresql-mcp/src/postgresql_mcp/models.py',
    '/c/the force/03_Context/projects/afaaS/postgresql-mcp/tests/conftest.py',
    '/c/the force/03_Context/projects/afaaS/postgresql-mcp/tests/test_core.py',
]

print("Fixing PostgreSQL MCP Server DSN issues...")
print("=" * 50)

for file_path in target_files:
    fix_dsn_in_file(file_path)

print("\nFixing test_core.py specific lines...")
print("=" * 50)

# Fix test_core.py manually since it has many lines
with open('/c/the force/03_Context/projects/afaaS/postgresql-mcp/tests/test_core.py', 'r') as f:
    content = f.read()

original = content
replacements = [
    ('dsn="postgresql://postgres:***@localhost:5432/postgres"', 'dsn="postgresql://postgres:postgres@localhost:5432/postgres"'),
    ('dsn="postgresql://postgres:***@localhost:5432/postgres",', 'dsn="postgresql://postgres:postgres@localhost:5432/postgres",'),
    ('assert core.config.dsn == "postgresql://postgres:***@localhost:5432/postgres"', 'assert core.config.dsn == "postgresql://postgres:postgres@localhost:5432/postgres"'),
]

for old_str, new_str in replacements:
    content = content.replace(old_str, new_str)

if content != original:
    with open('/c/the force/03_Context/projects/afaaS/postgresql-mcp/tests/test_core.py', 'w') as f:
        f.write(content)
    print("✓ Fixed: tests/test_core.py")
else:
    print("  No change needed: tests/test_core.py")

print("\n" + "=" * 50)
print("DSN fix process complete!")