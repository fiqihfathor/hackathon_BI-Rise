import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import uuid
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import Base, User
from db.config import SYNC_DATABASE_URL

# Setup Faker dan SQLAlchemy
fake = Faker('id_ID')
Faker.seed(42)

engine = create_engine(SYNC_DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(engine)

def generate_dummy_users(n=100000):
    risk_levels = ['normal', 'high_risk', 'low_risk', 'suspicious']
    kyc_status_choices = ['pending', 'verified', 'rejected']
    users = []

    for i in range(n):
        user_type = fake.random_element(risk_levels)
        kyc_status = fake.random_element(kyc_status_choices)

        if user_type == 'high_risk':
            risk_score = round(fake.pyfloat(min_value=0.7, max_value=1.0, right_digits=2), 2)
        elif user_type == 'suspicious':
            risk_score = round(fake.pyfloat(min_value=0.4, max_value=0.7, right_digits=2), 2)
        elif user_type == 'normal':
            risk_score = round(fake.pyfloat(min_value=0.2, max_value=0.4, right_digits=2), 2)
        else:  # low_risk
            risk_score = round(fake.pyfloat(min_value=0.0, max_value=0.2, right_digits=2), 2)

        kyc_verified_at = fake.date_time_this_decade() if kyc_status == 'verified' else None

        is_fraud = fake.boolean(chance_of_getting_true=0.5)
        if is_fraud:
            user_type = 'high_risk'
            risk_score = round(fake.pyfloat(min_value=0.7, max_value=1.0, right_digits=2), 2)

        # Get a random bank for source_bank_id
        from sqlalchemy.sql import func
        from db.models import Bank
        bank = session.query(Bank).order_by(func.random()).first()
        if not bank:
            raise Exception("No banks found in the database. Please generate dummy banks first.")

        user = User(
            user_id=str(uuid.uuid4()),
            source_user_id=fake.unique.bothify(text='SRCUSER-#######'),
            source_bank_id=bank.bank_id,
            name=fake.name(),
            email=fake.unique.email(),
            phone=fake.unique.phone_number(),
            address=fake.address().replace('\n', ', '),
            job_title=fake.job(),
            user_type=user_type,
            kyc_status=kyc_status,
            kyc_verified_at=kyc_verified_at,
            is_active=not is_fraud,
            is_fraud=is_fraud,
            registration_date=fake.date_time_this_decade(),
            last_login=fake.date_time_this_year(),
            device_count=fake.random_int(min=1, max=5),
            ip_count=fake.random_int(min=1, max=10),
            risk_score=risk_score,
            notes=fake.sentence(nb_words=8)
        )
        users.append(user)

        # Clear unique cache every 10,000 users to avoid memory issues
        if i % 10000 == 0 and i != 0:
            fake.unique.clear()

    return users

def insert_users(users, batch_size=5000):
    for i in range(0, len(users), batch_size):
        batch = users[i:i+batch_size]
        session.bulk_save_objects(batch)
        session.commit()
        print(f"Inserted users {i + 1} to {i + len(batch)}")

if __name__ == "__main__":
    print("Generate dummy users mulai...")
    dummy_users = generate_dummy_users(1000)
    print("Generate selesai, mulai insert ke database...")
    insert_users(dummy_users)
    print("1000 dummy users berhasil dimasukkan ke database.")
