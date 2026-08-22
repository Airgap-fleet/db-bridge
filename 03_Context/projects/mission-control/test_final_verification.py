#!/usr/bin/env python3
"""
Direct test of the evaluate_agent_rules function
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from server import evaluate_agent_rules

# Test Obi-Wan rules exactly as in server.py
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
print(f"Feature request: {len(result)} actions - {result}")

# Test bug report  
result2 = evaluate_agent_rules(obiwan_rules, "There's a bug in the system")
print(f"Bug report: {len(result2)} actions - {result2}")

# Test @mention filtering
result3 = evaluate_agent_rules(obiwan_rules, "I need a new feature for @obi-wan")
print(f"@mention test: {len(result3)} actions - {result3}")

# Check if all working correctly
if len(result) == 3 and len(result2) == 3 and len(result3) == 0:
    print("✅ ALL TESTS PASSING!")
    print("✅ evaluate_agent_rules function working correctly!")
else:
    print("❌ SOME TESTS FAILING!")
    print(f"Feature: {len(result)} actions (expected 3)")
    print(f"Bug: {len(result2)} actions (expected 3)") 
    print(f"@mention: {len(result3)} actions (expected 0)")