import sys
import os
import uuid
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db.models import Base, User, Bank, Account  # Pastikan path dan model sudah benar
from db.config import SYNC_DATABASE_URL

fake = Faker('id_ID')

engine = create_engine(SYNC_DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(engine)

def generate_dummy_accounts(n=300000):
    accounts = []
    users = session.query(User).all()
    banks = session.query(Bank).all()

    if not users:
        raise Exception("Data users belum ada, generate dummy user dulu.")
    if not banks:
        raise Exception("Data banks belum ada, generate dummy bank dulu.")

    account_types = ['e-wallet', 'bank', 'crypto']
    statuses = ['active', 'suspended', 'closed']

    used_account_numbers = set()
    used_user_accounttype = set()

    for i in range(n):
        # pastikan kombinasi (user_id, account_type) unik
        while True:
            user = fake.random_element(users)
            account_type = fake.random_element(account_types)
            combo_key = (user.user_id, account_type)
            if combo_key not in used_user_accounttype:
                used_user_accounttype.add(combo_key)
                break

        bank = None
        account_number = None
        bank_id = None

        if account_type == 'bank':
            while True:
                account_number = ''.join([str(fake.random_digit()) for _ in range(10)])
                if account_number not in used_account_numbers:
                    used_account_numbers.add(account_number)
                    break
            bank = fake.random_element(banks)
            bank_id = bank.bank_id

        account = Account(
            account_id=str(uuid.uuid4()),
            user_id=user.user_id,
            account_type=account_type,
            bank_id=bank_id,
            account_number=account_number,
            account_name=user.name,
            balance=round(fake.pyfloat(left_digits=5, right_digits=2, positive=True), 2),
            status=fake.random_element(statuses),
            created_at=fake.date_time_between(start_date='-5y', end_date='now')
        )
        accounts.append(account)

        if i % 10000 == 0 and i != 0:
            fake.unique.clear()

    return accounts

def insert_accounts(accounts, batch_size=5000):
    print("Menghapus data account lama...")
    session.query(Account).delete()
    session.commit()

    print(f"Memulai insert {len(accounts)} account baru dengan batch size {batch_size}...")
    for i in range(0, len(accounts), batch_size):
        batch = accounts[i:i+batch_size]
        session.bulk_save_objects(batch)
        session.commit()
        print(f"Inserted accounts {i + 1} to {i + len(batch)}")

if __name__ == "__main__":
    print("Generate 145.000 dummy accounts...")
    dummy_accounts = generate_dummy_accounts(145000)
    print("Insert dummy accounts ke database...")
    insert_accounts(dummy_accounts)
    print("145.000 dummy accounts berhasil dimasukkan ke database.")
