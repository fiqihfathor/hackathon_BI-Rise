import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid
import datetime
import random

from db.models import Base, User, Account, Bank, Merchant, Device, Transaction
from db.config import SYNC_DATABASE_URL

fake = Faker('id_ID')

engine = create_engine(SYNC_DATABASE_URL, pool_pre_ping=True)
Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(engine)

# Helper functions to convert ORM objects to dicts

def user_to_dict(user):
    return {"user_id": user.user_id}

def account_to_dict(account):
    return {"account_id": account.account_id, "user_id": account.user_id, "bank_id": account.bank_id}

def bank_to_dict(bank):
    return {"bank_id": bank.bank_id}

def merchant_to_dict(merchant):
    return {"merchant_id": merchant.merchant_id, "location": merchant.location}

def device_to_dict(device):
    return {"device_id": device.device_id}

def get_references():
    users = [user_to_dict(u) for u in session.query(User).all()]
    accounts = [account_to_dict(a) for a in session.query(Account).all()]
    banks = [bank_to_dict(b) for b in session.query(Bank).all()]
    merchants = [merchant_to_dict(m) for m in session.query(Merchant).all()]
    devices = [device_to_dict(d) for d in session.query(Device).all()]

    if not users or not accounts:
        raise Exception("Pastikan data User dan Account sudah ada dulu.")
    
    return users, accounts, banks, merchants, devices

def build_user_accounts_map(accounts):
    user_accounts_map = {}
    for acc in accounts:
        user_accounts_map.setdefault(acc["user_id"], []).append(acc)
    return user_accounts_map

def transaction_generator(n, users, user_accounts_map, banks, merchants, devices):
    transaction_types = ['debit', 'credit', 'transfer', 'digital_wallet']

    for i in range(n):
        user = fake.random_element(users)
        user_accounts = user_accounts_map.get(user["user_id"], [])
        if not user_accounts:
            continue

        account = fake.random_element(user_accounts)
        bank = next((b for b in banks if b["bank_id"] == account["bank_id"]), None)
        merchant = fake.random_element(merchants) if merchants else None
        device = fake.random_element(devices) if devices else None

        transaction = Transaction(
            transaction_id=str(uuid.uuid4()),
            user_id=user["user_id"],
            account_id=account["account_id"],
            bank_id=bank["bank_id"] if bank else None,
            amount=round(fake.pyfloat(left_digits=4, right_digits=2, positive=True, min_value=10.0), 2),
            transaction_time=fake.date_time_between(start_date='-2y', end_date='now'),
            merchant_id=merchant["merchant_id"] if merchant else None,
            location=merchant["location"] if merchant else None,
            transaction_type=fake.random_element(transaction_types),
            is_fraud=fake.boolean(chance_of_getting_true=10),
            device_id=device["device_id"] if device else None
        )

        yield transaction

        if i % 10000 == 0 and i != 0:
            fake.unique.clear()
            print(f"Generated: {i} transactions")

def insert_transactions_stream(n=2_000_000, batch_size=10_000, user_partition_size=1000):
    print("🧹 Menghapus transaksi lama...")
    session.query(Transaction).delete()
    session.commit()

    users, accounts, banks, merchants, devices = get_references()
    user_accounts_map = build_user_accounts_map(accounts)

    total_users = len(users)
    total_partitions = (total_users + user_partition_size - 1) // user_partition_size
    tx_per_partition = n // total_partitions
    remainder = n % total_partitions

    print(f"🚀 Insert {n} transaksi dalam batch {batch_size}, per {user_partition_size} users...")
    batch = []
    tx_count = 0
    for idx in range(total_partitions):
        start = idx * user_partition_size
        end = min((idx + 1) * user_partition_size, total_users)
        users_partition = users[start:end]
        # Distribute remainder to the first few partitions
        n_tx = tx_per_partition + (1 if idx < remainder else 0)
        if not users_partition:
            continue
        print(f"Generating {n_tx} transactions for users {start + 1} to {end}")
        for tx in transaction_generator(n_tx, users_partition, user_accounts_map, banks, merchants, devices):
            batch.append(tx)
            tx_count += 1
            if len(batch) >= batch_size:
                session.bulk_save_objects(batch)
                session.commit()
                session.expunge_all()  # Free memory
                print(f"✅ Inserted {tx_count - len(batch) + 1} to {tx_count}")
                batch = []
    # Insert remaining transactions
    if batch:
        session.bulk_save_objects(batch)
        session.commit()
        session.expunge_all()
        print(f"✅ Inserted final batch {tx_count - len(batch) + 1} to {tx_count}")

import csv
import multiprocessing
import tempfile
import shutil

def transaction_dict_generator(n, users, user_accounts_map, banks, merchants, devices, worker_id=None):
    # Like transaction_generator, but yields dicts for CSV
    from faker import Faker
    local_fake = Faker('id_ID')
    transaction_types = ['debit', 'credit', 'transfer', 'digital_wallet']
    for i in range(n):
        user = local_fake.random_element(users)
        user_accounts = user_accounts_map.get(user["user_id"], [])
        if not user_accounts:
            continue
        account = local_fake.random_element(user_accounts)
        bank = next((b for b in banks if b["bank_id"] == account["bank_id"]), None)
        merchant = local_fake.random_element(merchants) if merchants else None
        device = local_fake.random_element(devices) if devices else None
        if worker_id is not None and i % 10000 == 0 and i != 0:
            print(f"[Worker {worker_id}] Generated {i} transactions")
        yield {
            "transaction_id": str(uuid.uuid4()),
            "user_id": user["user_id"],
            "account_id": account["account_id"],
            "bank_id": bank["bank_id"] if bank else None,
            "amount": round(local_fake.pyfloat(left_digits=4, right_digits=2, positive=True, min_value=10.0), 2),
            "transaction_time": local_fake.date_time_between(start_date='-2y', end_date='now'),
            "merchant_id": merchant["merchant_id"] if merchant else None,
            "location": merchant["location"] if merchant else None,
            "transaction_type": local_fake.random_element(transaction_types),
            "is_fraud": local_fake.boolean(chance_of_getting_true=10),
            "device_id": device["device_id"] if device else None
        }

