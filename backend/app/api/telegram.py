from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Request
from ..schemas import TelegramWebhook
import logging
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from ..config import settings
from pathlib import Path
import uuid
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from redis_client import redis_client
from ..services.balance import check_balance, deduct_balance, refund_balance
import aiohttp

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/webhook")
async def telegram_webhook(request: Request, db: Session = Depends(get_db)):
    """Telegram webhook endpoint to receive updates from Telegram"""
    try:
        # Parse incoming JSON data from Telegram
        update_data = await request.json()
        logger.info(f"Received Telegram update: {update_data}")
        
        # Handle different types of updates
        if 'message' in update_data:
            message = update_data['message']
            
            # Get user ID
            user_id = message['from']['id']
            
            # Check if user exists
            user = db.query(models.User).filter(models.User.user_id == user_id).first()
            if not user:
                logger.warning(f"Unknown user tried to interact: {user_id}")
                return {"status": "ignored"}
            
            # Handle different message types
            if 'photo' in message:
                # User sent a photo - process image editing
                return await handle_photo_message(message, user_id, db)
            elif 'text' in message:
                # Text message - handle commands
                text = message['text']
                if text.startswith('/'):
                    return await handle_command(text, user_id, db)
        
        elif 'callback_query' in update_data:
            # Handle inline keyboard callbacks
            callback_query = update_data['callback_query']
            user_id = callback_query['from']['id']
            return await handle_callback(callback_query, user_id, db)
        
        return {"status": "processed"}
    
    except Exception as e:
        logger.error(f"Error processing Telegram webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing webhook: {str(e)}"
        )


async def handle_photo_message(message, user_id, db):
    """Handle photo messages from users"""
    try:
        from fastapi import Request
        from io import BytesIO
        import aiohttp
        
        # Check if unlimited processing is enabled
        unlimited_processing = getattr(settings, 'UNLIMITED_PROCESSING', False)
        
        # Check if user is admin
        is_admin = user_id in getattr(settings, 'ADMIN_IDS', [])
        
        # Determine cost based on admin status and unlimited processing
        cost = 0 if (is_admin or unlimited_processing) else settings.EDIT_COST
        
        # Skip balance checks completely during testing
        logger.info(f"Balance check skipped for user {user_id} during testing")
        
        # Get the highest resolution photo
        photos = message['photo']  # Array of photo sizes
        largest_photo = max(photos, key=lambda p: p.get('width', 0))
        
        # Get file info from Telegram
        file_id = largest_photo['file_id']
        
        # Get bot token from settings
        bot_token = settings.BOT_TOKEN
        
        # Get file path from Telegram API
        file_response = await aiohttp.ClientSession().get(
            f"https://api.telegram.org/bot{bot_token}/getFile?file_id={file_id}"
        )
        file_data = await file_response.json()
        
        if not file_data.get('ok'):
            logger.error(f"Could not get file info: {file_data}")
            return {"status": "error", "details": "Could not retrieve file from Telegram"}
        
        file_path = file_data['result']['file_path']
        
        # Download the actual file
        file_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
        async with aiohttp.ClientSession() as session:
            async with session.get(file_url) as resp:
                file_bytes = await resp.read()
        
        # Get prompt if provided (from caption)
        prompt = message.get('caption', '').strip()
        if not prompt:
            # Try to get the last message from this user as the prompt
            # In a real implementation, you'd want to store user sessions
            prompt = "Convert to in the comic style, while preserving composition and character identity. remove the progress bar and watermarks"
        
        # Create uploads directory if it doesn't exist
        uploads_dir = Path(settings.COMFY_INPUT_DIR)  # Use COMFY_INPUT_DIR instead of UPLOADS_DIR
        uploads_dir.mkdir(parents=True, exist_ok=True)
        
        # Save uploaded image to ComfyUI input directory
        file_ext = "jpg"  # Telegram photos are usually jpg
        task_id = str(uuid.uuid4().hex)[:8]  # Generate short unique task ID
        # Use the format expected by the workflow
        image_filename = f"input_{task_id}.{file_ext}"
        image_path = uploads_dir / image_filename
        
        # Save the file
        with open(image_path, "wb") as buffer:
            buffer.write(file_bytes)
        
        # Create job in database
        new_job = models.Job(
            user_id=user_id,
            image_path=str(image_path),  # Store the path to the image in the ComfyUI input directory
            prompt=prompt,
            status=models.JobStatus.queued
        )
        
        db.add(new_job)
        db.commit()
        db.refresh(new_job)
        
        # Skip balance deduction during testing
        logger.info(f"Balance deduction skipped for user {user_id} during testing")
        
        # Add job to Redis queue with task_id and image_path
        try:
            job_data = {
                'id': new_job.id,
                'task_id': task_id,
                'user_id': new_job.user_id,
                'image_path': str(image_path),
                'prompt': new_job.prompt,
                'status': new_job.status.value,
                'created_at': new_job.created_at.isoformat() if new_job.created_at else datetime.utcnow().isoformat(),
                'updated_at': new_job.updated_at.isoformat() if new_job.updated_at else datetime.utcnow().isoformat()
            }
            
            await redis_client.enqueue_job(job_data)
            logger.info(f"Job {new_job.id} with task_id {task_id} added to Redis queue")
            
            # Send confirmation to user
            await send_telegram_message(
                user_id,
                f"✅ Изображение загружено! ID задачи: {task_id}\n⏳ Обработка может занять несколько минут..."
            )
        except Exception as redis_error:
            logger.error(f"Failed to add job {new_job.id} to Redis queue: {redis_error}")
            # Send error message to user
            await send_telegram_message(
                user_id,
                "❌ Произошла ошибка при обработке изображения. Повторите попытку позже."
            )
            # Refund the deducted amount
            # Skip refund during testing
            logger.info(f"Refund skipped for user {user_id} during testing")
        
        return {"status": "received", "task_id": task_id, "job_id": new_job.id}
    
    except Exception as e:
        logger.error(f"Error handling photo message: {e}")
        return {"status": "error", "details": str(e)}


