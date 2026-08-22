#!/usr/bin/env python3
"""
Fix the evaluate_agent_rules function to properly handle message condition evaluation.
"""

import re

def fix_evaluate_agent_rules():
    """Fix the evaluate_agent_rules function in server.py"""
    
    # Read the current server.py file
    with open('server.py', 'r') as f:
        content = f.read()
    
    # Define the improved evaluate_agent_rules function
    improved_function = '''def evaluate_agent_rules(rules_text, message_content):
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
    
    return actions'''
    
    # Find the current evaluate_agent_rules function and replace it
    lines = content.split('\n')
    
    # Find the start of the evaluate_agent_rules function
    start_line = None
    for i, line in enumerate(lines):
        if line.strip().startswith('def evaluate_agent_rules('):
            start_line = i
            break
    
    if start_line is not None:
        # Find the end of the function (look for the next def or end of file)
        end_line = start_line + 1
        while end_line < len(lines):
            if lines[end_line].strip().startswith('def ') and end_line > start_line:
                break
            if lines[end_line].strip().startswith('class ') and end_line > start_line:
                break
            end_line += 1
        
        # Replace the function
        new_lines = lines[:start_line] + [improved_function] + lines[end_line:]
        new_content = '\n'.join(new_lines)
        
        # Write the updated content
        with open('server.py', 'w') as f:
            f.write(new_content)
        
        print("✓ Fixed evaluate_agent_rules function in server.py")
        return True
    else:
        print("✗ Could not find evaluate_agent_rules function in server.py")
        return False

if __name__ == "__main__":
    # Make the fix
    if fix_evaluate_agent_rules():
        print("\n✓ Successfully fixed the agent rule evaluation!")
        print("The function now properly parses and evaluates message conditions.")
        print("\nFeatures:")
        print("- Properly handles 'IF message contains \"feature\"' conditions")
        print("- Supports both quoted and keyword matching")
        print("- Maintains @mentioned filtering")
        print("- Maintains backward compatibility")
    else:
        print("\n✗ Failed to fix the evaluate_agent_rules function.")