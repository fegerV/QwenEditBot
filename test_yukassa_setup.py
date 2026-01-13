#!/usr/bin/env python3
"""
YuKassa Integration Test Suite

Run this to verify all payment components are working correctly.
"""

import asyncio
import sys
import os
from pathlib import Path

def test_yukassa_client():
    """Test YuKassa client import and initialization"""
    print("Testing YuKassaClient...")
    try:
        from backend.app.services.yukassa import YuKassaClient
        client = YuKassaClient()
        print("✅ YuKassaClient imported successfully")
        return True
    except Exception as e:
        print(f"❌ YuKassaClient import failed: {e}")
        return False

def test_payment_service():
    """Test payment service"""
    print("Testing PaymentService...")
    try:
        from backend.app.services.payment_service import PaymentService
        from backend.app.database import SessionLocal
        db = SessionLocal()
        service = PaymentService(db)
        print("✅ PaymentService initialized successfully")
        return True
    except Exception as e:
        print(f"❌ PaymentService initialization failed: {e}")
        return False

def test_payment_models():
    """Test payment models"""
    print("Testing payment models...")
    try:
        from backend.app import models
        # Check Payment model
        payment = models.Payment()
        print("✅ Payment model imported")
        
        # Check PaymentStatus
        assert hasattr(models.PaymentStatus, 'pending')
        assert hasattr(models.PaymentStatus, 'succeeded')
        print("✅ PaymentStatus enum working")
        
        # Check PaymentType
        assert hasattr(models.PaymentType, 'payment')
        assert hasattr(models.PaymentType, 'weekly_bonus')
        assert hasattr(models.PaymentType, 'refund')
        print("✅ PaymentType enum working")
        
        return True
    except Exception as e:
        print(f"❌ Payment model import failed: {e}")
        return False

def test_bot_api_client():
    """Test bot API client"""
    print("Testing bot API client...")
    try:
        sys.path.append('bot')
        from bot.services.api_client import BackendAPIClient
        client = BackendAPIClient()
        print("✅ BackendAPIClient imported successfully")
        return True
    except Exception as e:
        print(f"❌ Bot API client import failed: {e}")
        return False

def test_webhook_endpoint():
    """Test webhook endpoint accessibility"""
    print("Testing webhook endpoint...")
    try:
        sys.path.append('backend')
        from backend.app.main import app
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        response = client.get("/api/webhooks/test")
        if response.status_code == 200:
            print("✅ Webhook endpoint accessible")
            return True
        else:
            print(f"❌ Webhook endpoint returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Webhook endpoint test failed: {e}")
        return False

async def test_yukassa_signature_verification():
    """Test YuKassa signature verification"""
    print("Testing YuKassa signature verification...")
    try:
        from backend.app.services.yukassa import YuKassaClient
        
        client = YuKassaClient()
        secret = "test_secret_key_123"
        
        # Temporarily set secret
        import backend.app.config
        original_secret = backend.app.config.settings.YUKASSA_WEBHOOK_SECRET
        backend.app.config.settings.YUKASSA_WEBHOOK_SECRET = secret
        
        try:
            # Test valid signature
            test_body = '{"type": "notification", "event": "payment.succeeded"}'
            import hmac
            import hashlib
            expected_signature = hmac.new(
                secret.encode(),
                test_body.encode(),
                hashlib.sha256
            ).hexdigest()
            
            result = client.verify_signature(f"sha256={expected_signature}", test_body)
            if result:
                print("✅ Signature verification works")
                return True
            else:
                print("❌ Signature verification failed")
                return False
        finally:
            backend.app.config.settings.YUKASSA_WEBHOOK_SECRET = original_secret
    except Exception as e:
        print(f"❌ Signature test failed: {e}")
        return False

def test_database_tables():
    """Test that payment tables exist in database"""
    print("Testing database tables...")
    try:
        from backend.app.database import engine
        from backend.app import models
        from sqlalchemy import inspect
        
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if 'payments' in tables:
            print("✅ Payments table exists")
            return True
        else:
            print("❌ Payments table not found - run migrations")
            return False
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_payment_endpoints():
    """Test payment API endpoints"""
    print("Testing payment API endpoints...")
    try:
        sys.path.append('backend')
        from backend.app.main import app
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        # Check endpoints exist
        routes = [route.path for route in app.routes]
        
        checks = [
            ("/api/payments/create", "POST"),
            ("/api/payments/{payment_id}", "GET"),
            ("/api/payments/user/{user_id}", "GET"),
            ("/api/webhooks/yukassa", "POST"),
            ("/api/webhooks/test", "GET")
        ]
        
        all_ok = True
        for path, method in checks:
            # Check if path exists in routes (pattern matching for path parameters)
            path_found = any(p for p in routes if path.split('{')[0] in p)
            if path_found:
                print(f"✅ Endpoint {method} {path}")
            else:
                print(f"❌ Endpoint {method} {path} not found")
                all_ok = False
        
        return all_ok
    except Exception as e:
        print(f"❌ API endpoints test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("=" * 60)
    print("QwenEditBot YuKassa Integration Test Suite")
    print("=" * 60)
    print()
    
    sys.path.insert(0, '.')
    
    tests = [
        ("YuKassa Client", test_yukassa_client),
        ("Payment Service", test_payment_service),
        ("Payment Models", test_payment_models),
        ("Bot API Client", test_bot_api_client),
        ("Webhook Endpoint", test_webhook_endpoint),
        ("Database Tables", test_database_tables),
        ("API Endpoints", test_payment_endpoints),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error running {test_name}: {e}")
            results.append((test_name, False))
    
    # Test signature verification async
    print("Testing signature verification...")
    try:
        sig_result = await test_yukassa_signature_verification()
        results.append(("Signature Verification", sig_result))
    except Exception as e:
        print(f"❌ Signature test failed: {e}")
        results.append(("Signature Verification", False))
    
    print()
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    print("=" * 60)
    print(f"Result: {passed}/{total} tests passed")
    
    if passed == total:
        print()
        print("🎉 All tests passed! Your YuKassa integration is working correctly.")
        print()
        print("Next steps:")
        print("1. Add your YuKassa credentials to backend/.env")
        print("2. Run: python verify_payment_setup.py")
        print("3. Start backend: cd backend && python run.py")
        print("4. Start bot: cd bot && python run.py")
    else:
        print()
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
