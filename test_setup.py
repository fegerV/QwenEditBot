#!/usr/bin/env python3
"""
Simple test script to verify the backend setup
"""
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Set environment to use backend .env file
os.environ['BOT_TOKEN'] = 'test-bot-token-for-development'

def test_imports():
    """Test that all modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from typing import Optional
        from app.main import app
        print("✅ Main app imported successfully")
        
        from app.config import settings
        print("✅ Config imported successfully")
        
        from app.database import engine, Base
        print("✅ Database imported successfully")
        
        from app.models import User, Preset, Job, PaymentLog
        print("✅ Models imported successfully")
        
        from app.schemas import UserCreate, PresetCreate, JobCreate
        print("✅ Schemas imported successfully")
        
        from app.services.comfyui import ComfyUIClient
        print("✅ ComfyUI service imported successfully")
        
        from app.services.balance import check_balance, deduct_balance
        print("✅ Balance service imported successfully")
        
        print("\n🎉 All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_config():
    """Test configuration loading"""
    print("\n🧪 Testing configuration...")
    
    try:
        from app.config import settings
        
        print(f"✅ BOT_TOKEN: {settings.BOT_TOKEN[:10]}..." if settings.BOT_TOKEN else "✅ BOT_TOKEN: Not set (using default)")
        print(f"✅ COMFYUI_URL: {settings.COMFYUI_URL}")
        print(f"✅ DATABASE_URL: {settings.DATABASE_URL}")
        print(f"✅ INITIAL_BALANCE: {settings.INITIAL_BALANCE}")
        print(f"✅ EDIT_COST: {settings.EDIT_COST}")
        
        print("\n🎉 Configuration loaded successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_database():
    """Test database connection"""
    print("\n🧪 Testing database connection...")
    
    try:
        from app.database import engine, Base
        from sqlalchemy import text
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            if result.scalar() == 1:
                print("✅ Database connection successful")
            else:
                print("❌ Database connection test failed")
                return False
        
        print("\n🎉 Database connection test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 QwenEditBot Backend Setup Test")
    print("=" * 50)
    
    success = True
    success &= test_imports()
    success &= test_config()
    success &= test_database()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! Backend setup is working correctly.")
        print("\n📝 Next steps:")
        print("1. Run the backend: python backend/run.py")
        print("2. Access Swagger UI: http://localhost:8000/docs")
        print("3. Test the API endpoints")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    print("=" * 50)