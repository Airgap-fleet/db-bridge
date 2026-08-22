#!/usr/bin/env python3
"""
Simple script to fix the .env file.
This will replace the placeholder password with the actual password.
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
    with open(env_path, 'r') as f:
        content = f.read()
    
    print("\n=== Current .env content ===")
    print(content)
    
    # Check if the placeholder exists
    if "DATABASE_URL=postgresql://postgres:***@localhost:5432/dashboard_mcp" in content:
        print("\n🔍 Found placeholder password to fix")
        
        # Replace the placeholder with the actual password
        new_content = content.replace(
            "DATABASE_URL=postgresql://postgres:***@localhost:5432/dashboard_mcp",
            "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/dashboard_mcp"
        )
        
        # Write back to the file
        with open(env_path, 'w') as f:
            f.write(new_content)
        
        print("✅ Successfully fixed .env file!")
        
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
    else:
        print("\n✅ .env file already has correct DATABASE_URL")
        return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)