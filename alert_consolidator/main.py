import os
import json
import logging
import time
from confluent_kafka import Consumer, Producer
from collections import defaultdict
from db.config import SessionLocal
from db.models import Alert, Enrichment, Transaction
import uuid

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "broker:29092")
TOPIC_BSCORE = "fraud_bscore_output"
TOPIC_RULE = "fraud_ai_rule_base_output"
TOPIC_ALERT = "transactions_fraud_alert"

consumer_conf = {
    'bootstrap.servers': KAFKA_BROKER,
    'group.id': 'alert-consolidator',
    'auto.offset.reset': 'earliest'
}
producer_conf = {'bootstrap.servers': KAFKA_BROKER}

consumer = Consumer(consumer_conf)
producer = Producer(producer_conf)
consumer.subscribe([TOPIC_BSCORE, TOPIC_RULE])

logging.basicConfig(level=logging.INFO)

buffer = defaultdict(dict)
JOIN_TIMEOUT = 180

# Buffer global untuk alert yang gagal insert karena transaction_id belum ada
default_alert_retry_buffer = {}
alert_retry_buffer = default_alert_retry_buffer


def update_enrichment(tx_id, bscore, rule_result):
    """
    Update enrichment table for tx_id: set bscore and rule_result (as JSONB). Only one row per transaction.
    """
    session = SessionLocal()
    try:
        enrichment = session.query(Enrichment).filter_by(transaction_id=tx_id).first()
        if enrichment:
            enrichment.bscore = bscore
            enrichment.rule_result = rule_result
            session.commit()
    finally:
        session.close()

def save_alerts(tx_id, bank_id, bscore, rule_result):
    global alert_retry_buffer
    """
    Insert alerts for tx_id based on rule_result and bscore.
    - rule_result: dict {rule_name: bool}
    - bscore: float
    Insert alert for each alert_type that matches logic:
      - combined: any(rule True) and bscore > 0.8
      - rule_only: any(rule True) and bscore <= 0.8
      - ml_only: all(rule False) and bscore > 0.8
    Allow duplicates in alert table.
    """
    session = SessionLocal()
    try:
        # Pastikan tx_id adalah UUID
        if isinstance(tx_id, str):
            try:
                tx_id_uuid = uuid.UUID(tx_id)
            except Exception:
                logging.warning(f"Skip insert alert: tx_id {tx_id} is not valid UUID")
                return
        else:
            tx_id_uuid = tx_id
        # Cek apakah transaksi ada
        if not session.query(Transaction).filter_by(id=tx_id_uuid).first():
            logging.warning(f"Buffer alert: transaction_id {tx_id} not found in transactions table, will retry.")
            # Simpan ke buffer untuk retry
            alert_retry_buffer[tx_id] = (tx_id, bank_id, bscore, rule_result, time.time())
            return
        # Insert alert row for each rule that is True
        if rule_result:
            for rule_name, is_true in rule_result.items():
                if is_true:
                    alert_type = 'combined' if bscore > 0.8 else 'rule_only'
                    logging.info(f"Insert alert: tx_id={tx_id}, bank_id={bank_id}, bscore={bscore}, rule={rule_name}, alert_type={alert_type}")
                    alert = Alert(
                        transaction_id=tx_id_uuid,
                        score=bscore,
                        rule_name=rule_name,
                        alert_type=alert_type
                    )
                    session.add(alert)
        # ML only: if no rule True and bscore > 0.8
        if (not rule_result or not any(rule_result.values())) and bscore > 0.8:
            logging.info(f"Insert alert: tx_id={tx_id}, bank_id={bank_id}, bscore={bscore}, rule=None, alert_type=ml_only")
            alert = Alert(
                transaction_id=tx_id_uuid,
                score=bscore,
                rule_name=None,
                alert_type='ml_only'
            )
            session.add(alert)
        session.commit()
    finally:
        session.close()

