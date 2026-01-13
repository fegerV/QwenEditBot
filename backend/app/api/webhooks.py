"""Webhook endpoints for external services"""

from fastapi import APIRouter, Request, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import YuKassaWebhook
from ..services.payment_service import PaymentService
from ..services.yukassa import YuKassaClient
from ..services.telegram_client import TelegramClient
from ..config import settings
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/yukassa")
async def yukassa_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Webhook from YuKassa for payment status updates
    
    Receives notifications from YuKassa when payment status changes.
    Verifies signature and updates payment status in database.
    
    Expected payload:
    {
        "type": "notification",
        "event": "payment.succeeded",
        "object": {
            "id": "...",
            "status": "succeeded",
            "amount": {"value": "100.00", "currency": "RUB"},
            "created_at": "2024-01-12T20:00:00Z",
            "paid_at": "2024-01-12T20:05:00Z"
        }
    }
    """
    try:
        body = await request.body()
        body_str = body.decode()

        client_host = request.client.host if request.client else "unknown"

        signature = (
            request.headers.get("X-Yookassa-Signature")
            or request.headers.get("X-YooKassa-Signature")
            or request.headers.get("Content-Hmac")
        )
        if not signature:
            logger.warning("YuKassa webhook rejected (missing signature) from %s", client_host)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing signature",
            )

        yukassa_client = YuKassaClient()
        if not yukassa_client.verify_signature(signature, body_str):
            logger.warning(
                "YuKassa webhook rejected (invalid signature) from %s, signature=%s",
                client_host,
                signature,
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid signature",
            )

        # Parse webhook data
        data = json.loads(body_str)
        # webhook = YuKassaWebhook(**data) # We'll use raw data to get payment_method
        
        # Extract payment info
        object_data = data.get("object", {})
        yukassa_payment_id = object_data.get("id")
        payment_status = object_data.get("status")
        payment_method_data = object_data.get("payment_method", {})
        
        logger.info(f"YuKassa webhook: {yukassa_payment_id}, status: {payment_status}, method: {payment_method_data.get('type')}")
        
        # Process webhook
        payment_service = PaymentService(db)
        success = await payment_service.handle_webhook(
            yukassa_payment_id=yukassa_payment_id,
            status=payment_status,
            payment_method_details=payment_method_data
        )
        
        if not success:
            return {"status": "ignored"}
        
        # Send notification to user if payment succeeded
        if payment_status == "succeeded":
            payment = db.query(__import__("..models", fromlist=["Payment"]).Payment).filter(
                __import__("..models", fromlist=["Payment"]).Payment.yukassa_payment_id == yukassa_payment_id
            ).first()
            
            if payment:
                user = db.query(__import__("..models", fromlist=["User"]).User).filter(
                    __import__("..models", fromlist=["User"]).User.user_id == payment.user_id
                ).first()
                
                if user:
                    # Calculate points credited
                    points = (payment.amount // 100) * settings.POINTS_PER_RUBLE

                    try:
                        telegram_client = TelegramClient()
                        await telegram_client.send_message(
                            chat_id=user.telegram_id,
                            text=f"✅ Платёж успешен!\n\n💰 Пополнено: {points} баллов\n💳 Баланс: {int(user.balance)} баллов\n\nСпасибо за использование QwenEditBot! 🎉",
                        )
                        logger.info(f"Notification sent to user {user.user_id} about successful payment")
                    except Exception as e:
                        logger.error(f"Failed to send Telegram notification: {e}")
        
        return {"status": "ok"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing YuKassa webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process webhook: {str(e)}"
        )


@router.get("/test")
async def test_webhook():
    """Test endpoint to verify webhook is accessible"""
    return {"status": "ok", "message": "Webhook endpoint is accessible"}
