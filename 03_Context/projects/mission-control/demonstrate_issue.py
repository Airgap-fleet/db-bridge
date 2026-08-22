#!/usr/bin/env python3
"""
Simple direct test of the evaluate_agent_rules function from server.py
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
    """Current evaluate_agent_rules function from server.py"""
    if not rules_text:
        return []
    
    rules = parse_agent_rules(rules_text)
    actions = []
    
    for rule in rules:
        # Check if any condition matches
        for condition in rule['conditions']:
            # Normalize condition for matching
            condition_text = condition
            
            # Check if condition contains keywords
            if "contains" in condition_text.lower():
                # Extract the text inside quotes or between keywords
                # Find quoted text
                quoted_matches = re.findall(r'"([^"]*)"|\\\'([^\\\']*)\\\'', condition_text)
                if quoted_matches:
                    # Test each quoted term
                    for quoted_match in quoted_matches:
                        term = quoted_match[0] or quoted_match[1]
                        if term.lower() in message_content.lower():
                            # Check if @mentioned condition is present and if @mention is in the message
                            if '@mentioned' in condition_text.lower() and '@mentioned' in message_content.lower():
                                continue
                            actions.extend(rule['actions'])
                            break
                    else:
                        continue
                    break
                else:
                    # No quotes found, check for keywords directly
                    keywords = re.findall(r'\\b(feature|new capability|bug|broken|error|implement|build|create|review|check|examine)\\b', condition_text, re.I)
                    if any(keyword.lower() in message_content.lower() for keyword in keywords):
                        if '@mentioned' in condition_text.lower() and '@mentioned' in message_content.lower():
                            continue
                        actions.extend(rule['actions'])
                        break
            else:
                # For non-contains conditions, direct match
                if condition_text.strip().lower() in message_content.lower():
                    # Check if @mentioned condition is present and if @mention is in the message
                    if '@mentioned' in condition_text.lower() and '@mentioned' in message_content.lower():
                        continue
                    actions.extend(rule['actions'])
                    break
    
    return actions

def test_issue():
    """Test to demonstrate the issue"""
    
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
    print("DEMONSTRATING THE ISSUE")
    print("=" * 70)
    
    feature_msg = "I need a new feature for this system"
    
    print(f"Testing message: '{feature_msg}'")
    print(f"Looking for keywords: 'feature', 'new capability'")
    print()
    
    # Check what the regex pattern actually matches
    condition = 'message contains "feature" OR "new capability" AND not @mentioned:'
    quoted_matches = re.findall(r'"([^"]*)"|\\\'([^\\\']*)\\\'', condition)
    print(f"Quoted matches found: {quoted_matches}")
    
    # Test the actual pattern from server.py
    pattern = r'\\b(feature|new capability|bug|broken|error|implement|build|create|review|check|examine)\\b'
    print(f"Current pattern: {pattern}")
    
    keywords = re.findall(pattern, condition, re.I)
    print(f"Keywords matched by pattern: {keywords}")
    
    # The issue is that the pattern has double escaping
    # It should be: r'\\b(feature|new capability|bug|broken|error|implement|build|create|review|check|examine)\\b'
    # But in the file it's stored as double escaped: '\\\\b'
    
    print()
    print("The pattern has double escaping, which means it's looking for")
    print("'\\\\b' in the text, not normal word boundaries.")
    print("This is why feature requests are not being matched!")
    
    return True

if __name__ == "__main__":
    test_issue()
    print("\n" + "=" * 70)
    print("SOLUTION: Fix the regex pattern in server.py")
    print("=" * 70)
    print("The pattern should be: r'\\b(feature|new capability|bug|broken|error|implement|build|create|review|check|examine)\\b'")
    print("This is stored in the file as a single-escaped raw string literal.")