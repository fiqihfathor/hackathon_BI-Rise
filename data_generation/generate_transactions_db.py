import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import uuid
import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from db.models import User, Account, Bank, Merchant, Device, Transaction
from db.config import SYNC_DATABASE_URL

engine = create_engine(SYNC_DATABASE_URL, pool_pre_ping=True)
Session = sessionmaker(bind=engine)
session = Session()

TARGET_TOTAL = 2_000_000
BATCH_SIZE = 20000

# Helper to fetch reference data as lists of IDs/tuples only
users = [u.user_id for u in session.query(User.user_id).all()]
accounts = [(a.account_id, a.user_id, a.bank_id) for a in session.query(Account.account_id, Account.user_id, Account.bank_id).all()]
banks = [b.bank_id for b in session.query(Bank.bank_id).all()]
merchants = [(m.merchant_id, m.location) for m in session.query(Merchant.merchant_id, Merchant.location).all()]
devices = [d.device_id for d in session.query(Device.device_id).all()]

user_accounts_map = {}
for acc_id, user_id, bank_id in accounts:
    user_accounts_map.setdefault(user_id, []).append((acc_id, bank_id))

transaction_types = ['debit', 'credit', 'transfer', 'digital_wallet']
locations = ['Jakarta', 'Bandung', 'Surabaya', 'Yogyakarta', 'Semarang', 'Makassar', 'Medan', 'Palembang', 'Bekasi', 'Depok']

print(f"[Main] Reference loaded: {len(users)} users, {len(accounts)} accounts, {len(banks)} banks, {len(merchants)} merchants, {len(devices)} devices.")

# Count existing transactions
existing = session.query(Transaction).count()
to_generate = TARGET_TOTAL - existing
print(f"[Main] {existing} rows found in transaction table. Need to generate: {to_generate}")
if to_generate <= 0:
    print(f"[Main] No need to generate more. Already >= {TARGET_TOTAL} rows.")
    exit(0)

def random_transaction():
    user_id = random.choice(users)
    accs = user_accounts_map.get(user_id, [])
    if not accs:
        return None
    account_id, bank_id = random.choice(accs)
    merchant = random.choice(merchants) if merchants else (None, None)
    device_id = random.choice(devices) if devices else None
    location = merchant[1] if merchant and merchant[1] else random.choice(locations)
    tx = {
        "transaction_id": str(uuid.uuid4()),
        "user_id": user_id,
        "account_id": account_id,
        "bank_id": bank_id,
        "amount": round(random.uniform(10.0, 10000.0), 2),
        "transaction_time": (datetime.now() - timedelta(days=random.randint(0, 730), seconds=random.randint(0,86400))).strftime('%Y-%m-%d %H:%M:%S'),
        "merchant_id": merchant[0] if merchant else None,
        "location": location,
        "transaction_type": random.choice(transaction_types),
        "is_fraud": random.choices([0,1], weights=[0.9,0.1])[0],
        "device_id": device_id
    }
    return tx

def insert_transactions_batch(batch):
    session.bulk_insert_mappings(Transaction, batch)
    session.commit()

import time
start_time = time.time()
batch = []
total_inserted = 0
for i in range(to_generate):
    tx = random_transaction()
    if not tx:
        continue
    batch.append(tx)
    if len(batch) >= BATCH_SIZE:
        insert_transactions_batch(batch)
        total_inserted += len(batch)
        elapsed = time.time() - start_time
        percent = (total_inserted/to_generate)*100
        eta = (elapsed/total_inserted)*(to_generate-total_inserted) if total_inserted else 0
        print(f"[DB] Inserted {total_inserted:,}/{to_generate:,} ({percent:.2f}%) | Elapsed: {int(elapsed)//60}m{int(elapsed)%60}s | ETA: {int(eta)//60}m{int(eta)%60}s", flush=True)
        batch = []
if batch:
    insert_transactions_batch(batch)
    total_inserted += len(batch)
    print(f"[DB] Inserted final batch. Total: {total_inserted:,}")

print(f"[Main] Done. {TARGET_TOTAL} rows should now exist in the transaction table.")
