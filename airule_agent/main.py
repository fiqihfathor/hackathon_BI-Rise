import os
import json
import logging
import redis
from confluent_kafka import Consumer, Producer
from dotenv import load_dotenv

from dsl_rules import evaluate_rule, get_context
from scheduler import start_rule_refresh_scheduler, start_blacklist_refresh_scheduler
from db.config import SessionLocal

load_dotenv()

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "broker:29092")
INPUT_TOPIC = os.getenv("AIRULE_KAFKA_INPUT", "fraud_ai_rule_base_input")
OUTPUT_TOPIC = os.getenv("AIRULE_KAFKA_OUTPUT", "fraud_ai_rule_base_output")
REDIS_URL = os.getenv("AIRULE_REDIS_URL", "redis://redis:6379/0")
REDIS_RULES_KEY = os.getenv("AIRULE_REDIS_RULES_KEY", "rules:all")

logging.basicConfig(level=logging.INFO)

redis_client = redis.Redis.from_url(REDIS_URL)

session = SessionLocal()
start_rule_refresh_scheduler(session, redis_client)
start_blacklist_refresh_scheduler(session, redis_client)

consumer = Consumer({
    'bootstrap.servers': KAFKA_BROKER,
    'group.id': 'airule-agent',
    'auto.offset.reset': 'earliest'
})
consumer.subscribe([INPUT_TOPIC])
producer = Producer({'bootstrap.servers': KAFKA_BROKER,'linger.ms': 100})

logging.info("airule_agent listening...")

def run_dsl_rule(tx, redis_client, redis_key=REDIS_RULES_KEY, context=None):
    """
    Ambil rules dari Redis, evaluasi semua terhadap transaksi tx.
    Lebih robust: handle error parsing JSON, rule tanpa rule_dsl, dan pastikan return boolean.
    """
    rules_json = redis_client.get(redis_key)
    if not rules_json:
        logging.warning("No rules found in Redis, fallback always True")
        return {}
    try:
        rules = json.loads(rules_json)
    except Exception as e:
        logging.error(f"Failed to parse rules JSON from Redis: {e}")
        return {}
    results = {}
    for rule in rules:
        rule_name = rule.get("rule_name") or f'rule_{rule.get("id")}'
        try:
            rule_dsl_raw = rule.get("rule_dsl")
            if not rule_dsl_raw:
                logging.error(f"Rule {rule_name} missing 'rule_dsl' field.")
                results[rule_name] = False
                continue
            try:
                rule_dsl = json.loads(rule_dsl_raw) if isinstance(rule_dsl_raw, str) else rule_dsl_raw
            except Exception as e:
                logging.error(f"Rule {rule_name} has invalid JSON in 'rule_dsl': {e}")
                results[rule_name] = False
                continue
            result = evaluate_rule(rule_dsl, tx, context)
            results[rule_name] = bool(result)
        except Exception as e:
            logging.error(f"Rule evaluation error ({rule_name}): {e}")
            results[rule_name] = False
    return results

context = get_context()
flush_counter = 0
FLUSH_EVERY = 10

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            logging.error(msg.error())
            continue
        try:
            event = json.loads(msg.value().decode())
            logging.info(f"airule_agent received: {event}")
            rule_result = run_dsl_rule(event, redis_client, REDIS_RULES_KEY, context)
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
                "rule_result": rule_result
            }
            producer.produce(OUTPUT_TOPIC, json.dumps(output).encode('utf-8'))
            producer.flush()
            logging.info(f"airule_agent sent: {output}")
        except Exception as e:
            logging.error(f"Error processing event: {e}")
except KeyboardInterrupt:
    logging.info("Shutting down...")
finally:
    producer.flush()
    consumer.close()