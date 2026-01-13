"""Payment service for handling payment logic"""

import logging
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from .. import models, schemas
from ..config import settings
from .yukassa import YuKassaClient

logger = logging.getLogger(__name__)


class PaymentService:
    """Business logic for payments"""
    
    def __init__(self, db: Session):
        self.db = db
        self.yukassa_client = YuKassaClient() if settings.YUKASSA_SHOP_ID else None
    
    async def create_payment(self, user_id: int, amount: int) -> models.Payment:
        """
        Create a new payment through YuKassa
        
        Args:
            user_id: User ID
            amount: Amount in rubles
            
        Returns:
            Payment object with confirmation_url
        """
        # Validate user exists
        user = self.db.query(models.User).filter(
            models.User.user_id == user_id
        ).first()
        
        if not user:
            logger.warning(f"Payment creation failed: User {user_id} not found")
            raise ValueError(f"User {user_id} not found")
        
        # Validate amount
        if amount < settings.PAYMENT_MIN_AMOUNT:
            logger.warning(f"Payment creation failed: Amount {amount} rubles below minimum {settings.PAYMENT_MIN_AMOUNT} rubles for user {user_id}")
            raise ValueError(f"Minimum amount is {settings.PAYMENT_MIN_AMOUNT} rubles")
        if amount > settings.PAYMENT_MAX_AMOUNT:
            logger.warning(f"Payment creation failed: Amount {amount} rubles above maximum {settings.PAYMENT_MAX_AMOUNT} rubles for user {user_id}")
            raise ValueError(f"Maximum amount is {settings.PAYMENT_MAX_AMOUNT} rubles")
        
        # Convert to kopeks for storage
        amount_kopeks = amount * 100
        
        # Create payment in YuKassa
        if not self.yukassa_client:
            logger.error(f"Payment creation failed: YuKassa integration not configured for user {user_id}")
            raise Exception("YuKassa integration not configured")
        
        logger.info(f"Creating payment for user {user_id}: {amount} rubles ({amount_kopeks} kopeks)")
        
        yukassa_payment = await self.yukassa_client.create_payment(
            amount=amount_kopeks,
            description=f"QwenEditBot - пополнение баланса, пользователь {user_id}"
        )
        
        # Save to database
        payment = models.Payment(
            user_id=user_id,
            yukassa_payment_id=yukassa_payment["payment_id"],
            amount=amount_kopeks,
            currency="RUB",
            status=models.PaymentStatus.pending,
            payment_type=models.PaymentType.payment,
            description=f"Пополнение баланса",
            confirmation_url=yukassa_payment["confirmation_url"]
        )
        
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        
        logger.info(f"Payment created successfully: payment_id={payment.id}, user_id={user_id}, yukassa_payment_id={payment.yukassa_payment_id}, amount={amount} rubles, status=pending")
        
        return payment
    
    async def handle_webhook(self, yukassa_payment_id: str, status: str) -> bool:
        """
        Handle webhook from YuKassa
        
        Args:
            yukassa_payment_id: YuKassa payment ID
            status: Payment status from YuKassa
            
        Returns:
            True if webhook was processed successfully
        """
        logger.info(f"Processing YuKassa webhook: yukassa_payment_id={yukassa_payment_id}, status={status}")
        
        # Find payment in database
        payment = self.db.query(models.Payment).filter(
            models.Payment.yukassa_payment_id == yukassa_payment_id
        ).first()
        
        if not payment:
            logger.warning(f"Webhook processing failed: Payment not found for YuKassa ID: {yukassa_payment_id}")
            return False
        
        logger.info(f"Found payment: payment_id={payment.id}, user_id={payment.user_id}, current_status={payment.status}")
        
        # Update status
        if status == "succeeded":
            payment.status = models.PaymentStatus.succeeded
            payment.paid_at = datetime.now()
            
            # Credit points to user
            user = self.db.query(models.User).filter(
                models.User.user_id == payment.user_id
            ).first()
            
            if user:
                # Convert kopeks to points (1 ruble = 100 points)
                points = (payment.amount // 100) * settings.POINTS_PER_RUBLE
                user.balance += points
                
                # Create payment log entry
                payment_log = models.PaymentLog(
                    user_id=payment.user_id,
                    amount=float(points),
                    status="completed",
                    payment_id=str(payment.id)
                )
                self.db.add(payment_log)
                
                logger.info(f"Payment succeeded: payment_id={payment.id}, user_id={payment.user_id}, amount={payment.amount} kopeks, credited {points} points, new_balance={user.balance}")
                
        elif status == "failed":
            payment.status = models.PaymentStatus.failed
            logger.info(f"Payment failed: payment_id={payment.id}, user_id={payment.user_id}, yukassa_payment_id={yukassa_payment_id}")
        elif status == "cancelled":
            payment.status = models.PaymentStatus.cancelled
            logger.info(f"Payment cancelled: payment_id={payment.id}, user_id={payment.user_id}, yukassa_payment_id={yukassa_payment_id}")
        
        payment.updated_at = datetime.now()
        self.db.commit()
        
        logger.info(f"Webhook processed successfully: payment_id={payment.id}, new_status={payment.status}")
        
        return True
    
    async def refund_payment(self, user_id: int, amount: int, reason: str) -> models.Payment:
        """
        Create a refund payment (credit points back to user)
        
        Args:
            user_id: User ID
            amount: Amount in points
            reason: Reason for refund
            
        Returns:
            Payment object
        """
        logger.info(f"Creating refund for user {user_id}: amount={amount} points, reason={reason}")
        
        # Validate user exists
        user = self.db.query(models.User).filter(
            models.User.user_id == user_id
        ).first()
        
        if not user:
            logger.warning(f"Refund failed: User {user_id} not found")
            raise ValueError(f"User {user_id} not found")
        
        # Create refund payment
        payment = models.Payment(
            user_id=user_id,
            yukassa_payment_id=None,  # No YuKassa payment for refunds
            amount=amount,
            currency="RUB",
            status=models.PaymentStatus.succeeded,
            payment_type=models.PaymentType.refund,
            description=f"Refund: {reason}",
            paid_at=datetime.now()
        )
        
        # Credit points to user
        user.balance += amount
        
        # Create payment log entry
        payment_log = models.PaymentLog(
            user_id=user_id,
            amount=float(amount),
            status="completed",
            payment_id=str(payment.id)
        )
        self.db.add(payment_log)
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        
        logger.info(f"Refund created successfully: payment_id={payment.id}, user_id={user_id}, amount={amount} points, reason={reason}, new_balance={user.balance}")
        
        return payment
    
    async def get_payment(self, payment_id: int) -> Optional[models.Payment]:
        """
        Get payment by ID
        
        Args:
            payment_id: Payment ID
            
        Returns:
            Payment object or None
        """
        return self.db.query(models.Payment).filter(
            models.Payment.id == payment_id
        ).first()
    
    async def get_user_payments(
        self,
        user_id: int,
        limit: int = 20,
        offset: int = 0,
        status: Optional[str] = None
    ) -> schemas.PaymentHistoryResponse:
        """
        Get payment history for a user
        
        Args:
            user_id: User ID
            limit: Maximum number of payments to return
            offset: Offset for pagination
            status: Filter by payment status (optional)
            
        Returns:
            PaymentHistoryResponse with payments list and metadata
        """
        query = self.db.query(models.Payment).filter(
            models.Payment.user_id == user_id
        )
        
        if status:
            query = query.filter(models.Payment.status == status)
        
        # Get total count
        total = query.count()
        
        # Get payments with pagination
        payments = query.order_by(
            models.Payment.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        return schemas.PaymentHistoryResponse(
            payments=payments,
            total=total,
            limit=limit,
            offset=offset
        )
    
    async def issue_weekly_bonus(self, user_id: int, amount: int = None) -> models.Payment:
        """
        Issue weekly bonus to a user
        
        Args:
            user_id: User ID
            amount: Bonus amount in points (default from config)
            
        Returns:
            Payment object
        """
        if amount is None:
            amount = settings.WEEKLY_BONUS_AMOUNT
        
        logger.info(f"Issuing weekly bonus to user {user_id}: amount={amount} points")
        
        # Validate user exists
        user = self.db.query(models.User).filter(
            models.User.user_id == user_id
        ).first()
        
        if not user:
            logger.warning(f"Weekly bonus failed: User {user_id} not found")
            raise ValueError(f"User {user_id} not found")
        
        # Create weekly bonus payment
        payment = models.Payment(
            user_id=user_id,
            yukassa_payment_id=None,
            amount=amount,
            currency="RUB",
            status=models.PaymentStatus.succeeded,
            payment_type=models.PaymentType.weekly_bonus,
            description="Еженедельный бонус",
            paid_at=datetime.now()
        )
        
        # Credit points to user
        user.balance += amount
        
        # Create payment log entry
        payment_log = models.PaymentLog(
            user_id=user_id,
            amount=float(amount),
            status="completed",
            payment_id=str(payment.id)
        )
        self.db.add(payment_log)
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        
        logger.info(f"Weekly bonus issued successfully: payment_id={payment.id}, user_id={user_id}, amount={amount} points, new_balance={user.balance}")
        
        return payment
