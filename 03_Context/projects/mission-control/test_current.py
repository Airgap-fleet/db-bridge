#!/usr/bin/env python3
"""
Quick test of the evaluate_agent_rules function
"""

import sys
import os

# Change to the mission-control directory
os.chdir("C:\the force\03_Context\projects\mission-control")

sys.path.insert(0, os.getcwd())

from server import evaluate_agent_rules

# Test Obi-Wan rules
obiwan_rules = """# Protocol: Feature Requests
IF message contains "feature" OR "new capability" AND not @mentioned:
  - Reply with clarification questions
  - Create task in Backlog with priority Medium
  - Assign to self

# Protocol: Bug Reports
IF message contains "bug" OR "broken" OR "error":
  - Create task in Todo with priority High
  - Assign to self
  - Reply "On it"""

print("Testing evaluate_agent_rules function...")
print()

# Test feature request
result = evaluate_agent_rules(obiwan_rules, "I need a new feature for this system")
print(f"Feature request: {len(result)} actions")

# Test bug report  
result2 = evaluate_agent_rules(obiwan_rules, "There's a bug in the system")
print(f"Bug report: {len(result2)} actions")

# Test @mention filtering
result3 = evaluate_agent_rules(obiwan_rules, "I need a new feature for @obi-wan")
print(f"@mention test: {len(result3)} actions")

if len(result) == 3 and len(result2) == 3 and len(result3) == 0:
    print("✅ ALL TESTS PASSING!")
else:
    print("❌ SOME TESTS FAILING!")
    print(f"Feature: {len(result)} (expected 3)")
    print(f"Bug: {len(result2)} (expected 3)")
    print(f"@mention: {len(result3)} (expected 0)")