def _worker_generate_csv(args):
    # Worker for multiprocessing
    (n, users, user_accounts_map, banks, merchants, devices, csv_path, worker_id) = args
    print(f"[Worker {worker_id}] Starting, generating {n} transactions...")
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            "transaction_id", "user_id", "account_id", "bank_id", "amount", "transaction_time",
            "merchant_id", "location", "transaction_type", "is_fraud", "device_id"
        ])
        writer.writeheader()
        for tx in transaction_dict_generator(n, users, user_accounts_map, banks, merchants, devices, worker_id=worker_id):
            # Convert datetime to ISO string
            tx["transaction_time"] = tx["transaction_time"].isoformat(sep=' ')
            writer.writerow(tx)
    print(f"[Worker {worker_id}] Finished!")

def generate_transactions_to_csv_parallel(n=2_000_000, csv_path="transactions.csv", num_workers=None, user_partition_size=1000):
    import math
    if num_workers is None:
        num_workers = multiprocessing.cpu_count()
    users, accounts, banks, merchants, devices = get_references()
    user_accounts_map = build_user_accounts_map(accounts)
    total_users = len(users)
    partitions = [(i*user_partition_size, min((i+1)*user_partition_size, total_users)) for i in range((total_users+user_partition_size-1)//user_partition_size)]
    # Split n across workers
    chunk_sizes = [n // num_workers] * num_workers
    for i in range(n % num_workers):
        chunk_sizes[i] += 1
    # Assign users to workers
    user_chunks = []
    users_per_worker = total_users // num_workers
    for i in range(num_workers):
        start = i * users_per_worker
        end = min((i+1) * users_per_worker, total_users)
        user_chunks.append(users[start:end])
    # Prepare temp files for each worker
    temp_dir = tempfile.mkdtemp()
    temp_csvs = [os.path.join(temp_dir, f"transactions_part_{i}.csv") for i in range(num_workers)]
    # Prepare args for each worker
    worker_args = []
    for i in range(num_workers):
        worker_args.append((chunk_sizes[i], user_chunks[i], user_accounts_map, banks, merchants, devices, temp_csvs[i], i+1))
    print(f"Spawning {num_workers} processes to generate {n} transactions...")
    with multiprocessing.Pool(num_workers) as pool:
        pool.map(_worker_generate_csv, worker_args)
    # Combine CSVs
    with open(csv_path, 'w', newline='') as fout:
        writer = None
        for i, part_csv in enumerate(temp_csvs):
            with open(part_csv, 'r') as fin:
                if i == 0:
                    shutil.copyfileobj(fin, fout)
                else:
                    next(fin)  # skip header
                    shutil.copyfileobj(fin, fout)
    shutil.rmtree(temp_dir)
    print(f"✅ All transactions written to {csv_path}")

def generate_transactions_to_csv_python(n=2_000_000, csv_path="transactions_python.csv"):
    import csv
    users, accounts, banks, merchants, devices = get_references()
    user_accounts_map = build_user_accounts_map(accounts)
    transaction_types = ['debit', 'credit', 'transfer', 'digital_wallet']
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            "transaction_id", "user_id", "account_id", "bank_id", "amount", "transaction_time",
            "merchant_id", "location", "transaction_type", "is_fraud", "device_id"
        ])
        writer.writeheader()
        for i in range(n):
            user = fake.random_element(users)
            user_accounts = user_accounts_map.get(user["user_id"], [])
            if not user_accounts:
                continue
            account = fake.random_element(user_accounts)
            bank = next((b for b in banks if b["bank_id"] == account["bank_id"]), None)
            merchant = fake.random_element(merchants) if merchants else None
            device = fake.random_element(devices) if devices else None
            tx = {
                "transaction_id": str(uuid.uuid4()),
                "user_id": user["user_id"],
                "account_id": account["account_id"],
                "bank_id": bank["bank_id"] if bank else None,
                "amount": round(fake.pyfloat(left_digits=4, right_digits=2, positive=True, min_value=10.0), 2),
                "transaction_time": fake.date_time_between(start_date='-2y', end_date='now').isoformat(sep=' '),
                "merchant_id": merchant["merchant_id"] if merchant else None,
                "location": merchant["location"] if merchant else None,
                "transaction_type": fake.random_element(transaction_types),
                "is_fraud": fake.boolean(chance_of_getting_true=10),
                "device_id": device["device_id"] if device else None
            }
            writer.writerow(tx)
            if (i+1) % 10000 == 0:
                print(f"Generated {i+1} transactions", flush=True)
    print(f"✅ All {n} transactions written to {csv_path}")

if __name__ == "__main__":
    # Uncomment to use DB insert mode:
    # insert_transactions_stream()
    # print("🎉 2.000.000 dummy transactions berhasil dimasukkan ke database.")

    # Single-process CSV generation:
    generate_transactions_to_csv_python(n=2_000_000, csv_path="transactions_python.csv")
    print("🎉 2.000.000 dummy transactions berhasil digenerate ke transactions_python.csv!")
    print("\nUntuk import ke PostgreSQL, jalankan di psql:")
    print("""
    \COPY transaction (transaction_id, user_id, account_id, bank_id, amount, transaction_time, merchant_id, location, transaction_type, is_fraud, device_id) FROM './transactions_python.csv' DELIMITER ',' CSV HEADER;
    """)