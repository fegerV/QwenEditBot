import asyncio
from worker.services.telegram_client import TelegramClient
from worker.services.backend_client import BackendAPIClient
from pathlib import Path

async def test_send():
    # 1. Get user info
    print("Step 1: Getting user info...")
    backend = BackendAPIClient()
    user = await backend.get_user(1)  # user_id 1
    print(f"User: {user}")
    
    if not user:
        print("ERROR: User not found!")
        return
    
    # 2. Get telegram_id
    print("\nStep 2: Getting telegram_id...")
    telegram_id = user.get("telegram_id") or user.get("telegramId")
    print(f"Telegram ID: {telegram_id}")
    
    if not telegram_id:
        print("ERROR: No telegram_id found!")
        return
    
    # 3. Read result image
    print("\nStep 3: Reading result image...")
    result_path = Path("data/outputs/job_193_result.png")
    if not result_path.exists():
        print(f"ERROR: Result file not found: {result_path}")
        return
    
    with open(result_path, "rb") as f:
        image_data = f.read()
    print(f"Image size: {len(image_data)} bytes")
    
    # 4. Send photo
    print("\nStep 4: Sending photo to Telegram...")
    telegram = TelegramClient()
    caption = "Test photo from job 193!"
    success = await telegram.send_photo(telegram_id, image_data, caption)
    
    print(f"Send result: {success}")
    
    if success:
        print("SUCCESS! Photo sent to Telegram!")
    else:
        print("FAILED! Photo not sent!")

asyncio.run(test_send())
