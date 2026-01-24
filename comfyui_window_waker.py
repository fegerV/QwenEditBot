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
    
    def _get_process_command_line(self, process_id: int) -> Optional[str]:
        """Получить командную строку процесса"""
        try:
            # PROCESS_QUERY_INFORMATION | PROCESS_VM_READ
            h_process = kernel32.OpenProcess(0x0410, False, process_id)
            if h_process == 0:
                return None
            
            try:
                # Используем NtQueryInformationProcess для получения командной строки
                # Это более сложный способ, но попробуем через GetCommandLine
                # Для упрощения используем другой подход - проверяем рабочую директорию
                current_dir = ctypes.create_unicode_buffer(260)
                if kernel32.GetCurrentDirectoryW(260, current_dir):
                    # Это не работает для другого процесса, нужно использовать другой метод
                    pass
            except Exception:
                pass
            finally:
                kernel32.CloseHandle(h_process)
        except Exception:
            pass
        return None
    
    def _get_process_working_directory(self, process_id: int) -> Optional[str]:
        """Получить рабочую директорию процесса"""
        try:
            # PROCESS_QUERY_INFORMATION | PROCESS_VM_READ
            h_process = kernel32.OpenProcess(0x0410, False, process_id)
            if h_process == 0:
                return None
            
            try:
                # Используем QueryFullProcessImageName для получения пути к exe
                # Но для рабочей директории нужен другой подход
                # Для упрощения проверим через GetModuleFileNameEx
                exe_path = ctypes.create_unicode_buffer(260)
                size = ctypes.wintypes.DWORD(260)
                if psapi.GetModuleFileNameExW(h_process, None, exe_path, size):
                    # Это путь к exe, но нам нужна рабочая директория
                    # Для cmd.exe это сложнее, поэтому используем другой подход
                    pass
            except Exception:
                pass
            finally:
                kernel32.CloseHandle(h_process)
        except Exception:
            pass
        return None
    
    def find_comfyui_window(self) -> Optional[int]:
        """
        Найти окно ComfyUI - это cmd.exe, запущенный из C:\ComfyUI
        
        Returns:
            HWND окна или None
        """
        found_windows = []
        
        def enum_windows_callback(hwnd, lParam):
            """Callback для EnumWindows"""
            try:
                if user32.IsWindowVisible(hwnd):
                    # Получаем процесс окна
                    process_id = ctypes.wintypes.DWORD()
                    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
                    
                    if process_id.value == 0:
                        return True
                    
                    process_name = self._get_window_process_name(hwnd)
                    if not process_name:
                        return True
                    
                    process_lower = process_name.lower()
                    
                    # Ищем только cmd.exe окна
                    if 'cmd.exe' not in process_lower:
                        return True
                    
                    # Исключаем окна Cursor, VS Code и другие редакторы
                    length = user32.GetWindowTextLengthW(hwnd)
                    if length > 0:
                        buffer = ctypes.create_unicode_buffer(length + 1)
                        user32.GetWindowTextW(hwnd, buffer, length + 1)
                        window_title = buffer.value
                        title_lower = window_title.lower()
                        
                        excluded_keywords = ['cursor', 'vscode', 'visual studio', 'code', 'editor', 'qweneditbot', 'worker', 'bot', 'watchdog', 'waker']
                        if any(excluded in title_lower for excluded in excluded_keywords):
                            return True  # Пропускаем эти окна
                    
                    # Проверяем, что это окно cmd.exe
                    # ComfyUI запускается через run_nvidia_gpu.bat в C:\ComfyUI
                    # Проверяем по классу окна - консольные окна имеют класс "ConsoleWindowClass"
                    class_name = ctypes.create_unicode_buffer(260)
                    user32.GetClassNameW(hwnd, class_name, 260)
                    class_name_str = class_name.value
                    
                    # Консольные окна имеют класс "ConsoleWindowClass"
                    if 'console' in class_name_str.lower() or class_name_str == 'ConsoleWindowClass':
                        # Это консольное окно cmd.exe
                        # Проверяем, что это не окно наших сервисов (они имеют специфичные названия)
                        if length > 0:
                            window_title = buffer.value
                            # Если в названии есть "ComfyUI" или это просто консоль без специфичного названия
                            # (наши сервисы имеют названия типа "QwenEditBot Worker", "ComfyUI Watchdog")
                            if 'comfyui' in title_lower or (not any(keyword in title_lower for keyword in ['qwen', 'worker', 'bot', 'watchdog', 'waker'])):
                                found_windows.append({
                                    'hwnd': hwnd,
                                    'title': window_title if length > 0 else '(no title)',
                                    'process': process_name,
                                    'class': class_name_str
                                })
                                logger.debug(f"Found potential ComfyUI window: '{window_title if length > 0 else '(no title)'}' (Process: {process_name}, Class: {class_name_str}, HWND: {hwnd})")
            except Exception as e:
                logger.debug(f"Error in enum_windows_callback: {e}")
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
            logger.info(f"Selected ComfyUI window: '{selected['title']}' (Process: {selected['process']}, Class: {selected['class']}, HWND: {selected['hwnd']})")
            return selected['hwnd']
        
        logger.warning(f"No ComfyUI window found (cmd.exe console window)")
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
