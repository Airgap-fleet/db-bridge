#!/usr/bin/env python3
"""
Simple script to fix the .env file.
"""

import os
from pathlib import Path

def main():
    project_dir = Path("C:/the force/03_Context/projects/afaaS/dashboard-mcp")
    env_path = project_dir / ".env"
    
    print(f"Project directory: {project_dir}")
    print(f"Environment file: {env_path}")
    
    # Read the current content
    with open(env_path, 'r') as f:
        content = f.read()
    
    print("\n=== Current .env content ===")
    print(content)
    
    # Check for the placeholder pattern
    if "DATABASE_URL=postgresql://postgres:***@localhost:5432/dashboard_mcp" in content:
        print("\n🔍 Found placeholder password")
        
        # Create the corrected version
        corrected_content = """# Dashboard MCP Server Environment Variables

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
        
        # Write the corrected content
        with open(env_path, 'w') as f:
            f.write(corrected_content)
        
        print("✅ .env file fixed successfully!")
        
        # Verify
        with open(env_path, 'r') as f:
            verify_content = f.read()
        
        if "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/dashboard_mcp" in verify_content:
            print("✅ Verification: Database URL is now correct!")
            
            print("\n=== Final .env content ===")
            print(verify_content)
            return True
        else:
            print("❌ Verification FAILED")
            return False
    else:
        print("\n✅ .env file already has correct DATABASE_URL")
        return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)