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