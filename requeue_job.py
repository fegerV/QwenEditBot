import redis
import json
import asyncio

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Get job 193 from backend
from worker.services.backend_client import BackendAPIClient

async def requeue():
    client = BackendAPIClient()
    job = await client.get_job(193)
    
    if job:
        print(f"Job 193: {job}")
        # Add to Redis queue with retry count
        job['retry_count'] = 1
        r.rpush('qwenedit:job_queue', json.dumps(job))
        print("Job 193 re-added to Redis queue!")
        print(f"Queue length now: {r.llen('qwenedit:job_queue')}")
    else:
        print("Could not find job 193")

asyncio.run(requeue())

