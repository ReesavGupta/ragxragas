import redis

# Connect to local Redis instance (default Docker port)
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Test connection
try:
    redis_client.ping()
    print("Connected to Redis!")
except redis.ConnectionError:
    print("Failed to connect to Redis.") 