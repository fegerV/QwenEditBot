import logging
import asyncio
import os
import aiohttp
from pathlib import Path
from typing import Optional

from worker.services.comfyui_client import ComfyUIClient
from worker.services.backend_client import BackendAPIClient
from worker.job_queue.job_queue import Job
from worker.config import settings
from worker.workflows.qwen_edit_2511 import build_workflow as build_single_workflow
from worker.workflows.qwen_tryon import build_tryon_workflow

logger = logging.getLogger(__name__)


class ImageEditorProcessor:
    """Image processor through ComfyUI"""

    def __init__(self):
        self.comfyui_client = ComfyUIClient()
        self.backend_client = BackendAPIClient()

    async def process(self, job: Job) -> str:
        """
        Full processing cycle.
        
        1. Verify images exist at expected locations
        2. Prepare workflow JSON (single or try-on based on second_image_path)
        3. Send to ComfyUI
        4. Poll for result
        5. Download result
        6. Save to output directory
        7. Return path to result
        """
        logger.info(f"Processing job {job.id} (try-on: {job.second_image_path is not None})")

        try:
            # Step 1: Verify the first image exists
            source_path = Path(job.image_path)
            if not source_path.exists():
                raise Exception(f"Source image does not exist: {source_path}")
            
            logger.debug(f"Using first image at path: {source_path}")

            # If second image is provided, verify it exists (for try-on)
            if job.second_image_path:
                second_source_path = Path(job.second_image_path)
                if not second_source_path.exists():
                    raise Exception(f"Second source image does not exist: {second_source_path}")
                logger.debug(f"Using second image at path: {second_source_path}")

            # Step 2: Prepare workflow - choose workflow based on image count
            if job.second_image_path:
                # Try-on workflow (2 images)
                logger.info(f"Building try-on workflow for job {job.id}")
                workflow = build_tryon_workflow(job)
            else:
                # Standard workflow (1 image)
                logger.info(f"Building standard workflow for job {job.id}")
                workflow = build_single_workflow(job)

            # Log workflow for debugging
            logger.debug(f"Workflow prepared for job {job.id}")

            # Step 3: Send to ComfyUI
            comfyui_job_id = await self.comfyui_client.send_workflow(workflow)
            logger.info(f"ComfyUI job {comfyui_job_id} created for job {job.id}")

            # Step 4: Wait and download result
            result_path = await self._wait_and_download(comfyui_job_id, job.id)
            logger.info(f"Result saved to {result_path}")

            # Step 5: Clean up input files after processing
            try:
                source_path.unlink()  # Clean up the first image
                logger.debug(f"Cleaned up first input file: {source_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up first input file {source_path}: {str(e)}")

            # Clean up second image if it exists (for try-on)
            if job.second_image_path:
                try:
                    second_source_path.unlink()
                    logger.debug(f"Cleaned up second input file: {second_source_path}")
                except Exception as e:
                    logger.warning(f"Failed to clean up second input file {second_source_path}: {str(e)}")

            return str(result_path)

        except Exception as e:
            logger.error(f"Error processing job {job.id}: {str(e)}")
            raise

    async def _wait_and_download(self, comfyui_job_id: str, job_id: int) -> Path:
        """Wait for result and download"""
        max_attempts = 600 # Increased attempts to allow more time for processing (600 * 0.5s = 300s = 5 minutes)
        
        for attempt in range(max_attempts):
            try:
                # Check job status via history endpoint
                history = await self.comfyui_client.get_history(comfyui_job_id)
                
                if history and isinstance(history, dict) and comfyui_job_id in history:
                    job_result = history[comfyui_job_id]
                    
                    # Check if the job has outputs (meaning it's completed)
                    if job_result and 'outputs' in job_result:
                        # Look for the output image in the workflow nodes
                        output_image_info = None
                        
                        # Search for output image info in all nodes
                        if 'outputs' in job_result:
                            for node_id, node_output in job_result['outputs'].items():
                                if 'images' in node_output and len(node_output['images']) > 0:
                                    output_image_info = node_output['images'][0]  # Take first image
                                    break
                        
                        if output_image_info:
                            # Download the result image
                            filename = output_image_info['filename']
                            subfolder = output_image_info.get('subfolder', '')
                            image_type = output_image_info.get('type', 'output')
                            
                            # Construct the download URL according to ComfyUI API
                            download_url = f"{self.comfyui_client.base_url}/view?filename={filename}&subfolder={subfolder}&type={image_type}"
                            
                            try:
                                async with aiohttp.ClientSession(timeout=self.comfyui_client.timeout) as session:
                                    async with session.get(download_url) as img_response:
                                        if img_response.status == 200:
                                            result_data = await img_response.read()
                                            
                                            # Save to output directory
                                            results_dir = Path(settings.RESULTS_DIR)
                                            result_filename = f"job_{job_id}_result.png"
                                            result_path = results_dir / result_filename
                                            
                                            with open(result_path, "wb") as f:
                                                f.write(result_data)
                                            
                                            logger.info(f"Successfully downloaded and saved result for job {job_id}")
                                            return result_path
                                        else:
                                            error_text = await img_response.text()
                                            logger.error(f"Failed to download result image: {img_response.status} - {error_text}")
                                            raise Exception(f"Failed to download result image: {img_response.status}")
                            except Exception as e:
                                logger.error(f"Error downloading result for job {job_id}: {str(e)}")
                                raise
                        else:
                            logger.error(f"No output images found in job result for {comfyui_job_id}")
                            # Continue waiting as the job might still be processing
                    else:
                        # Outputs not ready yet, continue waiting
                        pass
                else:
                    # Job not in history yet, continue waiting
                    pass
            except Exception as e:
                logger.error(f"Error checking ComfyUI job status for {comfyui_job_id}: {str(e)}")
                # Continue waiting as this might be a temporary issue
            
            # Wait before checking again
            await asyncio.sleep(settings.COMFYUI_POLL_INTERVAL)
        
        raise Exception("ComfyUI job timeout")