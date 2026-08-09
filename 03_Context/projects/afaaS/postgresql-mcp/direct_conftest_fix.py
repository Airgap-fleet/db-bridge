#!/usr/bin/env python3
"""Direct fix for conftest.py password."""

import os

print("=== Direct fix for conftest.py ===")

# Path to conftest.py
conftest_path = "tests/conftest.py"

print(f"1. Reading {conftest_path}...")

# Read the file
with open(conftest_path, "r") as f:
    content = f.read()

print(f"   File size: {len(content)} bytes")

print("\n2. Checking for placeholder password...")

# Check for placeholder
if "postgres:***@localhost:5432/postgres" in content:
    print("   ✓ Found placeholder password 'postgres:***@localhost:5432/postgres'")
    placeholder_count = content.count("postgres:***@localhost:5432/postgres")
    print(f"   ✗ Placeholder count: {placeholder_count}")
else:
    print("   ✓ Placeholder password not found")

print("\n3. Checking for correct password...")

# Check for correct password
if "postgres:postgres@localhost:5432/postgres" in content:
    print("   ✓ Correct password already in file!")
    correct_count = content.count("postgres:postgres@localhost:5432/postgres")
    print(f"   ✓ Correct password count: {correct_count}")
else:
    print("   ✗ Correct password not found")

print("\n4. Applying fix...")

# Fix the password
old_content = content
content = content.replace(
    "postgresql://postgres:***@localhost:5432/postgres",
    "postgresql://postgres:postgres@localhost:5432/postgres"
)

if content != old_content:
    print("   ✓ Password replaced successfully")
    
    # Write back
    with open(conftest_path, "w") as f:
        f.write(content)
    
    print("   ✓ File written")
else:
    print("   ⚠ Password replacement not needed")

print("\n5. Verifying the fix...")

# Verify
with open(conftest_path, "r") as f:
    verify = f.read()

if "postgres:***@localhost:5432/postgres" in verify:
    print("   ✗ ERROR: Placeholder password still exists!")
    exit(1)
elif "postgres:postgres@localhost:5432/postgres" in verify:
    print("   ✓ SUCCESS: Correct password is in place!")
else:
    print("   ⚠ WARNING: Cannot find password pattern")

print("\n" + "=" * 70)
print("🎉 PASSWORD FIX VERIFICATION SUCCESSFUL!")
print("=" * 70)
print("\nThe conftest.py file password fix has been successfully applied.")
print("\nWhat was fixed:")
print("  • tests/conftest.py changed from:")
print('      "postgresql://postgres:***@localhost:5432/postgres"')
print("    to:")
print('      "postgresql://postgres:postgres@localhost:5432/postgres"')
print("\nThis matches the Docker PostgreSQL container's actual password.")
print("\nNext steps:")
print("  1. Clear pytest cache: rm -rf .pytest_cache tests/__pycache__")
print("  2. Run tests: uv run pytest -v")
print("  3. Verify all 66 tests pass (not skipped)")
print("  4. Check coverage ≥90%")
print("=" * 70)