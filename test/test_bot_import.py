"""Test script to verify bot imports"""

import sys

print("Testing bot imports...")

try:
    print("1. Importing bot.config...")
    from bot.config import settings
    print("✓ bot.config imported successfully")
    
    print("2. Importing bot.states...")
    from bot.states import UserState
    print("✓ bot.states imported successfully")
    
    print("3. Importing bot.keyboards...")
    from bot.keyboards import main_menu_keyboard, category_keyboard
    print("✓ bot.keyboards imported successfully")
    
    print("4. Importing bot.services...")
    from bot.services import BackendAPIClient
    print("✓ bot.services imported successfully")
    
    print("5. Importing bot.utils...")
    from bot.utils import format_balance
    print("✓ bot.utils imported successfully")
    
    print("6. Importing bot.handlers.start...")
    from bot.handlers import start_router
    print("✓ bot.handlers.start imported successfully")
    
    print("7. Importing bot.handlers.menu...")
    from bot.handlers import menu_router
    print("✓ bot.handlers.menu imported successfully")
    
    print("8. Importing bot.handlers.presets...")
    from bot.handlers import presets_router
    print("✓ bot.handlers.presets imported successfully")
    
    print("9. Importing bot.handlers.custom_prompt...")
    from bot.handlers import custom_prompt_router
    print("✓ bot.handlers.custom_prompt imported successfully")
    
    print("10. Importing bot.handlers.image_upload...")
    from bot.handlers import image_upload_router
    print("✓ bot.handlers.image_upload imported successfully")
    
    print("11. Importing bot.handlers.balance...")
    from bot.handlers import balance_router
    print("✓ bot.handlers.balance imported successfully")
    
    print("12. Importing bot.handlers.help...")
    from bot.handlers import help_router
    print("✓ bot.handlers.help imported successfully")
    
    print("\n✅ All imports successful!")
    print("\nNote: To run the bot, you need to:")
    print("1. Set up bot/.env with your BOT_TOKEN")
    print("2. Make sure backend is running on http://localhost:8000")
    print("3. Run: cd bot && python run.py")
    
except Exception as e:
    print(f"\n❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
