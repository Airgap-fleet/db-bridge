#!/usr/bin/env python3
"""
Quick verification script for Dashboard MCP server completion.
"""

import os
from pathlib import Path

def main():
    print("=" * 80)
    print("Dashboard MCP Server - Quick Verification")
    print("=" * 80)
    
    project_dir = Path("C:/the force/03_Context/projects/afaaS/dashboard-mcp")
    
    print(f"\n📂 Project: {project_dir.name}")
    
    # Quick checks
    checks = []
    
    # 1. Check .env file
    print("\n1. Checking .env file...")
    env_file = project_dir / ".env"
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
        if "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/dashboard_mcp" in content:
            print("✅ .env file has correct DATABASE_URL")
            checks.append(("✅ .env file fix", True))
        else:
            print("❌ .env file has incorrect DATABASE_URL")
            checks.append(("❌ .env file fix", False))
    else:
        print("❌ .env file missing")
        checks.append(("❌ .env file fix", False))
    
    # 2. Check server.py import
    print("\n2. Checking server.py import...")
    server_py = project_dir / "src/dashboard_mcp/server.py"
    if server_py.exists():
        with open(server_py, 'r') as f:
            content = f.read()
        if "from src.dashboard_mcp.core import CoreLogic" in content:
            print("❌ server.py imports CoreLogic (should import DashboardCore)")
            checks.append(("❌ server.py fix", False))
        elif "from .core import DashboardCore" in content:
            print("✅ server.py uses correct import")
            checks.append(("✅ server.py fix", True))
        else:
            print("⚠️  server.py import unclear")
            checks.append(("⚠️  server.py check", "warning"))
    else:
        print("❌ server.py missing")
        checks.append(("❌ server.py fix", False))
    
    # 3. Check alembic directory
    print("\n3. Checking alembic directory...")
    alembic_dir = project_dir / "alembic"
    if alembic_dir.exists() and alembic_dir.is_dir():
        env_py = alembic_dir / "env.py"
        if env_py.exists():
            print("✅ alembic/ directory and env.py present")
            checks.append(("✅ alembic setup", True))
        else:
            print("❌ alembic/env.py missing")
            checks.append(("❌ alembic setup", False))
    else:
        print("❌ alembic/ directory missing")
        checks.append(("❌ alembic setup", False))
    
    # 4. Check .env file content
    print("\n4. Checking .env file content...")
    env_file = project_dir / ".env"
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
        
        correct_patterns = [
            "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/dashboard_mcp",
            "REDIS_URL=redis://localhost:6379",
            "DASHBOARD_MCP_PORT=8000"
        ]
        
        all_found = True
        for pattern in correct_patterns:
            if pattern in content:
                print(f"✅ Found: {pattern[:30]}...")
            else:
                print(f"❌ Missing: {pattern[:30]}...")
                all_found = False
        
        if all_found:
            print("✅ .env file has all correct configuration")
            checks.append(("✅ .env file content", True))
        else:
            print("❌ .env file missing some configuration")
            checks.append(("❌ .env file content", False))
    else:
        print("❌ .env file missing")
        checks.append(("❌ .env file content", False))
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 QUICK VERIFICATION SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in checks if result is True)
    failed = sum(1 for _, result in checks if result is False)
    warnings = sum(1 for _, result in checks if result == "warning")
    
    print(f"\n📈 Status: {passed} passed, {failed} failed, {warnings} warnings")
    
    print("\n📋 Checklist:")
    for item, result in checks:
        status = "✅" if result is True else "❌" if result is False else "⚠️"
        print(f"   {status} {item}")
    
    print("\n" + "=" * 80)
    print("🎯 IMMEDIATE ACTION REQUIRED:")
    print("=" * 80)
    
    # Key issue that needs to be fixed
    critical_issues = []
    for item, result in checks:
        if result is False:
            critical_issues.append(item)
    
    if critical_issues:
        print(f"❌ Critical issues ({len(critical_issues)}):")
        for issue in critical_issues:
            print(f"   • {issue}")
        
        print("\n🔧 REQUIRED FIXES:")
        print("   1. Fix server.py import: Change 'CoreLogic' to 'DashboardCore'")
        print("   2. Ensure .env file has correct DATABASE_URL")
        print("   3. Verify all required imports exist")
        print("\n📝 Specific changes needed:")
        print("   1. In src/dashboard_mcp/server.py line 15:")
        print("      OLD: from src.dashboard_mcp.core import CoreLogic")
        print("      NEW: from .core import DashboardCore")
        print("   2. In .env file:")
        print("      Change: DATABASE_URL=postgresql://postgres:***@localhost:5432/dashboard_mcp")
        print("      To:      DATABASE_URL=postgresql://postgres:postgres@localhost:5432/dashboard_mcp")
    else:
        print("✅ All critical issues resolved!")
        print("🎉 Dashboard MCP server is ready for testing!")
    
    print("=" * 80)
    
    if failed == 0:
        return True
    else:
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)