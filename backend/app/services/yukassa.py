import logging
import uuid
from typing import Any, Dict, Optional

import httpx

from ..config import settings
from ..utils.validators import verify_hmac_sha256_signature

logger = logging.getLogger(__name__)


class YuKassaClient:
    """Minimal async HTTP client for YooKassa API (v3)."""

    def __init__(
        self,
        shop_id: str,
        api_key: str,
        webhook_secret: Optional[str] = None,
        base_url: str = "https://api.yookassa.ru/v3",
    ):
        self.shop_id = shop_id
        self.api_key = api_key
        self.webhook_secret = webhook_secret
        self.base_url = base_url.rstrip("/")

    @staticmethod
    def _kopeks_to_value(amount_kopeks: int) -> str:
        rub = amount_kopeks / 100
        return f"{rub:.2f}"

    async def create_payment(
        self,
        amount: int,
        currency: str = "RUB",
        description: str = "QwenEditBot - пополнение баланса",
        return_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        idempotence_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/payments"

        idem_key = idempotence_key or uuid.uuid4().hex
        payload: Dict[str, Any] = {
            "amount": {"value": self._kopeks_to_value(amount), "currency": currency},
            "confirmation": {
                "type": "redirect",
                "return_url": return_url or settings.PAYMENT_RETURN_URL or "https://t.me/",
            },
            "capture": True,
            "description": description,
        }
        if metadata:
            payload["metadata"] = metadata

        headers = {"Idempotence-Key": idem_key}

        auth = httpx.BasicAuth(self.shop_id, self.api_key)

        async with httpx.AsyncClient(timeout=30, auth=auth) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        return {
            "id": data.get("id"),
            "status": data.get("status"),
            "confirmation_url": (data.get("confirmation") or {}).get("confirmation_url"),
            "idempotence_key": idem_key,
            "raw": data,
        }

    async def get_payment(self, payment_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/payments/{payment_id}"
        auth = httpx.BasicAuth(self.shop_id, self.api_key)

        async with httpx.AsyncClient(timeout=30, auth=auth) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()

        return data

    def verify_signature(self, request_body: bytes, signature: Optional[str]) -> bool:
        """Verify webhook signature using HMAC-SHA256.

        NOTE: YooKassa supports setting a secret key for notifications.
        We follow the ticket requirements and validate HMAC(secret, body).
        """

        if not self.webhook_secret:
            logger.warning("YUKASSA_WEBHOOK_SECRET is not set; webhook signature verification is skipped")
            return True

        return verify_hmac_sha256_signature(request_body, signature, self.webhook_secret)
