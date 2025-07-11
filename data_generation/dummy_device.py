import sys
import os
import uuid
import datetime
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db.models import Base, User, Device
from db.config import SYNC_DATABASE_URL

fake = Faker()

engine = create_engine(SYNC_DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(engine)

def generate_dummy_devices(n=300000):
    devices = []
    users = session.query(User).all()
    if not users:
        raise Exception("Data users belum ada, generate dummy user dulu.")

    device_types = ['Android', 'iOS', 'Web', 'Windows', 'macOS']
    os_versions = {
        'Android': ['11', '12', '13'],
        'iOS': ['14', '15', '16'],
        'Web': ['Chrome 110', 'Firefox 105', 'Edge 100'],
        'Windows': ['10', '11'],
        'macOS': ['10.15', '11.0', '12.0']
    }

    for i in range(n):
        user = fake.random_element(users)
        device_type = fake.random_element(device_types)
        os_version = fake.random_element(os_versions[device_type])
        app_version = f"{fake.random_int(1, 5)}.{fake.random_int(0, 9)}.{fake.random_int(0, 9)}"
        is_emulator = fake.boolean(chance_of_getting_true=5)

        device = Device(
            device_id=str(uuid.uuid4()),
            user_id=user.user_id,
            device_type=device_type,
            os_version=os_version,
            app_version=app_version,
            is_emulator=is_emulator,
            created_at=fake.date_time_between(start_date='-3y', end_date='now')
        )
        devices.append(device)

        if i % 10000 == 0 and i != 0:
            fake.unique.clear()
            print(f"Generated {i} devices...")

    return devices

def insert_devices(devices, batch_size=10000):
    print("🧹 Menghapus data device lama...")
    session.query(Device).delete()
    session.commit()

    print(f"🚀 Insert {len(devices)} devices dalam batch {batch_size}...")
    for i in range(0, len(devices), batch_size):
        batch = devices[i:i + batch_size]
        session.bulk_save_objects(batch)
        session.commit()
        print(f"✅ Inserted devices {i+1} to {i+len(batch)}")

if __name__ == "__main__":
    dummy_devices = generate_dummy_devices(300000)
    insert_devices(dummy_devices)
    print("🎉 300.000 dummy devices berhasil dimasukkan ke database.")
