import os
import json
import logging
from confluent_kafka import Consumer, Producer
import time

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "broker:29092")
TOPIC_IN = "fraud_investigation"
TOPIC_RULE_BASE = "fraud_ai_rule_base_input"
TOPIC_BSCORE = "fraud_bscore_input"

consumer_conf = {
    'bootstrap.servers': KAFKA_BROKER,
    'group.id': 'fraud-dispatcher',
    'auto.offset.reset': 'earliest'
}
producer_conf = {
    'bootstrap.servers': KAFKA_BROKER,
    'linger.ms': 100,
    'batch.size': 32768,
    'compression.type': 'snappy'
}

consumer = Consumer(consumer_conf)
producer = Producer(producer_conf)
consumer.subscribe([TOPIC_IN])

logging.basicConfig(level=logging.INFO)

def delivery_report(err, msg):
    if err is not None:
        logging.error(f"Delivery failed: {err}")
    else:
        logging.debug(f"Message delivered to {msg.topic()} [{msg.partition()}] offset {msg.offset()}")

def dispatch(event):
    value = json.dumps(event).encode('utf-8')
    producer.produce(TOPIC_RULE_BASE, value, callback=delivery_report)
    producer.produce(TOPIC_BSCORE, value, callback=delivery_report)

def main():
    logging.info("Fraud Dispatcher started.")
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                logging.error(f"Consumer error: {msg.error()}")
                continue
            event = json.loads(msg.value().decode('utf-8'))
            dispatch(event)
            logging.info(f"Dispatched event {event.get('transaction_id')}")
    except KeyboardInterrupt:
        logging.info("Stopping dispatcher...")
    finally:
        producer.flush()
        consumer.close()

if __name__ == "__main__":
    main()
