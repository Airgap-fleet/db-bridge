#!/usr/bin/env python3
"""
Quick debug script to identify the issue with evaluate_agent_rules
"""

import re
import sys
import os

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from server import evaluate_agent_rules, parse_agent_rules

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

print("=" * 70)
print("DEBUG: evaluate_agent_rules function")
print("=" * 70)
print()

print("1. Testing rule parsing...")
parsed_rules = parse_agent_rules(obiwan_rules)
print(f"   Parsed {len(parsed_rules)} protocols")
for i, rule in enumerate(parsed_rules):
    print(f"   Protocol {i+1}: {rule['protocol']}")
    print(f"   Conditions: {rule['conditions']}")
    print(f"   Actions: {rule['actions']}")

print()
print("2. Testing feature request...")
test_msg = "I need a new feature for this system"
print(f"   Message: '{test_msg}'")

# Step by step debugging
print()
print("3. Step-by-step debugging:")
print("   a. Parsing rules...")
rules = parse_agent_rules(obiwan_rules)
print(f"      Parsed {len(rules)} rules")

print("   b. Checking conditions:")
for i, rule in enumerate(rules):
    print(f"\n   Rule {i+1}: {rule['protocol']}")
    for j, condition in enumerate(rule['conditions']):
        print(f"      Condition {j+1}: '{condition}'")
        print(f"      Has 'contains': {'contains' in condition.lower()}")
        
        # Check for quoted terms
        quoted_matches = re.findall(r'"([^"]*)"|\'([^\']*)\'', condition)
        print(f"      Quoted terms: {quoted_matches}")
        
        if quoted_matches:
            for quoted_match in quoted_matches:
                term = quoted_match[0] or quoted_match[1]
                print(f"        Term '{term}' in message: {term.lower() in test_msg.lower()}")
                
                if term.lower() in test_msg.lower():
                    print(f"        ✅ Match found!")
                    break

print()
print("4. Running evaluate_agent_rules function...")
actions = evaluate_agent_rules(obiwan_rules, test_msg)
print(f"   Actions returned: {actions}")
print(f"   Number of actions: {len(actions)}")

if len(actions) == 3:
    print("   ✅ SUCCESS: Feature request correctly matched!")
else:
    print("   ❌ FAILED: Feature request not matched!")
    
    # Let's debug further
    print("\n   Further debugging:")
    print(f"   Message: '{test_msg}'")
    print(f"   Looking for 'feature': {'feature' in test_msg.lower()}")
    print(f"   Looking for 'new capability': {'new capability' in test_msg.lower()}")
    print(f"   Checking if 'contains' in condition: {'contains' in 'message contains \"feature\" OR \"new capability\" AND not @mentioned:'}")

print("=" * 70)