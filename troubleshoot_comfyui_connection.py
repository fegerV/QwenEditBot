import subprocess
import sys
import os
import socket
import requests

def check_port_availability(port):
    """
    Проверяет, доступен ли порт
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        result = sock.connect_ex(('localhost', port))
        return result == 0

def check_process_running(process_name):
    """
    Проверяет, запущен ли процесс
    """
    try:
        result = subprocess.run(['tasklist'], capture_output=True, text=True, shell=True)
        return process_name.lower() in result.stdout.lower()
    except Exception:
        return False

def check_comfyui_connection():
    """
    Комплексная проверка подключения к ComfyUI
    """
    print("=== Диагностика подключения к ComfyUI ===\n")
    
    # Проверяем, доступен ли порт 8500
    print("1. Проверка доступности порта 8188...")
    if check_port_availability(8188):
        print("   ✓ Порт 8188 доступен")
    else:
        print("   ✗ Порт 8188 недоступен")
    
    # Проверяем, запущен ли Python процесс, связанный с ComfyUI
    print("\n2. Проверка запущенных процессов, связанных с ComfyUI...")
    python_processes_running = check_process_running("python")
    if python_processes_running:
        print("   ✓ Обнаружен один или несколько процессов Python")
        
        # Попробуем получить список процессов и найти ComfyUI
        try:
            result = subprocess.run(['tasklist', '/fo', 'csv'], capture_output=True, text=True, shell=True)
            lines = result.stdout.strip().split('\n')[1:]  # Пропускаем заголовки
            comfyui_processes = []
            for line in lines:
                if 'python' in line.lower() and ('comfyui' in line.lower() or 'main' in line.lower()):
                    comfyui_processes.append(line)
            
            if comfyui_processes:
                print("   Найдены процессы, связанные с ComfyUI:")
                for proc in comfyui_processes:
                    print(f"      {proc}")
            else:
                print("   ! Не найдено явных процессов ComfyUI")
        except Exception as e:
            print(f"   ! Ошибка при поиске процессов ComfyUI: {e}")
    else:
        print("   ✗ Не обнаружено процессов Python")
    
    # Проверяем подключение к API ComfyUI
    print("\n3. Проверка подключения к API ComfyUI...")
    try:
        response = requests.get("http://localhost:8188/system_stats", timeout=5)
        if response.status_code == 200:
            print("   ✓ Успешное подключение к API ComfyUI")
            try:
                stats = response.json()
                print(f"   Информация о системе: {stats}")
            except:
                print("   Не удалось получить JSON-информацию")
        else:
            print(f"   ✗ API ComfyUI вернул статус {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("   ✗ Не удалось подключиться к API ComfyUI - сервер не отвечает")
    except requests.exceptions.Timeout:
        print("   ✗ Таймаут подключения к API ComfyUI")
    except Exception as e:
        print(f"   ✗ Ошибка при подключении к API ComfyUI: {e}")
    
    # Проверяем, существует ли папка ComfyUI
    print("\n4. Проверка наличия папки ComfyUI...")
    comfyui_paths = [
        "C:\\ComfyUIDesk",
        "C:\\ComfyUI",
        os.path.expanduser("~\\ComfyUI"),
        os.path.expanduser("~\\Desktop\\ComfyUI")
    ]
    
    found_path = None
    for path in comfyui_paths:
        if os.path.exists(path) and os.path.exists(os.path.join(path, "main.py")):
            found_path = path
            print(f"   ✓ Найдена папка ComfyUI: {path}")
            break
    
    if not found_path:
        print("   ✗ Не найдена папка ComfyUI по стандартным путям")
        print("     Возможные причины:")
        print("     - ComfyUI установлен в другом месте")
        print("     - ComfyUI не установлен")
    
    # Рекомендации
    print("\n=== Рекомендации ===")
    if not check_port_availability(8188):
        print("- Убедитесь, что ComfyUI запущен на порту 8188")
        print("- Проверьте, не занят ли порт 8188 другим приложением")
    else:
        print("- Порт 8188 доступен, но ComfyUI может не отвечать на запросы")
    
    if found_path:
        print(f"- Проверьте файлы в папке {found_path} на предмет ошибок")
        print(f"- Убедитесь, что запускаете ComfyUI из правильной директории: cd {found_path}")
    
    print("- Проверьте, что все зависимости ComfyUI установлены")
    print("- Убедитесь, что запускаете ComfyUI с правильными параметрами: --listen --port 8188")

if __name__ == "__main__":
    check_comfyui_connection()