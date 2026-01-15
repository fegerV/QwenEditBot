import requests
import sys

def check_comfyui_status():
    """
    Проверка статуса ComfyUI сервера
    """
    comfyui_url = "http://localhost:8188"
    
    print(f"Проверка статуса ComfyUI по адресу: {comfyui_url}")
    
    try:
        # Проверяем системный статус
        response = requests.get(f"{comfyui_url}/system_stats", timeout=10)
        
        if response.status_code == 200:
            stats = response.json()
            print("✓ ComfyUI сервер запущен и доступен")
            print(f"  Системная информация: {stats}")
            return True
        else:
            print(f"✗ ComfyUI сервер вернул код {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ ComfyUI сервер недоступен - невозможно подключиться")
        print(" Убедитесь, что ComfyUI запущен на порту 850")
        return False
    except requests.exceptions.Timeout:
        print("✗ Превышено время ожидания при подключении к ComfyUI")
        return False
    except Exception as e:
        print(f"✗ Ошибка при проверке статуса ComfyUI: {e}")
        return False

def check_comfyui_queue():
    """
    Проверка очереди ComfyUI
    """
    comfyui_url = "http://localhost:8188"
    
    try:
        response = requests.get(f"{comfyui_url}/queue", timeout=10)
        
        if response.status_code == 200:
            queue_data = response.json()
            print("\n Очередь ComfyUI:")
            print(f"    Pending: {len(queue_data.get('queue_pending', []))}")
            print(f"    Running: {len(queue_data.get('queue_running', []))}")
        else:
            print(f"\n  Не удалось получить очередь: {response.status_code}")
            
    except Exception as e:
        print(f"\n  Ошибка при получении очереди: {e}")

if __name__ == "__main__":
    print("Проверка статуса ComfyUI...")
    is_running = check_comfyui_status()
    
    if is_running:
        check_comfyui_queue()
    
    print("\nПроверка завершена.")