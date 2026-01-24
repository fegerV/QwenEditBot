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
    
    def __init__(self, comfyui_url: str = "http://localhost:8188", interval: float = 5.0):
        """
        Инициализация watchdog
        
        Args:
            comfyui_url: URL ComfyUI сервера
            interval: Интервал между проверками (секунды) - уменьшен до 5 для более частых проверок
        """
        self.comfyui_url = comfyui_url.rstrip('/')
        self.interval = interval
        self.session: Optional[aiohttp.ClientSession] = None
        self.running = False
        self.stats = {
            'total_checks': 0,
            'successful_checks': 0,
            'failed_checks': 0,
            'wakeup_calls': 0,
            'window_wakeups': 0
        }
    
    async def _create_session(self):
        """Создать HTTP сессию"""
        if self.session is None or self.session.closed:
            # Увеличен timeout для wakeup запросов
            timeout = aiohttp.ClientTimeout(total=15, connect=5)
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
            
            # Используем более короткий timeout для обычных проверок
            health_timeout = aiohttp.ClientTimeout(total=3, connect=1)
            
            # Проверка через system_stats endpoint
            async with self.session.get(f"{self.comfyui_url}/system_stats", timeout=health_timeout) as response:
                if response.status == 200:
                    return True
                else:
                    logger.warning(f"ComfyUI returned status {response.status}")
                    return False
                    
        except asyncio.TimeoutError:
            logger.warning("ComfyUI health check timeout - ComfyUI may be sleeping")
            return False
        except aiohttp.ClientError as e:
            logger.warning(f"ComfyUI health check failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error in health check: {e}", exc_info=True)
            return False
    
    async def wakeup_comfyui(self) -> bool:
        """
        "Разбудить" ComfyUI через несколько запросов + Windows API
        
        Returns:
            True если удалось разбудить
        """
        try:
            await self._create_session()
            
            # 1. Попытка через Windows API (если доступно)
            try:
                window_wakeup = await self._wakeup_via_windows_api()
                if window_wakeup:
                    self.stats['window_wakeups'] += 1
                    logger.info("ComfyUI window woken via Windows API")
                    await asyncio.sleep(0.5)  # Даем время окну проснуться
            except Exception as e:
                logger.debug(f"Windows API wakeup not available: {e}")
            
            # 2. Отправляем несколько запросов для "пробуждения"
            # Используем более длинный timeout для wakeup
            wakeup_timeout = aiohttp.ClientTimeout(total=10, connect=3)
            
            wakeup_endpoints = [
                ("/system_stats", "GET"),
                ("/queue", "GET"),
                ("/history", "GET"),
                ("/prompt", "POST")  # POST с пустым body может помочь
            ]
            
            wakeup_success = False
            for endpoint, method in wakeup_endpoints:
                try:
                    if method == "GET":
                        async with self.session.get(
                            f"{self.comfyui_url}{endpoint}", 
                            timeout=wakeup_timeout
                        ) as response:
                            if response.status in (200, 404, 400):
                                wakeup_success = True
                                await asyncio.sleep(0.2)  # Задержка между запросами
                    elif method == "POST":
                        # POST с минимальным пустым workflow
                        empty_workflow = {"prompt": {}}
                        async with self.session.post(
                            f"{self.comfyui_url}{endpoint}",
                            json=empty_workflow,
                            timeout=wakeup_timeout
                        ) as response:
                            # Даже ошибка означает, что сервер отвечает
                            if response.status in (200, 400, 500):
                                wakeup_success = True
                                await asyncio.sleep(0.2)
                except asyncio.TimeoutError:
                    logger.debug(f"Wakeup request to {endpoint} timed out")
                    continue
                except Exception as e:
                    logger.debug(f"Wakeup request to {endpoint} failed: {e}")
                    continue
            
            if wakeup_success:
                self.stats['wakeup_calls'] += 1
                logger.info("ComfyUI wakeup sequence completed")
            
            return wakeup_success
            
        except Exception as e:
            logger.error(f"Error in wakeup sequence: {e}", exc_info=True)
            return False
    
    async def _proactive_wakeup(self) -> bool:
        """
        Профилактическое пробуждение - легкие запросы для поддержания активности
        
        Returns:
            True если успешно
        """
        try:
            await self._create_session()
            
            # Легкие запросы для поддержания активности
            proactive_timeout = aiohttp.ClientTimeout(total=3, connect=1)
            
            # Быстрая проверка queue - это легкий запрос, который не мешает обработке
            try:
                async with self.session.get(
                    f"{self.comfyui_url}/queue",
                    timeout=proactive_timeout
                ) as response:
                    if response.status == 200:
                        return True
            except Exception:
                pass
            
            # Если queue не ответил, пробуем system_stats
            try:
                async with self.session.get(
                    f"{self.comfyui_url}/system_stats",
                    timeout=proactive_timeout
                ) as response:
                    if response.status == 200:
                        return True
            except Exception:
                pass
            
            return False
            
        except Exception as e:
            logger.debug(f"Proactive wakeup failed: {e}")
            return False
    
    async def _wakeup_via_windows_api(self) -> bool:
        """
        Попытка разбудить через Windows API (если доступно)
        
        Returns:
            True если удалось
        """
        try:
            import ctypes
            import ctypes.wintypes
            
            user32 = ctypes.windll.user32
            
            # Определение типов для EnumWindows
            EnumWindowsProc = ctypes.WINFUNCTYPE(
                ctypes.c_bool,
                ctypes.POINTER(ctypes.c_int),
                ctypes.POINTER(ctypes.c_int)
            )
            
            def enum_windows_callback(hwnd, lParam):
                """Callback для EnumWindows"""
                if user32.IsWindowVisible(hwnd):
                    length = user32.GetWindowTextLengthW(hwnd)
                    if length > 0:
                        buffer = ctypes.create_unicode_buffer(length + 1)
                        user32.GetWindowTextW(hwnd, buffer, length + 1)
                        window_title = buffer.value.lower()
                        
                        if "comfyui" in window_title:
                            lParam.append(hwnd)
                return True
            
            windows = []
            callback = EnumWindowsProc(enum_windows_callback)
            user32.EnumWindows(callback, windows)
            
            if windows:
                hwnd = windows[0]
                # Активируем окно
                user32.SetForegroundWindow(hwnd)
                user32.ShowWindow(hwnd, 9)  # SW_RESTORE
                # Легкое событие
                WM_KEYDOWN = 0x0100
                WM_KEYUP = 0x0101
                VK_SPACE = 0x20
                user32.PostMessageW(hwnd, WM_KEYDOWN, VK_SPACE, 0)
                await asyncio.sleep(0.01)
                user32.PostMessageW(hwnd, WM_KEYUP, VK_SPACE, 0)
                return True
            
            return False
            
        except Exception:
            # Windows API не доступен (не Windows или ошибка)
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
        proactive_wakeup_counter = 0
        proactive_wakeup_interval = 6  # Каждые 6 проверок (30 секунд) - профилактическое пробуждение
        
        try:
            while self.running:
                is_healthy = await self.run_health_check()
                
                if is_healthy:
                    consecutive_failures = 0
                    # Профилактическое пробуждение даже при успешном health check
                    # Это предотвращает "засыпание" во время обработки
                    proactive_wakeup_counter += 1
                    if proactive_wakeup_counter >= proactive_wakeup_interval:
                        proactive_wakeup_counter = 0
                        logger.debug("Proactive wakeup to prevent ComfyUI sleeping...")
                        await self._proactive_wakeup()
                else:
                    consecutive_failures += 1
                    # При первой же неудаче пытаемся разбудить
                    if consecutive_failures == 1:
                        logger.warning("ComfyUI health check failed, attempting immediate wakeup...")
                        await self.wakeup_comfyui()
                    
                    if consecutive_failures >= max_consecutive_failures:
                        logger.error(
                            f"ComfyUI failed {consecutive_failures} consecutive checks. "
                            "Consider checking ComfyUI manually."
                        )
                        # При множественных неудачах - более агрессивное пробуждение
                        logger.warning("Attempting aggressive wakeup sequence...")
                        for _ in range(3):
                            await self.wakeup_comfyui()
                            await asyncio.sleep(1)
                
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
        logger.info(f"  Window wakeups: {self.stats['window_wakeups']}")
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
    interval = 5.0  # Проверка каждые 5 секунд (уменьшено для более частых проверок)
    
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
