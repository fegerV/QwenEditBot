import logging
import aiohttp
from typing import Optional, Dict, Any
from worker.config import settings

logger = logging.getLogger(__name__)


class ComfyUIClient:
    """HTTP client for ComfyUI API"""

    def __init__(self):
        self.base_url = settings.COMFYUI_URL.rstrip('/')
        self.timeout = aiohttp.ClientTimeout(total=settings.COMFYUI_TIMEOUT)

    async def send_workflow(self, workflow: Dict) -> str:
        """Send workflow to ComfyUI, return prompt_id"""
        url = f"{self.base_url}/prompt"
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(url, json=workflow) as response:
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
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    elif response.status == 404:
                        return None  # Job not found yet
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to get history: {response.status} - {error_text}")
                        return None
        except Exception as e:
            logger.error(f"Error getting ComfyUI history: {str(e)}")
            return None

    async def download_result(self, prompt_id: str, filename: str) -> Optional[bytes]:
        """Download result image"""
        url = f"{self.base_url}/view?filename={filename}"
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.read()
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to download result: {response.status} - {error_text}")
                        return None
        except Exception as e:
            logger.error(f"Error downloading ComfyUI result: {str(e)}")
            return None