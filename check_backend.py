#!/usr/bin/env python3
"""
Diagnostic script to check backend startup issues
"""

import sys
import os
import subprocess
import time
import traceback

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def check_python():
    print_section("Python Environment")
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    print(f"Python Path: {sys.path[:3]}...")
    return True

def check_imports():
    print_section("Import Checks")
    critical_imports = [
        "fastapi",
        "sqlalchemy", 
        "alembic",
        "redis",
        "pydantic",
        "uvicorn"
    ]
    
    failed = []
    for module in critical_imports:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module}: {e}")
            failed.append(module)
    
    return len(failed) == 0

def check_environment():
    print_section("Environment Variables")
    backend_env = os.path.join("backend", ".env")
    if not os.path.exists(backend_env):
        print(f"✗ backend/.env not found")
        return False
    
    print(f"✓ backend/.env exists")
    
    # Try to load the env file
    try:
        from dotenv import load_dotenv
        load_dotenv(backend_env)
        required_vars = ["DATABASE_URL"]
        missing = []
        for var in required_vars:
            if not os.getenv(var):
                missing.append(var)
        
        if missing:
            print(f"✗ Missing required variables: {missing}")
            return False
        print(f"✓ Required environment variables present")
    except Exception as e:
        print(f"✗ Error loading .env: {e}")
        return False
    
    return True

def check_database():
    print_section("Database Check")
    try:
        sys.path.insert(0, "backend")
        from app.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print(f"✓ Database connection successful")
        return True
    except Exception as e:
        print(f"✗ Database error: {e}")
        traceback.print_exc()
        return False

def test_backend_startup():
    print_section("Backend Startup Test")
    
    # Change to backend directory
    os.chdir("backend")
    
    # Test if we can import the main app
    try:
        print("Testing app import...")
        from app.main import app
        print("✓ App imported successfully")
        
        # Check routers
        print(f"✓ Number of routes: {len(app.routes)}")
        
        # Check middleware
        print(f"✓ Middleware: {len(app.user_middleware)} middlewares configured")
        
        return True
    except Exception as e:
        print(f"✗ App import failed: {e}")
        traceback.print_exc()
        return False

def run_backend_diagnostic():
    print_section("Running Backend Diagnostic")
    try:
        os.chdir("backend")
        result = subprocess.run(
            [sys.executable, "-c", """
import sys
sys.path.insert(0, '.')
try:
    from app.main import on_startup
    import asyncio
    asyncio.run(on_startup())
    print("✓ Startup routine completed successfully")
except Exception as e:
    print(f"✗ Startup failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
"""],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("✗ Startup diagnostic timed out (30s)")
        return False
    except Exception as e:
        print(f"✗ Diagnostic failed: {e}")
        return False

def main():
    print("QwenEditBot Backend Diagnostic Tool")
    print(f"Running from: {os.getcwd()}")
    
    all_checks = []
    
    all_checks.append(("Python Environment", check_python()))
    all_checks.append(("Critical Imports", check_imports()))
    all_checks.append(("Environment Variables", check_environment()))
    all_checks.append(("Database", check_database()))
    all_checks.append(("App Import", test_backend_startup()))
    all_checks.append(("Startup Routine", run_backend_diagnostic()))
    
    print_section("Summary")
    failed = []
    for check_name, result in all_checks:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {check_name}")
        if not result:
            failed.append(check_name)
    
    print(f"\n{'='*60}")
    if failed:
        print(f"FAILED CHECKS: {len(failed)}")
        for f in failed:
            print(f"  - {f}")
        print("\nFix the failed checks above and run this diagnostic again.")
        sys.exit(1)
    else:
        print("✓ ALL CHECKS PASSED - Backend should start successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main()