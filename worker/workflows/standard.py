"""Standard SD XL workflow for image editing"""

from worker.queue.job_queue import Job
from typing import Dict, Any

def get_standard_workflow(job: Job) -> Dict[str, Any]:
    """
    Standard SD XL workflow for basic image editing
    
    Args:
        job: Job object containing prompt, id, and other parameters
    
    Returns:
        Dictionary representing the standard ComfyUI workflow
    """
    input_filename = f"job_{job.id}_input.png"
    
    workflow = {
        "prompt": {
            "3": {
                "inputs": {
                    "text": job.prompt,
                    "clip": ["4", 0]
                },
                "class_type": "CLIPTextEncode"
            },
            "4": {
                "inputs": {
                    "ckpt_name": "sd_xl_base_1.0.safetensors"
                },
                "class_type": "CheckpointLoaderSimple"
            },
            "5": {
                "inputs": {
                    "image": f"{input_filename}",
                    "resize_mode": "0",
                    "crop_w": 1024,
                    "crop_h": 1024
                },
                "class_type": "LoadImage"
            },
            "6": {
                "inputs": {
                    "samples": ["7", 0],
                    "vae": ["4", 2]
                },
                "class_type": "VAEEncode"
            },
            "7": {
                "inputs": {
                    "positive": ["3", 0],
                    "negative": ["8", 0],
                    "empty_latent_image": ["5", 0],
                    "model": ["4", 0]
                },
                "class_type": "KSampler"
            },
            "8": {
                "inputs": {
                    "text": "bad quality, low quality",
                    "clip": ["4", 0]
                },
                "class_type": "CLIPTextEncode"
            },
            "9": {
                "inputs": {
                    "samples": ["7", 0],
                    "vae": ["4", 2]
                },
                "class_type": "VAEDecode"
            },
            "10": {
                "inputs": {
                    "filename_prefix": f"job_{job.id}_result",
                    "images": ["9", 0]
                },
                "class_type": "SaveImage"
            }
        },
        "output": ["10", 0]
    }
    
    return workflow