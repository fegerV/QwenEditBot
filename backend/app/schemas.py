from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class JobStatus(str, Enum):
    queued = "queued"
    processing = "processing"
    completed = "completed"
    failed = "failed"

# User schemas
class UserBase(BaseModel):
    telegram_id: int
    username: str

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    user_id: int
    balance: float
    created_at: datetime
    
    class Config:
        from_attributes = True

# Preset schemas
class PresetBase(BaseModel):
    category: str
    name: str
    prompt: str
    icon: str
    price: float = 30.0
    order: int = 0

class PresetCreate(PresetBase):
    pass

class PresetResponse(PresetBase):
    id: int
    
    class Config:
        from_attributes = True

# Job schemas
class JobBase(BaseModel):
    user_id: int
    image_path: str
    prompt: str

class JobCreate(JobBase):
    pass

class JobResponse(JobBase):
    id: int
    status: JobStatus
    result_path: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class JobUpdate(BaseModel):
    status: JobStatus
    result_path: Optional[str] = None
    error: Optional[str] = None

# Balance schemas
class BalanceResponse(BaseModel):
    user_id: int
    balance: float
    
    class Config:
        from_attributes = True

class BalanceCheck(BaseModel):
    required_points: float

class BalanceOperation(BaseModel):
    points: float
    reason: str

# Payment schemas
class PaymentLogBase(BaseModel):
    user_id: int
    amount: float
    status: str
    payment_id: str

class PaymentLogCreate(PaymentLogBase):
    pass

class PaymentLogResponse(PaymentLogBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Telegram webhook schema
class TelegramWebhook(BaseModel):
    update_id: int
    message: Optional[dict] = None
    callback_query: Optional[dict] = None