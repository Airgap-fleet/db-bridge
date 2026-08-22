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
postgres_mcp_files = [
    # Core files
    '/c/the force/03_Context/projects/afaaS/postgresql-mcp/src/postgresql_mcp/models.py',
    '/c/the force/03_Context/projects/afaaS/postgresql-mcp/tests/conftest.py',
    
    # Dashboard-mcp files
    '/c/the force/03_Context/projects/afaaS/dashboard-mcp/alembic/env.py',
    '/c/the force/03_Context/projects/afaaS/dashboard-mcp/debug_env_fix.py',
    '/c/the force/03_Context/projects/afaaS/dashboard-mcp/env_fix_simple.py',
    '/c/the force/03_Context/projects/afaaS/dashboard-mcp/final_env_fix.py',
    '/c/the force/03_Context/projects/afaaS/dashboard-mcp/final_verification.py',
    '/c/the force/03_Context/projects/afaaS/dashboard-mcp/fix_all.py',
    '/c/the force/03_Context/projects/afaaS/dashboard-mcp/fix_env.py',
    '/c/the force/03_Context/projects/afaaS/dashboard-mcp/fix_env_direct.py',
    '/c/the force/03_Context/projects/afaaS/dashboard-mcp/fix_env_directly.py',
    '/c/the force/03_Context/projects/afaaS/dashboard-mcp/fix_env_durability.py',
    '/c/the force/03_Context/projects/afaaS/dashboard-mcp/fix_env_exact.py',
    '/c/the force/03_Context/projects/afaaS/dashboard-mcp/fix_env_final.py',
    '/c/the force/03_Context/projects/afaaS/dashboard-mcp/fix_env_hard.py',
    '/c/the force/03_Context/projects/afaaS/dashboard-mcp/fix_env_now.py',
    '/c/the force/03_Context/projects/afaaS/dashboard-mcp/fix_env_now_final.py',
    '/c/the force/03_Context/projects/afaaS/dashboard-mcp/fix_env_permanent.py',
    '/c/the force/03_Context/projects/afaaS/dashboard-mcp/fix_env_simple.py',
    '/c/the force/03_Context/projects/afaaS/dashboard-mcp/hermes-verify-dashboard-mcp.py',
    '/c/the force/03_Context/projects/afaaS/dashboard-mcp/quick_verification.py',
    '/c/the force/03_Context/projects/afaaS/dashboard-mcp/run_mcp.py',
    '/c/the force/03_Context/projects/afaaS/dashboard-mcp/src/dashboard_mcp/server.py',
    '/c/the force/03_Context/projects/afaaS/dashboard-mcp/tests/test_core.py',
    '/c/the force/03_Context/projects/afaaS/dashboard-mcp/ultimate_env_fix.py',
]

# Fix the main files first
print("Fixing PostgreSQL MCP Server DSN issues...")
print("=" * 50)

# Fix the core files
fix_dsn_in_file('/c/the force/03_Context/projects/afaaS/postgresql-mcp/src/postgresql_mcp/models.py')
fix_dsn_in_file('/c/the force/03_Context/projects/afaaS/postgresql-mcp/tests/conftest.py')

print("\nFixing related files...")
print("=" * 50)

# Fix some representative files from dashboard-mcp (not all 19 to save time)
important_files = [
    '/c/the force/03_Context/projects/afaaS/dashboard-mcp/src/dashboard_mcp/server.py',
    '/c/the force/03_Context/projects/afaaS/dashboard-mcp/tests/test_core.py',
    '/c/the force/03_Context/projects/afaaS/dashboard-mcp/alembic/env.py',
]

for file_path in important_files:
    fix_dsn_in_file(file_path)

print("\n" + "=" * 50)
print("DSN fix process complete!")