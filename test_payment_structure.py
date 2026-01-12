"""Test payment system structure and syntax"""

import os
import ast

print("Checking payment system structure...")

# Check backend files
backend_files = [
    "backend/app/models.py",
    "backend/app/schemas.py",
    "backend/app/config.py",
    "backend/app/services/yukassa.py",
    "backend/app/services/payment_service.py",
    "backend/app/services/scheduler.py",
    "backend/app/services/telegram_client.py",
    "backend/app/api/payments.py",
    "backend/app/api/webhooks.py",
    "backend/app/main.py",
    "backend/requirements.txt",
    "backend/.env.example"
]

print("\n📁 Backend files:")
for file in backend_files:
    exists = os.path.exists(file)
    status = "✅" if exists else "❌"
    print(f"  {status} {file}")
    
    # Check syntax if Python file
    if exists and file.endswith('.py'):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                ast.parse(f.read())
        except SyntaxError as e:
            print(f"      ⚠️  Syntax error in {file}: {e}")

# Check bot files
bot_files = [
    "bot/handlers/payments.py",
    "bot/main.py",
    "bot/handlers/balance.py",
    "bot/keyboards.py",
    "bot/handlers/__init__.py",
    "bot/services/api_client.py"
]

print("\n📁 Bot files:")
for file in bot_files:
    exists = os.path.exists(file)
    status = "✅" if exists else "❌"
    print(f"  {status} {file}")
    
    # Check syntax if Python file
    if exists and file.endswith('.py'):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                ast.parse(f.read())
        except SyntaxError as e:
            print(f"      ⚠️  Syntax error in {file}: {e}")

print("\n✅ Payment system structure check complete!")
