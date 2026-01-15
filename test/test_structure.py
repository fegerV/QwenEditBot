#!/usr/bin/env python3
"""
Test script to verify all enhancements are implemented in the code structure
"""

import os
import ast

def test_payment_logging_structure():
    """Test that payment logging is implemented in the code"""
    print("Testing payment logging structure...")
    
    try:
        # Check if payment_service.py has enhanced logging
        with open('/home/engine/project/backend/app/services/payment_service.py', 'r') as f:
            content = f.read()
            
        # Check for logging statements
        logging_checks = [
            'logger.info(f"Payment created successfully:',
            'logger.info(f"Payment succeeded:',
            'logger.info(f"Refund created successfully:',
            'logger.info(f"Weekly bonus issued successfully:',
            'logger.warning(f"Payment creation failed:',
            'logger.warning(f"Webhook processing failed:',
        ]
        
        found_logging = []
        for check in logging_checks:
            if check in content:
                found_logging.append(check)
        
        if len(found_logging) >= 4:
            print(f"✅ Found {len(found_logging)} enhanced logging statements")
            return True
        else:
            print(f"⚠️  Only found {len(found_logging)} enhanced logging statements")
            return False
        
    except Exception as e:
        print(f"❌ Payment logging structure test failed: {e}")
        return False

def test_comfyui_health_check_structure():
    """Test ComfyUI health check implementation"""
    print("Testing ComfyUI health check structure...")
    
    try:
        # Check if ComfyUI client has health check method
        with open('/home/engine/project/worker/services/comfyui_client.py', 'r') as f:
            content = f.read()
        
        # Check for health check method
        if 'async def check_health(self)' in content:
            print("✅ ComfyUI health check method found")
            
            # Check if it uses system_stats endpoint
            if '/system_stats' in content:
                print("✅ Uses /system_stats endpoint")
                return True
            else:
                print("⚠️  Health check doesn't use /system_stats endpoint")
                return False
        else:
            print("❌ Health check method not found")
            return False
        
    except Exception as e:
        print(f"❌ ComfyUI health check structure test failed: {e}")
        return False

def test_worker_health_check_integration():
    """Test if worker integrates health check"""
    print("Testing worker health check integration...")
    
    try:
        # Check if worker main.py uses health check
        with open('/home/engine/project/worker/main.py', 'r') as f:
            content = f.read()
        
        # Check for health check usage
        checks = [
            'self.comfyui_client = ComfyUIClient()',
            'comfyui_healthy = await self.comfyui_client.check_health()',
            'if not comfyui_healthy:',
        ]
        
        found_checks = []
        for check in checks:
            if check in content:
                found_checks.append(check)
        
        if len(found_checks) >= 2:
            print(f"✅ Found {len(found_checks)} health check integration points")
            return True
        else:
            print(f"⚠️  Only found {len(found_checks)} health check integration points")
            return False
        
    except Exception as e:
        print(f"❌ Worker health check integration test failed: {e}")
        return False

def test_rate_limiting_structure():
    """Test rate limiting implementation"""
    print("Testing rate limiting structure...")
    
    try:
        # Check if payments.py has rate limiting
        with open('/home/engine/project/backend/app/api/payments.py', 'r') as f:
            content = f.read()
        
        # Check for rate limiting imports and usage
        rate_limit_checks = [
            'from slowapi import Limiter',
            'from slowapi.util import get_remote_address',
            'from slowapi.errors import RateLimitExceeded',
            'limiter = Limiter(key_func=get_remote_address)',
            '@limiter.limit(',
            'RATE_LIMIT_ENABLED',
        ]
        
        found_checks = []
        for check in rate_limit_checks:
            if check in content:
                found_checks.append(check)
        
        if len(found_checks) >= 4:
            print(f"✅ Found {len(found_checks)} rate limiting implementation points")
            return True
        else:
            print(f"⚠️  Only found {len(found_checks)} rate limiting implementation points")
            return False
        
    except Exception as e:
        print(f"❌ Rate limiting structure test failed: {e}")
        return False

