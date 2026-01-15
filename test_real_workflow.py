import requests
import json
import time
import uuid
from pathlib import Path

def test_real_workflow():
    """
    Тестирование отправки реального workflow в ComfyUI с правильными параметрами
    """
    # Параметры подключения к ComfyUI
    comfyui_url = "http://127.0.0.1:8188"
    
    # Проверяем подключение к ComfyUI
    try:
        print("Checking connection to ComfyUI...")
        response = requests.get(f"{comfyui_url}/system_stats", timeout=10)
        if response.status_code == 200:
            print("+ ComfyUI is available")
        else:
            print(f"- ComfyUI returned status {response.status_code}")
            return
    except Exception as e:
        print(f"- Failed to connect to ComfyUI: {e}")
        print("Make sure ComfyUI is running on port 8188")
        return

    # Проверяем наличие файлов в input директории
    input_dir = Path("C:/ComfyUIDesk/input")
    if not input_dir.exists():
        print(f"- Input directory does not exist: {input_dir}")
        return
    
    # Ищем файлы изображений в директории
    image_files = list(input_dir.glob("*.jpg")) + list(input_dir.glob("*.png"))
    if not image_files:
        print(f"- No image files found in {input_dir}")
        print("  Expected files like: input_*.jpg")
        return
    
    # Берем первый найденный файл
    image_file = image_files[0].name
    print(f"+ Found image file: {image_file}")

    # Реальный workflow из системы
    real_workflow = {
        "prompt": {
            "10": {
                "inputs": {
                    "vae_name": "qwen_image_vae.safetensors"
                },
                "class_type": "VAELoader",
                "_meta": {
                    "title": "Load VAE"
                }
            },
            "12": {
                "inputs": {
                    "unet_name": "qwen_image_edit_2511_fp8mixed.safetensors",
                    "weight_dtype": "default"
                },
                "class_type": "UNETLoader",
                "_meta": {
                    "title": "Load Diffusion Model"
                }
            },
            "41": {
                "inputs": {
                    "image": image_file  # Используем реальное имя файла
                },
                "class_type": "LoadImage",
                "_meta": {
                    "title": "Load Image"
                }
            },
            "61": {
                "inputs": {
                    "clip_name": "qwen_2.5_vl_7b_fp8_scaled.safetensors",
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
                    "steps": 4,
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
                    "prompt": "Test prompt for verification",
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
                    ]
                },
                "class_type": "TextEncodeQwenImageEditPlus",
                "_meta": {
                    "title": "TextEncodeQwenImageEditPlus (Positive)"
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
                    ]
                },
                "class_type": "TextEncodeQwenImageEditPlus",
                "_meta": {
                    "title": "TextEncodeQwenImageEditPlus"
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
                    "lora_name": "Qwen-Image-Edit-Lightning-4steps-V1.0-bf16.safetensors",
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
                    "title": "VAE Encode"
                }
            },
            "79": {
                "inputs": {
                    "upscale_method": "lanczos",
                    "megapixels": 2,
                    "resolution_steps": 1,
                    "image": [
                        "41",
                        0
                    ]
                },
                "class_type": "ImageScaleToTotalPixels",
                "_meta": {
                    "title": "ImageScaleToTotalPixels"
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
                    "filename_prefix": f"test_{int(time.time())}",
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
    }

    print("\nSending real job to ComfyUI...")
    
    try:
        # Отправляем workflow
        response = requests.post(
            f"{comfyui_url}/prompt",
            json=real_workflow,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            prompt_id = result.get("prompt_id")
            if prompt_id:
                print(f"+ Job successfully sent with ID: {prompt_id}")
                
                # Ждем выполнения задания
                print("Waiting for job completion...")
                max_wait_time = 300  # 5 minutes max wait time
                wait_time = 0
                
                while wait_time < max_wait_time:
                    try:
                        history_response = requests.get(f"{comfyui_url}/history/{prompt_id}")
                        
                        if history_response.status_code == 200:
                            history_data = history_response.json()
                            
                            if prompt_id in history_data:
                                job_result = history_data[prompt_id]
                                
                                if 'outputs' in job_result:
                                    print("+ Job completed successfully!")
                                    
                                    # Проверяем наличие изображений в результатах
                                    for node_id, node_output in job_result['outputs'].items():
                                        if 'images' in node_output:
                                            print(f"  - Found image: {node_output['images']}")
                                    
                                    return
                                else:
                                    print("  - Job still in progress...")
                            else:
                                print("  - Job info not yet available...")
                        else:
                            print(f"  - Error getting status: {history_response.status_code}")
                    
                    except Exception as e:
                        print(f"  - Error checking status: {e}")
                    
                    time.sleep(2)
                    wait_time += 2
                    
                    if wait_time >= max_wait_time:
                        print("- Maximum wait time exceeded for job completion")
                        return
                        
            else:
                print("- Response missing prompt_id")
                print(f"  Full response: {result}")
        else:
            print(f"- Error sending job: {response.status_code}")
            print(f"  Response body: {response.text}")
            
    except Exception as e:
        print(f"- Error interacting with ComfyUI: {e}")

if __name__ == "__main__":
    print("Testing real workflow in ComfyUI...")
    test_real_workflow()
    print("\nTesting completed.")