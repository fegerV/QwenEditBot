import logging
import aiohttp
from typing import Optional, List, Dict, Any
from worker.config import settings

logger = logging.getLogger(__name__)


class BackendAPIClient:
    """HTTP client for backend API"""

    def __init__(self):
        self.base_url = settings.BACKEND_API_URL.rstrip('/')
        self.timeout = aiohttp.ClientTimeout(total=settings.BACKEND_API_TIMEOUT)

    async def get_pending_jobs(self, limit: int = 1) -> List[Dict]:
        """Get jobs with status='queued'"""
        url = f"{self.base_url}/api/jobs?status=queued&limit={limit}"
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to get pending jobs: {response.status} - {error_text}")
                        return []
        except Exception as e:
            logger.error(f"Error getting pending jobs: {str(e)}")
            return []

    async def update_job(self, job_id: int, update_data: Dict) -> Optional[Dict]:
        """Update job status"""
        url = f"{self.base_url}/api/jobs/{job_id}"
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.put(url, json=update_data) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to update job {job_id}: {response.status} - {error_text}")
                        return None
        except Exception as e:
            logger.error(f"Error updating job {job_id}: {str(e)}")
            return None

    async def get_job(self, job_id: int) -> Optional[Dict]:
        """Get job by ID"""
        url = f"{self.base_url}/api/jobs/{job_id}"
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to get job {job_id}: {response.status} - {error_text}")
                        return None
        except Exception as e:
            logger.error(f"Error getting job {job_id}: {str(e)}")
            return None

    async def download_image(self, image_path: str) -> Optional[bytes]:
        """Download image from backend"""
        url = f"{self.base_url}/file/{image_path}"
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.read()
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to download image {image_path}: {response.status} - {error_text}")
                        return None
        except Exception as e:
            logger.error(f"Error downloading image {image_path}: {str(e)}")
            return None

    async def refund_balance(self, user_id: int, amount: int, reason: str) -> bool:
        """Refund balance to user"""
        url = f"{self.base_url}/api/balance/refund"
        
        try:
            payload = {
                "user_id": user_id,
                "amount": amount,
                "reason": reason
            }
            
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("success", False)
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to refund balance: {response.status} - {error_text}")
                        return False
        except Exception as e:
            logger.error(f"Error refunding balance: {str(e)}")
            return False

    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        url = f"{self.base_url}/api/users/{user_id}"
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to get user {user_id}: {response.status} - {error_text}")
                        return None
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {str(e)}")
            return None