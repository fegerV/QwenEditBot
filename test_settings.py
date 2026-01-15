import sys
import os
# Add worker directory to path
sys.path.insert(0, os.path.join(os.getcwd(), 'worker'))

try:
    from worker.config import settings
    print('Settings REDIS_JOB_QUEUE_KEY:', repr(settings.REDIS_JOB_QUEUE_KEY))
except Exception as e:
    print(f"Error importing settings: {e}")
    import traceback
    traceback.print_exc()