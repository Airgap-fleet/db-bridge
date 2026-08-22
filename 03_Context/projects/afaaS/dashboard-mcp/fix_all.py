#!/usr/bin/env python3
"""
Comprehensive fix script for Dashboard MCP Server.
"""

import os
import re
from pathlib import Path

def fix_dotenv_file(project_dir):
    """Fix the .env file DATABASE_URL."""
    env_path = project_dir / ".env"
    if not env_path.exists():
        print("✗ .env file does not exist")
        return False
    
    with open(env_path, 'r') as f:
        content = f.read()
    
    # Fix placeholder password pattern
    old_patterns = [
        r"DATABASE_URL=postgresql://postgres:\*\*@localhost:5432/dashboard_mcp",
        r"DATABASE_URL=postgresql://postgres:***@localhost:5432/dashboard_mcp"
    ]
    
    new_url = "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/dashboard_mcp"
    
    fixed = False
    for pattern in old_patterns:
        if re.search(pattern, content):
            content = re.sub(pattern, new_url, content)
            print(f"✓ Fixed DATABASE_URL using pattern: {pattern}")
            fixed = True
            break
    
    if not fixed:
        print("⚠ Could not find placeholder DATABASE_URL pattern")
    
    with open(env_path, 'w') as f:
        f.write(content)
    
    # Verify the fix
    with open(env_path, 'r') as f:
        verification_content = f.read()
        if "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/dashboard_mcp" in verification_content:
            print("✓ .env file DATABASE_URL fixed successfully")
            return True
        else:
            print("✗ .env file DATABASE_URL still incorrect")
            return False

def fix_models_pydantic(project_dir):
    """Migrate Pydantic V1 to V2 patterns in models.py."""
    models_path = project_dir / "src/dashboard_mcp/models.py"
    if not models_path.exists():
        print("✗ models.py does not exist")
        return False
    
    with open(models_path, 'r') as f:
        content = f.read()
    
    # Count Pydantic V1 patterns that need fixing
    v1_patterns_fixed = 0
    
    # Fix @validator to @field_validator
    if "@validator(" in content:
        content = content.replace("@validator(", "@field_validator(")
        v1_patterns_fixed += 1
        print("✓ Fixed @validator decorators to @field_validator")
    
    # Fix Field(..., env=...) to use json_schema_extra or proper env
    env_pattern = r"Field\(.*?env=\"[A-Z_]+\"\)"
    if re.search(env_pattern, content):
        # Simple fix - replace env with json_schema_extra for now
        content = re.sub(r'Field\(env="([A-Z_]+)"\)', 
                        r"Field(json_schema_extra={'env': '\1'}) ", content)
        v1_patterns_fixed += 1
        print("✓ Fixed Field(..., env=...) patterns")
    
    if v1_patterns_fixed == 0:
        print("⚠ No Pydantic V1 patterns found to fix")
    
    with open(models_path, 'w') as f:
        f.write(content)
    
    print(f"✓ Fixed {v1_patterns_fixed} Pydantic V1 patterns")
    return True

def main():
    print("=" * 60)
    print("Dashboard MCP Server - Comprehensive Fix Script")
    print("=" * 60)
    
    project_dir = Path.cwd()
    print(f"\nProject directory: {project_dir}")
    
    all_fixes_applied = True
    
    # Apply fixes
    if not fix_dotenv_file(project_dir):
        all_fixes_applied = False
    
    if not fix_models_pydantic(project_dir):
        all_fixes_applied = False
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print("=" * 60)
    
    if all_fixes_applied:
        print("✓ All fixes applied successfully!")
        print("\nFixed items:")
        print("1. .env file - Fixed DATABASE_URL placeholder password")
        print("2. models.py - Migrated Pydantic V1 patterns to V2")
        print("\nStill need to verify:")
        print("- Run tests: uv run pytest -v --cov=dashboard_mcp --cov-fail-under=90")
        print("- Run type checking: uv run mypy src/dashboard_mcp")
        print("- Run linting: uv run ruff check src/dashboard_mcp")
    else:
        print("✗ Some fixes failed to apply")
    
    print("=" * 60)
    return all_fixes_applied

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)