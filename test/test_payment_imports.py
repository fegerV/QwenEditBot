"""Test payment system imports"""

print("Testing payment system imports...")

# Test models
try:
    from backend.app.models import Payment, PaymentStatus, PaymentType
    print("✅ Models imported successfully")
except Exception as e:
    print(f"❌ Models import failed: {e}")

# Test schemas
try:
    from backend.app.schemas import PaymentCreate, PaymentResponse, PaymentHistoryResponse
    print("✅ Schemas imported successfully")
except Exception as e:
    print(f"❌ Schemas import failed: {e}")

# Test services
try:
    from backend.app.services.yukassa import YuKassaClient
    from backend.app.services.payment_service import PaymentService
    from backend.app.services.scheduler import WeeklyBonusScheduler
    from backend.app.services.telegram_client import TelegramClient
    print("✅ Services imported successfully")
except Exception as e:
    print(f"❌ Services import failed: {e}")

# Test API routes
try:
    from backend.app.api import payments, webhooks
    print("✅ API routes imported successfully")
except Exception as e:
    print(f"❌ API routes import failed: {e}")

print("\n✅ All payment system imports successful!")
