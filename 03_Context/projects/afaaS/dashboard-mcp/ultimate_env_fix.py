#!/usr/bin/env python3
"""
Comprehensive fix for .env file - writes the exact correct content.
"""

import os
from pathlib import Path

def main():
    # Get the project directory
    project_dir = Path("C:/the force/03_Context/projects/afaaS/dashboard-mcp")
    env_path = project_dir / ".env"
    
    print(f"Project directory: {project_dir}")
    print(f"Environment file: {env_path}")
    print(f"File exists: {env_path.exists()}")
    print(f"File permissions: {oct(env_path.stat().st_mode) if env_path.exists() else 'N/A'}")
    
    # The exact correct content
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
    
    if env_path.exists():
        # Read the current content
        with open(env_path, 'r', encoding='utf-8') as f:
            current_content = f.read()
        
        print(f"\n=== Current .env content ===")
        print(current_content)
        
        print(f"\n=== Checking if content is already correct ===")
        if current_content == correct_content:
            print("✅ .env file already has correct content!")
            return True
        
        print(f"\n=== Content differs - writing corrected version ===")
        
        # Write the correct content
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(correct_content)
        
        print("✅ .env file has been corrected")
        
        # Verify the write
        with open(env_path, 'r', encoding='utf-8') as f:
            verify_content = f.read()
        
        if verify_content == correct_content:
            print("✅ Verification: .env file is now correct")
            
            print(f"\n=== Final .env content ===")
            print(verify_content)
            return True
        else:
            print("❌ Verification FAILED: File content incorrect")
            print(f"Expected length: {len(correct_content)}")
            print(f"Actual length: {len(verify_content)}")
            return False
    else:
        print("❌ .env file does not exist!")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)