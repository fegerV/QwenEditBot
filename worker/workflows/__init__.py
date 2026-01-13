"""Workflow factory for ComfyUI workflows"""

from typing import Dict, Any
from worker.queue.job_queue import Job
from .qwen_edit_2511 import get_qwen_edit_2511_workflow
from .standard import get_standard_workflow

def get_workflow(workflow_type: str, job: Job, workflow_config: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Factory function to get the appropriate workflow based on type
    
    Args:
        workflow_type: Type of workflow ('standard', 'qwen_edit_2511', etc.)
        job: Job object containing parameters like prompt, id, etc.
        workflow_config: Optional dictionary with workflow-specific parameters
    
    Returns:
        Dictionary representing the ComfyUI workflow
    """
    if workflow_type == "qwen_edit_2511":
        return get_qwen_edit_2511_workflow(job, workflow_config or {})
    else:
        # Default to standard workflow for backward compatibility
        return get_standard_workflow(job)
