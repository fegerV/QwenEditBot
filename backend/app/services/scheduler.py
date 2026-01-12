import logging
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from ..config import settings
from ..database import SessionLocal
from ..models import Payment, PaymentStatus, PaymentType, User
from .telegram_notifier import TelegramNotifier

logger = logging.getLogger(__name__)


class WeeklyBonusScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone="UTC")
        self.notifier = TelegramNotifier()

    def start(self) -> None:
        if not settings.WEEKLY_BONUS_ENABLED:
            logger.info("Weekly bonus scheduler is disabled")
            return

        hour, minute = self._parse_time(settings.WEEKLY_BONUS_TIME)

        self.scheduler.add_job(
            self.issue_weekly_bonus,
            trigger=CronTrigger(day_of_week=settings.WEEKLY_BONUS_DAY, hour=hour, minute=minute),
            id="weekly_bonus",
            name="Weekly bonus distribution",
            replace_existing=True,
        )

        self.scheduler.start()
        logger.info(
            "Weekly bonus scheduler started: day_of_week=%s, time=%02d:%02d UTC",
            settings.WEEKLY_BONUS_DAY,
            hour,
            minute,
        )

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("Weekly bonus scheduler stopped")

    @staticmethod
    def _parse_time(value: str) -> tuple[int, int]:
        try:
            parts = value.split(":")
            hour = int(parts[0])
            minute = int(parts[1])
            return hour, minute
        except Exception:
            return 20, 0

    async def issue_weekly_bonus(self) -> None:
        logger.info("Issuing weekly bonus...")

        session = SessionLocal()
        try:
            users = session.query(User).all()
            now = datetime.now(timezone.utc)

            total_users = 0
            for user in users:
                user.balance += settings.WEEKLY_BONUS_AMOUNT

                amount_kopeks = 0
                rubles = settings.WEEKLY_BONUS_AMOUNT / max(settings.PAYMENT_POINTS_PER_RUBLE, 1)
                if int(rubles) == rubles:
                    amount_kopeks = int(rubles) * 100

                payment = Payment(
                    user_id=user.user_id,
                    type=PaymentType.weekly_bonus,
                    amount=amount_kopeks,
                    currency="RUB",
                    status=PaymentStatus.succeeded,
                    description="Weekly bonus",
                    paid_at=now,
                )
                session.add(payment)

                chat_id = user.telegram_id or user.user_id
                await self.notifier.send_message(
                    chat_id,
                    f"🎉 Пятничный бонус! +{settings.WEEKLY_BONUS_AMOUNT} баллов 🎉\nВаш баланс: {user.balance}",
                )
                total_users += 1

            session.commit()
            logger.info("Weekly bonus issued to %s users", total_users)

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to issue weekly bonus: {e}")
        finally:
            session.close()
