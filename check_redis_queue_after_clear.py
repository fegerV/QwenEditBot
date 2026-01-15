import asyncio
import json
from worker.redis_client import redis_client

async def check_redis_queue_after_clear():
    """
    Проверка очереди заданий в Redis после очистки
    """
    print("=== Проверка очереди заданий в Redis после очистки ===\n")
    
    # Подключаемся к Redis
    await redis_client.connect()
    
    # Проверим количество заданий в очереди
    queue_length = await redis_client.redis.llen("qwenedit:job_queue")
    print(f"Количество заданий в Redis очереди: {queue_length}")
    
    if queue_length > 0:
        # Получим задания из очереди
        pending_jobs = await redis_client.get_pending_jobs(limit=100)  # Получим до 100 заданий
        print(f"\nНайдено {len(pending_jobs)} заданий в очереди:")
        for i, job in enumerate(pending_jobs):
            print(f"  {i+1}. ID: {job.get('id', 'N/A')}, User: {job.get('user_id', 'N/A')}, Status: {job.get('status', 'N/A')}")
            print(f"      Image: {job.get('image_path', 'N/A')}")
            print(f"      Prompt: {job.get('prompt', 'N/A')[:100]}...")  # Первые 100 символов промпта
            print()
    else:
        print("\nОчередь заданий пуста. Это нормально после очистки очереди.")
        print("Новые задания будут отображаться корректно после их добавления.")
    
    # Также проверим другие ключи в Redis, связанные с заданиями
    print("\n=== Другие ключи, связанные с заданиями ===")
    job_result_keys = await redis_client.redis.keys(b"job_result:*")  # Используем байтовую строку
    if job_result_keys:
        print(f"Найдено {len(job_result_keys)} ключей с результатами заданий:")
        for key in job_result_keys:
            result_data = await redis_client.redis.get(key)
            try:
                result_obj = json.loads(result_data.decode('utf-8'))  # Декодируем байты в строку
                print(f"  - {key.decode('utf-8')}: {result_obj}")
            except Exception as e:
                print(f"  - {key.decode('utf-8')}: Ошибка при разборе ({e})")
    else:
        print("Ключи с результатами заданий не найдены")
    
    # Закрываем соединение с Redis
    await redis_client.close()
    
    print("\n=== Проверка завершена ===")

if __name__ == "__main__":
    asyncio.run(check_redis_queue_after_clear())