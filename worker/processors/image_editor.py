import logging
import asyncio
import os
from pathlib import Path
from typing import Optional

from worker.services.comfyui_client import ComfyUIClient
from worker.services.backend_client import BackendAPIClient
from worker.job_queue.job_queue import Job
from worker.config import settings
from worker.workflows.qwen_edit_2511 import build_workflow

logger = logging.getLogger(__name__)


class ImageEditorProcessor:
    """Image processor through ComfyUI"""

    def __init__(self):
        self.comfyui_client = ComfyUIClient()
        self.backend_client = BackendAPIClient()

    async def process(self, job: Job) -> str:
        """
        Full processing cycle.
        
        1. Copy image from upload location to ComfyUI/input
        2. Prepare workflow JSON
        3. Send to ComfyUI
        4. Poll for result
        5. Download result
        6. Save to output directory
        7. Return path to result
        """
        logger.info(f"Processing job {job.id}")

        try:
            # Step 1: Copy image from upload location to ComfyUI input directory
            source_path = Path(job.image_path)
            if not source_path.exists():
                raise Exception(f"Source image does not exist: {source_path}")

            # Extract filename and create destination path in ComfyUI input directory
            input_filename = f"input_{job.id}_{source_path.name}"
            input_path = Path(settings.COMFYUI_INPUT_DIR) / input_filename
            
            # Copy file to ComfyUI input directory
            import shutil
            shutil.copy2(source_path, input_path)
            
            logger.info(f"Job {job.id}: input_path={input_path}, exists={os.path.exists(input_path)}")

            # Step 3: Prepare workflow using build_workflow
            workflow = build_workflow(job)

            # Step 4: Send to ComfyUI
            comfyui_job_id = await self.comfyui_client.send_workflow(workflow)
            logger.info(f"ComfyUI job {comfyui_job_id} created for job {job.id}")

            # Step 5: Wait and download result
            result_path = await self._wait_and_download(comfyui_job_id, job.id)
            logger.info(f"Result saved to {result_path}")

            return str(result_path)

        except Exception as e:
            logger.error(f"Error processing job {job.id}: {str(e)}")
            raise

    async def _wait_and_download(self, comfyui_job_id: str, job_id: int) -> Path:
        """Wait for result and download"""
        max_attempts = 100  # 50 seconds max (0.5s * 100)
        
        for attempt in range(max_attempts):
            # Check job status
            history = await self.comfyui_client.get_history(comfyui_job_id)
            
            if history and history.get("status") == "completed":
                # Job completed, download result
                result_filename = f"job_{job_id}_result.png"
                result_data = await self.comfyui_client.download_result(comfyui_job_id, result_filename)
                
                if result_data:
                    # Save to output directory
                    results_dir = Path(settings.RESULTS_DIR)
                    result_path = results_dir / result_filename
                    
                    with open(result_path, "wb") as f:
                        f.write(result_data)
                    
                    return result_path
                else:
                    raise Exception("Failed to download result from ComfyUI")
            elif history and history.get("status") == "failed":
                raise Exception(f"ComfyUI job failed: {history.get('error', 'Unknown error')}")
            
            # Wait before checking again
            await asyncio.sleep(settings.COMFYUI_POLL_INTERVAL)
        
        raise Exception("ComfyUI job timeout")