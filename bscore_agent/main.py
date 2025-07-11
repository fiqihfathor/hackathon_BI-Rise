import os
import json
import logging
import time
from confluent_kafka import Consumer, Producer

# --- BScore calculation ---
def calculate_bscore(event):
    score = 0.0
    if event.get('is_weekend', False):
        score += 10
    hour = event.get('hour_of_day', 12)
    if hour >= 22 or hour <= 5:
        score += 15
    if event.get('txn_count_5min', 0) > 10:
        score += 20
    if event.get('txn_amount_sum_5min', 0.0) > 100_000_000:
        score += 25
    if event.get('is_proxy', 'False').lower() == 'true':
        score += 30
    if float(event.get('amount', 0)) > 10_000_000:
        score += 40
    return min(score, 100)

# --- Kafka config ---
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "broker:29092")
INPUT_TOPIC = "fraud_bscore_input"
OUTPUT_TOPIC = "fraud_bscore_output"

consumer = Consumer({
    'bootstrap.servers': KAFKA_BROKER,
    'group.id': 'bscore-agent',
    'auto.offset.reset': 'earliest'
})
producer = Producer({
    'bootstrap.servers': KAFKA_BROKER,
    'linger.ms': 100
})

consumer.subscribe([INPUT_TOPIC])
logging.basicConfig(level=logging.INFO)

# --- Callback untuk cek sukses/fail ---
def delivery_report(err, msg):
    if err is not None:
        logging.error(f"❌ Delivery failed: {err}")
    else:
        logging.info(f"✅ Produced to {msg.topic()} [partition {msg.partition()}] @ offset {msg.offset()}")

# --- Main loop ---
logging.info("🔍 bscore_agent started and listening...")

last_flush = time.time()
FLUSH_INTERVAL = 5  # seconds

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            logging.error(f"Consumer error: {msg.error()}")
            continue

        event = json.loads(msg.value().decode())
        logging.info(f"📥 Received tx: {event.get('transaction_id')}")

        score = calculate_bscore(event)
        output = {
            "transaction_id": event.get("transaction_id"),
            "source_transaction_id": event.get("source_transaction_id"),
            "source_user_id": event.get("source_user_id"),
            "source_account_id": event.get("source_account_id"),
            "source_merchant_code": event.get("source_merchant_code"),
            "amount": event.get("amount"),
            "currency": event.get("currency"),
            "transaction_type": event.get("transaction_type"),
            "transaction_time": event.get("transaction_time"),
            "location": event.get("location"),
            "device_id": event.get("device_id"),
            "device_type": event.get("device_type"),
            "os_version": event.get("os_version"),
            "app_version": event.get("app_version"),
            "is_emulator": event.get("is_emulator"),
            "ip_address": event.get("ip_address"),
            "ip_location": event.get("ip_location"),
            "bank_id": event.get("bank_id"),
            "notes": event.get("notes"),
            "device_type_category": event.get("device_type_category"),
            "ip_is_private": event.get("ip_is_private"),
            "is_night": event.get("is_night"),
            "day_of_week": event.get("day_of_week"),
            "is_weekend": event.get("is_weekend"),
            "hour_of_day": event.get("hour_of_day"),
            "amount_idr": event.get("amount_idr"),
            "txn_count_5min": event.get("txn_count_5min"),
            "txn_amount_sum_5min": event.get("txn_amount_sum_5min"),
            "is_proxy": event.get("is_proxy"),
            "bscore": score
        }

        producer.produce(
            OUTPUT_TOPIC,
            json.dumps(output).encode('utf-8'),
            callback=delivery_report
        )
        producer.poll(0)  # process delivery report callback

        # flush periodik
        now = time.time()
        if now - last_flush > FLUSH_INTERVAL:
            logging.info("⏳ Flushing producer buffer...")
            producer.flush()
            last_flush = now

except KeyboardInterrupt:
    logging.info("⛔ Stopping bscore_agent...")

finally:
    logging.info("✅ Final flush and cleanup...")
    producer.flush()
    consumer.close()
