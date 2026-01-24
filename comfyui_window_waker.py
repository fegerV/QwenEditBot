#!/usr/bin/env python3
"""
ComfyUI Window Waker - программно "пробуждает" окно ComfyUI
Использует Windows API для отправки событий в окно консоли
"""

import ctypes
import ctypes.wintypes
import logging
import sys
import time
from pathlib import Path
from typing import Optional

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/comfyui_waker.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Windows API константы
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_CHAR = 0x0102
VK_SPACE = 0x20
VK_RETURN = 0x0D

# Windows API функции
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Определение типов для EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(
    ctypes.c_bool,
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int)
)


class ComfyUIWindowWaker:
    """Класс для пробуждения окна ComfyUI через Windows API"""
    
    def __init__(self, window_title: str = "ComfyUI", interval: float = 30.0):
        """
        Инициализация
        
        Args:
            window_title: Заголовок окна ComfyUI (часть названия)
            interval: Интервал между пробуждениями (секунды)
        """
        self.window_title = window_title
        self.interval = interval
        self.running = False
        self.stats = {
            'total_wakes': 0,
            'successful_wakes': 0,
            'failed_wakes': 0,
            'window_not_found': 0
        }
    
    def find_comfyui_window(self) -> Optional[int]:
        """
        Найти окно ComfyUI по заголовку
        
        Returns:
            HWND окна или None
        """
        def enum_windows_callback(hwnd, lParam):
            """Callback для EnumWindows"""
            if user32.IsWindowVisible(hwnd):
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buffer = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buffer, length + 1)
                    window_title = buffer.value
                    
                    if self.window_title.lower() in window_title.lower():
                        # Сохраняем найденное окно
                        lParam.append(hwnd)
            return True
        
        windows = []
        callback = EnumWindowsProc(enum_windows_callback)
        user32.EnumWindows(callback, windows)
        
        if windows:
            return windows[0]
        return None
    
    def wake_window(self, hwnd: int) -> bool:
        """
        "Разбудить" окно через отправку событий
        
        Args:
            hwnd: Handle окна
            
        Returns:
            True если успешно
        """
        try:
            # Активируем окно
            user32.SetForegroundWindow(hwnd)
            user32.ShowWindow(hwnd, 9)  # SW_RESTORE
            
            # Отправляем легкое событие (пробел) для пробуждения
            # Но не реально нажимаем, а просто отправляем сообщение
            user32.PostMessageW(hwnd, WM_KEYDOWN, VK_SPACE, 0)
            time.sleep(0.01)
            user32.PostMessageW(hwnd, WM_KEYUP, VK_SPACE, 0)
            
            # Возвращаем фокус обратно (если нужно)
            return True
            
        except Exception as e:
            logger.error(f"Error waking window: {e}", exc_info=True)
            return False
    
    def wake_comfyui(self) -> bool:
        """
        Найти и разбудить окно ComfyUI
        
        Returns:
            True если успешно
        """
        self.stats['total_wakes'] += 1
        
        hwnd = self.find_comfyui_window()
        
        if hwnd is None:
            self.stats['window_not_found'] += 1
            logger.debug(f"ComfyUI window not found (title contains: '{self.window_title}')")
            return False
        
        success = self.wake_window(hwnd)
        
        if success:
            self.stats['successful_wakes'] += 1
            logger.debug(f"ComfyUI window woken successfully (HWND: {hwnd})")
        else:
            self.stats['failed_wakes'] += 1
            logger.warning(f"Failed to wake ComfyUI window (HWND: {hwnd})")
        
        return success
    
    def run(self):
        """Основной цикл"""
        logger.info(f"Starting ComfyUI Window Waker (window: '{self.window_title}', interval: {self.interval}s)")
        self.running = True
        
        try:
            while self.running:
                self.wake_comfyui()
                
                # Ждем перед следующей попыткой
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            logger.info("Window Waker stopped by user")
        except Exception as e:
            logger.error(f"Window Waker error: {e}", exc_info=True)
        finally:
            self._print_stats()
    
    def _print_stats(self):
        """Вывести статистику"""
        logger.info("=" * 60)
        logger.info("ComfyUI Window Waker Statistics:")
        logger.info(f"  Total wake attempts: {self.stats['total_wakes']}")
        logger.info(f"  Successful: {self.stats['successful_wakes']}")
        logger.info(f"  Failed: {self.stats['failed_wakes']}")
        logger.info(f"  Window not found: {self.stats['window_not_found']}")
        if self.stats['total_wakes'] > 0:
            success_rate = (self.stats['successful_wakes'] / self.stats['total_wakes']) * 100
            logger.info(f"  Success rate: {success_rate:.1f}%")
        logger.info("=" * 60)
    
    def stop(self):
        """Остановить"""
        logger.info("Stopping ComfyUI Window Waker...")
        self.running = False


def main():
    """Главная функция"""
    # Создаем директорию для логов
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Параметры
    window_title = "ComfyUI"  # Можно изменить на точное название окна
    interval = 15.0  # Пробуждение каждые 15 секунд (уменьшено для более частых пробуждений)
    
    waker = ComfyUIWindowWaker(window_title=window_title, interval=interval)
    
    try:
        waker.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Window Waker stopped")
        sys.exit(0)
