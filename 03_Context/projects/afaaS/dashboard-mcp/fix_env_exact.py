#!/usr/bin/env python3
"""
Simple script to fix the .env file format to match the exact requirements.
"""

import os
from pathlib import Path

def main():
    project_dir = Path("C:/the force/03_Context/projects/afaaS/dashboard-mcp")
    env_path = project_dir / ".env"
    
    print(f"Fixing .env file at: {env_path}")
    
    # Correct content as specified in the requirements
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
    
    # Read current content
    try:
        with open(env_path, 'r') as f:
            current_content = f.read()
        
        print("\n=== Current .env content ===")
        print(current_content)
        
        # Check if it matches the expected format
        if current_content == correct_content:
            print("\n✅ .env file already has the correct format!")
            return True
        else:
            print("\n🔄 Fixing .env file to match the exact format...")
            
            # Write the correct content
            with open(env_path, 'w') as f:
                f.write(correct_content)
            
            print("✅ .env file format corrected!")
            
            # Verify the fix
            with open(env_path, 'r') as f:
                verify_content = f.read()
            
            if verify_content == correct_content:
                print("✅ Verification: .env file format is now correct!")
                
                print("\n=== Final .env content ===")
                print(verify_content)
                return True
            else:
                print("❌ Verification FAILED: .env file format still incorrect")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)