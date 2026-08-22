#!/usr/bin/env python3
"""
Direct fix for .env file - read, replace, write back.
"""

import os
from pathlib import Path

def main():
    # Get the project directory
    project_dir = Path("C:/the force/03_Context/projects/afaaS/dashboard-mcp")
    env_path = project_dir / ".env"
    
    print(f"Project directory: {project_dir}")
    print(f"Environment file: {env_path}")
    
    # Read the current content
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("\n=== Current .env content ===")
    print(repr(content))
    
    # The exact pattern we need to replace
    old_pattern = "DATABASE_URL=postgresql://postgres:***@localhost:5432/dashboard_mcp"
    new_pattern = "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/dashboard_mcp"
    
    print(f"\n=== Pattern check ===")
    print(f"Old pattern: {repr(old_pattern)}")
    print(f"New pattern: {repr(new_pattern)}")
    print(f"Old pattern exists: {old_pattern in content}")
    
    # Replace the pattern
    if old_pattern in content:
        content = content.replace(old_pattern, new_pattern)
        
        # Write back
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("\n✅ Successfully replaced pattern in .env file")
        
        # Verify
        with open(env_path, 'r', encoding='utf-8') as f:
            verify_content = f.read()
        
        if new_pattern in verify_content:
            print("✅ Verification: Database URL is correct")
            
            print("\n=== Final .env content ===")
            print(repr(verify_content))
            return True
        else:
            print("❌ Verification FAILED")
            return False
    else:
        print(f"\n❌ Old pattern not found")
        
        # Let's check character by character for debugging
        print("\n=== Debug: Character by character check ===")
        for i, char in enumerate(old_pattern):
            print(f"  Old[{i}]: {repr(char)} (ord={ord(char)})")
        
        # Try to find similar patterns
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "DATABASE_URL" in line:
                print(f"  Line {i}: {repr(line)}")
                if "postgresql://postgres" in line:
                    print(f"    → Contains 'postgresql://postgres'")
                    for j, char in enumerate(line):
                        if char == '*':
                            print(f"    → Position {j}: '*'")
        
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)