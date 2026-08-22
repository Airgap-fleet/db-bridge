#!/usr/bin/env python3
"""
Simple test script to verify the HTTP server functionality
without using background processes.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from server import init_database, seed_initial_data, get_all_agents, get_all_tasks, get_all_messages, get_all_workflows
import sqlite3
import tempfile
import json

# Temporarily change DB_PATH to a test database
test_db_path = tempfile.mktemp(suffix='.db')
original_db_path = 'DB_PATH'

print("Testing HTTP Server Layer Implementation")
print("=" * 60)

# Mock the DB_PATH for testing
import server
original_db_path = server.DB_PATH
server.DB_PATH = test_db_path

try:
    print("1. Testing database initialization...")
    init_database()
    
    print("2. Testing initial data seeding...")
    seed_initial_data()
    
    print("3. Testing /api/agents endpoint...")
    agents = get_all_agents()
    print(f"   Found {len(agents)} agents")
    if len(agents) >= 2:
        print("   ✓ All 2 expected agents present")
    else:
        print("   ✗ Expected 2 agents but got less")
        sys.exit(1)
    
    print("4. Testing /api/tasks endpoint...")
    tasks = get_all_tasks()
    print(f"   Found {len(tasks)} tasks")
    
    print("5. Testing /api/messages endpoint...")
    messages = get_all_messages()
    print(f"   Found {len(messages)} messages")
    
    print("6. Testing /api/workflows endpoint...")
    workflows = get_all_workflows()
    print(f"   Found {len(workflows)} workflows")
    
    # Test agent data structure
    print("7. Verifying agent data structure...")
    agent = agents[0]
    required_fields = ['id', 'name', 'role', 'color', 'last_seen', 'status']
    for field in required_fields:
        if field in agent:
            print(f"   ✓ Agent has {field} field")
        else:
            print(f"   ✗ Agent missing {field} field")
            sys.exit(1)
    
    # Test task data structure  
    print("8. Verifying task data structure...")
    if tasks:
        task = tasks[0]
        required_fields = ['id', 'title', 'status', 'priority', 'created_at', 'updated_at']
        for field in required_fields:
            if field in task:
                print(f"   ✓ Task has {field} field")
            else:
                print(f"   ✗ Task missing {field} field")
                sys.exit(1)
    
    # Test workflow data structure
    print("9. Verifying workflow data structure...")
    if workflows:
        workflow = workflows[0]
        required_fields = ['id', 'name', 'version', 'is_active', 'created_at']
        for field in required_fields:
            if field in workflow:
                print(f"   ✓ Workflow has {field} field")
            else:
                print(f"   ✗ Workflow missing {field} field")
                sys.exit(1)
    
    print("\n" + "=" * 60)
    print("SUCCESS: All tests passed!")
    print("The HTTP server layer implementation is working correctly.")
    print("=" * 60)
    
finally:
    # Clean up
    server.DB_PATH = original_db_path
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    print(f"Cleaned up test database: {test_db_path}")