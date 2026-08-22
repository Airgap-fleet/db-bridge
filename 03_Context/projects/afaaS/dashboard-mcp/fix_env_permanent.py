#!/usr/bin/env python3
"""
Direct fix for .env file placeholder password issue.
This script reads the .env file, fixes the DATABASE_URL, and writes it back.
"""

import os
from pathlib import Path

def fix_env_file():
    # Project directory
    project_dir = Path("C:/the force/03_Context/projects/afaaS/dashboard-mcp")
    env_path = project_dir / ".env"
    
    print(f"Project directory: {project_dir}")
    print(f"Environment file: {env_path}")
    
    # Read the current content
    try:
        with open(env_path, 'r') as f:
            content = f.read()
        
        print("\n=== Current .env content ===")
        print(content)
        
        # Check if the placeholder exists
        if "DATABASE_URL=postgresql://postgres:***@localhost:5432/dashboard_mcp" in content:
            print("\n🔍 Found placeholder password pattern")
            
            # Replace the placeholder with actual password
            new_content = content.replace(
                "DATABASE_URL=postgresql://postgres:***@localhost:5432/dashboard_mcp",
                "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/dashboard_mcp"
            )
            
            # Write back to file
            with open(env_path, 'w') as f:
                f.write(new_content)
            
            print("✅ Successfully replaced placeholder password")
            
            # Verify the change
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
                
        elif "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/dashboard_mcp" in content:
            print("✅ Database URL is already correct!")
            return True
        else:
            print("⚠️  Could not find expected DATABASE_URL pattern")
            # Show what we found instead
            for line in content.split('\n'):
                if "DATABASE_URL" in line:
                    print(f"Found: {line}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = fix_env_file()
    exit(0 if success else 1)