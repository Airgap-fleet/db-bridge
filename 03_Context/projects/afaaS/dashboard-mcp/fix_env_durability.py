#!/usr/bin/env python3
"""
Simple script to fix the .env file DATABASE_URL placeholder password.
"""

import os
from pathlib import Path

def fix_env_file():
    project_dir = Path("C:/the force/03_Context/projects/afaaS/dashboard-mcp")
    env_path = project_dir / ".env"
    
    print(f"Fixing .env file at: {env_path}")
    
    # Read the current content
    with open(env_path, 'r') as f:
        content = f.read()
    
    print("\n=== Current .env content ===")
    print(content)
    
    # Check if it has the placeholder
    if "DATABASE_URL=postgresql://postgres:***@localhost:5432/dashboard_mcp" in content:
        print("\n✅ Found placeholder password to fix")
        
        # Replace the placeholder with actual password
        new_content = content.replace(
            "DATABASE_URL=postgresql://postgres:***@localhost:5432/dashboard_mcp",
            "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/dashboard_mcp"
        )
        
        # Write back
        with open(env_path, 'w') as f:
            f.write(new_content)
        
        print("\n✅ Successfully fixed .env file!")
        
        # Verify the fix
        with open(env_path, 'r') as f:
            verify_content = f.read()
        
        if "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/dashboard_mcp" in verify_content:
            print("✅ Verification: Database URL is now correct!")
            return True
        else:
            print("❌ Verification FAILED: Database URL still incorrect")
            return False
    elif "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/dashboard_mcp" in content:
        print("\n✅ Database URL is already correct!")
        return True
    else:
        print(f"\n⚠️  Unexpected .env content. Could not find expected DATABASE_URL pattern.")
        return False

if __name__ == "__main__":
    success = fix_env_file()
    exit(0 if success else 1)