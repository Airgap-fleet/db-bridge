#!/usr/bin/env python3
"""
Focused debug of evaluate_agent_rules function
"""

import re
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from server import parse_agent_rules, evaluate_agent_rules

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

print("=" * 70)
print("DEBUGGING evaluate_agent_rules function")
print("=" * 70)

# Let's trace through what happens step by step
test_message = "I need a new feature for this system"
print(f"\nTest Message: '{test_message}'")
print()

# Step 1: Parse the rules
print("1. Parsing rules...")
parsed_rules = parse_agent_rules(obiwan_rules)
print(f"   Parsed {len(parsed_rules)} protocols")
for i, rule in enumerate(parsed_rules):
    print(f"\n   Protocol {i+1}: {rule['protocol']}")
    print(f"   Conditions: {rule['conditions']}")
    print(f"   Actions: {rule['actions']}")

print("\n" + "=" * 70)

# Step 2: Try to evaluate manually
print("2. Manual evaluation check...")
print(f"   Test message: '{test_message}'")
print(f"   Looking for keywords: 'feature', 'new capability'")
print(f"   'feature' in message: {'feature' in test_message.lower()}")
print(f"   'new capability' in message: {'new capability' in test_message.lower()}")

# Step 3: Check if condition contains "contains"
condition = "message contains \"feature\" OR \"new capability\" AND not @mentioned"
print(f"\n   Condition: '{condition}'")
print(f"   Condition contains 'contains': {'contains' in condition.lower()}")

# Step 4: Extract quoted terms
quoted_matches = re.findall(r'"([^"]*)"|\'([^\']*)\'', condition)
print(f"   Quoted matches: {quoted_matches}")

if quoted_matches:
    for quoted_match in quoted_matches:
        term = quoted_match[0] or quoted_match[1]
        print(f"   Term: '{term}'")
        if term.lower() in test_message.lower():
            print(f"   ✅ MATCH: '{term}' found in message")
        else:
            print(f"   ❌ NO MATCH: '{term}' not in message")

print("\n" + "=" * 70)

# Step 5: Now try the actual function
print("3. Running evaluate_agent_rules function...")
actions = evaluate_agent_rules(obiwan_rules, test_message)
print(f"   Actions returned: {actions}")
print(f"   Number of actions: {len(actions)}")

if len(actions) == 0:
    print("\n❌ CRITICAL ISSUE: Function returned 0 actions!")
    print("This means the evaluate_agent_rules function is broken.")
    
    # Let's check the actual condition from the parsed rules
    print("\n   Let's examine the actual condition from parsed rules:")
    for rule in parsed_rules:
        for condition in rule['conditions']:
            print(f"   Parsed condition: '{condition}'")
            print(f"   Contains 'contains': {'contains' in condition.lower()}")
            
            # Try to extract terms from this condition
            quoted_matches = re.findall(r'"([^"]*)"|\'([^\']*)\'', condition)
            print(f"   Extracted terms: {quoted_matches}")
            
            if quoted_matches:
                for quoted_match in quoted_matches:
                    term = quoted_match[0] or quoted_match[1]
                    print(f"     Term '{term}' in message: {term.lower() in test_message.lower()}")
else:
    print(f"\n✅ SUCCESS: Function returned {len(actions)} actions")

print("\n" + "=" * 70)
print("Test completed.")