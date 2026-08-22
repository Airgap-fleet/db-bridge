#!/usr/bin/env python3
"""
Dashboard MCP Server - Fix .env file placeholder password.
"""

import os
from pathlib import Path

def main():
    project_dir = Path("C:/the force/03_Context/projects/afaaS/dashboard-mcp")
    env_path = project_dir / ".env"
    
    print(f"Fixing .env file at: {env_path}")
    
    # Read current content
    with open(env_path, 'r') as f:
        lines = f.readlines()
    
    print("\n=== Current .env content ===")
    for i, line in enumerate(lines):
        print(f"{i+1}: {line.rstrip()}")
    
    # Fix the DATABASE_URL line
    fixed_lines = []
    for line in lines:
        if "DATABASE_URL=postgresql://postgres:***@localhost:5432/dashboard_mcp" in line:
            new_line = "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/dashboard_mcp\n"
            print(f"\n🔄 Fixed line: {line.rstrip()} -> {new_line.rstrip()}")
            fixed_lines.append(new_line)
        else:
            fixed_lines.append(line)
    
    # Write back
    with open(env_path, 'w') as f:
        f.writelines(fixed_lines)
    
    print("\n✅ .env file has been fixed!")
    
    # Verify the fix
    with open(env_path, 'r') as f:
        verify_content = f.read()
    
    if "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/dashboard_mcp" in verify_content:
        print("✅ Verification: Database URL is now correct!")
        
        print("\n=== Final .env content ===")
        print(verify_content)
        return True
    else:
        print("❌ Verification FAILED: Database URL still incorrect")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)