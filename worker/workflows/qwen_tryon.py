"""QwenEdit 2511 workflow for try-on (fitting room) with TWO images"""

from worker.job_queue.job_queue import Job
from worker.config import settings
from pathlib import Path

def build_tryon_workflow(job: Job) -> dict:
    """
    QwenEdit 2511 workflow for try-on (fitting room) with TWO images.
    
    Image 1 (Node 41): User photo (person to dress)
    Image 2 (Node 42): Clothing photo (clothing item to apply)
    
    Args:
        job: Job object containing prompt, id, and TWO image paths
    
    Returns:
        Dictionary representing the QwenEdit 2511 ComfyUI workflow for try-on
    """
    if not job.second_image_path:
        raise ValueError("Try-on workflow requires second_image_path (clothing photo)")
    
    # Extract just the filenames from the paths
    first_image_filename = Path(job.image_path).name
    second_image_filename = Path(job.second_image_path).name
    
    # Workflow parameters
    scale_megapixels = settings.QWEN_EDIT_SCALE_MEGAPIXELS
    steps = settings.QWEN_EDIT_STEPS
    
    # Try-on workflow with TWO LoadImage nodes
    workflow_json = {
        "10": {
            "inputs": {
                "vae_name": settings.QWEN_EDIT_VAE_NAME
            },
            "class_type": "VAELoader",
            "_meta": {
                "title": "Load VAE"
            }
        },
        "12": {
            "inputs": {
                "unet_name": settings.QWEN_EDIT_UNET_NAME,
                "weight_dtype": "default"
            },
            "class_type": "UNETLoader",
            "_meta": {
                "title": "Load Diffusion Model"
            }
        },
        "41": {
            "inputs": {
                "image": first_image_filename
            },
            "class_type": "LoadImage",
            "_meta": {
                "title": "Load Image 1 (User)"
            }
        },
        "42": {
            "inputs": {
                "image": second_image_filename
            },
            "class_type": "LoadImage",
            "_meta": {
                "title": "Load Image 2 (Clothing)"
            }
        },
        "61": {
            "inputs": {
                "clip_name": settings.QWEN_EDIT_CLIP_NAME,
                "type": "qwen_image",
                "device": "default"
            },
            "class_type": "CLIPLoader",
            "_meta": {
                "title": "Load CLIP"
            }
        },
        "64": {
            "inputs": {
                "strength": 1,
                "model": [
                    "67",
                    0
                ]
            },
            "class_type": "CFGNorm",
            "_meta": {
                "title": "CFGNorm"
            }
        },
        "65": {
            "inputs": {
                "seed": 0,
                "steps": steps,
                "cfg": 1,
                "sampler_name": "euler",
                "scheduler": "simple",
                "denoise": 1,
                "model": [
                    "64",
                    0
                ],
                "positive": [
                    "70",
                    0
                ],
                "negative": [
                    "71",
                    0
                ],
                "latent_image": [
                    "75",
                    0
                ]
            },
            "class_type": "KSampler",
            "_meta": {
                "title": "KSampler"
            }
        },
        "67": {
            "inputs": {
                "shift": 3.1,
                "model": [
                    "74",
                    0
                ]
            },
            "class_type": "ModelSamplingAuraFlow",
            "_meta": {
                "title": "ModelSamplingAuraFlow"
            }
        },
        "68": {
            "inputs": {
                "prompt": job.prompt,
                "clip": [
                    "61",
                    0
                ],
                "vae": [
                    "10",
                    0
                ],
                "image1": [
                    "79",
                    0
                ],
                "image2": [
                    "80",
                    0
                ]
            },
            "class_type": "TextEncodeQwenImageEditPlus",
            "_meta": {
                "title": "TextEncodeQwenImageEditPlus (Positive) - Two Images"
            }
        },
        "69": {
            "inputs": {
                "prompt": "",
                "clip": [
                    "61",
                    0
                ],
                "vae": [
                    "10",
                    0
                ],
                "image1": [
                    "79",
                    0
                ],
                "image2": [
                    "80",
                    0
                ]
            },
            "class_type": "TextEncodeQwenImageEditPlus",
            "_meta": {
                "title": "TextEncodeQwenImageEditPlus (Negative) - Two Images"
            }
        },
        "70": {
            "inputs": {
                "reference_latents_method": "index_timestep_zero",
                "conditioning": [
                    "68",
                    0
                ]
            },
            "class_type": "FluxKontextMultiReferenceLatentMethod",
            "_meta": {
                "title": "Edit Model Reference Method"
            }
        },
        "71": {
            "inputs": {
                "reference_latents_method": "index_timestep_zero",
                "conditioning": [
                    "69",
                    0
                ]
            },
            "class_type": "FluxKontextMultiReferenceLatentMethod",
            "_meta": {
                "title": "Edit Model Reference Method"
            }
        },
        "74": {
            "inputs": {
                "lora_name": settings.QWEN_EDIT_LORA_NAME,
                "strength_model": 1,
                "model": [
                    "12",
                    0
                ]
            },
            "class_type": "LoraLoaderModelOnly",
            "_meta": {
                "title": "LoraLoaderModelOnly"
            }
        },
        "75": {
            "inputs": {
                "pixels": [
                    "79",
                    0
                ],
                "vae": [
                    "10",
                    0
                ]
            },
            "class_type": "VAEEncode",
            "_meta": {
                "title": "VAE Encode (First Image)"
            }
        },
        "79": {
            "inputs": {
                "upscale_method": "lanczos",
                "megapixels": scale_megapixels,
                "resolution_steps": 1,
                "image": [
                    "41",
                    0
                ]
            },
            "class_type": "ImageScaleToTotalPixels",
            "_meta": {
                "title": "ImageScaleToTotalPixels (First Image)"
            }
        },
        "80": {
            "inputs": {
                "upscale_method": "lanczos",
                "megapixels": scale_megapixels,
                "resolution_steps": 1,
                "image": [
                    "42",
                    0
                ]
            },
            "class_type": "ImageScaleToTotalPixels",
            "_meta": {
                "title": "ImageScaleToTotalPixels (Second Image)"
            }
        },
        "8": {
            "inputs": {
                "samples": [
                    "65",
                    0
                ],
                "vae": [
                    "10",
                    0
                ]
            },
            "class_type": "VAEDecode",
            "_meta": {
                "title": "VAE Decode"
            }
        },
        "9": {
            "inputs": {
                "filename_prefix": f"job_{job.id}_tryon_result",
                "images": [
                    "8",
                    0
                ]
            },
            "class_type": "SaveImage",
            "_meta": {
                "title": "Save Image"
            }
        }
    }

    return workflow_json
