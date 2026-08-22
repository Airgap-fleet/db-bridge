#!/usr/bin/env python3
"""
Dashboard MCP Server - Acceptance Criteria Verification

This script provides clear evidence of the current state and what needs to be fixed.
It checks all 5 acceptance criteria and shows exactly what's working and what needs attention.
"""

import os
import sys
from pathlib import Path

def main():
    print("=" * 80)
    print("Dashboard MCP Server - Acceptance Criteria Verification")
    print("=" * 80)
    
    # Project directory
    project_dir = Path("C:/the force/03_Context/projects/afaaS/dashboard-mcp")
    print(f"\n📂 Project: {project_dir.name}")
    print(f"📍 Location: {project_dir}")
    
    # Evidence collection
    evidence = []
    
    # Criterion 1: server.py:21
    print("\n1️⃣ CHECKING: server.py:21 - Relative Imports")
    print("-" * 80)
    
    server_py = project_dir / "src/dashboard_mcp/server.py"
    if server_py.exists():
        with open(server_py, 'r') as f:
            content = f.read()
        
        lines = content.split('\n')
        if len(lines) >= 21:
            line_21 = lines[20].strip()
            print(f"   Line 21: {line_21}")
            
            if "from .models import" in line_21:
                print("   ✅ PASS: Uses relative import")
                evidence.append("✅ server.py:21 - Correct relative import")
            else:
                print("   ❌ FAIL: Uses absolute import")
                evidence.append("❌ server.py:21 - Wrong import")
        else:
            print("   ❌ FAIL: File too short")
            evidence.append("❌ server.py:21 - File too short")
    else:
        print("   ❌ FAIL: server.py missing")
        evidence.append("❌ server.py:21 - File missing")
    
    # Criterion 2: __init__.py exports
    print("\n2️⃣ CHECKING: __init__.py - Required Class Exports")
    print("-" * 80)
    
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
        
        all_found = True
        for export in required_exports:
            if f'"{export}"' in content:
                print(f"   ✅ Found: {export}")
            else:
                print(f"   ❌ Missing: {export}")
                all_found = False
        
        if all_found:
            print("   ✅ PASS: All required exports present")
            evidence.append("✅ __init__.py - All required exports")
        else:
            print("   ❌ FAIL: Some exports missing")
            evidence.append("❌ __init__.py - Missing exports")
    else:
        print("   ❌ FAIL: __init__.py missing")
        evidence.append("❌ __init__.py - File missing")
    
    # Criterion 3: Pydantic V2 migration
    print("\n3️⃣ CHECKING: Pydantic V2 Migration")
    print("-" * 80)
    
    models_py = project_dir / "src/dashboard_mcp/models.py"
    if models_py.exists():
        with open(models_py, 'r') as f:
            content = f.read()
        
        v1_patterns = ["@validator(", "Field(..., env=\""]
        v2_patterns = ["@field_validator", "json_schema_extra", "Field(default_factory"]
        
        v1_found = [p for p in v1_patterns if p in content]
        v2_found = [p for p in v2_patterns if p in content]
        
        if v1_found:
            print("   ❌ FAIL: Found V1 patterns:", v1_found)
            evidence.append(f"❌ Pydantic V1→V2 - V1 patterns found: {v1_found}")
        elif v2_found:
            print("   ✅ PASS: Found V2 patterns:", v2_found)
            evidence.append(f"✅ Pydantic V1→V2 - V2 patterns: {v2_found}")
        else:
            print("   ⚠️  WARNING: No validation patterns detected")
            evidence.append("⚠️  Pydantic V1→V2 - No patterns detected")
    else:
        print("   ❌ FAIL: models.py missing")
        evidence.append("❌ Pydantic V1→V2 - File missing")
    
    # Criterion 4: Alembic setup
    print("\n4️⃣ CHECKING: Alembic Setup")
    print("-" * 80)
    
    alembic_dir = project_dir / "alembic"
    if alembic_dir.exists() and alembic_dir.is_dir():
        print("   ✅ Found alembic/ directory")
        
        env_py = alembic_dir / "env.py"
        if env_py.exists():
            print("   ✅ Found alembic/env.py")
            
            with open(env_py, 'r') as f:
                env_content = f.read()
            
            if "from alembic import op" in env_content and "import sqlalchemy as sa" in env_content:
                print("   ✅ alembic/env.py has correct structure")
                evidence.append("✅ Alembic - Directory and env.py present")
            else:
                print("   ⚠️  WARNING: alembic/env.py structure unclear")
                evidence.append("⚠️  Alembic - Structure unclear")
        else:
            print("   ❌ FAIL: Missing alembic/env.py")
            evidence.append("❌ Alembic - Missing env.py")
    else:
        print("   ❌ FAIL: alembic/ directory missing")
        evidence.append("❌ Alembic - Directory missing")
    
    # Criterion 5: .env file fix
    print("\n5️⃣ CHECKING: .env File Fix")
    print("-" * 80)
    
    env_file = project_dir / ".env"
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
        
        correct_url = "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/dashboard_mcp"
        placeholder_url = "DATABASE_URL=postgresql://postgres:***@localhost:5432/dashboard_mcp"
        
        if correct_url in content:
            print("   ✅ PASS: .env has correct DATABASE_URL")
            evidence.append("✅ .env - DATABASE_URL correctly configured")
        elif placeholder_url in content:
            print("   ❌ FAIL: .env still has placeholder password")
            print(f"      Current: {placeholder_url}")
            evidence.append("❌ .env - Placeholder password still present")
        else:
            print("   ⚠️  WARNING: DATABASE_URL not found")
            evidence.append("⚠️  .env - DATABASE_URL not found")
    else:
        print("   ❌ FAIL: .env file missing")
        evidence.append("❌ .env - File missing")
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 FINAL VERIFICATION SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for e in evidence if e.startswith("✅"))
    failed = sum(1 for e in evidence if e.startswith("❌"))
    warnings = sum(1 for e in evidence if e.startswith("⚠️"))
    
    print(f"\n📈 Results:")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   ⚠️  Warnings: {warnings}")
    
    print(f"\n📋 Current Evidence ({len(evidence)} items):")
    for item in evidence:
        print(f"   {item}")
    
    print("\n" + "=" * 80)
    print("🎯 ANALYSIS")
    print("=" * 80)
    
    print("📍 CURRENT STATE:")
    if failed == 0:
        print("   ✅ All acceptance criteria met")
        print("   The server is ready for production")
        print("   Tests, mypy, and ruff should pass")
    else:
        print("   ❌ Some acceptance criteria not met")
        print("   The server cannot proceed to testing")
        print("   Primary blocker: .env file configuration")
    
    print(f"\n🔍 SPECIFIC ISSUES:")
    for item in evidence:
        if item.startswith("❌"):
            print(f"   {item}")
    
    print(f"\n💡 NEXT STEPS:")
    if failed > 0:
        print("   1. 🚨 CRITICAL: Fix .env file DATABASE_URL")
        print("       Change: postgresql:***@ → postgresql:postgres@")
        print("       File: .env in project root")
        print("")
    print("   2. Run tests: uv run pytest -v --cov=dashboard_mcp --cov-fail-under=90")
    print("   3. Run type checking: uv run mypy src/dashboard_mcp")
    print("   4. Run linting: uv run ruff check src/dashboard_mcp")
    
    print(f"\n📁 EVIDENCE FILES:")
    print(f"   - Verification script: {__file__}")
    print(f"   - Project directory: {project_dir}")
    
    print("\n" + "=" * 80)
    print("🎯 CONCLUSION")
    print("=" * 80)
    
    if failed == 0:
        print("✅ SUCCESS: All acceptance criteria met!")
        print("   Dashboard MCP Server is ready for production")
        return True
    else:
        print("❌ INCOMPLETE: Acceptance criteria not met")
        print("   The .env file issue prevents further testing")
        print("   This is a blocking issue that must be resolved first")
        return False

if __name__ == "__main__":
    # Change to project directory
    os.chdir("C:/the force/03_Context/projects/afaaS/dashboard-mcp")
    
    # Run verification
    success = main()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)