"""Payment API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..schemas import PaymentCreate, PaymentResponse, PaymentHistoryResponse
from ..services.payment_service import PaymentService
from ..config import settings
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from redis_client import redis_client
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging

logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
router = APIRouter()

# Add rate limit exceeded handler
from fastapi import FastAPI

# Create a FastAPI app instance just for the exception handler
app_for_exception = FastAPI()

@app_for_exception.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    logger.warning(f"Rate limit exceeded for {get_remote_address(request)}: {exc.detail}")
    return HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail=f"Too many requests. Please try again in {exc.detail['X-RateLimit-Reset']} seconds."
    )


@router.post("/create", response_model=PaymentResponse)
@limiter.limit(settings.PAYMENT_RATE_LIMIT if settings.RATE_LIMIT_ENABLED else "unlimited")
async def create_payment(
    request: Request,
    payment_data: PaymentCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new payment
    
    Creates a payment in YuKassa and returns the confirmation URL.
    
    Args:
        payment_data: Payment creation request with user_id and amount (in rubles)
        
    Returns:
        Payment object with confirmation_url for user to complete payment
    """
    try:
        logger.info(f"Payment creation request from {get_remote_address(request)}: user_id={payment_data.user_id}, amount={payment_data.amount} rubles, method={payment_data.payment_method}")
        
        payment_service = PaymentService(db)
        payment = await payment_service.create_payment(
            user_id=payment_data.user_id,
            amount=payment_data.amount,
            payment_method=payment_data.payment_method
        )
        
        logger.info(f"Payment creation successful for user {payment_data.user_id}: payment_id={payment.id}")
        
        return PaymentResponse.model_validate(payment)
        
    except ValueError as e:
        logger.warning(f"Payment creation failed for user {payment_data.user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating payment for user {payment_data.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create payment: {str(e)}"
        )


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int,
    db: Session = Depends(get_db)
):
    """
    Get payment status
    
    Returns the current status of a payment.
    
    Args:
        payment_id: Payment ID
        
    Returns:
        Payment object with current status
    """
    try:
        payment_service = PaymentService(db)
        payment = await payment_service.get_payment(payment_id)
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        
        return PaymentResponse.model_validate(payment)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting payment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get payment: {str(e)}"
        )


@router.get("/user/{user_id}", response_model=PaymentHistoryResponse)
async def get_user_payments(
    user_id: int,
    limit: int = 20,
    offset: int = 0,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get payment history for a user
    
    Returns a paginated list of payments for a user, optionally filtered by status.
    
    Args:
        user_id: User ID
        limit: Maximum number of payments to return (default: 20)
        offset: Offset for pagination (default: 0)
        status: Filter by payment status (optional)
        
    Returns:
        PaymentHistoryResponse with payments list and metadata
    """
    try:
        payment_service = PaymentService(db)
        history = await payment_service.get_user_payments(
            user_id=user_id,
            limit=limit,
            offset=offset,
            status=status
        )
        
        return history
        
    except Exception as e:
        logger.error(f"Error getting payment history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get payment history: {str(e)}"
        )