def publish_alert(data,rule_result,bscore):
    save_alerts(data.get('transaction_id'), data.get('bank_id'), bscore, rule_result)
    alert = {
        "transaction_id": data.get('transaction_id'),
        "source_transaction_id": data.get('source_transaction_id'),
        "source_user_id": data.get('source_user_id'),
        "source_account_id": data.get('source_account_id'),
        "source_merchant_code": data.get('source_merchant_code'),
        "amount": data.get('amount'),
        "currency": data.get('currency'),
        "transaction_type": data.get('transaction_type'),
        "transaction_time": data.get('transaction_time'),
        "location": data.get('location'),
        "device_id": data.get('device_id'),
        "device_type": data.get('device_type'),
        "os_version": data.get('os_version'),
        "app_version": data.get('app_version'),
        "is_emulator": data.get('is_emulator'),
        "ip_address": data.get('ip_address'),
        "ip_location": data.get('ip_location'),
        "is_proxy": data.get('is_proxy'),
        "notes": data.get('notes'),
        "bank_id": data.get('bank_id'),
        "bscore": bscore,
        "rule_result": [k for k, v in rule_result.items() if v]    
    }
    producer.produce(TOPIC_ALERT, json.dumps(alert).encode('utf-8'))
    logging.info(f"Published alert: {alert}")

def main():
    last_cleanup = time.time()
    try:
        while True:
            # add log
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                logging.error(f"Consumer error: {msg.error()}")
                continue
            event = json.loads(msg.value().decode('utf-8'))
            logging.info(f"📥 Received tx: {event.get('transaction_id'), event.get('bscore'), event.get('rule_result')}")
            logging.info(f"Topic: {msg.topic()}")
            topic = msg.topic()
            tx_id = event.get('transaction_id')
            key = tx_id
            now = time.time()
            if topic == TOPIC_BSCORE:
                buffer[key]['bscore'] = event.get('bscore')
                buffer[key]['event'] = event  # <-- simpan event lengkap!
            elif topic == TOPIC_RULE:
                buffer[key]['rule'] = event.get('rule_result')
            buffer[key]['last_update'] = now
            if 'bscore' in buffer[key] and 'rule' in buffer[key]:
                bscore_val = buffer[key].get('bscore')
                rule_val = buffer[key].get('rule')
                merged_data = {**buffer[key].get('event', {}), 'transaction_id': tx_id}

                # Update enrichment selalu dilakukan
                update_enrichment(tx_id, bscore_val, rule_val)

                # Insert alert hanya kalau memenuhi kondisi
                if (bscore_val is not None and bscore_val > 0.8) or (rule_val is not None and rule_val != {}):
                    publish_alert(merged_data, rule_val, bscore_val)
                else:
                    logging.info(f"Skipped alert insert for tx_id={tx_id} due to low score and empty rule")
                del buffer[key]
            if now - last_cleanup > 10:
                expired = [k for k, v in buffer.items() if now - v['last_update'] > JOIN_TIMEOUT]
                for k in expired:
                    v = buffer[k]
                    logging.warning(f"Partial alert: timeout join for {k}, bscore={v.get('bscore')}, rule={v.get('rule')}")
                    publish_alert({'transaction_id': k}, v.get('rule'), v.get('bscore'))
                    del buffer[k]
                # Retry alert buffer (jika ada alert yang gagal insert karena transaction_id belum ada)
                retry_keys = list(alert_retry_buffer.keys())
                for tx_id in retry_keys:
                    tx_id_val, bank_id_val, bscore_val, rule_result_val, ts = alert_retry_buffer[tx_id]
                    logging.info(f"Retry insert alert for tx_id={tx_id}")
                    save_alerts(tx_id_val, bank_id_val, bscore_val, rule_result_val)
                last_cleanup = now

    except KeyboardInterrupt:
        logging.info("Stopping alert consolidator...")
    finally:
        producer.flush()
        consumer.close()

if __name__ == "__main__":
    main()
