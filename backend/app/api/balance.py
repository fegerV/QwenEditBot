from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..services.balance import check_balance, deduct_balance, refund_balance, add_balance
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from redis_client import redis_client
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/{user_id}", response_model=schemas.BalanceResponse)
def get_balance(user_id: int, db: Session = Depends(get_db)):
    """Get user balance"""
    try:
        user = db.query(models.User).filter(models.User.user_id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return {"user_id": user.user_id, "balance": user.balance}
    except Exception as e:
        logger.error(f"Error getting balance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting balance: {str(e)}"
        )

@router.post("/{user_id}/check", response_model=dict)
def check_user_balance(
    user_id: int,
    balance_check: schemas.BalanceCheck,
    db: Session = Depends(get_db)
):
    """Check if user has sufficient balance"""
    try:
        result = check_balance(user_id, balance_check.required_points, db)
        return {
            "has_sufficient_balance": result,
            "required": balance_check.required_points,
            "user_id": user_id
        }
    except Exception as e:
        logger.error(f"Error checking balance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking balance: {str(e)}"
        )

@router.post("/{user_id}/deduct", response_model=schemas.BalanceResponse)
def deduct_user_balance(
    user_id: int,
    balance_operation: schemas.BalanceOperation,
    db: Session = Depends(get_db)
):
    """Deduct points from user balance"""
    try:
        updated_balance = deduct_balance(
            user_id, 
            balance_operation.points, 
            balance_operation.reason, 
            db
        )
        return {"user_id": user_id, "balance": updated_balance}
    except Exception as e:
        db.rollback()
        logger.error(f"Error deducting balance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deducting balance: {str(e)}"
        )

@router.post("/{user_id}/refund", response_model=schemas.BalanceResponse)
def refund_user_balance(
    user_id: int,
    balance_operation: schemas.BalanceOperation,
    db: Session = Depends(get_db)
):
    """Refund points to user balance"""
    try:
        updated_balance = refund_balance(
            user_id, 
            balance_operation.points, 
            balance_operation.reason, 
            db
        )
        return {"user_id": user_id, "balance": updated_balance}
    except Exception as e:
        db.rollback()
        logger.error(f"Error refunding balance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error refunding balance: {str(e)}"
        )

@router.post("/{user_id}/add", response_model=schemas.BalanceResponse)
def add_user_balance(
    user_id: int,
    balance_operation: schemas.BalanceOperation,
    db: Session = Depends(get_db)
):
    """Add points to user balance (Admin only)"""
    try:
        updated_balance = add_balance(
            user_id, 
            balance_operation.points, 
            balance_operation.reason, 
            db
        )
        return {"user_id": user_id, "balance": updated_balance}
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding balance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding balance: {str(e)}"
        )