"""Promocode API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from .. import models, schemas
from ..database import get_db
from ..services.balance import add_balance

router = APIRouter()
logger = logging.getLogger(__name__)


def generate_promocode_code(length: int = 8) -> str:
    """Generate a random promocode"""
    import random
    import string
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


@router.post("/generate", response_model=schemas.PromocodeResponse)
def generate_promocode(
    amount: int,
    db: Session = Depends(get_db),
    custom_code: str = None
):
    """Generate a new promocode (for admin use)"""
    try:
        # Validate amount
        valid_amounts = [100, 200, 300, 400, 500, 1000, 2000, 3000, 5000]
        if amount not in valid_amounts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid amount. Must be one of: {valid_amounts}"
            )
        
        # Generate or use custom code
        if custom_code:
            # Check if code already exists
            existing = db.query(models.Promocode).filter(
                models.Promocode.code == custom_code.upper()
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Promocode with this code already exists"
                )
            code = custom_code.upper()
        else:
            # Generate unique code
            code = generate_promocode_code()
            while db.query(models.Promocode).filter(models.Promocode.code == code).first():
                code = generate_promocode_code()
        
        # Create promocode
        promocode = models.Promocode(
            code=code,
            amount=amount
        )
        db.add(promocode)
        db.commit()
        db.refresh(promocode)
        
        logger.info(f"Generated promocode: {code} for {amount} points")
        return promocode
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error generating promocode: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating promocode: {str(e)}"
        )


@router.post("/batch-generate")
def batch_generate_promocodes(
    amounts: dict,
    db: Session = Depends(get_db)
):
    """
    Generate multiple promocodes and save to file
    Request body: {"amounts": [100, 200, 300, ...]}
    Returns file path with all promocodes
    """
    try:
        import os
        
        promocodes_data = []
        valid_amounts = [100, 200, 300, 400, 500, 1000, 2000, 3000, 5000]
        
        # Validate all amounts
        for amount in amounts.get("amounts", []):
            if amount not in valid_amounts:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid amount: {amount}. Must be one of: {valid_amounts}"
                )
        
        # Generate promocodes
        for amount in amounts.get("amounts", []):
            code = generate_promocode_code()
            while db.query(models.Promocode).filter(models.Promocode.code == code).first():
                code = generate_promocode_code()
            
            promocode = models.Promocode(
                code=code,
                amount=amount
            )
            db.add(promocode)
            db.commit()
            db.refresh(promocode)
            
            promocodes_data.append({
                "code": code,
                "amount": amount,
                "created_at": promocode.created_at.isoformat()
            })
        
<<<<<<< Updated upstream
        # Save to file
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data")
=======
        # Save to file
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data")
>>>>>>> Stashed changes
        os.makedirs(data_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(data_dir, f"promocodes_{timestamp}.txt")
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"# Generated Promocodes - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Total: {len(promocodes_data)} promocodes\n")
            f.write(f"# Format: CODE - AMOUNT (points)\n\n")
            
            for pc in promocodes_data:
                f.write(f"{pc['code']} - {pc['amount']}\n")
        
        logger.info(f"Generated {len(promocodes_data)} promocodes, saved to {file_path}")
        
        return {
            "success": True,
            "count": len(promocodes_data),
            "file_path": file_path,
            "promocodes": promocodes_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error batch generating promocodes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating promocodes: {str(e)}"
        )


@router.post("/use", response_model=schemas.PromocodeUseResponse)
def use_promocode(
    promocode_data: schemas.PromocodeUse,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Use a promocode to add points to user balance"""
    try:
        # Get user
        user = db.query(models.User).filter(models.User.user_id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Find promocode
        promocode = db.query(models.Promocode).filter(
            models.Promocode.code == promocode_data.code.upper()
        ).first()
        
        if not promocode:
            return {
                "success": False,
                "message": "Промокод не найден"
            }
        
        if promocode.is_used:
            return {
                "success": False,
                "message": "Промокод уже был использован"
            }
        
        # Mark promocode as used
        promocode.is_used = True
        promocode.used_at = datetime.now()
        promocode.used_by_user_id = user_id
        
        # Add points to user balance
        new_balance = add_balance(
            user_id,
            promocode.amount,
            f"Promocode: {promocode.code}",
            db
        )
        
        # Create payment record for promocode
        payment = models.Payment(
            user_id=user_id,
            yukassa_payment_id=f"promocode_{promocode.code}",
            amount=promocode.amount * 100,  # Store in kopeks for consistency
            currency="RUB",
            status=models.PaymentStatus.succeeded,
            payment_type=models.PaymentType.promocode,
            payment_method="promocode",
            description=f"Promocode: {promocode.code}"
        )
        db.add(payment)
        db.commit()
        
        logger.info(f"User {user_id} used promocode {promocode.code} for {promocode.amount} points")
        
        return {
            "success": True,
            "message": f"Промокод активирован! +{promocode.amount} баллов",
            "amount": promocode.amount,
            "new_balance": new_balance
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error using promocode: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error using promocode: {str(e)}"
        )


@router.get("/list", response_model=list[schemas.PromocodeResponse])
def list_promocodes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all promocodes (for admin use)"""
    try:
        promocodes = db.query(models.Promocode).order_by(
            models.Promocode.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        return promocodes
        
    except Exception as e:
        logger.error(f"Error listing promocodes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing promocodes: {str(e)}"
        )


@router.get("/{code}", response_model=schemas.PromocodeResponse)
def get_promocode(code: str, db: Session = Depends(get_db)):
    """Get promocode by code"""
    try:
        promocode = db.query(models.Promocode).filter(
            models.Promocode.code == code.upper()
        ).first()
        
        if not promocode:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Promocode not found"
            )
        
        return promocode
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting promocode: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting promocode: {str(e)}"
        )
