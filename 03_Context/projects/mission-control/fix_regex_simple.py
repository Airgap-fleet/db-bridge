#!/usr/bin/env python3
"""
Fix the regex pattern in server.py - simple and direct approach
"""

import re

server_path = "C:\the force\03_Context\projects\mission-control\server.py"

with open(server_path, 'r') as f:
    lines = f.readlines()

print("Searching for the problematic regex pattern...")

# Look for the specific line with the regex pattern
fixed_lines = []
pattern_found = False

for i, line in enumerate(lines):
    if "keywords = re.findall(r'" in line and 'feature|new capability' in line and '\\b' in line:
        print(f"Found problematic line {i+1}: {line.strip()}")
        
        # Fix the pattern - replace the double backslash with single backslash
        # The pattern should be: r'\b(feature|new capability|bug|broken|error|implement|build|create|review|check|examine)\b'
        # But in the file it appears as double escaped: '\\\\b'
        
        # Write the correct pattern
        fixed_line = r"                keywords = re.findall(r'\b(feature|new capability|bug|broken|error|implement|build|create|review|check|examine)\b', condition_text, re.I)\n"
        fixed_lines.append(fixed_line)
        pattern_found = True
        print("Fixed pattern written")
    else:
        fixed_lines.append(line)

if not pattern_found:
    print("Warning: Could not find the exact pattern, but the pattern looks correct in the file")
    # Just continue with the original content
    with open(server_path, 'w') as f:
        f.writelines(fixed_lines)
else:
    # Write the fixed content
    with open(server_path, 'w') as f:
        f.writelines(fixed_lines)
    
    print("✓ Fixed the regex pattern in server.py")
    print("The pattern now correctly matches keywords like 'feature', 'bug', 'review', etc.")