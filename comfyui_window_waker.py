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
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
WM_MOUSEMOVE = 0x0200
VK_SPACE = 0x20
VK_RETURN = 0x0D

# Windows API функции
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
psapi = ctypes.windll.psapi

# Определение типов для EnumWindows будет создано внутри метода


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
    
    def _get_window_process_name(self, hwnd: int) -> Optional[str]:
        """Получить имя процесса для окна"""
        try:
            process_id = ctypes.wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
            
            if process_id.value == 0:
                return None
            
            # PROCESS_QUERY_INFORMATION | PROCESS_VM_READ
            h_process = kernel32.OpenProcess(0x0410, False, process_id.value)
            if h_process == 0:
                return None
            
            try:
                process_name = ctypes.create_unicode_buffer(260)
                size = ctypes.wintypes.DWORD(260)
                if psapi.GetModuleBaseNameW(h_process, None, process_name, size):
                    return process_name.value
            finally:
                kernel32.CloseHandle(h_process)
        except Exception:
            pass
        return None
    
    def find_comfyui_window(self) -> Optional[int]:
        """
        Найти окно ComfyUI по заголовку и процессу
        
        Returns:
            HWND окна или None
        """
        found_windows = []
        
        def enum_windows_callback(hwnd, lParam):
            """Callback для EnumWindows"""
            try:
                if user32.IsWindowVisible(hwnd):
                    length = user32.GetWindowTextLengthW(hwnd)
                    if length > 0:
                        buffer = ctypes.create_unicode_buffer(length + 1)
                        user32.GetWindowTextW(hwnd, buffer, length + 1)
                        window_title = buffer.value
                        title_lower = window_title.lower()
                        
                        # Проверяем название окна
                        if self.window_title.lower() in title_lower:
                            # Дополнительная проверка: это должно быть окно консоли Python
                            # Исключаем окна Cursor, VS Code и другие редакторы
                            excluded_keywords = ['cursor', 'vscode', 'visual studio', 'code', 'editor']
                            if any(excluded in title_lower for excluded in excluded_keywords):
                                return True  # Пропускаем эти окна
                            
                            # Проверяем процесс - должно быть python.exe или pythonw.exe
                            process_name = self._get_window_process_name(hwnd)
                            if process_name:
                                process_lower = process_name.lower()
                                # Ищем окна Python (ComfyUI запускается через Python)
                                if 'python' in process_lower or 'pythonw' in process_lower:
                                    found_windows.append({
                                        'hwnd': hwnd,
                                        'title': window_title,
                                        'process': process_name
                                    })
                                    logger.debug(f"Found potential ComfyUI window: '{window_title}' (Process: {process_name}, HWND: {hwnd})")
            except Exception:
                pass
            return True
        
        # Определяем тип callback с правильными типами
        EnumWindowsProcType = ctypes.WINFUNCTYPE(
            ctypes.c_bool,
            ctypes.wintypes.HWND,
            ctypes.wintypes.LPARAM
        )
        
        callback = EnumWindowsProcType(enum_windows_callback)
        try:
            user32.EnumWindows(callback, 0)
        except Exception as e:
            logger.error(f"EnumWindows error: {e}", exc_info=True)
            return None
        
        if found_windows:
            # Если найдено несколько окон, выбираем первое
            # Логируем информацию о найденном окне
            selected = found_windows[0]
            logger.info(f"Selected ComfyUI window: '{selected['title']}' (Process: {selected['process']}, HWND: {selected['hwnd']})")
            return selected['hwnd']
        
        logger.warning(f"No ComfyUI window found matching '{self.window_title}' with Python process")
        return None
    
    def wake_window(self, hwnd: int) -> bool:
        """
        "Разбудить" окно через реальные клики и события
        
        Args:
            hwnd: Handle окна
            
        Returns:
            True если успешно
        """
        try:
            # Получаем координаты окна для клика
            rect = ctypes.wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            
            # Вычисляем центр окна
            center_x = (rect.left + rect.right) // 2
            center_y = (rect.top + rect.bottom) // 2
            
            # Активируем окно
            user32.SetForegroundWindow(hwnd)
            user32.ShowWindow(hwnd, 9)  # SW_RESTORE
            time.sleep(0.05)  # Даем время окну активироваться
            
            # Реальный клик по окну (более эффективно, чем PostMessage)
            # Конвертируем координаты в lParam для SendMessage
            lParam = center_y << 16 | (center_x & 0xFFFF)
            
            # Отправляем события клика мыши
            WM_LBUTTONDOWN = 0x0201
            WM_LBUTTONUP = 0x0202
            WM_MOUSEMOVE = 0x0200
            
            # Движение мыши
            user32.SendMessageW(hwnd, WM_MOUSEMOVE, 0, lParam)
            time.sleep(0.01)
            
            # Нажатие левой кнопки мыши
            user32.SendMessageW(hwnd, WM_LBUTTONDOWN, 0x0001, lParam)  # MK_LBUTTON
            time.sleep(0.01)
            
            # Отпускание левой кнопки мыши
            user32.SendMessageW(hwnd, WM_LBUTTONUP, 0, lParam)
            time.sleep(0.01)
            
            # Дополнительно: отправляем событие клавиатуры
            user32.PostMessageW(hwnd, WM_KEYDOWN, VK_SPACE, 0)
            time.sleep(0.01)
            user32.PostMessageW(hwnd, WM_KEYUP, VK_SPACE, 0)
            
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
            # Логируем только периодически, чтобы не засорять логи
            if self.stats['window_not_found'] % 10 == 1:  # Каждые 10 попыток
                logger.info(f"ComfyUI window not found (title contains: '{self.window_title}') - attempt {self.stats['window_not_found']}")
            return False
        
        success = self.wake_window(hwnd)
        
        if success:
            self.stats['successful_wakes'] += 1
            # Получаем название окна для логирования
            try:
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buffer = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buffer, length + 1)
                    window_title = buffer.value
                    process_name = self._get_window_process_name(hwnd) or "Unknown"
                    logger.info(f"ComfyUI window woken successfully: '{window_title}' (Process: {process_name}, HWND: {hwnd}, total: {self.stats['successful_wakes']})")
                else:
                    logger.info(f"ComfyUI window woken successfully (HWND: {hwnd}, total: {self.stats['successful_wakes']})")
            except Exception:
                logger.info(f"ComfyUI window woken successfully (HWND: {hwnd}, total: {self.stats['successful_wakes']})")
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
