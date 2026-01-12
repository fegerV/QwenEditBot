from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base
from enum import Enum as PyEnum
import datetime

class JobStatus(str, PyEnum):
    queued = "queued"
    processing = "processing"
    completed = "completed"
    failed = "failed"

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    username = Column(String(100), index=True)
    balance = Column(Float, default=60.0)  # Initial balance
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    jobs = relationship("Job", back_populates="user")
    payment_logs = relationship("PaymentLog", back_populates="user")

class Preset(Base):
    __tablename__ = "presets"
    
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), index=True)
    name = Column(String(100), index=True)
    prompt = Column(Text)
    icon = Column(String(255))
    price = Column(Float, default=30.0)
    order = Column(Integer, default=0)

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    image_path = Column(String(255))
    prompt = Column(Text)
    status = Column(Enum(JobStatus), default=JobStatus.queued)
    result_path = Column(String(255))
    error = Column(Text)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="jobs")

class PaymentLog(Base):
    __tablename__ = "payment_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    amount = Column(Float)
    status = Column(String(50), default="pending")
    payment_id = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="payment_logs")