def test_migrations_structure():
    """Test database migrations structure"""
    print("Testing database migrations structure...")
    
    try:
        # Check if migrations directory exists
        migrations_dir = '/home/engine/project/backend/migrations'
        if os.path.exists(migrations_dir):
            print("✅ Migrations directory exists")
            
            # Check if versions directory exists
            versions_dir = os.path.join(migrations_dir, 'versions')
            if os.path.exists(versions_dir):
                print("✅ Migrations versions directory exists")
                
                # Check if any migration files exist
                migration_files = [f for f in os.listdir(versions_dir) if f.endswith('.py')]
                if migration_files:
                    print(f"✅ Found {len(migration_files)} migration files")
                    
                    # Check if initial migration exists
                    initial_migration = any('initial' in f.lower() for f in migration_files)
                    if initial_migration:
                        print("✅ Initial migration found")
                        return True
                    else:
                        print("⚠️  No initial migration found")
                        return False
                else:
                    print("⚠️  No migration files found")
                    return False
            else:
                print("⚠️  No versions directory found")
                return False
        else:
            print("⚠️  No migrations directory found")
            return False
        
    except Exception as e:
        print(f"❌ Migrations structure test failed: {e}")
        return False

def test_main_migrations_integration():
    """Test if main.py integrates migrations"""
    print("Testing main.py migrations integration...")
    
    try:
        # Check if main.py has migration support
        with open('/home/engine/project/backend/app/main.py', 'r') as f:
            content = f.read()
        
        # Check for migration functions
        migration_checks = [
            'def run_migrations():',
            'alembic upgrade head',
            'run_migrations()',
        ]
        
        found_checks = []
        for check in migration_checks:
            if check in content:
                found_checks.append(check)
        
        if len(found_checks) >= 2:
            print(f"✅ Found {len(found_checks)} migration integration points")
            return True
        else:
            print(f"⚠️  Only found {len(found_checks)} migration integration points")
            return False
        
    except Exception as e:
        print(f"❌ Main.py migrations integration test failed: {e}")
        return False

def test_config_rate_limiting():
    """Test if config has rate limiting settings"""
    print("Testing config rate limiting settings...")
    
    try:
        # Check if config.py has rate limiting settings
        with open('/home/engine/project/backend/app/config.py', 'r') as f:
            content = f.read()
        
        # Check for rate limiting configuration
        config_checks = [
            'RATE_LIMIT_ENABLED',
            'PAYMENT_RATE_LIMIT',
        ]
        
        found_checks = []
        for check in config_checks:
            if check in content:
                found_checks.append(check)
        
        if len(found_checks) >= 2:
            print(f"✅ Found {len(found_checks)} rate limiting config settings")
            return True
        else:
            print(f"⚠️  Only found {len(found_checks)} rate limiting config settings")
            return False
        
    except Exception as e:
        print(f"❌ Config rate limiting test failed: {e}")
        return False

def test_enhanced_features():
    """Test all enhanced features"""
    print("\n" + "="*60)
    print("Testing Enhanced Features Implementation")
    print("="*60 + "\n")
    
    results = []
    
    # Test payment logging
    results.append(("Payment Logging", test_payment_logging_structure()))
    print()
    
    # Test ComfyUI health check
    results.append(("ComfyUI Health Check", test_comfyui_health_check_structure()))
    print()
    
    # Test worker health check integration
    results.append(("Worker Health Check Integration", test_worker_health_check_integration()))
    print()
    
    # Test rate limiting
    results.append(("Rate Limiting", test_rate_limiting_structure()))
    print()
    
    # Test config rate limiting
    results.append(("Config Rate Limiting", test_config_rate_limiting()))
    print()
    
    # Test migrations
    results.append(("Database Migrations", test_migrations_structure()))
    print()
    
    # Test main.py migrations integration
    results.append(("Main.py Migrations Integration", test_main_migrations_integration()))
    print()
    
    # Print summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 All enhancement tests passed!")
        print("All requested features have been implemented:")
        print("  ✅ Enhanced payment logging")
        print("  ✅ ComfyUI health check")
        print("  ✅ Rate limiting on payments")
        print("  ✅ Database migrations with Alembic")
    else:
        print("⚠️  Some tests failed. Please check the output above.")
    print("="*60)
    
    return all_passed

if __name__ == "__main__":
    success = test_enhanced_features()
    exit(0 if success else 1)