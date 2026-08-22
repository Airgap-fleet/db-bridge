#!/usr/bin/env python3
"""
Focused verification for the evaluate_agent_rules function.
"""

import re

def parse_agent_rules(rules_text):
    """Parse agent rules from markdown format and return list of rule dictionaries"""
    rules = []
    if not rules_text:
        return rules
    
    current_rule = None
    current_protocol = None
    
    for line in rules_text.split('\n'):
        line = line.strip()
        
        if line.startswith('# Protocol:'):
            current_protocol = line.replace('# Protocol:', '').strip()
            current_rule = {
                'protocol': current_protocol,
                'conditions': [],
                'actions': []
            }
            rules.append(current_rule)
        
        elif line.startswith('IF ') and current_rule:
            condition = line[3:].strip()
            if condition.endswith(':'):
                condition = condition[:-1].strip()
            current_rule['conditions'].append(condition)
        
        elif line.startswith('- '):
            action = line[2:].strip()
            current_rule['actions'].append(action)
    
    return rules

def evaluate_agent_rules_current(rules_text, message_content):
    """Evaluate if a message matches any of the agent's rules and return actions"""
    if not rules_text:
        return []
    
    rules = parse_agent_rules(rules_text)
    actions = []
    
    for rule in rules:
        # Check if any condition matches
        for condition in rule['conditions']:
            # Normalize condition for matching
            # Extract the actual condition from IF condition: format
            condition_text = condition
            
            # Check if condition contains keywords
            # Handle simple conditions like "message contains 'feature'"
            if "contains" in condition_text.lower():
                # Extract the text inside quotes or between keywords
                # Find quoted text
                quoted_matches = re.findall(r'"([^"]*)"|\\'([^\\']*)\\'', condition_text)
                if quoted_matches:
                    # Test each quoted term
                    for quoted_match in quoted_matches:
                        # quoted_match is a tuple (first_group, second_group)
                        term = quoted_match[0] or quoted_match[1]
                        if term.lower() in message_content.lower():
                            # Check if @mentioned condition is present and if @mention is in the message
                            if '@mentioned' in condition_text.lower() and '@mentioned' in message_content.lower():
                                continue  # Skip this rule if @mentioned is mentioned
                            actions.extend(rule['actions'])
                            break  # Only use first matching condition per rule
                    else:
                        continue
                    break  # Found a match for this rule
                else:
                    # No quotes found, check for keywords directly
                    keywords = re.findall(r'\\b(feature|new capability|bug|broken|error|implement|build|create|review|check|examine)\\b', condition_text, re.I)
                    if any(keyword.lower() in message_content.lower() for keyword in keywords):
                        if '@mentioned' in condition_text.lower() and '@mentioned' in message_content.lower():
                            continue  # Skip this rule if @mentioned is mentioned
                        actions.extend(rule['actions'])
                        break  # Only use first matching condition per rule
            else:
                # For non-contains conditions, direct match
                if condition_text.strip().lower() in message_content.lower():
                    # Check if @mentioned condition is present and if @mention is in the message
                    if '@mentioned' in condition_text.lower() and '@mentioned' in message_content.lower():
                        continue  # Skip this rule if @mentioned is mentioned
                    actions.extend(rule['actions'])
                    break  # Only use first matching condition per rule
    
    return actions

def evaluate_agent_rules_fixed(rules_text, message_content):
    """Fixed version of evaluate_agent_rules"""
    if not rules_text:
        return []
    
    rules = parse_agent_rules(rules_text)
    actions = []
    
    for rule in rules:
        # Check if any condition matches
        for condition in rule['conditions']:
            condition_text = condition
            
            # Handle both with and without "contains" keywords
            if "contains" in condition_text.lower():
                # Extract the text inside quotes
                import re
                # Look for quoted text in various formats
                quoted_matches = re.findall(r'"([^"]*)"|\'([^\']*)\'', condition_text)
                if quoted_matches:
                    # Test each quoted term
                    for quoted_match in quoted_matches:
                        term = quoted_match[0] or quoted_match[1]
                        if term.lower() in message_content.lower():
                            if '@mentioned' in condition_text.lower() and '@mentioned' in message_content.lower():
                                continue
                            actions.extend(rule['actions'])
                            break
                    if not actions:  # If no quoted match found, check for keywords
                        keywords = re.findall(r'\b(feature|new capability|bug|broken|error|implement|build|create|review|check|examine)\b', condition_text, re.I)
                        if any(keyword.lower() in message_content.lower() for keyword in keywords):
                            if '@mentioned' in condition_text.lower() and '@mentioned' in message_content.lower():
                                continue
                            actions.extend(rule['actions'])
                            break
                else:
                    # Check for keywords directly
                    keywords = re.findall(r'\b(feature|new capability|bug|broken|error|implement|build|create|review|check|examine)\b', condition_text, re.I)
                    if any(keyword.lower() in message_content.lower() for keyword in keywords):
                        if '@mentioned' in condition_text.lower() and '@mentioned' in message_content.lower():
                            continue
                        actions.extend(rule['actions'])
                        break
            elif condition_text.strip().lower() in message_content.lower():
                # Direct match for non-contains conditions
                if '@mentioned' in condition_text.lower() and '@mentioned' in message_content.lower():
                    continue
                actions.extend(rule['actions'])
                break
    
    return actions

def test_feature_request():
    """Test feature request matching"""
    obiwan_rules = """# Protocol: Feature Requests
IF message contains "feature" OR "new capability" AND not @mentioned:
  - Reply with clarification questions
  - Create task in Backlog with priority Medium
  - Assign to self

# Protocol: Bug Reports
IF message contains "bug" OR "broken" OR "error":
  - Create task in Todo with priority High
  - Assign to self
  - Reply "On it""""
    
    test_message = "I need a new feature for this system"
    
    print(f"Testing feature request: '{test_message}'")
    print(f"Rules: {obiwan_rules[:100]}...")
    print()
    
    # Test current implementation
    current_actions = evaluate_agent_rules_current(obiwan_rules, test_message)
    print(f"Current implementation: {len(current_actions)} actions")
    
    # Test fixed implementation
    fixed_actions = evaluate_agent_rules_fixed(obiwan_rules, test_message)
    print(f"Fixed implementation: {len(fixed_actions)} actions")
    
    if fixed_actions:
        print(f"✓ Fixed implementation correctly matched the feature request")
        print(f"Actions: {fixed_actions}")
        return True
    else:
        print(f"✗ Fixed implementation still failed to match feature request")
        return False

def test_bug_report():
    """Test bug report matching"""
    obiwan_rules = """# Protocol: Feature Requests
IF message contains "feature" OR "new capability" AND not @mentioned:
  - Reply with clarification questions
  - Create task in Backlog with priority Medium
  - Assign to self

# Protocol: Bug Reports
IF message contains "bug" OR "broken" OR "error":
  - Create task in Todo with priority High
  - Assign to self
  - Reply "On it""""
    
    test_message = "There's a bug in the system"
    
    print(f"\nTesting bug report: '{test_message}'")
    
    fixed_actions = evaluate_agent_rules_fixed(obiwan_rules, test_message)
    print(f"Fixed implementation: {len(fixed_actions)} actions")
    
    if fixed_actions:
        print(f"✓ Fixed implementation correctly matched the bug report")
        print(f"Actions: {fixed_actions}")
        return True
    else:
        print(f"✗ Fixed implementation failed to match bug report")
        return False

def test_mention_filtering():
    """Test @mention filtering"""
    obiwan_rules = """# Protocol: Feature Requests
IF message contains "feature" OR "new capability" AND not @mentioned:
  - Reply with clarification questions
  - Create task in Backlog with priority Medium
  - Assign to self

# Protocol: Bug Reports
IF message contains "bug" OR "broken" OR "error":
  - Create task in Todo with priority High
  - Assign to self
  - Reply "On it""""
    
    test_message = "I need a new feature for @obi-wan"
    
    print(f"\nTesting @mention filtering: '{test_message}'")
    
    fixed_actions = evaluate_agent_rules_fixed(obiwan_rules, test_message)
    print(f"Fixed implementation: {len(fixed_actions)} actions")
    
    if fixed_actions:
        print(f"✗ Fixed implementation incorrectly matched message with @mention")
        return False
    else:
        print(f"✓ Fixed implementation correctly ignored message with @mention")
        return True

def main():
    print("=" * 70)
    print("Focused Verification of evaluate_agent_rules Function")
    print("=" * 70)
    
    feature_test = test_feature_request()
    bug_test = test_bug_report()
    mention_test = test_mention_filtering()
    
    print("\n" + "=" * 70)
    print("SUMMARY:")
    print("=" * 70)
    
    if feature_test and bug_test and mention_test:
        print("✓ All tests PASSED")
        print()
        print("The evaluate_agent_rules function has been successfully fixed!")
        print()
        print("Key improvements:")
        print("✓ Properly handles 'IF message contains \"feature\"' conditions")
        print("✓ Correctly matches feature requests")
        print("✓ Correctly matches bug reports")
        print("✓ Properly filters messages with @mentions")
        print()
        print("The Mission Control Dashboard agent listener system")
        print("is now ready for production!")
        return True
    else:
        print("✗ Some tests FAILED")
        print(f"Feature request test: {'PASS' if feature_test else 'FAIL'}")
        print(f"Bug report test: {'PASS' if bug_test else 'FAIL'}")
        print(f"Mention filtering test: {'PASS' if mention_test else 'FAIL'}")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)