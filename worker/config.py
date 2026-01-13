from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """Worker configuration settings"""

    # Backend API configuration
    BACKEND_API_URL: str = Field("http://localhost:8000", env="BACKEND_API_URL")
    BACKEND_API_TIMEOUT: int = Field(60, env="BACKEND_API_TIMEOUT")

    # Redis configuration
    REDIS_HOST: str = Field("localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(6379, env="REDIS_PORT")
    REDIS_PASSWORD: str = Field("", env="REDIS_PASSWORD")
    REDIS_DB: int = Field(0, env="REDIS_DB")
    REDIS_JOB_QUEUE_KEY: str = Field("qwenedit:job_queue", env="REDIS_JOB_QUEUE_KEY")
    REDIS_RESULT_TTL: int = Field(3600, env="REDIS_RESULT_TTL")  # 1 hour

    # ComfyUI configuration
    COMFYUI_URL: str = Field("http://127.0.0.1:8500", env="COMFYUI_URL")
    COMFYUI_TIMEOUT: int = Field(300, env="COMFYUI_TIMEOUT")
    COMFYUI_POLL_INTERVAL: float = Field(0.5, env="COMFYUI_POLL_INTERVAL")
    COMFYUI_INPUT_DIR: str = Field("C:/ComfyUI/input", env="COMFYUI_INPUT_DIR")
    COMFYUI_OUTPUT_DIR: str = Field("C:/ComfyUI/output", env="COMFYUI_OUTPUT_DIR")

    # Telegram configuration
    BOT_TOKEN: str = Field(..., env="BOT_TOKEN")
    TELEGRAM_API_URL: str = Field("https://api.telegram.org", env="TELEGRAM_API_URL")

    # Worker configuration
    WORKER_POLLING_INTERVAL: int = Field(2, env="WORKER_POLLING_INTERVAL")
    WORKER_GPU_LOCK_TIMEOUT: int = Field(30, env="WORKER_GPU_LOCK_TIMEOUT")
    WORKER_LOG_LEVEL: str = Field("INFO", env="WORKER_LOG_LEVEL")

    # Retry configuration
    MAX_RETRIES: int = Field(3, env="MAX_RETRIES")
    RETRY_DELAYS: str = Field("5,10,20", env="RETRY_DELAYS")  # comma-separated seconds

    # Results configuration
    RESULTS_DIR: str = Field("C:/QwenEditBot/data/outputs", env="RESULTS_DIR")

    # QwenEdit 2511 configuration
    QWEN_EDIT_VAE_NAME: str = Field("qwen_image_vae.safetensors", env="QWEN_EDIT_VAE_NAME")
    QWEN_EDIT_UNET_NAME: str = Field("qwen_image_edit_2511_fp8mixed.safetensors", env="QWEN_EDIT_UNET_NAME")
    QWEN_EDIT_CLIP_NAME: str = Field("qwen_2.5_vl_7b_fp8_scaled.safetensors", env="QWEN_EDIT_CLIP_NAME")
    QWEN_EDIT_LORA_NAME: str = Field("Qwen-Image-Edit-2511-Lightning-4steps-V1.0-bf16.safetensors", env="QWEN_EDIT_LORA_NAME")
    QWEN_EDIT_SCALE_MEGAPIXELS: int = Field(2, env="QWEN_EDIT_SCALE_MEGAPIXELS")
    QWEN_EDIT_STEPS: int = Field(4, env="QWEN_EDIT_STEPS")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# Create settings instance
settings = Settings()

# Ensure directories exist
def ensure_directories():
    results_dir = Path(settings.RESULTS_DIR)
    if not results_dir.exists():
        results_dir.mkdir(parents=True, exist_ok=True)
    
    input_dir = Path(settings.COMFYUI_INPUT_DIR)
    if not input_dir.exists():
        input_dir.mkdir(parents=True, exist_ok=True)
    
    output_dir = Path(settings.COMFYUI_OUTPUT_DIR)
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)


# Initialize directories
ensure_directories()