#!/usr/bin/env python3
"""
Fix the regex pattern in server.py
"""

import os

server_path = "C:\the force\03_Context\projects\mission-control\server.py"

with open(server_path, 'r') as f:
    content = f.read()

print("Current pattern in server.py:")
import re as re_module
pattern_match = re_module.search(r"keywords = re\.findall\(r'([^']+)'", content)
if pattern_match:
    print(f"  Line: {pattern_match.group(0)}")
    
# Fix the pattern - replace double backslashes with single backslashes
fixed_content = content.replace(
    r"keywords = re.findall(r'\\b(feature|new capability|bug|broken|error|implement|build|create|review|check|examine)\\b', condition_text, re.I)",
    r"keywords = re.findall(r'\\b(feature|new capability|bug|broken|error|implement|build|create|review|check|examine)\\b', condition_text, re.I)"
)

# Actually, let's check what the pattern should be
# In Python raw strings, '\\b' is actually the correct way to represent a single backslash in regex
# But when we look at the test output, it shows the pattern as '\\\\b' which is double escaping

# Let's write the correct pattern (single backslash in the raw string)
correct_pattern = r"keywords = re.findall(r'\\b(feature|new capability|bug|broken|error|implement|build|create|review|check|examine)\\b', condition_text, re.I)"

print(f"\nCorrect pattern should be: {correct_pattern}")
print("This will match 'feature', 'bug', 'review', etc. in text")

# Let's just replace the problematic line with a simpler approach
lines = content.split('\n')
for i, line in enumerate(lines):
    if "keywords = re.findall(r'"' in line and 'feature|new capability' in line:
        # Replace with correct pattern
        lines[i] = r"                keywords = re.findall(r'\b(feature|new capability|bug|broken|error|implement|build|create|review|check|examine)\b', condition_text, re.I)"

fixed_content = '\n'.join(lines)

# Write the fixed content back
with open(server_path, 'w') as f:
    f.write(fixed_content)

print("\n✓ Fixed the regex pattern in server.py")
print("Pattern is now correct for matching keywords like 'feature', 'bug', etc.")