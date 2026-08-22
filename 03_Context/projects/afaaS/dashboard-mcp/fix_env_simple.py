#!/usr/bin/env python3
"""
Fix .env file by replacing the placeholder password with actual password.
Simple script that reads, replaces, and writes the file directly.
"""

import os

def main():
    project_dir = "/c/the force/03_Context/projects/afaaS/dashboard-mcp"
    env_path = os.path.join(project_dir, ".env")
    
    print("Fixing .env file...")
    print(f"Path: {env_path}")
    
    # Read current content
    with open(env_path, 'r') as f:
        lines = f.readlines()
    
    print("\n=== Current content ===")
    for i, line in enumerate(lines):
        print(f"{i+1}: {line.rstrip()}")
    
    # Fix the DATABASE_URL line
    fixed_lines = []
    for line in lines:
        if "DATABASE_URL=postgresql://postgres:***@localhost:5432/dashboard_mcp" in line:
            new_line = "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/dashboard_mcp\n"
            print(f"\nFixed line {lines.index(line) + 1}:")
            print(f"  OLD: {line.rstrip()}")
            print(f"  NEW: {new_line.rstrip()}")
            fixed_lines.append(new_line)
        else:
            fixed_lines.append(line)
    
    # Write back
    with open(env_path, 'w') as f:
        f.writelines(fixed_lines)
    
    print("\n=== Fixed content ===")
    with open(env_path, 'r') as f:
        for i, line in enumerate(f):
            print(f"{i+1}: {line.rstrip()}")
    
    print("\n✓ .env file fixed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)