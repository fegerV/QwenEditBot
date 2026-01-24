import logging
import aiohttp
from typing import Optional, Dict, Any
from worker.config import settings

logger = logging.getLogger(__name__)


class ComfyUIClient:
    """HTTP client for ComfyUI API with connection pooling"""

    def __init__(self):
        self.base_url = settings.COMFYUI_URL.rstrip('/')
        logger.info(f"ComfyUI Client initialized with URL: {self.base_url}")
        self.timeout = aiohttp.ClientTimeout(total=settings.COMFYUI_TIMEOUT)
        # Connection pooling - will be created lazily when session is first accessed
        self.connector = None
        self.session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session with connection pooling"""
        if self.session is None or self.session.closed:
            # Create connector only when we have a running event loop
            if self.connector is None:
                self.connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
            
            self.session = aiohttp.ClientSession(
                connector=self.connector,
                timeout=self.timeout
            )
            logger.debug("Created new aiohttp session with connection pooling")
        return self.session
    
    async def close(self):
        """Cleanup session and connector"""
        if self.session and not self.session.closed:
            await self.session.close()
        if self.connector:
            await self.connector.close()
        logger.debug("Closed aiohttp session")

    async def send_workflow(self, workflow: Dict) -> str:
        """Send workflow to ComfyUI, return prompt_id"""
        url = f"{self.base_url}/prompt"
        
        try:
            payload = {"prompt": workflow}
            session = await self._get_session()
            
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    prompt_id = data.get("prompt_id")
                    if prompt_id:
                        return prompt_id
                    else:
                        logger.error("No prompt_id in ComfyUI response")
                        raise Exception("No prompt_id in ComfyUI response")
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to send workflow: {response.status} - {error_text}")
                    raise Exception(f"ComfyUI error: {error_text}")
        except Exception as e:
            logger.error(f"Error sending workflow to ComfyUI: {str(e)}")
            raise

    async def get_history(self, prompt_id: str) -> Optional[Dict]:
        """Get job history/status"""
        url = f"{self.base_url}/history/{prompt_id}"
        
        try:
            session = await self._get_session()
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if prompt_id in data:
                        return data
                    else:
                        return {}
                elif response.status == 404:
                    return {}
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to get history: {response.status} - {error_text}")
                    return None
        except Exception as e:
            logger.error(f"Error getting ComfyUI history: {str(e)}")
            return None

    async def download_result(self, prompt_id: str, filename: str) -> Optional[bytes]:
        """Download result image - This method is now deprecated as we get the URL from history"""
        logger.warning("download_result method is deprecated, use image info from history instead")
        return None

    async def check_health(self) -> bool:
        """Check ComfyUI health status with timeout"""
        url = f"{self.base_url}/system_stats"
        
        try:
            session = await self._get_session()
            
            # Use a shorter timeout for health checks
            health_timeout = aiohttp.ClientTimeout(total=10)
            async with session.get(url, timeout=health_timeout) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.debug(f"ComfyUI health check successful: {data}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"ComfyUI health check failed: {response.status} - {error_text}")
                    return False
        except asyncio.TimeoutError:
            logger.error(f"ComfyUI health check timeout - service may be unresponsive")
            return False
        except Exception as e:
            logger.error(f"Error checking ComfyUI health: {str(e)}")
            return False