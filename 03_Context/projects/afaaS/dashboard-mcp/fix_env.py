#!/usr/bin/env python3
"""
Fix .env file directly.
"""

import os

project_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(project_dir, ".env")

# Read the current content
with open(env_path, 'r') as f:
    lines = f.readlines()

# Fix the DATABASE_URL if it has placeholder
fixed_lines = []
for line in lines:
    if "DATABASE_URL=postgresql://postgres:***@localhost:5432/dashboard_mcp" in line:
        line = line.replace("DATABASE_URL=postgresql://postgres:***@localhost:5432/dashboard_mcp", "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/dashboard_mcp")
        print(f"Fixed DATABASE_URL: {line.strip()}")
    fixed_lines.append(line)

# Write back
with open(env_path, 'w') as f:
    f.writelines(fixed_lines)

print("Fixed .env file")
print("Content:")
with open(env_path, 'r') as f:
    print(f.read())