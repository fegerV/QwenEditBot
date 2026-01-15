"""Test database connection and basic functionality"""

import asyncio
from backend.app.database import SessionLocal, seed_presets_if_empty
from backend.app.models import User
from bot.services.api_client import BackendAPIClient

async def test_db_connection():
    """Test database connectivity"""
    print("Testing database connection...")
    try:
        db = SessionLocal()
        # Try to query users table to verify connection
        users = db.query(User).limit(5).all()
        print(f"✓ Successfully connected to database. Found {len(users)} users.")
        db.close()
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

async def test_seed_presets():
    """Test seeding presets if empty"""
    print("\nTesting presets seeding...")
    try:
        db = SessionLocal()
        await seed_presets_if_empty(db)
        preset_count = db.query(backend.app.models.Preset).count()
        print(f"✓ Presets seeded successfully. Total presets: {preset_count}")
        db.close()
        return True
    except Exception as e:
        print(f"✗ Presets seeding failed: {e}")
        return False

async def test_api_connection():
    """Test API client connection"""
    print("\nTesting API connection...")
    try:
        client = BackendAPIClient()
        # Test health check endpoint
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:8000/health') as resp:
                if resp.status == 200:
                    print("✓ API connection successful")
                    return True
                else:
                    print(f"✗ API connection failed with status {resp.status}")
                    return False
    except Exception as e:
        print(f"✗ API connection failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("Running database and API tests...\n")
    
    db_ok = await test_db_connection()
    api_ok = await test_api_connection()
    
    if db_ok and api_ok:
        print("\n✓ All tests passed! Database and API connections are working correctly.")
        return True
    else:
        print("\n✗ Some tests failed.")
        return False

if __name__ == "__main__":
    import backend.app.models  # Import to ensure models are loaded
    result = asyncio.run(main())
    exit(0 if result else 1)
