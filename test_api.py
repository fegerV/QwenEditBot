#!/usr/bin/env python3
"""
Simple API test script to verify endpoints are working
"""
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Set environment to use backend .env file
os.environ['BOT_TOKEN'] = 'test-bot-token-for-development'

from fastapi.testclient import TestClient
from app.main import app
from app.database import engine, Base
from sqlalchemy import text

def test_api_endpoints():
    """Test basic API endpoints"""
    print("🧪 Testing API endpoints...")
    
    # Create database tables for testing
    print("📦 Creating test database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")
    
    client = TestClient(app)
    
    # Test root endpoint
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "QwenEditBot Backend is running"
    print("✅ Root endpoint working")
    
    # Test health endpoint
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("✅ Health endpoint working")
    
    # Test user registration
    response = client.post(
        "/api/users/register",
        json={"telegram_id": 123456, "username": "testuser"}
    )
    assert response.status_code == 201
    user_data = response.json()
    assert user_data["username"] == "testuser"
    assert user_data["balance"] == 60.0
    user_id = user_data["user_id"]
    print(f"✅ User registration working, created user {user_id}")
    
    # Test get user
    response = client.get(f"/api/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"
    print("✅ Get user endpoint working")
    
    # Test get user balance
    response = client.get(f"/api/users/{user_id}/balance")
    assert response.status_code == 200
    assert response.json()["balance"] == 60.0
    print("✅ Get user balance endpoint working")
    
    # Test get balance
    response = client.get(f"/api/balance/{user_id}")
    assert response.status_code == 200
    assert response.json()["balance"] == 60.0
    print("✅ Get balance endpoint working")
    
    # Test check balance
    response = client.post(
        f"/api/balance/{user_id}/check",
        json={"required_points": 30}
    )
    assert response.status_code == 200
    assert response.json()["has_sufficient_balance"] == True
    print("✅ Check balance endpoint working")
    
    # Test get presets (should be empty initially)
    response = client.get("/api/presets")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    print("✅ Get presets endpoint working")
    
    # Test create preset
    response = client.post(
        "/api/presets",
        json={
            "category": "test",
            "name": "Test Preset",
            "prompt": "Test prompt content",
            "icon": "test-icon",
            "price": 30.0,
            "order": 1
        }
    )
    assert response.status_code == 201
    preset_data = response.json()
    preset_id = preset_data["id"]
    print(f"✅ Create preset endpoint working, created preset {preset_id}")
    
    # Test get specific preset
    response = client.get(f"/api/presets/{preset_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Preset"
    print("✅ Get specific preset endpoint working")
    
    print("\n🎉 All API endpoint tests passed!")
    return True

if __name__ == "__main__":
    print("🚀 QwenEditBot API Endpoint Test")
    print("=" * 50)
    
    try:
        test_api_endpoints()
        print("\n" + "=" * 50)
        print("🎉 All API tests passed! The backend is fully functional.")
        print("\n📝 You can now:")
        print("1. Run the backend: python backend/run.py")
        print("2. Access Swagger UI: http://localhost:8000/docs")
        print("3. Test all endpoints interactively")
        print("4. Integrate with ComfyUI and Telegram bot")
    except Exception as e:
        print(f"\n❌ API test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 50)