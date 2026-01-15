#!/usr/bin/env python3
"""Seed database with default presets"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.database import seed_presets_if_empty as sync_seed_presets

def seed():
    """Seed database with default presets"""
    print("Seeding database with presets...")
    
    db = SessionLocal()
    
    try:
        # Seed presets
        sync_seed_presets(db)
        print("Presets seeded successfully!")
        
    except Exception as e:
        print(f"Error seeding presets: {e}")
        sys.exit(1)
        
    finally:
        db.close()

def main():
    """Run the seeding function"""
    seed()

if __name__ == "__main__":
    main()