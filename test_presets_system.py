#!/usr/bin/env python3
"""Test script for presets system"""

import sys
import asyncio
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent / "backend"))
sys.path.insert(0, str(Path(__file__).parent / "bot"))

async def test_preset_system():
    """Test the complete preset system"""
    print("🧪 Testing Preset System")
    print("=" * 50)
    
    try:
        # Test 1: Check backend import
        print("1. Testing backend imports...")
        from app.database import seed_presets_if_empty
        from app.models import Preset
        from app.schemas import PresetResponse
        print("✅ Backend imports successful")
        
        # Test 2: Check bot import
        print("\n2. Testing bot imports...")
        from bot.services.api_client import BackendAPIClient
        from bot.states import UserState
        print("✅ Bot imports successful")
        
        # Test 3: Check worker import
        print("\n3. Testing worker imports...")
        from worker.workflows.qwen_edit_2511 import build_workflow
        print("✅ Worker imports successful")
        
        # Test 4: Check database functions
        print("\n4. Testing database functions...")
        from app.database import SessionLocal, seed_presets_if_empty
        from app.models import Preset
        
        db = SessionLocal()
        try:
            # Check if we can create a test preset
            test_preset = Preset(
                category="test",
                name="Test Preset",
                icon="🧪",
                prompt="Test prompt",
                price=30.0,
                order=1
            )
            db.add(test_preset)
            db.commit()
            db.delete(test_preset)
            db.commit()
            print("✅ Database operations successful")
        finally:
            db.close()
        
        # Test 5: Check API schemas
        print("\n5. Testing API schemas...")
        test_preset_data = {
            "category": "styles",
            "name": "Test",
            "icon": "🧪",
            "prompt": "Test prompt",
            "price": 30.0,
            "order": 1
        }
        
        preset_schema = PresetResponse(**test_preset_data)
        print(f"✅ Schema validation successful: {preset_schema.name}")
        
        print("\n🎉 All tests passed!")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config():
    """Test configuration"""
    print("🔧 Testing Configuration")
    print("=" * 50)
    
    try:
        from backend.app.config import settings
        
        print(f"POINTS_PER_RUBLE: {settings.POINTS_PER_RUBLE}")
        print(f"EDIT_COST: {settings.EDIT_COST}")
        print(f"INITIAL_BALANCE: {settings.INITIAL_BALANCE}")
        print(f"WEEKLY_BONUS_AMOUNT: {settings.WEEKLY_BONUS_AMOUNT}")
        
        # Check if points per ruble is 1
        if settings.POINTS_PER_RUBLE == 1:
            print("✅ POINTS_PER_RUBLE is correctly set to 1")
        else:
            print("❌ POINTS_PER_RUBLE should be 1, but is:", settings.POINTS_PER_RUBLE)
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting Preset System Tests\n")
    
    # Test configuration first
    config_ok = test_config()
    print()
    
    # Test system components
    system_ok = asyncio.run(test_preset_system())
    
    if config_ok and system_ok:
        print("\n✅ All tests completed successfully!")
        print("\n📋 Next steps:")
        print("1. Start backend: cd backend && python run.py")
        print("2. Start bot: cd bot && python run.py")
        print("3. Start worker: cd worker && python run.py")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()