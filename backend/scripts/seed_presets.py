#!/usr/bin/env python3
"""Seed database with default presets"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal, seed_presets_if_empty

def seed():
    """Seed database with default presets"""
    print("🌱 Seeding database with presets...")
    
    db = SessionLocal()
    
    try:
        # Seed presets
        seed_presets_if_empty(db)
        print("✅ Presets seeded successfully!")
        
    except Exception as e:
        print(f"❌ Error seeding presets: {e}")
        sys.exit(1)
        
    finally:
        db.close()

if __name__ == "__main__":
    seed()