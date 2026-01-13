import asyncio
import sys
import os

# Add project root to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'worker'))

from backend.redis_client import redis_client as backend_redis_client
from worker.redis_client import redis_client as worker_redis_client
from worker.config import settings as worker_settings
from backend.app.config import settings as backend_settings


async def test_redis_connection():
    """Test Redis connection from both backend and worker perspectives"""
    print("Testing Redis connection...")
    
    try:
        # Test backend Redis connection
        print("\n1. Testing backend Redis connection...")
        await backend_redis_client.connect()
        print("+ Backend Redis connection successful")
        
        # Test basic Redis operations
        test_key = "test:connection"
        test_value = "Hello from backend"
        
        await backend_redis_client.redis.set(test_key, test_value)
        retrieved_value = await backend_redis_client.redis.get(test_key)
        
        if retrieved_value == test_value:
            print("+ Backend Redis read/write successful")
        else:
            print("- Backend Redis read/write failed")
            
        # Clean up test key
        await backend_redis_client.redis.delete(test_key)
        
    except Exception as e:
        print(f"- Backend Redis connection failed: {e}")
        return False
    
    try:
        # Test worker Redis connection
        print("\n2. Testing worker Redis connection...")
        await worker_redis_client.connect()
        print("+ Worker Redis connection successful")
        
        # Test basic Redis operations
        test_key = "test:connection"
        test_value = "Hello from worker"
        
        await worker_redis_client.redis.set(test_key, test_value)
        retrieved_value = await worker_redis_client.redis.get(test_key)
        
        if retrieved_value == test_value:
            print("+ Worker Redis read/write successful")
        else:
            print("- Worker Redis read/write failed")
            
        # Clean up test key
        await worker_redis_client.redis.delete(test_key)
        
    except Exception as e:
        print(f"- Worker Redis connection failed: {e}")
        return False
    
    try:
        # Test cross-component communication
        print("\n3. Testing cross-component communication...")
        
        # Set a value using backend client
        shared_key = "test:shared"
        shared_value = "Shared data"
        
        await backend_redis_client.redis.set(shared_key, shared_value)
        print("+ Value set using backend client")
        
        # Retrieve using worker client
        retrieved_value = await worker_redis_client.redis.get(shared_key)
        if retrieved_value == shared_value:
            print("+ Value retrieved successfully using worker client")
        else:
            print("- Cross-component retrieval failed")
            return False
            
        # Clean up
        await worker_redis_client.redis.delete(shared_key)
        print("+ Cross-component communication test successful")
        
    except Exception as e:
        print(f"- Cross-component communication failed: {e}")
        return False
    
    try:
        # Test job queue functionality
        print("\n4. Testing job queue functionality...")
        
        queue_key = worker_settings.REDIS_JOB_QUEUE_KEY
        test_job = {
            'id': 1,
            'user_id': 123,
            'image_path': '/test/path.jpg',
            'prompt': 'Test prompt',
            'status': 'queued',
            'created_at': '2023-01-01T00:00:00',
            'updated_at': '2023-01-01T00:00:00'
        }
        
        # Add job to queue using backend client
        import json
        await backend_redis_client.redis.lpush(queue_key, json.dumps(test_job))
        print("+ Job added to queue using backend client")
        
        # Get job from queue using worker client
        job_json = await worker_redis_client.redis.lpop(queue_key)
        retrieved_job = json.loads(job_json)
        
        if retrieved_job['id'] == test_job['id']:
            print("+ Job retrieved from queue using worker client")
        else:
            print("- Job retrieval failed")
            return False
            
        print("+ Job queue functionality test successful")
        
    except Exception as e:
        print(f"- Job queue functionality test failed: {e}")
        return False
    
    print("\n+ All Redis connection tests passed!")
    return True


async def main():
    success = await test_redis_connection()
    
    if success:
        print("\nRedis configuration is working correctly.")
        print("The system is ready for deployment with Redis-based job queuing.")
    else:
        print("\nRedis configuration has issues that need to be resolved.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())