#!/bin/env python3
"""Simple test runner for PostgreSQL MCP Server."""

import subprocess
import sys

print("=== PostgreSQL MCP Server Test Runner ===")

# First, check if asyncpg is available
print("\n1. Checking asyncpg availability...")
try:
    import asyncpg
    print(f"✓ asyncpg is available, version: {asyncpg.__version__}")
except ImportError as e:
    print(f"✗ asyncpg not available: {e}")
    print("Installing asyncpg...")
    # Try to install asyncpg
    result = subprocess.run([
        sys.executable, "-m", "pip", "install", "asyncpg>=0.29"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✓ asyncpg installed successfully")
        import asyncpg
        print(f"✓ asyncpg version: {asyncpg.__version__}")
    else:
        print(f"✗ Failed to install asyncpg: {result.stderr}")
        sys.exit(1)

# Now run the actual tests
print("\n2. Running pytest tests...")
print("Running: uv run pytest -v --tb=short")
print("=" * 50)

# Clear cache first
print("Clearing test cache...")
subprocess.run([sys.executable, "-m", "pytest", "--cache-clear"], 
               capture_output=True, text=True)

# Run pytest
result = subprocess.run([
    sys.executable, "-m", "pytest", "-v", "--tb=short", 
    "--cov=postgresql_mcp", "--cov-report=term-missing"
], capture_output=True, text=True)

print("STDOUT:")
print(result.stdout)

if result.stderr:
    print("\nSTDERR:")
    print(result.stderr)

print(f"\nReturn code: {result.returncode}")

# Check if tests passed
if result.returncode == 0:
    print("\n🎉 ALL TESTS PASSED!")
    print("The PostgreSQL MCP Server test suite is working correctly.")
    
    # Check coverage
    if "coverage" in result.stdout.lower():
        print("\n=== Coverage Report ===")
        # Extract coverage information
        lines = result.stdout.split('\n')
        for line in lines:
            if "coverage" in line.lower() or "passed" in line.lower():
                print(line)
else:
    print("\n❌ TESTS FAILED")
    print("The test suite has issues that need to be fixed.")
    
    # Exit with the same code
    sys.exit(result.returncode)