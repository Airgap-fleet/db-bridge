#!/usr/bin/env python3
"""
Fix PostgreSQL MCP Server DSN in all files.
"""

import re

def fix_file(file_path):
    """Fix DSN in a specific file."""
    print(f"\n🔧 Processing {file_path}")
    
    if not __import__("os").path.exists(file_path):
        print(f"  ✗ File not found: {file_path}")
        return False
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check if DSN needs fixing
    if 'postgres:***@localhost:5432/postgres' not in content:
        print(f"  ✓ No DSN fix needed - pattern already correct")
        return True
    
    # Fix the DSN
    old_pattern = 'postgres:***@localhost:5432/postgres'
    new_pattern = 'postgres:postgres@localhost:5432/postgres'
    
    # Try exact replacement first
    content = content.replace(old_pattern, new_pattern)
    
    # If exact replacement didn't work, try regex
    if content.count(old_pattern) > 0:
        content = re.sub(
            r'postgres:\*\*@localhost:5432/postgres',
            'postgres:postgres@localhost:5432/postgres',
            content
        )
    
    # Write back to file
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"  ✓ DSN fixed in {file_path}")
    return True

def main():
    print("=" * 70)
    print("POSTGRESQL MCP SERVER DSN FIX SCRIPT")
    print("=" * 70)
    
    # Files to fix
    files_to_fix = [
        "/c/the force/03_Context/projects/afaaS/postgresql-mcp/src/postgresql_mcp/models.py",
        "/c/the force/03_Context/projects/afaaS/postgresql-mcp/tests/conftest.py",
        "/c/the force/03_Context/projects/afaaS/postgresql-mcp/tests/test_core.py",
    ]
    
    success_count = 0
    total_count = len(files_to_fix)
    
    for file_path in files_to_fix:
        if fix_file(file_path):
            success_count += 1
    
    print("\n" + "=" * 70)
    print("FIX SUMMARY")
    print("=" * 70)
    print(f"Files processed: {total_count}")
    print(f"Successfully fixed: {success_count}")
    
    if success_count == total_count:
        print("\n🎉 ALL FILES FIXED SUCCESSFULLY!")
        print("The PostgreSQL MCP Server DSN issues have been resolved.")
        return 0
    else:
        print(f"\n⚠️  {total_count - success_count} files still need fixing")
        return 1

if __name__ == "__main__":
    exit(main())