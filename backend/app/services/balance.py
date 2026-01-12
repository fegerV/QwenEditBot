from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import logging

from ..models import User
from .users import get_user_by_any_id

logger = logging.getLogger(__name__)

def check_balance(user_id: int, required_points: float, db: Session) -> bool:
    """Check if user has sufficient balance"""
    try:
        user = get_user_by_any_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        has_sufficient = user.balance >= required_points
        logger.info(f"Balance check for user {user_id}: required={required_points}, available={user.balance}, sufficient={has_sufficient}")
        return has_sufficient
        
    except Exception as e:
        logger.error(f"Error checking balance: {e}")
        raise

def deduct_balance(user_id: int, points: float, reason: str, db: Session) -> float:
    """Deduct points from user balance"""
    try:
        user = get_user_by_any_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if user.balance < points:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Insufficient balance: {user.balance} < {points}"
            )
        
        user.balance -= points
        db.commit()
        logger.info(f"Balance deducted: user={user_id}, points={points}, reason={reason}, new_balance={user.balance}")
        return user.balance
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deducting balance: {e}")
        raise

def refund_balance(user_id: int, points: float, reason: str, db: Session) -> float:
    """Refund points to user balance"""
    try:
        user = get_user_by_any_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        user.balance += points
        db.commit()
        logger.info(f"Balance refunded: user={user_id}, points={points}, reason={reason}, new_balance={user.balance}")
        return user.balance
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error refunding balance: {e}")
        raise

def add_balance(user_id: int, points: float, reason: str, db: Session) -> float:
    """Add points to user balance (Admin only)"""
    try:
        user = get_user_by_any_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        user.balance += points
        db.commit()
        logger.info(f"Balance added: user={user_id}, points={points}, reason={reason}, new_balance={user.balance}")
        return user.balance
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding balance: {e}")
        raise