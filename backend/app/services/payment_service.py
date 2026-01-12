import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..config import settings
from ..models import Payment, PaymentStatus, PaymentType
from .telegram_notifier import TelegramNotifier
from .users import get_user_by_any_id
from .yukassa import YuKassaClient

logger = logging.getLogger(__name__)


def _ensure_yukassa_configured() -> None:
    if not settings.YUKASSA_SHOP_ID or not settings.YUKASSA_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment service unavailable",
        )


def _get_yukassa_client() -> YuKassaClient:
    _ensure_yukassa_configured()
    return YuKassaClient(
        shop_id=settings.YUKASSA_SHOP_ID,  # type: ignore[arg-type]
        api_key=settings.YUKASSA_API_KEY,  # type: ignore[arg-type]
        webhook_secret=settings.YUKASSA_WEBHOOK_SECRET,
    )


def _rub_to_kopeks(amount_rub: int) -> int:
    return amount_rub * 100


def _kopeks_to_rub(amount_kopeks: int) -> int:
    return int(amount_kopeks / 100)


class PaymentService:
    def __init__(self, notifier: Optional[TelegramNotifier] = None):
        self.notifier = notifier or TelegramNotifier()

    async def create_payment(self, db: Session, user_id: int, amount_rub: int) -> Payment:
        user = get_user_by_any_id(db, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid user_id")

        if amount_rub < settings.PAYMENT_MIN_AMOUNT or amount_rub > settings.PAYMENT_MAX_AMOUNT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid amount. Allowed range: {settings.PAYMENT_MIN_AMOUNT}-{settings.PAYMENT_MAX_AMOUNT} RUB",
            )

        amount_kopeks = _rub_to_kopeks(amount_rub)

        yukassa = _get_yukassa_client()
        try:
            yk_payment = await yukassa.create_payment(
                amount=amount_kopeks,
                currency="RUB",
                return_url=settings.PAYMENT_RETURN_URL,
                metadata={"user_id": str(user.user_id)},
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to create YooKassa payment: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Payment service unavailable",
            )

        payment = Payment(
            user_id=user.user_id,
            type=PaymentType.payment,
            yukassa_payment_id=yk_payment.get("id"),
            idempotence_key=yk_payment.get("idempotence_key"),
            amount=amount_kopeks,
            currency="RUB",
            status=PaymentStatus.pending,
            description="QwenEditBot - пополнение баланса",
            confirmation_url=yk_payment.get("confirmation_url"),
        )

        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment

    async def refresh_payment_status(self, db: Session, payment: Payment) -> Payment:
        if payment.type != PaymentType.payment:
            return payment

        if payment.status != PaymentStatus.pending:
            return payment

        if not payment.yukassa_payment_id:
            return payment

        try:
            yukassa = _get_yukassa_client()
        except HTTPException:
            return payment

        try:
            remote = await yukassa.get_payment(payment.yukassa_payment_id)
        except Exception as e:
            logger.warning(f"Failed to refresh YooKassa payment status {payment.yukassa_payment_id}: {e}")
            return payment

        remote_status = remote.get("status")
        if remote_status == "cancelled":
            remote_status = "canceled"

        if remote_status and remote_status != payment.status:
            payment.status = PaymentStatus(remote_status)
            if payment.status == PaymentStatus.succeeded and not payment.paid_at:
                payment.paid_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(payment)

        return payment

    async def handle_webhook(self, db: Session, yukassa_payment_id: str, new_status: str) -> bool:
        payment = (
            db.query(Payment)
            .filter(Payment.yukassa_payment_id == yukassa_payment_id)
            .first()
        )

        if not payment:
            return False

        previous_status = payment.status

        normalized_status = new_status
        if normalized_status == "cancelled":
            normalized_status = "canceled"

        payment.status = PaymentStatus(normalized_status)

        if payment.status == PaymentStatus.succeeded and previous_status != PaymentStatus.succeeded:
            payment.paid_at = payment.paid_at or datetime.now(timezone.utc)

            user = get_user_by_any_id(db, payment.user_id)
            if user:
                points_to_add = _kopeks_to_rub(payment.amount) * settings.PAYMENT_POINTS_PER_RUBLE
                user.balance += points_to_add

                db.commit()
                db.refresh(user)
                db.refresh(payment)

                chat_id = user.telegram_id or user.user_id
                await self.notifier.send_message(
                    chat_id,
                    f"✅ Платёж успешен!\nНачислено: {points_to_add} баллов\nВаш баланс: {user.balance}",
                )
                return True

        db.commit()
        return True

    async def refund_payment(self, db: Session, user_id: int, amount_points: int, reason: str) -> Payment:
        user = get_user_by_any_id(db, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid user_id")

        rubles = amount_points / settings.PAYMENT_POINTS_PER_RUBLE
        if int(rubles) != rubles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Refund amount is not representable in RUB with current PAYMENT_POINTS_PER_RUBLE",
            )

        payment = Payment(
            user_id=user.user_id,
            type=PaymentType.refund,
            amount=_rub_to_kopeks(int(rubles)),
            currency="RUB",
            status=PaymentStatus.succeeded,
            description=reason,
            paid_at=datetime.now(timezone.utc),
        )

        user.balance += amount_points
        db.add(payment)
        db.commit()
        db.refresh(payment)

        chat_id = user.telegram_id or user.user_id
        await self.notifier.send_message(
            chat_id,
            f"🔄 Возврат баллов\n+{amount_points} баллов\nВаш баланс: {user.balance}",
        )

        return payment
