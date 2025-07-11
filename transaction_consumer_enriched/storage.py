import os
import json
import io
from minio import Minio
from minio.error import S3Error
import logging

def get_minio_client():
    minio_host = os.getenv("MINIO_HOST", "minio")
    minio_port = os.getenv("MINIO_PORT", "9000")
    minio_endpoint = f"{minio_host}:{minio_port}"
    minio_access_key = os.getenv("MINIO_ACCESS_KEY")
    minio_secret_key = os.getenv("MINIO_SECRET_KEY")
    return Minio(
        minio_endpoint,
        access_key=minio_access_key,
        secret_key=minio_secret_key,
        secure=False
    )

def save_to_minio(record: dict, minio_client: Minio, bucket: str):
    object_name = f"enriched/{record.get('transaction_id', 'unknown')}.json"
    data = json.dumps(record).encode("utf-8")
    data_stream = io.BytesIO(data)
    try:
        if not minio_client.bucket_exists(bucket):
            minio_client.make_bucket(bucket)
        minio_client.put_object(
            bucket,
            object_name,
            data_stream,
            length=len(data),
        )
        logging.info(f"Saved transaction {record.get('transaction_id', 'unknown')} to MinIO.")
    except S3Error as e:
        logging.error(f"Failed to save to MinIO: {e}")

def save_to_minio_dlq(record: dict, minio_client: Minio, bucket: str, reason: str = None):
    """
    Simpan event gagal ke MinIO pada folder dlq/ dengan nama file unik (pakai transaction_id dan timestamp).
    """
    import datetime
    ts = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%S%fZ')
    transaction_id = record.get('transaction_id', 'unknown')
    object_name = f"dlq/{transaction_id}_{ts}.json"
    dlq_record = {
        "event": record,
        "reason": reason,
        "timestamp": ts
    }
    data = json.dumps(dlq_record, ensure_ascii=False).encode("utf-8")
    data_stream = io.BytesIO(data)
    try:
        if not minio_client.bucket_exists(bucket):
            minio_client.make_bucket(bucket)
        minio_client.put_object(
            bucket,
            object_name,
            data_stream,
            length=len(data),
        )
        logging.info(f"Saved DLQ event {transaction_id} to MinIO DLQ as {object_name}.")
    except S3Error as e:
        logging.error(f"Failed to save DLQ to MinIO: {e}")
