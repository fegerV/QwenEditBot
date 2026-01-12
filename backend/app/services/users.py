import logging
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..models import User

logger = logging.getLogger(__name__)


def get_user_by_any_id(db: Session, user_id: int) -> Optional[User]:
    """Find user by either internal user_id or telegram_id.

    The bot currently uses Telegram user id as the main identifier.
    To be resilient to older databases, we search both columns.
    """

    return (
        db.query(User)
        .filter(or_(User.user_id == user_id, User.telegram_id == user_id))
        .first()
    )


def get_user_or_404(db: Session, user_id: int) -> User:
    user = get_user_by_any_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
