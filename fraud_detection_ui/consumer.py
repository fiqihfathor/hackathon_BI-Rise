import os
import redis
import json
from confluent_kafka import Consumer

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "broker:29092")
TOPIC_ALERT = "transactions_fraud_alert"
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_KEY = "fraud_alerts"

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

consumer_conf = {
    'bootstrap.servers': KAFKA_BROKER,
    'group.id': 'dashboard-streamlit',
    'auto.offset.reset': 'latest'
}
consumer = Consumer(consumer_conf)
consumer.subscribe([TOPIC_ALERT])

print("[dashboard_streamlit] Kafka consumer started...")

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue
        event = json.loads(msg.value().decode('utf-8'))
        # Simpan ke Redis (push ke depan, trim jika >1000)
        r.lpush(REDIS_KEY, json.dumps(event))
        r.ltrim(REDIS_KEY, 0, 999)
        print(f"Cached alert: {event.get('transaction_id')}")
except KeyboardInterrupt:
    print("Stopping dashboard consumer...")
finally:
    consumer.close()
