#!/usr/bin/env python3
"""
Quick verification of the current evaluate_agent_rules function
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

# First, let's check what's in the current server.py file
print("Checking current server.py...")
print("=" * 70)

# Read the server.py file to check the evaluate_agent_rules function
server_path = "C:\the force\03_Context\projects\mission-control\server.py"

with open(server_path, 'r') as f:
    content = f.read()

# Find the evaluate_agent_rules function
eval_start = content.find('def evaluate_agent_rules(rules_text, message_content):')
if eval_start == -1:
    print("❌ evaluate_agent_rules function not found in server.py!")
    sys.exit(1)

# Find the end of the function (next function definition)
next_func = content.find('\nclass AgentListener:', eval_start)
if next_func == -1:
    next_func = len(content)

function_code = content[eval_start:next_func]
print("Current evaluate_agent_rules function:")
print("=" * 70)
print(function_code)
print("=" * 70)
print()

# Now try to test it
try:
    from server import evaluate_agent_rules

    # Test with simple case
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

    print("Testing with simple case...")
    result = evaluate_agent_rules(obiwan_rules, "I need a new feature for this system")
    print(f"Feature request result: {result}")
    print(f"Number of actions: {len(result)}")

    if len(result) == 3:
        print("✅ SUCCESS: Function is working!")
    else:
        print(f"❌ FAILED: Expected 3 actions, got {len(result)}")

except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()