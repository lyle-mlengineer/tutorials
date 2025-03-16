import redis

# Connect to local Redis instance
redis_client = redis.StrictRedis(host="localhost", port=6379, db=0)
channel = "events"
pubsub = redis_client.pubsub()
pubsub.subscribe(channel)
print(f"Subscribed to {channel}. Waiting for messages...")
for message in pubsub.listen():
    if message["type"] == "message":
        print(f"Received: {message['data'].decode('utf-8')}")
