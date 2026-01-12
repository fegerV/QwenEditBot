"""Payment API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..schemas import PaymentCreate, PaymentResponse, PaymentHistoryResponse
from ..services.payment_service import PaymentService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/create", response_model=PaymentResponse)
async def create_payment(
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
        payment_service = PaymentService(db)
        payment = await payment_service.create_payment(
            user_id=payment_data.user_id,
            amount=payment_data.amount
        )
        
        return PaymentResponse.model_validate(payment)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating payment: {e}")
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
