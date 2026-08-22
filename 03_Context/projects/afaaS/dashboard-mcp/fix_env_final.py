#!/usr/bin/env python3
"""
Simple script to fix the .env file DATABASE_URL issue.
This addresses the blocking issue that prevents tests from running.
"""

import os
from pathlib import Path

def main():
    # Get the project directory
    project_dir = Path("C:/the force/03_Context/projects/afaaS/dashboard-mcp")
    env_path = project_dir / ".env"
    
    print(f"Project directory: {project_dir}")
    print(f"Environment file path: {env_path}")
    print(f"File exists: {env_path.exists()}")
    
    # Read the current content
    if not env_path.exists():
        print("❌ .env file does not exist!")
        return False
    
    with open(env_path, 'r') as f:
        content = f.read()
    
    print("\n=== Current .env content ===")
    print(content)
    
    # Check if the placeholder is still there
    if "DATABASE_URL=postgresql://postgres:***@localhost:5432/dashboard_mcp" in content:
        print("\n🔍 Found placeholder password that needs to be fixed")
        
        # Create the correct content
        correct_content = """# Dashboard MCP Server Environment Variables

# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/dashboard_mcp
REDIS_URL=redis://localhost:6379

# Server Configuration
DASHBOARD_MCP_PORT=8000
DASHBOARD_MCP_WS_ENABLED=true

# Paths
DASHBOARD_MCP_AGENTCOMMS_PATH=AgentComms.md
DASHBOARD_MCP_FLEET_CONFIG=fleet.yaml
DASHBOARD_MCP_CHANNELS_DIR=channels

# Application Settings
DASHBOARD_MCP_ENABLE_GROUP_CHAT=true
DASHBOARD_MCP_DEFAULT_CHANNELS=general,alerts,handoffs
DASHBOARD_MCP_CORS_ORIGINS=*

# Security
DASHBOARD_MCP_AUTH_TOKEN=your-secret-token-here

# Logging (optional)
DASHBOARD_MCP_LOG_LEVEL=INFO
LOG_DIR=logs"""
        
        # Write the correct content
        with open(env_path, 'w') as f:
            f.write(correct_content)
        
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
        print("✅ .env file appears to have the correct DATABASE_URL")
        return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)