import sys
import os
sys.path.append('./worker')

# Print current working directory and environment
print("Current working directory:", os.getcwd())
print("Environment REDIS_JOB_QUEUE_KEY:", os.environ.get('REDIS_JOB_QUEUE_KEY', 'NOT SET'))

# Change to worker directory to ensure .env is loaded
original_cwd = os.getcwd()
os.chdir('./worker')

try:
    from config import settings
    print('Settings REDIS_JOB_QUEUE_KEY:', repr(settings.REDIS_JOB_QUEUE_KEY))
finally:
    os.chdir(original_cwd)  # Restore original directory