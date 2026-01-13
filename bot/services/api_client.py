"""Backend API client for bot integration"""

import aiohttp
import logging
from typing import Optional, List, Dict, Any
from ..config import settings

logger = logging.getLogger(__name__)


class BackendAPIClient:
    """HTTP client for backend API communication"""

    def __init__(self):
        self.base_url = settings.BACKEND_URL
        self.timeout = aiohttp.ClientTimeout(total=settings.BACKEND_API_TIMEOUT)
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to backend API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                if files:
                    # For file uploads
                    async with session.post(url, data=files, params=params) as response:
                        response.raise_for_status()
                        return await response.json()
                elif data:
                    # For POST/PUT with JSON data
                    async with session.request(method, url, json=data, params=params) as response:
                        response.raise_for_status()
                        return await response.json()
                else:
                    # For GET requests
                    async with session.get(url, params=params) as response:
                        response.raise_for_status()
                        return await response.json()
                        
        except aiohttp.ClientError as e:
            logger.error(f"Backend API request failed: {method} {url} - {e}")
            raise Exception(f"Failed to connect to backend: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in API request: {e}")
            raise
    
    async def register_user(self, telegram_id: int, username: str) -> Dict[str, Any]:
        """Register a new user"""
        try:
            response = await self._request(
                "POST",
                "/api/users/register",
                data={
                    "telegram_id": telegram_id,
                    "username": username
                }
            )
            logger.info(f"User registered: {telegram_id}")
            return response
        except Exception as e:
            logger.error(f"Failed to register user {telegram_id}: {e}")
            raise
    
    async def get_user(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """Get user information by telegram_id"""
        try:
            response = await self._request("GET", f"/api/users/by-telegram-id/{telegram_id}")
            return response
        except Exception as e:
            logger.error(f"Failed to get user by telegram_id {telegram_id}: {e}")
            return None
    
    async def get_balance(self, telegram_id: int) -> Optional[int]:
        """Get user balance by telegram_id"""
        try:
            response = await self._request("GET", f"/api/users/by-telegram-id/{telegram_id}")
            return response.get("balance")
        except Exception as e:
            logger.error(f"Failed to get balance for user by telegram_id {telegram_id}: {e}")
            return None
    
    async def check_balance(self, telegram_id: int, required_points: int) -> bool:
        """Check if user has sufficient balance"""
        try:
            balance = await self.get_balance(telegram_id)
            if balance is None:
                return False
            return balance >= required_points
        except Exception as e:
            logger.error(f"Failed to check balance for user by telegram_id {telegram_id}: {e}")
            return False
    
    async def get_preset(self, preset_id: int) -> Optional[Dict[str, Any]]:
        """Get preset by ID"""
        try:
            response = await self._request("GET", f"/api/presets/{preset_id}")
            return response
        except Exception as e:
            logger.error(f"Failed to get preset {preset_id}: {e}")
            return None
    
    async def get_presets(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get presets, optionally filtered by category"""
        try:
            params = {"category": category} if category else {}
            response = await self._request("GET", "/api/presets", params=params)
            return response
        except Exception as e:
            logger.error(f"Failed to get presets (category: {category}): {e}")
            return []
    
    async def get_preset_prompt(self, preset_id: int) -> Optional[str]:
        """Get preset prompt by ID"""
        try:
            response = await self._request("GET", f"/api/presets/{preset_id}")
            return response.get('prompt')
        except Exception as e:
            logger.error(f"Failed to get preset prompt for {preset_id}: {e}")
            return None
    
    async def create_job(
        self,
        telegram_id: int,
        image_file: tuple,  # (filename, file_content, content_type)
        prompt: str
    ) -> Dict[str, Any]:
        """Create a new job with prompt by telegram_id"""
        try:
            # Get user by telegram_id to retrieve internal user_id
            user_data = await self.get_user(telegram_id)
            if not user_data:
                raise Exception(f"User with telegram_id {telegram_id} not found")
            
            user_id = user_data['user_id']
            
            # Prepare multipart form data
            files = {
                'image_file': image_file
            }
            
            params = {
                'user_id': user_id,
                'prompt': prompt
            }
            
            response = await self._request("POST", "/api/jobs/create", params=params, files=files)
            logger.info(f"Job created for user {telegram_id} (internal user_id {user_id}): {response.get('id')}")
            return response
        except Exception as e:
            logger.error(f"Failed to create job for user by telegram_id {telegram_id}: {e}")
            raise
    
    async def get_job_status(self, job_id: int) -> Optional[Dict[str, Any]]:
        """Get job status"""
        try:
            response = await self._request("GET", f"/api/jobs/{job_id}")
            return response
        except Exception as e:
            logger.error(f"Failed to get job status {job_id}: {e}")
            return None
    
    async def get_user_jobs(self, telegram_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user's jobs by telegram_id"""
        try:
            params = {"limit": limit}
            response = await self._request("GET", f"/api/jobs/user/{telegram_id}", params=params)
            return response
        except Exception as e:
            logger.error(f"Failed to get jobs for user by telegram_id {telegram_id}: {e}")
            return []
    
    async def create_payment(self, telegram_id: int, amount: int, payment_method: str = "card") -> Dict[str, Any]:
        """Create a payment by telegram_id"""
        try:
            # Get user by telegram_id to retrieve internal user_id
            user_data = await self.get_user(telegram_id)
            if not user_data:
                raise Exception(f"User with telegram_id {telegram_id} not found")
            
            user_id = user_data['user_id']
            
            response = await self._request(
                "POST",
                "/api/payments/create",
                data={
                    "user_id": user_id,
                    "amount": amount,
                    "payment_method": payment_method
                }
            )
            logger.info(f"Payment created for user {telegram_id} (internal user_id {user_id}): amount {amount}, method {payment_method}")
            return response
        except Exception as e:
            logger.error(f"Failed to create payment for user by telegram_id {telegram_id}: {e}")
            raise
    
    async def get_payment(self, payment_id: int) -> Optional[Dict[str, Any]]:
        """Get payment information"""
        try:
            response = await self._request("GET", f"/api/payments/{payment_id}")
            return response
        except Exception as e:
            logger.error(f"Failed to get payment {payment_id}: {e}")
            return None
    
    async def get_user_payments(
        self,
        telegram_id: int,
        limit: int = 20,
        offset: int = 0,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get user's payment history by telegram_id"""
        try:
            params = {"limit": limit, "offset": offset}
            if status:
                params["status"] = status
            response = await self._request("GET", f"/api/payments/user/{telegram_id}", params=params)
            return response
        except Exception as e:
            logger.error(f"Failed to get payments for user by telegram_id {telegram_id}: {e}")
            return {"payments": [], "total": 0, "limit": limit, "offset": offset}
