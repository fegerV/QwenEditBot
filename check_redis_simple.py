import redis

# Connect to Redis
r = redis.Redis(host='localhost', port=6379, password='', db=0, decode_responses=False)

# Check both queue lengths
qwenedit_len = r.llen(b'qwenedit:job_queue')
job_len = r.llen(b'job_queue')

print(f'Length of qwenedit:job_queue: {qwenedit_len}')
print(f'Length of job_queue: {job_len}')

# Close connection
r.close()