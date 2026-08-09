import os

print("=== Fixing conftest.py ===")

# Read the file
with open("tests/conftest.py", "r") as f:
    content = f.read()

print(f"File size: {len(content)} bytes")

# Check for placeholder
if "postgres:***@localhost:5432/postgres" in content:
    print("✓ Found placeholder password")
    print("🔧 Fixing...")
    
    # Replace the placeholder with correct password
    content = content.replace(
        "postgresql://postgres:***@localhost:5432/postgres",
        "postgresql://postgres:postgres@localhost:5432/postgres"
    )
    
    print("✓ Fixed password")
else:
    print("✗ Placeholder not found")
    # Check if correct password is there
    if "postgres:postgres@localhost:5432/postgres" in content:
        print("✓ Correct password already in file")
    else:
        print("? Cannot find password pattern")

# Write back
with open("tests/conftest.py", "w") as f:
    f.write(content)

print("✓ File written")

# Verify
with open("tests/conftest.py", "r") as f:
    verify = f.read()

print("\n=== Verification ===")
print(f"Placeholder count: {verify.count('postgres:***@localhost:5432/postgres')}")
print(f"Correct password count: {verify.count('postgres:postgres@localhost:5432/postgres')}")

if "postgres:***@localhost:5432/postgres" in verify:
    print("✗ ERROR: Placeholder still exists!")
else:
    print("✓ Placeholder removed")
    
    if "postgres:postgres@localhost:5432/postgres" in verify:
        print("✓ Correct password added")
        
        # Show line 16
        lines = verify.split("\n")
        if len(lines) > 15:
            print(f"\nLine 16: {lines[15]}")
            if "postgres:postgres@localhost:5432/postgres" in lines[15]:
                print("✓ Line 16 has correct password")
            else:
                print("✗ Line 16 does not have correct password")
    else:
        print("✗ Correct password not found")

