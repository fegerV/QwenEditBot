from sqlalchemy.orm import Session
from ..models import User
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)

def check_balance(user_id: int, required_points: float, db: Session) -> bool:
    """Check if user has sufficient balance"""
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if unlimited processing is enabled
        from ..config import settings
        if getattr(settings, 'UNLIMITED_PROCESSING', False):
            logger.info(f"Unlimited processing enabled: Balance check bypassed for user {user_id}")
            return True
        
        # Check if user is admin (admins always have sufficient balance)
        is_admin = user.telegram_id in getattr(settings, 'ADMIN_IDS', [])
        
        if is_admin:
            logger.info(f"Balance check passed for admin {user_id}: admins always have sufficient balance")
            return True

        has_sufficient = user.balance >= required_points
        logger.info(f"Balance check for user {user_id}: required={required_points}, available={user.balance}, sufficient={has_sufficient}")
        return has_sufficient
        
        # Original code (commented out for testing):
        # # Check if user is admin (admins always have sufficient balance)
        # from ..config import settings
        # is_admin = user.telegram_id in getattr(settings, 'ADMIN_IDS', [])
        #
        # if is_admin:
        #     logger.info(f"Balance check passed for admin {user_id}: admins always have sufficient balance")
        #     return True
        #
        # has_sufficient = user.balance >= required_points
        # logger.info(f"Balance check for user {user_id}: required={required_points}, available={user.balance}, sufficient={has_sufficient}")
        # return has_sufficient
        
    except Exception as e:
        logger.error(f"Error checking balance: {e}")
        raise

def deduct_balance(user_id: int, points: float, reason: str, db: Session) -> float:
    """Deduct points from user balance"""
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if unlimited processing is enabled
        from ..config import settings
        if getattr(settings, 'UNLIMITED_PROCESSING', False):
            logger.info(f"Unlimited processing enabled: Balance deduction skipped for user {user_id}: {points} points, reason: {reason}")
            return user.balance

        # Check if user is admin (admins don't pay)
        is_admin = user.telegram_id in getattr(settings, 'ADMIN_IDS', [])

        if is_admin:
            # Admins don't pay, return current balance
            logger.info(f"Balance deduction skipped for admin {user_id}: {points} points, reason: {reason}")
            return user.balance

        if user.balance < points:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Insufficient balance: {user.balance} < {points}"
            )

        user.balance -= points
        db.commit()
        logger.info(f"Balance deducted: user={user_id}, points={points}, reason={reason}, new_balance={user.balance}")
        return user.balance
        
        # Original code (commented out for testing):
        # # Check if user is admin (admins don't pay)
        # from ..config import settings
        # is_admin = user.telegram_id in getattr(settings, 'ADMIN_IDS', [])
        #
        # if is_admin:
        #     # Admins don't pay, return current balance
        #     logger.info(f"Balance deduction skipped for admin {user_id}: {points} points, reason: {reason}")
        #     return user.balance
        #
        # if user.balance < points:
        #     raise HTTPException(
        #         status_code=status.HTTP_402_PAYMENT_REQUIRED,
        #         detail=f"Insufficient balance: {user.balance} < {points}"
        #     )
        #
        # user.balance -= points
        # db.commit()
        # logger.info(f"Balance deducted: user={user_id}, points={points}, reason={reason}, new_balance={user.balance}")
        # return user.balance
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deducting balance: {e}")
        raise

def refund_balance(user_id: int, points: float, reason: str, db: Session) -> float:
    """Refund points to user balance"""
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if unlimited processing is enabled
        from ..config import settings
        if getattr(settings, 'UNLIMITED_PROCESSING', False):
            logger.info(f"Unlimited processing enabled: Balance refund skipped for user {user_id}: {points} points, reason: {reason}")
            return user.balance

        # Check if user is admin (admins don't need refunds since they don't pay)
        is_admin = user.telegram_id in getattr(settings, 'ADMIN_IDS', [])

        if is_admin:
            # Admins don't pay, so no need to refund
            logger.info(f"Balance refund skipped for admin {user_id}: {points} points, reason: {reason}")
            return user.balance

        user.balance += points
        db.commit()
        logger.info(f"Balance refunded: user={user_id}, points={points}, reason={reason}, new_balance={user.balance}")
        return user.balance
        
        # Original code (commented out for testing):
        # # Check if user is admin (admins don't need refunds since they don't pay)
        # from ..config import settings
        # is_admin = user.telegram_id in getattr(settings, 'ADMIN_IDS', [])
        #
        # if is_admin:
        #     # Admins don't pay, so no need to refund
        #     logger.info(f"Balance refund skipped for admin {user_id}: {points} points, reason: {reason}")
        #     return user.balance
        #
        # user.balance += points
        # db.commit()
        # logger.info(f"Balance refunded: user={user_id}, points={points}, reason={reason}, new_balance={user.balance}")
        # return user.balance
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error refunding balance: {e}")
        raise

def add_balance(user_id: int, points: float, reason: str, db: Session) -> float:
    """Add points to user balance (Admin only)"""
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
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