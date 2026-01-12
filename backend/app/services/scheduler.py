"""Scheduler service for weekly bonus distribution"""

import asyncio
import logging
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from .. import models
from ..config import settings
from .payment_service import PaymentService

logger = logging.getLogger(__name__)


class WeeklyBonusScheduler:
    """Scheduler for issuing weekly bonuses"""
    
    def __init__(self, db_session_factory):
        self.db_session_factory = db_session_factory
        self.running = False
        self.task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start the scheduler"""
        if not settings.WEEKLY_BONUS_ENABLED:
            logger.info("Weekly bonus is disabled")
            return
        
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        self.running = True
        self.task = asyncio.create_task(self._run_scheduler())
        logger.info("Weekly bonus scheduler started")
    
    async def stop(self):
        """Stop the scheduler"""
        if not self.running:
            return
        
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        
        logger.info("Weekly bonus scheduler stopped")
    
    async def _run_scheduler(self):
        """Main scheduler loop"""
        while self.running:
            try:
                await self._check_and_issue_bonus()
                # Check every hour
                await asyncio.sleep(3600)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in scheduler: {e}")
                await asyncio.sleep(3600)
    
    async def _check_and_issue_bonus(self):
        """Check if it's time to issue weekly bonus and issue it"""
        now = datetime.utcnow()
        
        # Check if it's the right day (Friday = 4)
        if now.weekday() != settings.WEEKLY_BONUS_DAY:
            return
        
        # Parse scheduled time
        try:
            scheduled_hour, scheduled_minute = map(int, settings.WEEKLY_BONUS_TIME.split(":"))
            scheduled_time = now.replace(
                hour=scheduled_hour,
                minute=scheduled_minute,
                second=0,
                microsecond=0
            )
            
            # Check if we're within 1 hour of scheduled time
            time_diff = (now - scheduled_time).total_seconds()
            if not (-3600 <= time_diff < 3600):
                return
            
        except Exception as e:
            logger.error(f"Error parsing bonus time: {e}")
            return
        
        # Issue bonuses to all users
        logger.info("Issuing weekly bonuses to all users")
        
        db = self.db_session_factory()
        try:
            from .telegram_client import TelegramClient
            payment_service = PaymentService(db)
            telegram_client = TelegramClient()
            
            # Get all users
            users = db.query(models.User).all()
            
            success_count = 0
            for user in users:
                try:
                    payment = await payment_service.issue_weekly_bonus(user.user_id)
                    
                    # Send notification to user
                    try:
                        await telegram_client.send_message(
                            chat_id=user.telegram_id,
                            text=f"🎉 *Пятничный бонус!* 🎉\n\n💰 +{settings.WEEKLY_BONUS_AMOUNT} баллов\n💳 Новый баланс: {int(user.balance)} баллов\n\nСпасибо за использование QwenEditBot!"
                        )
                    except Exception as e:
                        logger.error(f"Failed to send bonus notification to user {user.user_id}: {e}")
                    
                    success_count += 1
                except Exception as e:
                    logger.error(f"Failed to issue bonus to user {user.user_id}: {e}")
            
            logger.info(f"Weekly bonuses issued: {success_count}/{len(users)} users")
            
        except Exception as e:
            logger.error(f"Error issuing weekly bonuses: {e}")
        finally:
            db.close()
    
    async def issue_bonus_now(self):
        """Issue bonus immediately (for testing or manual trigger)"""
        logger.info("Manually triggering weekly bonus distribution")
        
        db = self.db_session_factory()
        try:
            payment_service = PaymentService(db)
            
            # Get all users
            users = db.query(models.User).all()
            
            success_count = 0
            for user in users:
                try:
                    await payment_service.issue_weekly_bonus(user.user_id)
                    success_count += 1
                except Exception as e:
                    logger.error(f"Failed to issue bonus to user {user.user_id}: {e}")
            
            logger.info(f"Manual bonuses issued: {success_count}/{len(users)} users")
            return {"success": True, "count": success_count, "total": len(users)}
            
        except Exception as e:
            logger.error(f"Error issuing manual bonuses: {e}")
            return {"success": False, "error": str(e)}
        finally:
            db.close()
