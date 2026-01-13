from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    # Bot configuration
    BOT_TOKEN: str = Field(..., env="BOT_TOKEN")
    
    # ComfyUI configuration
    COMFYUI_URL: str = Field("http://127.0.0.1:8188", env="COMFYUI_URL")
    COMFY_INPUT_DIR: str = Field("C:/ComfyUI/input", env="COMFY_INPUT_DIR")
    COMFYUI_TIMEOUT: int = Field(300, env="COMFYUI_TIMEOUT")
    COMFYUI_HEALTH_CHECK_INTERVAL: int = Field(10, env="COMFYUI_HEALTH_CHECK_INTERVAL")
    COMFY_OUTPUT_FILENAME: str = Field("qwen_result.png", env="COMFY_OUTPUT_FILENAME")
    
    # Database configuration
    DATABASE_URL: str = Field("sqlite:///./qwen.db", env="DATABASE_URL")
    
    # Backend configuration
    BACKEND_URL: str = Field("http://localhost:8000", env="BACKEND_URL")
    
    # Balance configuration
    INITIAL_BALANCE: int = Field(60, env="INITIAL_BALANCE")
    EDIT_COST: int = Field(30, env="EDIT_COST")
    WEEKLY_BONUS: int = Field(10, env="WEEKLY_BONUS")
    
    # Payment configuration
    YUKASSA_SHOP_ID: Optional[str] = Field(None, env="YUKASSA_SHOP_ID")
    YUKASSA_API_KEY: Optional[str] = Field(None, env="YUKASSA_API_KEY")
    YUKASSA_WEBHOOK_SECRET: Optional[str] = Field(None, env="YUKASSA_WEBHOOK_SECRET")
    PAYMENT_MIN_AMOUNT: int = Field(1, env="PAYMENT_MIN_AMOUNT")  # rubles
    PAYMENT_MAX_AMOUNT: int = Field(10000, env="PAYMENT_MAX_AMOUNT")  # rubles
    PAYMENT_RETURN_URL: str = Field("https://t.me/YourBotUsername", env="PAYMENT_RETURN_URL")
    POINTS_PER_RUBLE: int = Field(100, env="POINTS_PER_RUBLE")
    
    # Rate limiting configuration
    RATE_LIMIT_ENABLED: bool = Field(True, env="RATE_LIMIT_ENABLED")
    PAYMENT_RATE_LIMIT: str = Field("5/minute", env="PAYMENT_RATE_LIMIT")  # 5 payments per minute per user
    
    # Weekly bonus configuration
    WEEKLY_BONUS_ENABLED: bool = Field(True, env="WEEKLY_BONUS_ENABLED")
    WEEKLY_BONUS_AMOUNT: int = Field(10, env="WEEKLY_BONUS_AMOUNT")  # points
    WEEKLY_BONUS_DAY: int = Field(4, env="WEEKLY_BONUS_DAY")  # 0=Monday, 4=Friday
    WEEKLY_BONUS_TIME: str = Field("20:00", env="WEEKLY_BONUS_TIME")  # HH:MM UTC
    
    # QwenEdit 2511 configuration
    QWEN_EDIT_VAE_NAME: str = Field("qwen_image_vae.safetensors", env="QWEN_EDIT_VAE_NAME")
    QWEN_EDIT_UNET_NAME: str = Field("qwen_image_edit_2511_fp8mixed.safetensors", env="QWEN_EDIT_UNET_NAME")
    QWEN_EDIT_CLIP_NAME: str = Field("qwen_2.5_vl_7b_fp8_scaled.safetensors", env="QWEN_EDIT_CLIP_NAME")
    QWEN_EDIT_LORA_NAME: str = Field("Qwen-Image-Edit-2511-Lightning-4steps-V1.0-bf16.safetensors", env="QWEN_EDIT_LORA_NAME")
    QWEN_EDIT_SCALE_MEGAPIXELS: int = Field(2, env="QWEN_EDIT_SCALE_MEGAPIXELS")
    QWEN_EDIT_STEPS: int = Field(4, env="QWEN_EDIT_STEPS")
    
    # Security
    SECRET_KEY: str = Field("dev-secret-key-change-in-production", env="SECRET_KEY")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

# Create settings instance
settings = Settings()

# Ensure directories exist
def ensure_directories():
    input_dir = Path(settings.COMFY_INPUT_DIR)
    if not input_dir.exists():
        input_dir.mkdir(parents=True, exist_ok=True)

# Initialize directories
ensure_directories()