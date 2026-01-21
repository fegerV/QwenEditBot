from pathlib import Path

from worker.config import settings
from worker.job_queue.job_queue import Job


def build_workflow(job: Job) -> dict:
    """Build ComfyUI workflow for Qwen Image Edit 2511.

    Notes:
    - Primary (single) image is always loaded in node 41.
    - In try-on mode the second image is loaded in node 83.
    - Workflow supports up to 3 reference images (image1/image2/image3).
    """

    input_filename = Path(job.image_path).name

    second_filename = (
        Path(job.second_image_path).name if job.second_image_path else input_filename
    )

    # We currently don't pass a dedicated third image from the bot.
    # Keep it equal to image1 to satisfy the workflow input contract.
    third_filename = input_filename

    scale_megapixels = settings.QWEN_EDIT_SCALE_MEGAPIXELS
    steps = settings.QWEN_EDIT_STEPS

    workflow_json = {
        "10": {
            "inputs": {"vae_name": settings.QWEN_EDIT_VAE_NAME},
            "class_type": "VAELoader",
            "_meta": {"title": "Load VAE"},
        },
        "12": {
            "inputs": {"unet_name": settings.QWEN_EDIT_UNET_NAME, "weight_dtype": "default"},
            "class_type": "UNETLoader",
            "_meta": {"title": "Load Diffusion Model"},
        },
        "41": {
            "inputs": {"image": input_filename},
            "class_type": "LoadImage",
            "_meta": {"title": "Load Image"},
        },
        "83": {
            "inputs": {"image": second_filename},
            "class_type": "LoadImage",
            "_meta": {"title": "Load Image"},
        },
        "87": {
            "inputs": {"image": third_filename},
            "class_type": "LoadImage",
            "_meta": {"title": "Load Image"},
        },
        "61": {
            "inputs": {"clip_name": settings.QWEN_EDIT_CLIP_NAME, "type": "qwen_image", "device": "default"},
            "class_type": "CLIPLoader",
            "_meta": {"title": "Load CLIP"},
        },
        "74": {
            "inputs": {
                "lora_name": settings.QWEN_EDIT_LORA_NAME,
                "strength_model": 1,
                "model": ["12", 0],
            },
            "class_type": "LoraLoaderModelOnly",
            "_meta": {"title": "LoraLoaderModelOnly"},
        },
        "67": {
            "inputs": {"shift": 3.1, "model": ["74", 0]},
            "class_type": "ModelSamplingAuraFlow",
            "_meta": {"title": "ModelSamplingAuraFlow"},
        },
        "64": {
            "inputs": {"strength": 1, "model": ["67", 0]},
            "class_type": "CFGNorm",
            "_meta": {"title": "CFGNorm"},
        },
        "79": {
            "inputs": {
                "upscale_method": "lanczos",
                "megapixels": scale_megapixels,
                "resolution_steps": 1,
                "image": ["41", 0],
            },
            "class_type": "ImageScaleToTotalPixels",
            "_meta": {"title": "ImageScaleToTotalPixels"},
        },
        "75": {
            "inputs": {"pixels": ["79", 0], "vae": ["10", 0]},
            "class_type": "VAEEncode",
            "_meta": {"title": "VAE Encode"},
        },
        "68": {
            "inputs": {
                "prompt": job.prompt,
                "clip": ["61", 0],
                "vae": ["10", 0],
                "image1": ["79", 0],
                "image2": ["83", 0],
                "image3": ["87", 0],
            },
            "class_type": "TextEncodeQwenImageEditPlus",
            "_meta": {"title": "TextEncodeQwenImageEditPlus (Positive)"},
        },
        "69": {
            "inputs": {
                "prompt": "",
                "clip": ["61", 0],
                "vae": ["10", 0],
                "image1": ["79", 0],
                "image2": ["83", 0],
                "image3": ["87", 0],
            },
            "class_type": "TextEncodeQwenImageEditPlus",
            "_meta": {"title": "TextEncodeQwenImageEditPlus"},
        },
        "70": {
            "inputs": {"reference_latents_method": "index_timestep_zero", "conditioning": ["68", 0]},
            "class_type": "FluxKontextMultiReferenceLatentMethod",
            "_meta": {"title": "Edit Model Reference Method"},
        },
        "71": {
            "inputs": {"reference_latents_method": "index_timestep_zero", "conditioning": ["69", 0]},
            "class_type": "FluxKontextMultiReferenceLatentMethod",
            "_meta": {"title": "Edit Model Reference Method"},
        },
        "65": {
            "inputs": {
                "seed": 0,
                "steps": steps,
                "cfg": 1,
                "sampler_name": "euler",
                "scheduler": "simple",
                "denoise": 1,
                "model": ["64", 0],
                "positive": ["70", 0],
                "negative": ["71", 0],
                "latent_image": ["75", 0],
            },
            "class_type": "KSampler",
            "_meta": {"title": "KSampler"},
        },
        "8": {
            "inputs": {"samples": ["65", 0], "vae": ["10", 0]},
            "class_type": "VAEDecode",
            "_meta": {"title": "VAE Decode"},
        },
        "9": {
            "inputs": {"filename_prefix": f"job_{job.id}_result", "images": ["8", 0]},
            "class_type": "SaveImage",
            "_meta": {"title": "Save Image"},
        },
    }

    return workflow_json
