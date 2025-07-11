import json
import logging
from confluent_kafka import Consumer, KafkaException, KafkaError
from processor import dict_to_transaction, upsert_transaction, upsert_user, upsert_device, upsert_ipaddress, upsert_account, upsert_merchant
from db_session import SessionLocal
from storage import get_minio_client, save_to_minio
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

conf = {
    'bootstrap.servers': 'broker:29092',
    'group.id': 'consumer-raw',
    'auto.offset.reset': 'earliest'
}
topic = 'transactions_raw'

consumer = Consumer(conf)
consumer.subscribe([topic])

def main():
    minio_bucket = os.getenv('MINIO_BUCKET')
    minio_client = get_minio_client()

    logging.info("Starting Confluent Kafka consumer...")

    try:
        session = SessionLocal()
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    logging.error(f"Kafka error: {msg.error()}")
                    continue
            try:
                event = json.loads(msg.value().decode('utf-8'))
                # 1. Save raw event to MinIO
                save_to_minio(event, minio_client, minio_bucket)
                # 2. Process and upsert user, device, ipaddress, then transaction
                user = None
                device = None
                try:
                    user = upsert_user(session, event)
                    device = upsert_device(session, event, user.user_id if user else None)
                    account = upsert_account(session, event, user.user_id if user else None)
                    merchant = upsert_merchant(session, event, event.get('bank_id'))
                    upsert_ipaddress(session, event, user.user_id if user else None)
                    txn = dict_to_transaction(event, user=user, device=device, account=account, merchant=merchant)
                    upsert_transaction(session, txn)
                    session.commit()
                    logging.info(f"Saved to MinIO and upserted user/device/account/merchant/ip/txn {txn.transaction_id}")
                except Exception as e:
                    session.rollback()
                    logging.error(f"Failed to process DB entities: {e}")
            except Exception as e:
                logging.error(f"Failed to process message: {e}")
    except KeyboardInterrupt:
        logging.info("Stopping consumer...")
    finally:
        consumer.close()
        session.close()
        logging.info("Consumer closed cleanly.")

if __name__ == "__main__":
    main()
