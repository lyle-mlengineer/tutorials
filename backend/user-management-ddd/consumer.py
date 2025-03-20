import json
import redis

r = redis.Redis(host="localhost", port=6379, db=0)

# youtube.authenticate(client_secret_file)

while True:
    # Blocking pop to wait for new messages
    metadata = r.brpop("alarm_queue")
    message_info = json.loads(metadata[1].decode("utf-8"))
    print(message_info)
