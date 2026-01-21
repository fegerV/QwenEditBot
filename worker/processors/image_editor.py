import asyncio
import logging
from pathlib import Path

import aiohttp

from worker.config import settings
from worker.job_queue.job_queue import Job
from worker.services.comfyui_client import ComfyUIClient
from worker.workflows.qwen_edit_2511 import build_workflow

logger = logging.getLogger(__name__)


class ImageEditorProcessor:
    """Image processor through ComfyUI."""

    def __init__(self):
        self.comfyui_client = ComfyUIClient()

    async def process(self, job: Job) -> str:
        """Process a job via ComfyUI and return a local path to the result image."""

        source_path = Path(job.image_path)
        second_path = Path(job.second_image_path) if job.second_image_path else None

        workflow_type = "try-on" if second_path else "standard"
        logger.info(f"Processing job {job.id} (workflow: {workflow_type})")

        cleanup_paths = [source_path]
        if second_path:
            cleanup_paths.append(second_path)

        try:
            if not source_path.exists():
                raise Exception(f"Source image does not exist: {source_path}")

            if second_path and not second_path.exists():
                raise Exception(f"Second image does not exist: {second_path}")

            workflow = build_workflow(job)
            logger.debug(f"Workflow prepared for job {job.id}")

            comfyui_job_id = await self.comfyui_client.send_workflow(workflow)
            logger.info(f"ComfyUI job {comfyui_job_id} created for job {job.id}")

            result_path = await self._wait_and_download(comfyui_job_id, job.id)
            logger.info(f"Result saved to {result_path}")

        except Exception as e:
            logger.error(f"Error processing job {job.id}: {str(e)}")
            raise

        # Clean up input files only after a successful run.
        # This is important because the worker can re-queue jobs for retry on failures.
        for path in cleanup_paths:
            try:
                path.unlink()
                logger.debug(f"Cleaned up input file: {path}")
            except FileNotFoundError:
                pass
            except Exception as e:
                logger.warning(f"Failed to clean up input file {path}: {str(e)}")

        return str(result_path)

    async def _wait_and_download(self, comfyui_job_id: str, job_id: int) -> Path:
        """Wait for result and download."""

        max_attempts = 600  # 600 * 0.5s = 300s = 5 minutes

        for _attempt in range(max_attempts):
            try:
                history = await self.comfyui_client.get_history(comfyui_job_id)

                if history and isinstance(history, dict) and comfyui_job_id in history:
                    job_result = history[comfyui_job_id]

                    if job_result and "outputs" in job_result:
                        output_image_info = None

                        for _node_id, node_output in job_result["outputs"].items():
                            if "images" in node_output and len(node_output["images"]) > 0:
                                output_image_info = node_output["images"][0]
                                break

                        if output_image_info:
                            filename = output_image_info["filename"]
                            subfolder = output_image_info.get("subfolder", "")
                            image_type = output_image_info.get("type", "output")

                            download_url = (
                                f"{self.comfyui_client.base_url}/view"
                                f"?filename={filename}&subfolder={subfolder}&type={image_type}"
                            )

                            async with aiohttp.ClientSession(
                                timeout=self.comfyui_client.timeout
                            ) as session:
                                async with session.get(download_url) as img_response:
                                    if img_response.status == 200:
                                        result_data = await img_response.read()

                                        results_dir = Path(settings.RESULTS_DIR)
                                        result_filename = f"job_{job_id}_result.png"
                                        result_path = results_dir / result_filename

                                        with open(result_path, "wb") as f:
                                            f.write(result_data)

                                        logger.info(
                                            f"Successfully downloaded and saved result for job {job_id}"
                                        )
                                        return result_path

                                    error_text = await img_response.text()
                                    logger.error(
                                        f"Failed to download result image: {img_response.status} - {error_text}"
                                    )
                                    raise Exception(
                                        f"Failed to download result image: {img_response.status}"
                                    )

            except Exception as e:
                logger.error(
                    f"Error checking ComfyUI job status for {comfyui_job_id}: {str(e)}"
                )

            await asyncio.sleep(settings.COMFYUI_POLL_INTERVAL)

        raise Exception("ComfyUI job timeout")
