#!/usr/bin/env python3
"""
Simple script to run alembic migrations
"""
import subprocess
import sys

def run_migrations():
    """Run alembic upgrade head"""
    print("Running alembic migrations...")
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    if result.returncode != 0:
        print(f"Migration failed with exit code {result.returncode}")
        sys.exit(1)
    else:
        print("Migrations applied successfully!")

if __name__ == "__main__":
    run_migrations()
