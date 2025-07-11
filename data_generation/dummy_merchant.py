import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid
import datetime

from db.models import Base, Merchant
from db.config import SYNC_DATABASE_URL

fake = Faker('id_ID')

engine = create_engine(SYNC_DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(engine)

def generate_dummy_merchants(n=5000):
    risk_levels = ['low', 'medium', 'high']
    statuses = ['active', 'inactive', 'suspended']
    merchants = []
    now = datetime.datetime.utcnow()

    for i in range(n):
        risk_level = fake.random_element(risk_levels)
        status = fake.random_element(statuses)

        registered_at = fake.date_time_between(start_date='-5y', end_date='-1y')
        created_at = registered_at + datetime.timedelta(days=fake.random_int(min=0, max=30))
        last_transaction_date = None
        if fake.boolean(chance_of_getting_true=90):
            last_transaction_date = fake.date_time_between(start_date=registered_at, end_date='now')

        merchant_code = f"MER{i:05d}"

        merchant = Merchant(
            merchant_id=str(uuid.uuid4()),
            merchant_code=merchant_code,
            name=fake.company(),
            category=fake.random_element(['Retail', 'Food & Beverage', 'E-commerce', 'Services', 'Health']),
            location=fake.address().replace('\n', ', '),
            phone=fake.phone_number(),
            email=fake.company_email(),
            risk_level=risk_level,
            status=status,
            registered_at=registered_at,
            last_transaction_date=last_transaction_date,
            notes=None,
            created_at=created_at,
        )
        merchants.append(merchant)

        # Optional: Bersihkan cache unique Faker jika kamu pakai fake.unique (tidak dipakai di sini)
        # if i % 10000 == 0 and i != 0:
        #     fake.unique.clear()

    return merchants

def insert_merchants(merchants, batch_size=1000):
    session.query(Merchant).delete()
    session.commit()

    for i in range(0, len(merchants), batch_size):
        batch = merchants[i:i+batch_size]
        session.bulk_save_objects(batch)
        session.commit()
        print(f"Inserted merchants {i + 1} to {i + len(batch)}")

if __name__ == "__main__":
    print("Generating 5000 dummy merchants...")
    dummy_merchants = generate_dummy_merchants(5000)
    print("Inserting merchants into database...")
    insert_merchants(dummy_merchants)
    print("5000 dummy merchant records berhasil dimasukkan ke database.")
