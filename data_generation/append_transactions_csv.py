import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import csv
import os
import math
import multiprocessing
import uuid
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import Base, User, Account, Bank, Merchant, Device
from db.config import SYNC_DATABASE_URL
import numpy as np

CSV_PATH = "transactions_python.csv"
TARGET_TOTAL = 2_000_000
WORKERS = 4
BATCH_SIZE = 10_000

# Setup DB and Faker
fake = Faker('id_ID')
engine = create_engine(SYNC_DATABASE_URL, pool_pre_ping=True)
Session = sessionmaker(bind=engine)
session = Session()

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
    return users, accounts, banks, merchants, devices

def build_user_accounts_map(accounts):
    user_accounts_map = {}
    for acc in accounts:
        user_accounts_map.setdefault(acc["user_id"], []).append(acc)
    return user_accounts_map

def count_existing_rows(csv_path):
    if not os.path.exists(csv_path):
        return 0
    with open(csv_path, 'r') as f:
        return sum(1 for _ in f) - 1  # minus header

from datetime import datetime, timedelta

def transaction_dict_generator(n, users, user_accounts_map, banks, merchants, devices, worker_id=None, start_idx=0):
    np.random.seed()
    transaction_types = ['debit', 'credit', 'transfer', 'digital_wallet']
    locations = ['Jakarta', 'Bandung', 'Surabaya', 'Yogyakarta', 'Semarang', 'Makassar', 'Medan', 'Palembang', 'Bekasi', 'Depok']
    user_ids = np.random.choice([u["user_id"] for u in users], size=n)
    user_accounts = [user_accounts_map.get(uid, []) for uid in user_ids]
    account_ids = np.random.choice([acc["account_id"] for accs in user_accounts for acc in accs], size=n)
    bank_ids = np.random.choice([b["bank_id"] for b in banks], size=n)
    merchant_ids = np.random.choice([m["merchant_id"] for m in merchants], size=n)
    device_ids = np.random.choice([d["device_id"] for d in devices], size=n)
    amounts = np.round(np.random.uniform(10.0, 10000.0, size=n), 2)
    transaction_times = [(datetime.now() - timedelta(days=np.random.randint(0, 730))).isoformat(sep=' ') for _ in range(n)]
    transaction_type_ids = np.random.choice(len(transaction_types), size=n)
    is_frauds = np.random.choice([True, False], size=n, p=[0.1, 0.9])
    locations = np.random.choice(locations, size=n)
    for i in range(n):
        if (i+1) % 10000 == 0 or i == 0:
            now = datetime.now()
            elapsed = now - datetime.now()
            done = i+1
            total = n
            percent = (done/total)*100
            est_total = (elapsed / done * total) if done > 0 else timedelta(0)
            eta = (datetime.now() + est_total) - now if done > 0 else timedelta(0)
            print(f"[{now.strftime('%H:%M:%S')}] [Worker {worker_id}] {done+start_idx:,}/{total+start_idx:,} ({percent:.2f}%) | Elapsed: {str(elapsed).split('.')[0]} | ETA: {str(eta).split('.')[0]}", flush=True)
        yield {
            "transaction_id": str(uuid.uuid4()),
            "user_id": user_ids[i],
            "account_id": account_ids[i],
            "bank_id": bank_ids[i],
            "amount": amounts[i],
            "transaction_time": transaction_times[i],
            "merchant_id": merchant_ids[i],
            "location": locations[i],
            "transaction_type": transaction_types[transaction_type_ids[i]],
            "is_fraud": is_frauds[i],
            "device_id": device_ids[i]
        }

def worker_append_csv(args):
    from datetime import datetime
    n, users, user_accounts_map, banks, merchants, devices, csv_path, worker_id, start_idx = args
    start_time = datetime.now()
    print(f"[{start_time.strftime('%H:%M:%S')}] [Worker {worker_id}] Start, target: {n} transactions (starting at {start_idx})", flush=True)
    mode = 'a' if os.path.exists(csv_path) else 'w'
    with open(csv_path, mode, newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            "transaction_id", "user_id", "account_id", "bank_id", "amount", "transaction_time",
            "merchant_id", "location", "transaction_type", "is_fraud", "device_id"
        ])
        if mode == 'w' and start_idx == 0:
            writer.writeheader()
        for tx in transaction_dict_generator(n, users, user_accounts_map, banks, merchants, devices, worker_id, start_idx):
            writer.writerow(tx)
    end_time = datetime.now()
    print(f"[{end_time.strftime('%H:%M:%S')}] [Worker {worker_id}] Finished! Duration: {str(end_time - start_time).split('.')[0]}", flush=True)

def append_transactions_csv(total_needed=TARGET_TOTAL, csv_path=CSV_PATH, workers=WORKERS):
    existing = count_existing_rows(csv_path)
    to_generate = total_needed - existing
    print(f"[Main] {existing} rows found in {csv_path}. Need to generate: {to_generate}")
    if to_generate <= 0:
        print(f"[Main] No need to generate more. Already >= {total_needed} rows.")
        return
    users, accounts, banks, merchants, devices = get_references()
    user_accounts_map = build_user_accounts_map(accounts)
    chunk = math.ceil(to_generate / workers)
    worker_args = []
    for i in range(workers):
        this_n = min(chunk, to_generate - i*chunk)
        if this_n <= 0:
            continue
        worker_args.append((this_n, users, user_accounts_map, banks, merchants, devices, csv_path, i+1, existing + i*chunk))
    with multiprocessing.Pool(workers) as pool:
        pool.map(worker_append_csv, worker_args)
    print(f"[Main] Done. {csv_path} now has {total_needed} rows (or more).")

if __name__ == "__main__":
    append_transactions_csv()
