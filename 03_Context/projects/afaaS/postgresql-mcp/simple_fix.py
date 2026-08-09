#!/usr/bin/env python3
import re

print("=== Simple password fix for conftest.py ===")

# Read the current file
with open("tests/conftest.py", "r") as f:
    content = f.read()

print(f"File size: {len(content)} bytes")

# Check current state
if "postgres:***@localhost:5432/postgres" in content:
    print("✓ Found placeholder password")
    placeholder_count = content.count("postgres:***@localhost:5432/postgres")
    print(f"  Placeholder count: {placeholder_count}")
else:
    print("✗ Placeholder password not found")
    placeholder_count = 0

if "postgres:postgres@localhost:5432/postgres" in content:
    print("✓ Correct password already in file")
    correct_count = content.count("postgres:postgres@localhost:5432/postgres")
    print(f"  Correct count: {correct_count}")
else:
    print("✗ Correct password not found")
    correct_count = 0

# Fix the password - simple regex replacement
if placeholder_count > 0:
    print("\n🔧 Replacing placeholder with correct password...")
    
    # Replace all occurrences
    old_content = content
    content = content.replace("postgresql://postgres:***@localhost:5432/postgres", "postgresql://postgres:postgres@localhost:5432/postgres")
    
    if content != old_content:
        print("✓ Password replaced")
        
        # Write back
        with open("tests/conftest.py", "w") as f:
            f.write(content)
        
        print("✓ File written")
        
        # Verify
        with open("tests/conftest.py", "r") as f:
            verify = f.read()
        
        verify_placeholder = verify.count("postgres:***@localhost:5432/postgres")
        verify_correct = verify.count("postgres:postgres@localhost:5432/postgres")
        
        print(f"\n=== Verification ===")
        print(f"Placeholder count after fix: {verify_placeholder}")
        print(f"Correct count after fix: {verify_correct}")
        
        if verify_placeholder == 0 and verify_correct > 0:
            print("🎉 SUCCESS: Password is fixed!")
            
            # Show the critical line (line 16)
            lines = verify.split('\n')
            if len(lines) > 15:
                print(f"\nLine 16: {repr(lines[15])}")
                if "postgres:postgres@localhost:5432/postgres" in lines[15]:
                    print("✓ Line 16 has correct password")
                else:
                    print("✗ Line 16 does not have correct password")
        else:
            print("❌ FAILED: Password not fixed")
    else:
        print("⚠ Content didn't change after replacement")
else:
    print("\n⚠ No placeholder to replace")

print("\n=== Final verification ===")
with open("tests/conftest.py", "r") as f:
    final_content = f.read()

if "postgres:***@localhost:5432/postgres" in final_content:
    print("✗ Placeholder password still exists!")
elif "postgres:postgres@localhost:5432/postgres" in final_content:
    print("✓ Correct password is in place!")
else:
    print("? Cannot find password pattern")
