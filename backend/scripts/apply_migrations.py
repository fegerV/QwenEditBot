#!/usr/bin/env python3
"""
Script to apply database migrations
"""

import subprocess
import sys
import os

# Change to backend directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

try:
    result = subprocess.run([
        sys.executable, "-m", "alembic", "upgrade", "head"
    ], cwd="..", capture_output=True, text=True)
    
    if result.returncode == 0:
        print("Migrations applied successfully")
    else:
        print(f"Failed to apply migrations: {result.stderr}")
        sys.exit(1)
        
except Exception as e:
    print(f"Error applying migrations: {e}")
    sys.exit(1)