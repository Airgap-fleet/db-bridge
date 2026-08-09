#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

print("=== Testing simple import ===")
try:
    # First check if asyncpg is available
    import asyncpg
    print(f"✓ asyncpg imported successfully, version: {asyncpg.__version__}")
    
    # Then try to import conftest
    import tests.conftest
    print("✓ tests.conftest imported successfully")
    
    # Check TEST_DSN
    from tests.conftest import TEST_DSN
    print(f"✓ TEST_DSN = {TEST_DSN}")
    
    # Check if password is correct
    if "postgres:***@localhost:5432/postgres" in str(TEST_DSN):
        print("✗ ERROR: Placeholder password in TEST_DSN!")
        exit(1)
    elif "postgres:postgres@localhost:5432/postgres" in str(TEST_DSN):
        print("✓ SUCCESS: Correct password in TEST_DSN!")
    else:
        print("? Password not found in TEST_DSN")
        
except ImportError as e:
    print(f"✗ Import error: {e}")
    exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n🎉 All imports successful!")
