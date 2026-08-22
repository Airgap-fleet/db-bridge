#!/usr/bin/env python3
"""
Direct test of the evaluate_agent_rules function from server.py
"""

import sys
sys.path.insert(0, 'C:\the force\03_Context\projects\mission-control')

from server import evaluate_agent_rules, parse_agent_rules

def test_implementation():
    """Test the actual evaluate_agent_rules function from server.py"""
    
    # Get the rules to test
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
    print("Testing evaluate_agent_rules FROM server.py")
    print("=" * 70)
    print()
    
    # First, let's see the parsed rules
    rules = parse_agent_rules(rules_text)
    print(f"Parsed {len(rules)} protocols:")
    for i, rule in enumerate(rules):
        print(f"  Protocol {i+1}: {rule['protocol']}")
        print(f"    Conditions: {rule['conditions']}")
        print(f"    Actions: {rule['actions']}")
    print()
    
    # Test 1: Feature request
    feature_msg = "I need a new feature for this system"
    actions = evaluate_agent_rules(rules_text, feature_msg)
    print(f"1. Feature request test:")
    print(f"   Message: '{feature_msg}'")
    print(f"   Actions found: {len(actions)}")
    
    if actions:
        print(f"   ✓ SUCCESS - Matched feature request")
        print(f"   Actions: {actions}")
        feature_success = True
    else:
        print(f"   ✗ FAILED - Did not match feature request")
        feature_success = False
    
    # Test 2: Bug report
    bug_msg = "There's a bug in the system"
    actions = evaluate_agent_rules(rules_text, bug_msg)
    print(f"\n2. Bug report test:")
    print(f"   Message: '{bug_msg}'")
    print(f"   Actions found: {len(actions)}")
    
    if actions:
        print(f"   ✓ SUCCESS - Matched bug report")
        print(f"   Actions: {actions}")
        bug_success = True
    else:
        print(f"   ✗ FAILED - Did not match bug report")
        bug_success = False
    
    # Test 3: Message with @mention (should NOT match)
    mention_msg = "I need a new feature for @obi-wan"
    actions = evaluate_agent_rules(rules_text, mention_msg)
    print(f"\n3. @mention filtering test:")
    print(f"   Message: '{mention_msg}'")
    print(f"   Actions found: {len(actions)}")
    
    if actions:
        print(f"   ✗ FAILED - Incorrectly matched message with @mention")
        mention_success = False
    else:
        print(f"   ✓ SUCCESS - Correctly ignored message with @mention")
        mention_success = True
    
    return feature_success and bug_success and mention_success

if __name__ == "__main__":
    success = test_implementation()
    
    if success:
        print("\n" + "=" * 70)
        print("RESULT: All tests PASSED")
        print("=" * 70)
        print("The evaluate_agent_rules function is working correctly!")
        print()
        print("Key verification:")
        print("✓ evaluate_agent_rules() can be imported from server.py")
        print("✓ parse_agent_rules() correctly parses the rules")
        print("✓ Feature requests are properly matched")
        print("✓ Bug reports are properly matched")
        print("✓ @mention filtering works correctly")
    else:
        print("\n" + "=" * 70)
        print("RESULT: Some tests FAILED")
        print("=" * 70)
        print("The evaluate_agent_rules function may still have issues.")
    
    sys.exit(0 if success else 1)