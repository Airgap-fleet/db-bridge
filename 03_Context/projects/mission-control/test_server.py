#!/usr/bin/env python3
"""
Simple test script to verify the HTTP server functionality
"""

import subprocess
import time
import requests
import sys
import os

# Kill any existing python processes on port 8420
subprocess.run(['pkill', '-f', 'server.py'], stderr=subprocess.DEVNULL)

print("Starting server...")

# Start the server in background
proc = subprocess.Popen(['python3', 'server.py'], 
                       stdout=subprocess.PIPE, 
                       stderr=subprocess.PIPE)

# Give server time to start
time.sleep(3)

print("Testing server endpoints...")

# Test API endpoints
test_passed = True

# Test /api/agents endpoint
try:
    response = requests.get('http://localhost:8420/api/agents')
    if response.status_code == 200:
        agents = response.json()
        print(f"✓ /api/agents endpoint returned {len(agents)} agents")
        if len(agents) == 4:
            print("✓ All 4 expected agents present")
        else:
            print(f"✗ Expected 4 agents but got {len(agents)}")
            test_passed = False
    else:
        print(f"✗ /api/agents endpoint returned status {response.status_code}")
        test_passed = False
except Exception as e:
    print(f"✗ Error testing /api/agents: {e}")
    test_passed = False

# Test /api/tasks endpoint
try:
    response = requests.get('http://localhost:8420/api/tasks')
    if response.status_code == 200:
        tasks = response.json()
        print(f"✓ /api/tasks endpoint returned {len(tasks)} tasks")
    else:
        print(f"✗ /api/tasks endpoint returned status {response.status_code}")
        test_passed = False
except Exception as e:
    print(f"✗ Error testing /api/tasks: {e}")
    test_passed = False

# Test /api/messages endpoint
try:
    response = requests.get('http://localhost:8420/api/messages')
    if response.status_code == 200:
        messages = response.json()
        print(f"✓ /api/messages endpoint returned {len(messages)} messages")
    else:
        print(f"✗ /api/messages endpoint returned status {response.status_code}")
        test_passed = False
except Exception as e:
    print(f"✗ Error testing /api/messages: {e}")
    test_passed = False

# Test /api/workflows endpoint
try:
    response = requests.get('http://localhost:8420/api/workflows')
    if response.status_code == 200:
        workflows = response.json()
        print(f"✓ /api/workflows endpoint returned {len(workflows)} workflows")
    else:
        print(f"✗ /api/workflows endpoint returned status {response.status_code}")
        test_passed = False
except Exception as e:
    print(f"✗ Error testing /api/workflows: {e}")
    test_passed = False

# Test POST /api/messages endpoint
post_data = {
    "agent_id": "scotty",
    "content": "Test message from HTTP server"
}
try:
    response = requests.post('http://localhost:8420/api/messages', 
                            json=post_data,
                            headers={'Content-Type': 'application/json'})
    if response.status_code == 200:
        result = response.json()
        print(f"✓ POST /api/messages succeeded: {result}")
    else:
        print(f"✗ POST /api/messages returned status {response.status_code}")
        test_passed = False
except Exception as e:
    print(f"✗ Error testing POST /api/messages: {e}")
    test_passed = False

# Test SSE endpoint
try:
    # Create a simple SSE client
    import threading
    import queue
    
    sse_events = []
    def read_sse():
        try:
            with requests.get('http://localhost:8420/events', stream=True) as r:
                for line in r.iter_content(decode_unicode=True):
                    if line:
                        sse_events.append(line)
                        if len(sse_events) > 5:  # Limit to 5 events
                            break
        except Exception:
            pass
    
    sse_thread = threading.Thread(target=read_sse)
    sse_thread.daemon = True
    sse_thread.start()
    
    time.sleep(3)
    
    if len(sse_events) > 0:
        print(f"✓ SSE endpoint returned {len(sse_events)} events")
        test_passed = True
    else:
        print("✗ SSE endpoint returned no events")
        test_passed = False
        
except Exception as e:
    print(f"✗ Error testing SSE endpoint: {e}")
    test_passed = False

# Kill server
proc.terminate()
proc.wait(timeout=5)

print("\n" + "="*60)
if test_passed:
    print("SUCCESS: All tests passed!")
    print("The HTTP server is working correctly.")
else:
    print("FAILURE: Some tests failed.")
    print("The HTTP server needs further debugging.")
print("="*60)

sys.exit(0 if test_passed else 1)