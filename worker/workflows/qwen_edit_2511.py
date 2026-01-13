"""QwenEdit 2511 workflow for comic style transformation"""

from worker.queue.job_queue import Job
from worker.config import settings

def build_workflow(job: Job) -> dict:
    """
    QwenEdit 2511 workflow for converting images to comic style with watermark removal
    
    Args:
        job: Job object containing prompt and id
    
    Returns:
        Dictionary representing the QwenEdit 2511 ComfyUI workflow
    """
    input_filename = f"job_{job.id}_input.png"
    
    # Hardcoded parameters for QwenEdit workflow
    scale_megapixels = 2
    steps = 20
    
    workflow = {
        "prompt": {
            "1": {
                "inputs": {
                    "vae_name": settings.QWEN_EDIT_VAE_NAME
                },
                "class_type": "VAELoader",
                "_meta": {
                    "title": "VAEloader"
                }
            },
            "2": {
                "inputs": {
                    "unet_name": settings.QWEN_EDIT_UNET_NAME,
                    "weight_dtype": "fp8_e4m3fn"
                },
                "class_type": "UNETLoader",
                "_meta": {
                    "title": "UNETLoader"
                }
            },
            "3": {
                "inputs": {
                    "clip_name": settings.QWEN_EDIT_CLIP_NAME,
                    "type": "qwen2_5_vl",
                    "device": "auto"
                },
                "class_type": "CLIPLoader",
                "_meta": {
                    "title": "CLIPLoader (Qwen2.5VL)"
                }
            },
            "4": {
                "inputs": {
                    "text": job.prompt,
                    "clip": ["3", 0]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {
                    "title": "CLIP Text Encode (Prompt)"
                }
            },
            "5": {
                "inputs": {
                    "lora_name": settings.QWEN_EDIT_LORA_NAME,
                    "strength": 1,
                    "unet": ["2", 0]
                },
                "class_type": "LoraLoader",
                "_meta": {
                    "title": "LoRALoader"
                }
            },
            "6": {
                "inputs": {
                    "image": input_filename
                },
                "class_type": "LoadImage",
                "_meta": {
                    "title": "Load Image"
                }
            },
            "7": {
                "inputs": {
                    "pixels": ["6", 0],
                    "vae": ["1", 0]
                },
                "class_type": "VAEEncode",
                "_meta": {
                    "title": "VAE Encode"
                }
            },
            "8": {
                "inputs": {
                    "samples": ["7", 0],
                    "scale_megapixels": scale_megapixels
                },
                "class_type": "QwenImageEditLatentProcessor",
                "_meta": {
                    "title": "QwenImageEditLatentProcessor"
                }
            },
            "9": {
                "inputs": {
                    "width": 1024,
                    "height": 1024,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage",
                "_meta": {
                    "title": "Empty Latent Image"
                }
            },
            "10": {
                "inputs": {
                    "seed": 0,
                    "steps": steps,
                    "cfg": 1,
                    "sampler_name": "euler_ancestral",
                    "scheduler": "normal",
                    "denoise": 1,
                    "model": ["5", 0],
                    "positive": ["4", 0],
                    "negative": ["4", 1],
                    "latent_image": ["8", 0]
                },
                "class_type": "KSampler",
                "_meta": {
                    "title": "KSampler"
                }
            },
            "11": {
                "inputs": {
                    "samples": ["10", 0],
                    "vae": ["1", 0]
                },
                "class_type": "VAEDecode",
                "_meta": {
                    "title": "VAE Decode"
                }
            },
            "12": {
                "inputs": {
                    "filename_prefix": f"job_{job.id}_result",
                    "images": ["11", 0]
                },
                "class_type": "SaveImage",
                "_meta": {
                    "title": "Save Image"
                }
            }
        },
        "output": ["12", 0]
    }
    
    return workflow