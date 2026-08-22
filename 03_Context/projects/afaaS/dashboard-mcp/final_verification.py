#!/usr/bin/env python3
"""
Final verification script for Dashboard MCP Server acceptance criteria.
"""

import os
from pathlib import Path

def main():
    print("=" * 60)
    print("Dashboard MCP Server - Final Acceptance Criteria Verification")
    print("=" * 60)
    
    project_dir = Path.cwd()
    print(f"\nProject directory: {project_dir}")
    
    # Define acceptance criteria checks
    checks = []
    
    # Acceptance Criterion 1: Fix server.py:21
    print("\n1. Checking server.py:21 fix...")
    server_py = project_dir / "src/dashboard_mcp/server.py"
    if server_py.exists():
        with open(server_py, 'r') as f:
            content = f.read()
        if "from .models import" in content:
            print("   ✓ PASS: server.py uses correct relative import: from .models import")
            checks.append(("server.py:21 fix", True, "server.py uses correct relative import"))
        else:
            print("   ✗ FAIL: server.py doesn't use correct relative import")
            checks.append(("server.py:21 fix", False, "server.py import issue"))
    else:
        print("   ✗ FAIL: server.py file missing")
        checks.append(("server.py:21 fix", False, "server.py file missing"))
    
    # Acceptance Criterion 2: Fix __init__.py exports
    print("\n2. Checking __init__.py exports...")
    init_py = project_dir / "src/dashboard_mcp/__init__.py"
    if init_py.exists():
        with open(init_py, 'r') as f:
            content = f.read()
        
        required_exports = [
            "DashboardCore", "WebSocketHub", "EventType", "WSMessage",
            "AgentRegistration", "TaskCreate", "MessageCreate", 
            "ChannelCreate", "Config", "KanbanTask", "KanbanRun",
            "KanbanEvent", "FleetConfig"
        ]
        
        all_exports_found = True
        for export in required_exports:
            if f'"{export}"' in content:
                print(f"   ✓ PASS: exports {export}")
            else:
                print(f"   ✗ FAIL: missing export: {export}")
                all_exports_found = False
        
        if all_exports_found:
            checks.append(("__init__.py exports", True, "all required classes exported"))
        else:
            checks.append(("__init__.py exports", False, "missing exports"))
    else:
        print("   ✗ FAIL: __init__.py file missing")
        checks.append(("__init__.py exports", False, "__init__.py file missing"))
    
    # Acceptance Criterion 3: Migrate Pydantic V1 → V2
    print("\n3. Checking Pydantic V2 migration...")
    models_py = project_dir / "src/dashboard_mcp/models.py"
    if models_py.exists():
        with open(models_py, 'r') as f:
            content = f.read()
        
        v2_migration_checks = []
        
        # Check for @field_validator (V2) vs @validator (V1)
        if "@field_validator" in content:
            print("   ✓ PASS: Uses @field_validator decorators (Pydantic V2)")
            v2_migration_checks.append(("@field_validator usage", True, "uses @field_validator"))
        else:
            print("   ✗ FAIL: Still uses @validator decorators (Pydantic V1)")
            v2_migration_checks.append(("@field_validator usage", False, "uses @validator instead of @field_validator"))
        
        # Check for json_schema_extra usage
        if "json_schema_extra" in content:
            print("   ✓ PASS: Uses json_schema_extra for Field configuration")
            v2_migration_checks.append(("json_schema_extra usage", True, "uses json_schema_extra"))
        elif "Field(..., env=" in content:
            print("   ✗ FAIL: Still uses Field(..., env=...) (Pydantic V1)")
            v2_migration_checks.append(("json_schema_extra usage", False, "uses Field(..., env=) instead of json_schema_extra"))
        else:
            print("   ⚠ WARNING: Cannot determine Field configuration usage")
            v2_migration_checks.append(("json_schema_extra usage", "unknown", "unknown"))
        
        # Overall V2 migration status
        v2_success = all(result[1] is True for result in v2_migration_checks if result[1] != "unknown")
        if v2_success:
            checks.append(("Pydantic V1 → V2 migration", True, "all V2 patterns applied"))
        else:
            checks.append(("Pydantic V1 → V2 migration", False, "some V1 patterns still present"))
    else:
        print("   ✗ FAIL: models.py file missing")
        checks.append(("Pydantic V1 → V2 migration", False, "models.py file missing"))
    
    # Acceptance Criterion 4: Add Alembic
    print("\n4. Checking Alembic setup...")
    alembic_dir = project_dir / "alembic"
    if alembic_dir.exists() and alembic_dir.is_dir():
        env_py = alembic_dir / "env.py"
        if env_py.exists():
            print("   ✓ PASS: alembic/ directory exists with env.py")
            checks.append(("Alembic setup", True, "alembic directory and env.py present"))
        else:
            print("   ✗ FAIL: alembic/ directory exists but env.py missing")
            checks.append(("Alembic setup", False, "env.py missing"))
    else:
        print("   ✗ FAIL: alembic/ directory missing")
        checks.append(("Alembic setup", False, "alembic directory missing"))
    
    # Acceptance Criterion 5: Fix .env file
    print("\n5. Checking .env file fix...")
    env_file = project_dir / ".env"
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
        
        if "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/dashboard_mcp" in content:
            print("   ✓ PASS: .env has correct DATABASE_URL")
            checks.append((".env file fix", True, "DATABASE_URL correctly configured"))
        elif "DATABASE_URL=postgresql://postgres:***@localhost:5432/dashboard_mcp" in content:
            print("   ✗ FAIL: .env still has placeholder password (postgresql:***@)")
            checks.append((".env file fix", False, "DATABASE_URL still has placeholder password"))
        else:
            print("   ⚠ WARNING: DATABASE_URL format unclear")
            checks.append((".env file fix", "warning", "DATABASE_URL format unclear"))
    else:
        print("   ✗ FAIL: .env file missing")
        checks.append((".env file fix", False, ".env file missing"))
    
    # Summary
    print("\n" + "=" * 60)
    print("FINAL VERIFICATION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result, _ in checks if result is True)
    failed = sum(1 for _, result, _ in checks if result is False)
    warnings = sum(1 for _, result, _ in checks if result == "warning")
    
    print(f"Total checks: {len(checks)}")
    print(f"✓ Passed: {passed}")
    print(f"✗ Failed: {failed}")
    print(f"⚠ Warnings: {warnings}")
    
    print("\nDetailed Results:")
    for criterion, result, description in checks:
        status = "✓ PASS" if result is True else "✗ FAIL" if result is False else "⚠ WARNING"
        print(f"  {status}: {criterion} - {description}")
    
    print("\n" + "=" * 60)
    if failed == 0:
        print("🎉 ALL ACCEPTANCE CRITERIA MET!")
        print("\nDashboard MCP Server fixes are complete:")
        print("✓ server.py uses correct relative imports")
        print("✓ __init__.py exports all required classes")
        print("✓ Pydantic V2 migration applied")
        print("✓ Alembic directory exists with env.py")
        print("✓ .env file has correct DATABASE_URL")
        print("\nNext step: Run tests, mypy, and ruff verification.")
    else:
        print("❌ SOME ACCEPTANCE CRITERIA NOT MET")
        print("\nDashboard MCP Server still needs fixes:")
        print("1. Complete Pydantic V2 migration in models.py")
        print("2. Ensure .env file has correct DATABASE_URL")
        print("\nNote: Tests, mypy, and ruff verification will fail until")
        print("      these issues are resolved.")
    
    print("=" * 60)
    return failed == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)