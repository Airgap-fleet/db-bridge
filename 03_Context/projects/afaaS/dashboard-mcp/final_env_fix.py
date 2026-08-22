#!/usr/bin/env python3
"""
Fix the .env file DATABASE_URL placeholder password.
This script handles the escaping issues properly.
"""

import os
from pathlib import Path

def main():
    project_dir = Path("C:/the force/03_Context/projects/afaaS/dashboard-mcp")
    env_path = project_dir / ".env"
    
    print(f"Project directory: {project_dir}")
    print(f"Environment file: {env_path}")
    print(f"Exists: {env_path.exists()}")
    
    if not env_path.exists():
        print("❌ .env file does not exist!")
        return False
    
    # Read the current content
    with open(env_path, 'r') as f:
        content = f.read()
    
    print("\n=== Current .env content ===")
    print(content)
    
    # Check what we need to fix
    if "DATABASE_URL=postgresql://postgres:***@localhost:5432/dashboard_mcp" in content:
        print("\n🔍 Found placeholder password to fix")
        
        # Create the corrected line
        corrected_line = "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/dashboard_mcp"
        
        # Split into lines and replace
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "DATABASE_URL=postgresql://postgres:***@localhost:5432/dashboard_mcp" in line:
                lines[i] = corrected_line
                print(f"✅ Fixed line {i+1}: {line}")
                print(f"   → {corrected_line}")
                break
        
        # Join back and write
        new_content = '\n'.join(lines)
        
        with open(env_path, 'w') as f:
            f.write(new_content)
        
        print("\n✅ .env file fixed successfully!")
        
        # Verify
        with open(env_path, 'r') as f:
            verify_content = f.read()
        
        if corrected_line in verify_content:
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