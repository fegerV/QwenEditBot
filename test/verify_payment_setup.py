#!/usr/bin/env python3
"""
YuKassa Payment Setup Verification Tool

This script verifies that all YuKassa configuration is correct and complete
for production deployment. Run this before starting the payment system.
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple

color_codes = {
    'green': '\033[92m',
    'red': '\033[91m',
    'yellow': '\033[93m',
    'blue': '\033[94m',
    'reset': '\033[0m'
}

def print_colored(text: str, color: str):
    """Print colored text"""
    print(f"{color_codes.get(color, color_codes['reset'])}{text}{color_codes['reset']}")

def check_env_file() -> bool:
    """Check if .env file exists and contains all required YuKassa variables"""
    env_path = Path("backend/.env")
    if not env_path.exists():
        print_colored("❌ backend/.env file not found!", 'red')
        print_colored("   Run: cp backend/.env.example backend/.env", 'yellow')
        return False
    
    required_vars = [
        "YUKASSA_SHOP_ID",
        "YUKASSA_API_KEY",
        "YUKASSA_WEBHOOK_SECRET"
    ]
    
    with open(env_path, 'r') as f:
        content = f.read()
        missing_vars = []
        empty_vars = []
        
        for var in required_vars:
            if var not in content:
                missing_vars.append(var)
            else:
                # Check if the variable has a value (not empty)
                for line in content.split('\n'):
                    if line.strip().startswith(f"{var}="):
                        value = line.split('=', 1)[1].strip().strip('"').strip("'")
                        if not value or value == "":
                            empty_vars.append(var)
                        elif len(value) < 10 and var == "YUKASSA_WEBHOOK_SECRET":
                            print_colored(f"⚠️  {var} seems unusually short", 'yellow')
                        
        if missing_vars:
            print_colored(f"❌ Missing variables in .env: {', '.join(missing_vars)}", 'red')
            return False
        
        if empty_vars:
            print_colored(f"❌ Empty variables in .env: {', '.join(empty_vars)}", 'red')
            print_colored("   Please fill in these values from your YuKassa dashboard", 'yellow')
            return False
    
    print_colored("✅ All required YuKassa variables present in .env", 'green')
    return True

def check_yukassa_credentials() -> bool:
    """Check if YuKassa credentials are properly formatted"""
    try:
        from backend.app.config import settings
        
        issues = []
        
        shop_id = settings.YUKASSA_SHOP_ID
        if not shop_id:
            issues.append("YUKASSA_SHOP_ID is not set")
        elif not isinstance(shop_id, str):
            issues.append("YUKASSA_SHOP_ID must be a string")
        elif len(shop_id) < 5:
            issues.append("YUKASSA_SHOP_ID seems too short")
            
        api_key = settings.YUKASSA_API_KEY
        if not api_key:
            issues.append("YUKASSA_API_KEY is not set")
        elif not isinstance(api_key, str):
            issues.append("YUKASSA_API_KEY must be a string")
        elif len(api_key) < 30:
            issues.append("YUKASSA_API_KEY seems too short")
        elif not (api_key.startswith("test_") or api_key.startswith("live_")):
            issues.append("YUKASSA_API_KEY should start with 'test_' or 'live_'")
            
        webhook_secret = settings.YUKASSA_WEBHOOK_SECRET
        if not webhook_secret:
            issues.append("YUKASSA_WEBHOOK_SECRET is not set")
        elif not isinstance(webhook_secret, str):
            issues.append("YUKASSA_WEBHOOK_SECRET must be a string")
        elif len(webhook_secret) < 20:
            issues.append("YUKASSA_WEBHOOK_SECRET seems too short")
            
        if issues:
            for issue in issues:
                print_colored(f"❌ {issue}", 'red')
            return False
        
        print_colored("✅ YuKassa credentials properly configured", 'green')
        
        # Detect environment
        if api_key and api_key.startswith("test_"):
            print_colored("   ℹ️  Using TEST mode (test_ API key)", 'blue')
        elif api_key and api_key.startswith("live_"):
            print_colored("   ℹ️  Using PRODUCTION mode (live_ API key)", 'green')
            print_colored("   ⚠️  WARNING: Real money will be processed!", 'yellow')
        
        return True
        
    except Exception as e:
        print_colored(f"❌ Error checking credentials: {e}", 'red')
        return False

def check_payment_limits() -> bool:
    """Check payment limits configuration"""
    try:
        from backend.app.config import settings
        
        min_amount = settings.PAYMENT_MIN_AMOUNT
        max_amount = settings.PAYMENT_MAX_AMOUNT
        
        if not isinstance(min_amount, (int, float)) or min_amount < 1:
            print_colored(f"❌ Invalid PAYMENT_MIN_AMOUNT: {min_amount}", 'red')
            return False
            
        if not isinstance(max_amount, (int, float)) or max_amount > 100000:
            print_colored(f"❌ Invalid PAYMENT_MAX_AMOUNT: {max_amount} (too high for safety)", 'red')
            return False
            
        if min_amount >= max_amount:
            print_colored(f"❌ PAYMENT_MIN_AMOUNT ({min_amount}) >= PAYMENT_MAX_AMOUNT ({max_amount})", 'red')
            return False
        
        points_per_ruble = settings.POINTS_PER_RUBLE
        if not isinstance(points_per_ruble, (int, float)) or points_per_ruble <= 0:
            print_colored(f"❌ Invalid POINTS_PER_RUBLE: {points_per_ruble}", 'red')
            return False
        
        print_colored(f"✅ Payment limits valid: {min_amount}₽ - {max_amount}₽ ({points_per_ruble} points per ruble)", 'green')
        return True
        
    except Exception as e:
        print_colored(f"❌ Error checking payment limits: {e}", 'red')
        return False

def check_backend_url() -> bool:
    """Check if backend URL is configured"""
    try:
        from backend.app.config import settings
        
        backend_url = settings.BACKEND_URL
        return_url = settings.PAYMENT_RETURN_URL
        
        issues = []
        
        if not backend_url or backend_url == "http://localhost:8000":
            issues.append("BACKEND_URL is localhost - webhook won't work in production")
            
        if not return_url or return_url == "https://t.me/YourBotUsername":
            issues.append("PAYMENT_RETURN_URL not configured (default value)")
        
        if issues:
            for issue in issues:
                print_colored(f"⚠️  {issue}", 'yellow')
            print_colored("   Fix this before production deployment", 'yellow')
            # Don't fail the check, just warn
        
        print_colored(f"✅ Backend URL configured: {backend_url}", 'green')
        print_colored(f"✅ Return URL configured: {return_url}", 'green')
        return True
        
    except Exception as e:
        print_colored(f"❌ Error checking backend URLs: {e}", 'red')
        return False

def check_weekly_bonus_config() -> bool:
    """Check weekly bonus configuration"""
    try:
        from backend.app.config import settings
        
        if not settings.WEEKLY_BONUS_ENABLED:
            print_colored("ℹ️  Weekly bonus is disabled", 'blue')
            return True
        
        bonus_amount = settings.WEEKLY_BONUS_AMOUNT
        bonus_day = settings.WEEKLY_BONUS_DAY
        bonus_time = settings.WEEKLY_BONUS_TIME
        
        issues = []
        
        if not isinstance(bonus_amount, int) or bonus_amount < 0:
            issues.append(f"Invalid WEEKLY_BONUS_AMOUNT: {bonus_amount}")
            
        if not isinstance(bonus_day, int) or bonus_day < 0 or bonus_day > 6:
            issues.append(f"Invalid WEEKLY_BONUS_DAY: {bonus_day} (must be 0-6, Monday=0)")
            
        if not isinstance(bonus_time, str) or not re.match(r'^\d{2}:\d{2}$', bonus_time):
            issues.append(f"Invalid WEEKLY_BONUS_TIME: {bonus_time} (must be HH:MM)")
        
        if issues:
            for issue in issues:
                print_colored(f"❌ {issue}", 'red')
            return False
        
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        print_colored(f"✅ Weekly bonus enabled: +{bonus_amount} points every {days[bonus_day]} at {bonus_time} UTC", 'green')
        return True
        
    except Exception as e:
        print_colored(f"❌ Error checking weekly bonus config: {e}", 'red')
        return False

def check_rate_limiting() -> bool:
    """Check rate limiting configuration"""
    try:
        from backend.app.config import settings
        
        if not settings.RATE_LIMIT_ENABLED:
            print_colored("⚠️  Rate limiting is DISABLED - not recommended for production!", 'yellow')
            return True
        
        rate_limit = settings.PAYMENT_RATE_LIMIT
        if not rate_limit or not isinstance(rate_limit, str):
            print_colored(f"❌ Invalid PAYMENT_RATE_LIMIT: {rate_limit}", 'red')
            return False
        
        print_colored(f"✅ Rate limiting enabled: {rate_limit}", 'green')
        return True
        
    except Exception as e:
        print_colored(f"❌ Error checking rate limiting: {e}", 'red')
        return False

def test_imports() -> bool:
    """Test that all payment modules can be imported"""
    try:
        print_colored("Testing imports...", 'blue')
        
        # Test backend imports
        try:
            from backend.app.services.yukassa import YuKassaClient
            from backend.app.services.payment_service import PaymentService
            from backend.app import models
            print_colored("✅ Backend payment modules import successfully", 'green')
        except Exception as e:
            print_colored(f"❌ Backend import error: {e}", 'red')
            return False
        
        # Test bot imports
        try:
            sys.path.append('bot')
            from bot.services.api_client import BackendAPIClient
            print_colored("✅ Bot API client imports successfully", 'green')
        except Exception as e:
            print_colored(f"❌ Bot import error: {e}", 'red')
            return False
        
        return True
        
    except Exception as e:
        print_colored(f"❌ Unexpected import error: {e}", 'red')
        return False

def print_summary(results: List[Tuple[str, bool]]):
    """Print summary of all checks"""
    print("\n" + "=" * 60)
    print_colored("SETUP VERIFICATION SUMMARY", 'blue')
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "✅" if result else "❌"
        color = 'green' if result else 'red'
        print_colored(f"{status} {check_name}", color)
    
    print("=" * 60)
    
    if passed == total:
        print_colored(f"🎉 ALL CHECKS PASSED ({passed}/{total})", 'green')
        print()
        print_colored("Your YuKassa integration is ready!", 'green')
        print_colored("You can now start processing payments.", 'green')
    else:
        print_colored(f"❌ SOME CHECKS FAILED ({passed}/{total})", 'red')
        print()
        print_colored("Please fix the issues above before deploying to production.", 'red')
        
        if passed >= total - 2:
            print()
            print_colored("Most checks passed. You can test locally but fix warnings before production.", 'yellow')

def main():
    """Main verification function"""
    print("\n" + "=" * 60)
    print_colored("QwenEditBot YuKassa Setup Verification", 'blue')
    print("=" * 60)
    print()
    
    # Add parent directory to path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    results = []
    
    # Run all checks
    checks = [
        ("Environment file exists", check_env_file),
        ("YuKassa credentials valid", check_yukassa_credentials),
        ("Payment limits valid", check_payment_limits),
        ("Backend URLs configured", check_backend_url),
        ("Weekly bonus configuration", check_weekly_bonus_config),
        ("Rate limiting enabled", check_rate_limiting),
        ("Module imports work", test_imports)
    ]
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print_colored(f"❌ Error running {check_name}: {e}", 'red')
            results.append((check_name, False))
        print()
    
    # Print summary
    print_summary(results)
    
    # Exit with appropriate code
    sys.exit(0 if all(result for _, result in results) else 1)

if __name__ == "__main__":
    # Add color support for Windows
    if sys.platform == "win32":
        os.system("color")
    
    try:
        import re
    except ImportError:
        pass
    
    main()
