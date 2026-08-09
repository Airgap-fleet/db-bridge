#!/usr/bin/env python3
"""Verify conftest.py fix and run tests."""

import subprocess
import sys

print("=== Verifying conftest.py fix ===")

# Check the conftest.py file
with open("tests/conftest.py", "r") as f:
    content = f.read()

print(f"File size: {len(content)} bytes")

# Check for placeholder
if "postgres:***@localhost:5432/postgres" in content:
    print("✗ ERROR: Placeholder password still exists!")
    # Find and show the line
    for i, line in enumerate(content.split('\n')):
        if "postgres:***@localhost:5432/postgres" in line:
            print(f"Line {i+1}: {repr(line)}")
    sys.exit(1)
elif "postgres:postgres@localhost:5432/postgres" in content:
    print("✓ SUCCESS: Correct password is in conftest.py!")
    
    # Show critical lines
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if "postgres:" in line:
            print(f"Line {i+1}: {repr(line)}")
else:
    print("? Cannot find password pattern in conftest.py")

print("\n=== Importing conftest to check TEST_DSN ===")
sys.path.insert(0, ".")

try:
    import tests.conftest
    from tests.conftest import TEST_DSN
    print(f"✓ Successfully imported TEST_DSN: {TEST_DSN}")
    
    if "postgres:***@localhost:5432/postgres" in str(TEST_DSN):
        print("✗ ERROR: Placeholder password in TEST_DSN!")
        sys.exit(1)
    elif "postgres:postgres@localhost:5432/postgres" in str(TEST_DSN):
        print("✓ SUCCESS: Correct password in TEST_DSN!")
    else:
        print("? Password not found in TEST_DSN")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"✗ Other error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n=== Running pytest ===")

# Run pytest
try:
    # Clear cache first
    subprocess.run([sys.executable, "-m", "pytest", "--version"], check=True)
    
    # Run the actual tests
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-v", "--tb=short", "--cov=postgresql_mcp", "--cov-report=term-missing"],
        capture_output=True,
        text=True
    )
    
    print("STDOUT:")
    print(result.stdout)
    
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    print(f"\nReturn code: {result.returncode}")
    
    # Check if all tests passed
    if result.returncode == 0:
        print("✓ ALL TESTS PASSED!")
        
        # Check coverage
        if "coverage" in result.stdout.lower():
            print("\n=== Coverage Report ===")
            # Extract coverage lines
            for line in result.stdout.split('\n'):
                if 'coverage' in line.lower() and ('%' in line or 'passed' in line):
                    print(line)
    else:
        print("✗ TESTS FAILED")
        sys.exit(result.returncode)
        
except Exception as e:
    print(f"✗ Error running tests: {e}")
    sys.exit(1)

print("\n=== Task completed successfully ===")