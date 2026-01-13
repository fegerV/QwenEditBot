from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class JobStatus(str, Enum):
    queued = "queued"
    processing = "processing"
    completed = "completed"
    failed = "failed"

class PaymentStatus(str, Enum):
    pending = "pending"
    succeeded = "succeeded"
    failed = "failed"
    cancelled = "cancelled"

class PaymentType(str, Enum):
    payment = "payment"
    weekly_bonus = "weekly_bonus"
    refund = "refund"

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
    retry_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class JobUpdate(BaseModel):
    status: JobStatus
    result_path: Optional[str] = None
    error: Optional[str] = None
    retry_count: Optional[int] = None

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

# New Payment schemas for YuKassa integration
class PaymentCreate(BaseModel):
    user_id: int
    amount: int  # in rubles
    payment_method: Optional[str] = "card"

class PaymentResponse(BaseModel):
    id: int
    user_id: int
    yukassa_payment_id: Optional[str] = None
    amount: int  # in kopeks
    currency: str
    status: PaymentStatus
    payment_type: PaymentType
    payment_method: Optional[str] = "card"
    payment_method_details: Optional[str] = None
    description: Optional[str] = None
    confirmation_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    paid_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class PaymentHistoryResponse(BaseModel):
    payments: List[PaymentResponse]
    total: int
    limit: int
    offset: int

# YuKassa webhook schema
class YuKassaWebhookObject(BaseModel):
    id: str
    status: str
    amount: dict
    currency: str
    created_at: str
    paid_at: Optional[str] = None

class YuKassaWebhook(BaseModel):
    type: str
    event: str
    object: YuKassaWebhookObject

# Telegram webhook schema
class TelegramWebhook(BaseModel):
    update_id: int
    message: Optional[dict] = None
    callback_query: Optional[dict] = None