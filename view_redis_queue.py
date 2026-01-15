import asyncio
import json
from worker.config import settings
from redis.asyncio import Redis


async def view_redis_queue():
    """View the contents of the Redis job queue"""
    redis = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        db=settings.REDIS_DB,
        decode_responses=False
    )
    
    try:
        # Get all items in the queue
        queue_items = await redis.lrange(settings.REDIS_JOB_QUEUE_KEY, 0, -1)
        
        print(f"Found {len(queue_items)} items in Redis queue '{settings.REDIS_JOB_QUEUE_KEY}':")
        
        for i, item in enumerate(queue_items):
            try:
                # Decode and parse the JSON
                decoded_item = item.decode('utf-8')
                job_data = json.loads(decoded_item)
                print(f"\nItem {i + 1}:")
                print(json.dumps(job_data, indent=2, ensure_ascii=False))
            except Exception as e:
                print(f"\nItem {i + 1} (raw): {item}")
                print(f"Error parsing JSON: {e}")
        
        # Also check the length of the queue
        queue_length = await redis.llen(settings.REDIS_JOB_QUEUE_KEY)
        print(f"\nTotal queue length: {queue_length}")
        
    except Exception as e:
        print(f"Error accessing Redis: {e}")
    finally:
        await redis.close()


if __name__ == "__main__":
    asyncio.run(view_redis_queue())