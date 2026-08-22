#!/usr/bin/env python3
"""
Quick verification of the evaluate_agent_rules function
"""

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

# Test feature request
test_msg = "I need a new feature for this system"
actions = evaluate_agent_rules(obiwan_rules, test_msg)
print(f'Feature request actions: {actions}')
print(f'Number of actions: {len(actions)}')

# Test bug report
test_msg2 = "There's a bug in the system"
actions2 = evaluate_agent_rules(obiwan_rules, test_msg2)
print(f'Bug report actions: {actions2}')
print(f'Number of actions: {len(actions2)}')

if len(actions) == 3 and len(actions2) == 3:
    print('✅ All tests PASSED!')
else:
    print('❌ Some tests FAILED!')