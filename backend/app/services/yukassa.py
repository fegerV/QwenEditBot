"""YuKassa API client for payment processing"""

import httpx
import hmac
import hashlib
import logging
from typing import Optional, Dict, Any
from ..config import settings

logger = logging.getLogger(__name__)


class YuKassaClient:
    """HTTP client for YuKassa API"""
    
    def __init__(self):
        self.shop_id = settings.YUKASSA_SHOP_ID
        self.api_key = settings.YUKASSA_API_KEY
        self.base_url = "https://api.yookassa.ru/v3"
        self.timeout = 30
        
    def _get_auth_header(self) -> str:
        """Generate Basic Auth header for YuKassa"""
        import base64
        credentials = f"{self.shop_id}:{self.api_key}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"
    
    async def create_payment(
        self,
        amount: int,
        currency: str = "RUB",
        description: str = "QwenEditBot - пополнение баланса",
        return_url: str = None
    ) -> Dict[str, Any]:
        """
        Create a payment in YuKassa
        
        Args:
            amount: amount in kopeks (100 = 1 ruble)
            currency: currency code (default: RUB)
            description: payment description
            return_url: URL to redirect after payment
            
        Returns:
            Dictionary with payment details including confirmation_url
        """
        if not self.shop_id or not self.api_key:
            raise ValueError("YuKassa credentials not configured")
        
        if return_url is None:
            return_url = settings.PAYMENT_RETURN_URL
        
        # YuKassa expects amount in fractional units (100.00 for 100 rubles)
        amount_rubles = amount / 100.0
        
        payload = {
            "amount": {
                "value": f"{amount_rubles:.2f}",
                "currency": currency
            },
            "confirmation": {
                "type": "redirect",
                "return_url": return_url
            },
            "capture": True,
            "description": description
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": self._get_auth_header(),
            "Idempotence-Key": f"payment-{amount}-{hash(payload)}"
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/payments",
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                
                data = response.json()
                logger.info(f"YuKassa payment created: {data['id']}")
                
                return {
                    "payment_id": data["id"],
                    "status": data["status"],
                    "confirmation_url": data["confirmation"]["confirmation_url"],
                    "amount": amount,
                    "created_at": data["created_at"]
                }
                
        except httpx.HTTPError as e:
            logger.error(f"YuKassa API error: {e}")
            raise Exception(f"Failed to create YuKassa payment: {str(e)}")
    
    async def get_payment(self, payment_id: str) -> Dict[str, Any]:
        """
        Get payment information from YuKassa
        
        Args:
            payment_id: YuKassa payment ID
            
        Returns:
            Dictionary with payment details
        """
        if not self.shop_id or not self.api_key:
            raise ValueError("YuKassa credentials not configured")
        
        headers = {
            "Authorization": self._get_auth_header()
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/payments/{payment_id}",
                    headers=headers
                )
                response.raise_for_status()
                
                data = response.json()
                logger.info(f"YuKassa payment retrieved: {payment_id}, status: {data['status']}")
                
                return {
                    "payment_id": data["id"],
                    "status": data["status"],
                    "amount": int(float(data["amount"]["value"]) * 100),  # Convert to kopeks
                    "currency": data["amount"]["currency"],
                    "created_at": data["created_at"],
                    "paid_at": data.get("captured_at")
                }
                
        except httpx.HTTPError as e:
            logger.error(f"YuKassa API error: {e}")
            raise Exception(f"Failed to get YuKassa payment: {str(e)}")
    
    def verify_signature(self, request_body: str, signature: str) -> bool:
        """
        Verify YuKassa webhook signature
        
        YuKassa sends HMAC-SHA256 signature.
        
        Args:
            request_body: Raw request body as string
            signature: Signature from request header
            
        Returns:
            True if signature is valid, False otherwise
        """
        if not settings.YUKASSA_WEBHOOK_SECRET:
            logger.warning("YuKassa webhook secret not configured, skipping signature verification")
            return True
        
        try:
            expected_signature = hmac.new(
                settings.YUKASSA_WEBHOOK_SECRET.encode(),
                request_body.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Use constant-time comparison to prevent timing attacks
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"Error verifying YuKassa signature: {e}")
            return False
