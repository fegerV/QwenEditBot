import aiohttp
import json
from typing import Optional, Dict, Any
from ..config import settings
import logging
from pathlib import Path
import uuid

logger = logging.getLogger(__name__)

class ComfyUIClient:
    def __init__(self):
        self.base_url = settings.COMFYUI_URL
        self.input_dir = Path(settings.COMFYUI_INPUT_DIR)
        self.output_filename = settings.COMFY_OUTPUT_FILENAME
        self.timeout = settings.COMFYUI_TIMEOUT
        
        # Ensure input directory exists
        self.input_dir.mkdir(parents=True, exist_ok=True)
    
    async def send_to_queue(self, image_path: str, prompt: str) -> str:
        """
        Send image and prompt to ComfyUI
        Returns ComfyUI job ID (prompt_id)
        """
        try:
            # Prepare workflow JSON
            workflow = {
                "prompt": prompt,
                "input_image": image_path
            }
            
            # Send to ComfyUI
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/prompt",
                    json=workflow,
                    timeout=self.timeout
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        prompt_id = result.get("prompt_id")
                        logger.info(f"ComfyUI job created: {prompt_id}")
                        return prompt_id
                    else:
                        error_text = await response.text()
                        logger.error(f"ComfyUI error: {response.status} - {error_text}")
                        raise Exception(f"ComfyUI API error: {response.status} - {error_text}")
        except Exception as e:
            logger.error(f"Error sending to ComfyUI: {e}")
            raise
    
    async def check_status(self, job_id: str) -> Dict[str, Any]:
        """
        Check status of ComfyUI job
        Returns status and progress
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/prompt/{job_id}",
                    timeout=self.timeout
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "status": result.get("status", "unknown"),
                            "progress": result.get("progress", 0)
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"ComfyUI status check error: {response.status} - {error_text}")
                        raise Exception(f"ComfyUI API error: {response.status} - {error_text}")
        except Exception as e:
            logger.error(f"Error checking ComfyUI status: {e}")
            raise
    
    async def get_result(self, job_id: str) -> str:
        """
        Get result from ComfyUI job
        Returns path to result file
        """
        try:
            # Check if job is completed
            status = await self.check_status(job_id)
            if status.get("status") != "completed":
                raise Exception(f"Job not completed yet: {status.get('status')}")
            
            # Get history to find output file
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/history/{job_id}",
                    timeout=self.timeout
                ) as response:
                    if response.status == 200:
                        history = await response.json()
                        # Find output file path
                        output_path = None
                        for node_id, node_data in history.get("outputs", {}).items():
                            if "images" in node_data:
                                for image in node_data["images"]:
                                    if self.output_filename in image.get("filename", ""):
                                        output_path = image.get("path")
                                        break
                        
                        if output_path:
                            # Download and save locally
                            local_path = self.input_dir / f"result_{uuid.uuid4().hex}.png"
                            async with session.get(f"{self.base_url}/{output_path}") as img_response:
                                if img_response.status == 200:
                                    with open(local_path, "wb") as f:
                                        f.write(await img_response.read())
                                    return str(local_path)
                        
                        raise Exception("Could not find output file in ComfyUI response")
                    else:
                        error_text = await response.text()
                        logger.error(f"ComfyUI result error: {response.status} - {error_text}")
                        raise Exception(f"ComfyUI API error: {response.status} - {error_text}")
        except Exception as e:
            logger.error(f"Error getting ComfyUI result: {e}")
            raise

# Create client instance
comfyui_client = ComfyUIClient()