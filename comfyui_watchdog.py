#!/usr/bin/env python3
"""
ComfyUI Watchdog - предотвращает "засыпание" ComfyUI процесса
Отправляет периодические keep-alive запросы к ComfyUI API
"""

import asyncio
import aiohttp
import logging
import sys
from pathlib import Path
from typing import Optional

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/comfyui_watchdog.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class ComfyUIWatchdog:
    """Watchdog для поддержания активности ComfyUI"""
    
    def __init__(self, comfyui_url: str = "http://localhost:8188", interval: float = 10.0):
        """
        Инициализация watchdog
        
        Args:
            comfyui_url: URL ComfyUI сервера
            interval: Интервал между проверками (секунды)
        """
        self.comfyui_url = comfyui_url.rstrip('/')
        self.interval = interval
        self.session: Optional[aiohttp.ClientSession] = None
        self.running = False
        self.stats = {
            'total_checks': 0,
            'successful_checks': 0,
            'failed_checks': 0,
            'wakeup_calls': 0
        }
    
    async def _create_session(self):
        """Создать HTTP сессию"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=5, connect=2)
            self.session = aiohttp.ClientSession(timeout=timeout)
    
    async def _close_session(self):
        """Закрыть HTTP сессию"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def check_comfyui_health(self) -> bool:
        """
        Проверить здоровье ComfyUI
        
        Returns:
            True если ComfyUI отвечает, False иначе
        """
        try:
            await self._create_session()
            
            # Проверка через system_stats endpoint
            async with self.session.get(f"{self.comfyui_url}/system_stats") as response:
                if response.status == 200:
                    return True
                else:
                    logger.warning(f"ComfyUI returned status {response.status}")
                    return False
                    
        except asyncio.TimeoutError:
            logger.warning("ComfyUI health check timeout")
            return False
        except aiohttp.ClientError as e:
            logger.warning(f"ComfyUI health check failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error in health check: {e}", exc_info=True)
            return False
    
    async def wakeup_comfyui(self) -> bool:
        """
        "Разбудить" ComfyUI через несколько запросов
        
        Returns:
            True если удалось разбудить
        """
        try:
            await self._create_session()
            
            # Отправляем несколько легких запросов для "пробуждения"
            wakeup_endpoints = [
                "/system_stats",
                "/prompt",
                "/queue"
            ]
            
            wakeup_success = False
            for endpoint in wakeup_endpoints:
                try:
                    async with self.session.get(f"{self.comfyui_url}{endpoint}") as response:
                        if response.status in (200, 404):  # 404 тоже нормально для некоторых endpoints
                            wakeup_success = True
                            await asyncio.sleep(0.1)  # Небольшая задержка между запросами
                except Exception:
                    continue
            
            if wakeup_success:
                self.stats['wakeup_calls'] += 1
                logger.info("ComfyUI wakeup sequence completed")
            
            return wakeup_success
            
        except Exception as e:
            logger.error(f"Error in wakeup sequence: {e}", exc_info=True)
            return False
    
    async def run_health_check(self):
        """Выполнить проверку здоровья"""
        self.stats['total_checks'] += 1
        
        is_healthy = await self.check_comfyui_health()
        
        if is_healthy:
            self.stats['successful_checks'] += 1
            logger.debug(f"ComfyUI health check OK ({self.stats['successful_checks']}/{self.stats['total_checks']})")
        else:
            self.stats['failed_checks'] += 1
            logger.warning(f"ComfyUI health check FAILED ({self.stats['failed_checks']}/{self.stats['total_checks']})")
            
            # Попытка разбудить
            logger.info("Attempting to wake up ComfyUI...")
            await self.wakeup_comfyui()
        
        return is_healthy
    
    async def run(self):
        """Основной цикл watchdog"""
        logger.info(f"Starting ComfyUI Watchdog (URL: {self.comfyui_url}, interval: {self.interval}s)")
        self.running = True
        
        consecutive_failures = 0
        max_consecutive_failures = 3
        
        try:
            while self.running:
                is_healthy = await self.run_health_check()
                
                if is_healthy:
                    consecutive_failures = 0
                else:
                    consecutive_failures += 1
                    if consecutive_failures >= max_consecutive_failures:
                        logger.error(
                            f"ComfyUI failed {consecutive_failures} consecutive checks. "
                            "Consider checking ComfyUI manually."
                        )
                
                # Ждем перед следующей проверкой
                await asyncio.sleep(self.interval)
                
        except KeyboardInterrupt:
            logger.info("Watchdog stopped by user")
        except Exception as e:
            logger.error(f"Watchdog error: {e}", exc_info=True)
        finally:
            await self._close_session()
            self._print_stats()
    
    def _print_stats(self):
        """Вывести статистику"""
        logger.info("=" * 60)
        logger.info("ComfyUI Watchdog Statistics:")
        logger.info(f"  Total checks: {self.stats['total_checks']}")
        logger.info(f"  Successful: {self.stats['successful_checks']}")
        logger.info(f"  Failed: {self.stats['failed_checks']}")
        logger.info(f"  Wakeup calls: {self.stats['wakeup_calls']}")
        if self.stats['total_checks'] > 0:
            success_rate = (self.stats['successful_checks'] / self.stats['total_checks']) * 100
            logger.info(f"  Success rate: {success_rate:.1f}%")
        logger.info("=" * 60)
    
    def stop(self):
        """Остановить watchdog"""
        logger.info("Stopping ComfyUI Watchdog...")
        self.running = False


async def main():
    """Главная функция"""
    # Создаем директорию для логов
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Параметры из переменных окружения или значения по умолчанию
    comfyui_url = "http://localhost:8188"
    interval = 10.0  # Проверка каждые 10 секунд
    
    watchdog = ComfyUIWatchdog(comfyui_url=comfyui_url, interval=interval)
    
    try:
        await watchdog.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Watchdog stopped")
        sys.exit(0)
