import requests
import sys

def check_job_status(prompt_id):
    """
    Проверка статуса задания в ComfyUI по его ID
    
    Args:
        prompt_id (str): ID задания в ComfyUI
    """
    comfyui_url = "http://localhost:8188"
    
    try:
        # Формируем URL для запроса статуса задания
        url = f"{comfyui_url}/history/{prompt_id}"
        
        response = requests.get(url)
        
        if response.status_code == 20:
            history_data = response.json()
            
            if prompt_id in history_data:
                job_info = history_data[prompt_id]
                
                print(f"Статус задания {prompt_id}:")
                print(f"- Статус: {'Выполнено' if 'outputs' in job_info else 'В процессе'}")
                
                if 'outputs' in job_info:
                    print("- Результаты:")
                    for node_id, node_output in job_info['outputs'].items():
                        if 'images' in node_output:
                            for img_info in node_output['images']:
                                print(f"  - Изображение: {img_info['filename']}")
                else:
                    print("- Результаты пока не готовы")
            else:
                print(f"Задание с ID {prompt_id} не найдено в истории")
        else:
            print(f"Ошибка при запросе к ComfyUI: {response.status_code}")
            print(f"Ответ: {response.text}")
            
    except Exception as e:
        print(f"Ошибка при проверке статуса задания: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Использование: python check_comfyui_job_status.py <prompt_id>")
        print("Пример: python check_comfyui_job_status.py 1234567890")
        sys.exit(1)
    
    prompt_id = sys.argv[1]
    check_job_status(prompt_id)