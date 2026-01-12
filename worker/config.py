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

    # ComfyUI configuration
    COMFYUI_URL: str = Field("http://127.0.0.1:8188", env="COMFYUI_URL")
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
    RESULTS_DIR: str = Field("./results", env="RESULTS_DIR")

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