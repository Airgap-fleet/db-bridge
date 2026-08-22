#!/usr/bin/env python3
"""
Direct test of the current evaluate_agent_rules function
"""

import sys
import os
sys.path.insert(0, 'C:\the force\03_Context\projects\mission-control')

# Import the server module to get the evaluate_agent_rules function
from server import evaluate_agent_rules, parse_agent_rules

def test_current_implementation():
    """Test the current evaluate_agent_rules function"""
    
    rules_text = """# Protocol: Feature Requests
IF message contains "feature" OR "new capability" AND not @mentioned:
  - Reply with clarification questions
  - Create task in Backlog with priority Medium
  - Assign to self

# Protocol: Bug Reports
IF message contains "bug" OR "broken" OR "error":
  - Create task in Todo with priority High
  - Assign to self
  - Reply "On it""""
    
    print("=" * 70)
    print("TESTING CURRENT evaluate_agent_rules FROM server.py")
    print("=" * 70)
    
    # First, check if parse_agent_rules works
    rules = parse_agent_rules(rules_text)
    print(f"Parsed {len(rules)} protocols")
    for i, rule in enumerate(rules):
        print(f"Protocol {i+1}: {rule['protocol']}")
        print(f"  Conditions: {rule['conditions']}")
        print(f"  Actions: {rule['actions']}")
    
    print()
    
    # Test feature request
    feature_msg = "I need a new feature for this system"
    actions = evaluate_agent_rules(rules_text, feature_msg)
    print(f"Feature request test:")
    print(f"  Message: '{feature_msg}'")
    print(f"  Actions: {actions}")
    print(f"  Success: {len(actions) > 0}")
    
    if not actions:
        # Debug the condition checking
        print("\nDEBUG: Checking condition matching...")
        for rule in rules:
            for condition in rule['conditions']:
                print(f"  Condition: '{condition}'")
                print(f"    Contains 'contains': {'contains' in condition.lower()}")
                print(f"    Contains 'feature': {'feature' in condition.lower()}")
                print(f"    Message contains 'feature': {'feature' in feature_msg.lower()}")
                print(f"    Full condition match: {condition.replace('"', '').strip().lower()} in message_content.lower(): {condition.replace('"', '').strip().lower() in feature_msg.lower()}")
    
    return len(actions) > 0

if __name__ == "__main__":
    success = test_current_implementation()
    print(f"\nOverall result: {'SUCCESS' if success else 'FAILURE'}")
    sys.exit(0 if success else 1)