async def handle_command(command, user_id, db):
    """Handle text commands from users"""
    try:
        if command == '/start':
            # Send welcome message
            welcome_text = (
                f"Добро пожаловать в QwenEditBot 🎨\n\n"
                f"Вам начислено {settings.INITIAL_BALANCE} баллов!\n\n"
                f"Загрузите фото и получите результат после обработки AI."
            )
            await send_telegram_message(user_id, welcome_text)
        elif command == '/balance':
            # Send user balance
            user = db.query(models.User).filter(models.User.user_id == user_id).first()
            if user:
                await send_telegram_message(user_id, f"💰 Ваш баланс: {user.balance} баллов")
            else:
                await send_telegram_message(user_id, "❌ Не удалось получить информацию о балансе")
        else:
            # Unknown command
            await send_telegram_message(
                user_id,
                f"🤖 Команда '{command}' не распознана.\n\nДоступные команды:\n/start - Начать работу\n/balance - Проверить баланс"
            )
        
        return {"status": "command_handled"}
    
    except Exception as e:
        logger.error(f"Error handling command {command}: {e}")
        return {"status": "error", "details": str(e)}


async def handle_callback(callback_query, user_id, db):
    """Handle inline keyboard callbacks"""
    try:
        # Answer the callback query
        await answer_callback_query(callback_query['id'])
        
        # Process the callback based on its data
        callback_data = callback_query.get('data', '')
        
        # In a real implementation, you'd handle various callback types here
        # For now, we'll just log the callback
        logger.info(f"Received callback: {callback_data} from user {user_id}")
        
        return {"status": "callback_handled"}
    
    except Exception as e:
        logger.error(f"Error handling callback: {e}")
        return {"status": "error", "details": str(e)}


async def send_telegram_message(chat_id, text):
    """Send a message to a Telegram user"""
    try:
        import aiohttp
        
        bot_token = settings.BOT_TOKEN
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={
                'chat_id': chat_id,
                'text': text,
                'parse_mode': 'HTML'
            }) as response:
                result = await response.json()
                
                if not result.get('ok'):
                    logger.error(f"Failed to send message to {chat_id}: {result}")
    
    except Exception as e:
        logger.error(f"Error sending Telegram message: {e}")


async def answer_callback_query(callback_query_id, text=None):
    """Answer a callback query to close the loading animation"""
    try:
        import aiohttp
        
        bot_token = settings.BOT_TOKEN
        url = f"https://api.telegram.org/bot{bot_token}/answerCallbackQuery"
        
        payload = {'callback_query_id': callback_query_id}
        if text:
            payload['text'] = text
            
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                result = await response.json()
                
                if not result.get('ok'):
                    logger.error(f"Failed to answer callback query {callback_query_id}: {result}")
    
    except Exception as e:
        logger.error(f"Error answering callback query: {e}")