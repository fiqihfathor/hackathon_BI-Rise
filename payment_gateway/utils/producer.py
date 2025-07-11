from confluent_kafka.serialization import StringSerializer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka import SerializingProducer

import uuid
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# SCHEMA_REGISTRY_URL = os.getenv("SCHEMA_REGISTRY_URL", "http://localhost:8081")
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
TOPIC = "transactions_raw"

# schema_registry_conf = {"url": SCHEMA_REGISTRY_URL}
# schema_registry_client = SchemaRegistryClient(schema_registry_conf)

# subject = f"{TOPIC}-value"
# registered_schema = schema_registry_client.get_latest_version(subject)
# schema_str = registered_schema.schema.schema_str

def to_dict(data, ctx):
    return data

# avro_serializer = AvroSerializer(
#     schema_registry_client,
#     schema_str,
#     to_dict=to_dict,
# )

producer_conf = {
    "bootstrap.servers": KAFKA_BROKER,
    "key.serializer": StringSerializer("utf_8"),
    "value.serializer": StringSerializer("utf_8"),
}

producer = SerializingProducer(producer_conf)

def delivery_report(err, msg):
    try:
        if err is not None:
            print(f"[❌] Delivery failed for message {msg.key()}: {err}")
        else:
            print(f"[✅] Delivered message {msg.key()} to {msg.topic()} [{msg.partition()}] @ {msg.offset()}")
    except Exception as e:
        print(f"[⚠️] Exception in delivery_report callback: {e}")

import json

def send_transaction(data: dict):
    stringified_data = {k: str(v) for k, v in data.items()}
    producer.produce(
        topic=TOPIC,
        key=stringified_data["transaction_id"],
        value=json.dumps(stringified_data),
        on_delivery=delivery_report
    )



import threading
import time

FLUSH_INTERVAL = 5  # detik, bisa diatur ke 10 juga

def periodic_flush():
    while True:
        time.sleep(FLUSH_INTERVAL)
        try:
            producer.flush(timeout=1)  # flush dengan timeout supaya gak blocking lama
            print("[ℹ️] Kafka producer flushed")
        except Exception as e:
            print(f"[⚠️] Error flushing Kafka producer: {e}")

flush_thread = threading.Thread(target=periodic_flush, daemon=True)
flush_thread.start()

import atexit

def shutdown_handler():
    print("Flushing Kafka producer before shutdown...")
    producer.flush()
    producer.poll(0)

atexit.register(shutdown_handler)