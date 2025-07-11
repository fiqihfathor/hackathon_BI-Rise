import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from faker import Faker
import uuid
import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from db.models import Base, DeviceUsageLog, User, Device
from db.config import SYNC_DATABASE_URL
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

fake = Faker()
engine = create_engine(SYNC_DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(engine)

def generate_dummy_device_logs(n=200):
    users = session.query(User).limit(n).all()
    devices = session.query(Device).limit(n).all()
    logs = []

    for _ in range(n):
        user = fake.random_element(users)
        user_devices = [d for d in devices if d.user_id == user.user_id]
        if not user_devices:
            continue

        device = fake.random_element(user_devices)
        ip = fake.ipv4_public()
        location = fake.city()

        log = DeviceUsageLog(
            log_id=uuid.uuid4(),
            user_id=user.user_id,
            device_id=device.device_id,
            ip_address=ip,
            login_time=fake.date_time_between(start_date='-1y', end_date='now'),
            location=location
        )
        logs.append(log)
    return logs

def insert_logs(logs):
    session.bulk_save_objects(logs)
    session.commit()

if __name__ == "__main__":
    logs = generate_dummy_device_logs(10000)
    insert_logs(logs)
    print(f"{len(logs)} device usage logs berhasil dimasukkan.")
