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


class PaymentStatus(str, Enum):
    pending = "pending"
    succeeded = "succeeded"
    failed = "failed"
    canceled = "canceled"


class PaymentType(str, Enum):
    payment = "payment"
    weekly_bonus = "weekly_bonus"
    refund = "refund"


class PaymentCreate(BaseModel):
    user_id: int
    amount: int = Field(..., description="Amount in RUB")


class PaymentCreateResponse(BaseModel):
    payment_id: int
    status: PaymentStatus
    confirmation_url: Optional[str] = None
    amount: int
    created_at: datetime


class PaymentResponse(BaseModel):
    id: int
    user_id: int
    type: PaymentType
    status: PaymentStatus
    amount: int
    confirmation_url: Optional[str] = None
    created_at: datetime
    paid_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PaymentHistoryItem(BaseModel):
    id: int
    amount: int
    status: PaymentStatus
    type: PaymentType
    created_at: datetime
    paid_at: Optional[datetime] = None


class PaymentHistoryResponse(BaseModel):
    payments: List[PaymentHistoryItem]
    total: int
    limit: int
    offset: int


# Telegram webhook schema
class TelegramWebhook(BaseModel):
    update_id: int
    message: Optional[dict] = None
    callback_query: Optional[dict] = None