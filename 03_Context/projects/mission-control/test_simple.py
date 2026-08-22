#!/usr/bin/env python3
"""
Quick verification of the evaluate_agent_rules function
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from server import evaluate_agent_rules

# Test Obi-Wan rules (from server.py seeding)
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
print(f"Rules: {obiwan_rules}")
print()

# Test feature request
test_msg = "I need a new feature for this system"
print(f"Test message: '{test_msg}'")
print(f"Looking for keywords: 'feature', 'new capability'")
print(f"'feature' in message: {'feature' in test_msg.lower()}")
print(f"'new capability' in message: {'new capability' in test_msg.lower()}")
print()

# Parse rules to see what we're working with
from server import parse_agent_rules
parsed_rules = parse_agent_rules(obiwan_rules)
print(f"Parsed {len(parsed_rules)} protocols")
for i, rule in enumerate(parsed_rules):
    print(f"Protocol {i+1}: {rule['protocol']}")
    print(f"  Condition: '{rule['conditions'][0]}'")
    print(f"  Actions: {rule['actions']}")
    
    # Check if this matches our message
    condition = rule['conditions'][0]
    if "contains" in condition.lower():
        # Extract quoted terms
        import re
        quoted_matches = re.findall(r'"([^"]*)"|\'([^\']*)\'', condition)
        print(f"  Quoted terms: {quoted_matches}")
        
        for quoted_match in quoted_matches:
            term = quoted_match[0] or quoted_match[1]
            print(f"    Term '{term}' in message: {term.lower() in test_msg.lower()}")

print()
print("Now running evaluate_agent_rules function...")
actions = evaluate_agent_rules(obiwan_rules, test_msg)
print(f"Actions returned: {actions}")
print(f"Number of actions: {len(actions)}")

if len(actions) == 3:
    print("✅ SUCCESS: Function returned 3 actions as expected")
else:
    print(f"❌ FAILURE: Expected 3 actions, got {len(actions)}")