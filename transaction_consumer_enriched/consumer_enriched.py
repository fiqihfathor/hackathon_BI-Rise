import json
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from confluent_kafka import Consumer, KafkaError
from processor import upsert_enrichment, User, Transaction
from db_session import SessionLocal
from storage import get_minio_client, save_to_minio, save_to_minio_dlq

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

conf = {
    'bootstrap.servers': 'broker:29092',
    'group.id': 'consumer-enriched',
    'auto.offset.reset': 'earliest'
}
topic = 'transactions_enriched'

consumer = Consumer(conf)
consumer.subscribe([topic])

MAX_RETRY = 5
RETRY_DELAY = 10  # detik

def check_dependencies(session, event):
    user_id = event.get('source_user_id')
    transaction_id = event.get('transaction_id')
    bank_id = event.get('bank_id')
    user = session.query(User).filter_by(source_user_id=user_id, source_bank_id=bank_id).first()
    txn = session.query(Transaction).filter_by(id=transaction_id).first()
    return all([user, txn])

def process_event(event, minio_client, minio_bucket):
    session = SessionLocal()
    try:
        # Simpan raw ke MinIO (optional)
        save_to_minio(event, minio_client, minio_bucket)
        
        user_obj = session.query(User).filter_by(source_user_id=event.get('source_user_id'), source_bank_id=event.get('bank_id')).first()
        user_id = user_obj.user_id if user_obj else None
        transaction_id = event.get('transaction_id')
        success = False
        last_exc = None

        for attempt in range(1, MAX_RETRY + 1):
            session.expire_all()
            if check_dependencies(session, event):
                try:
                    upsert_enrichment(session, event, user_id, transaction_id)
                    session.commit()
                    logging.info(f"Upserted enrichment for transaction {transaction_id}")
                    success = True
                    break
                except Exception as e:
                    session.rollback()
                    last_exc = e
                    logging.error(f"Failed to process enrichment entity (attempt {attempt}): {e}")
            else:
                logging.warning(f"Dependency missing for transaction {transaction_id}, attempt {attempt}/{MAX_RETRY}")
            time.sleep(RETRY_DELAY)

        if not success:
            reason = f"Failed after {MAX_RETRY} attempts. Last error: {last_exc}"
            save_to_minio_dlq(event, minio_client, minio_bucket, reason=reason)
            logging.error(f"Event sent to DLQ for transaction {transaction_id}: {reason}")
    except Exception as e:
        logging.error(f"Exception in process_event: {e}")
    finally:
        session.close()

def main():
    minio_bucket = os.getenv('MINIO_BUCKET')
    minio_client = get_minio_client()
    logging.info("Starting Confluent Kafka consumer for ENRICHED...")

    executor = ThreadPoolExecutor(max_workers=4)
    futures = []

    try:
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
                # Submit ke thread pool untuk proses async
                future = executor.submit(process_event, event, minio_client, minio_bucket)
                futures.append(future)
                # Bersihkan futures yang sudah selesai supaya tidak menumpuk
                futures = [f for f in futures if not f.done()]
            except Exception as e:
                logging.error(f"Failed to process message: {e}")
    except KeyboardInterrupt:
        logging.info("Stopping enriched consumer...")
    finally:
        consumer.close()
        executor.shutdown(wait=True)
        logging.info("Enriched consumer closed cleanly.")

if __name__ == "__main__":
    main()
