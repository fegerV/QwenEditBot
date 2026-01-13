#!/usr/bin/env python3
"""
Script to create a new database migration
"""

import subprocess
import sys
import os

# Change to backend directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

if len(sys.argv) < 2:
    print("Usage: python create_migration.py <message>")
    sys.exit(1)

message = sys.argv[1]

try:
    result = subprocess.run([
        sys.executable, "-m", "alembic", "revision", "--autogenerate", "-m", message
    ], cwd="..", capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"Migration created successfully: {message}")
    else:
        print(f"Failed to create migration: {result.stderr}")
        sys.exit(1)
        
except Exception as e:
    print(f"Error creating migration: {e}")
    sys.exit(1)