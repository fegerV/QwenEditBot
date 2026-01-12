from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..database import get_db
from ..config import settings
from ..services.users import get_user_by_any_id
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user with initial balance"""
    try:
        existing_user = db.query(models.User).filter(models.User.telegram_id == user.telegram_id).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this telegram_id already exists"
            )

        # The bot uses Telegram user id as the main identifier.
        # To keep the rest of the API consistent, we also set user_id = telegram_id.
        new_user = models.User(
            user_id=user.telegram_id,
            telegram_id=user.telegram_id,
            username=user.username,
            balance=settings.INITIAL_BALANCE,
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        logger.info(f"User registered: {new_user.user_id}")
        return new_user

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error registering user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registering user: {str(e)}"
        )

@router.get("/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user information"""
    try:
        user = get_user_by_any_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting user: {str(e)}"
        )

@router.get("/{user_id}/balance", response_model=schemas.BalanceResponse)
def get_user_balance(user_id: int, db: Session = Depends(get_db)):
    """Get user balance"""
    try:
        user = get_user_by_any_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return {"user_id": user.user_id, "balance": user.balance}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user balance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting user balance: {str(e)}"
        )