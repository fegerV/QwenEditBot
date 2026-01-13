from pydantic_settings import BaseSettings
from pydantic import Field, AliasChoices
from typing import Optional


class Settings(BaseSettings):
    """Bot configuration settings"""

    # Bot token
    BOT_TOKEN: Optional[str] = Field(None, env="BOT_TOKEN")

    # Backend API configuration
    BACKEND_URL: str = Field(
        "http://localhost:8000",
        validation_alias=AliasChoices("BACKEND_URL", "BACKEND_API_URL"),
    )
    BACKEND_API_TIMEOUT: int = Field(30, env="BACKEND_API_TIMEOUT")

    # Telegram configuration
    TELEGRAM_WEBHOOK_URL: Optional[str] = Field(None, env="TELEGRAM_WEBHOOK_URL")
    
    # Balance configuration
    INITIAL_BALANCE: int = Field(60, env="INITIAL_BALANCE")
    EDIT_COST: int = Field(30, env="EDIT_COST")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# Create settings instance
settings = Settings()
