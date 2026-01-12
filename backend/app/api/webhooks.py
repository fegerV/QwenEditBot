import json
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..services.payment_service import PaymentService
from ..utils.validators import verify_hmac_sha256_signature

logger = logging.getLogger(__name__)

router = APIRouter()

payment_service = PaymentService()


def _get_signature_from_headers(headers) -> Optional[str]:
    for key in (
        "X-YooKassa-Signature",
        "X-Yookassa-Signature",
        "X-Webhook-Signature",
        "Notification-API-Request-ID",  # as in the ticket
    ):
        value = headers.get(key)
        if value:
            return value
    return None


@router.post("/yukassa")
async def yukassa_webhook(request: Request, db: Session = Depends(get_db)):
    body = await request.body()

    signature = _get_signature_from_headers(request.headers)
    if settings.YUKASSA_WEBHOOK_SECRET:
        if not verify_hmac_sha256_signature(body, signature, settings.YUKASSA_WEBHOOK_SECRET):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")

    try:
        data = json.loads(body.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON")

    obj = data.get("object") or {}
    yukassa_payment_id = obj.get("id")
    payment_status = obj.get("status")

    if not yukassa_payment_id or not payment_status:
        return {"status": "ignored"}

    handled = await payment_service.handle_webhook(db, yukassa_payment_id, payment_status)

    if not handled:
        return {"status": "ignored"}

    return {"status": "ok"}
