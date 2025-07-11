import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from faker import Faker
import uuid
import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from db.models import Base, ComplianceRecord, User, Account, Transaction
from db.config import SYNC_DATABASE_URL
import random
fake = Faker()
engine = create_engine(SYNC_DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine)

def generate_compliance_record(user=None, account=None, transaction=None):
    # Penentuan tipe compliance
    if transaction:
        compliance_type = "AML"
    elif account:
        compliance_type = "CDD"
    else:
        compliance_type = "KYC"

    # Status realistis
    if compliance_type == "KYC":
        status = "passed" if user.kyc_status == "verified" else random.choice(["rejected", "flagged"])
    elif compliance_type == "AML":
        status = "flagged" if transaction.amount > 10000000 else "passed"
    elif compliance_type == "CDD":
        status = random.choices(["passed", "flagged"], weights=[0.85, 0.15])[0]

    return ComplianceRecord(
        record_id=uuid.uuid4(),
        user_id=user.user_id if user else None,
        account_id=account.account_id if account else None,
        transaction_id=transaction.transaction_id if transaction else None,
        compliance_type=compliance_type,
        status=status,
        notes=fake.sentence(nb_words=8),
        checked_at=fake.date_time_between(start_date='-180d', end_date='now')
    )

def insert_realistic_compliance(n=10000):
    users = session.query(User).limit(n).all()
    accounts = session.query(Account).limit(n).all()
    transactions = session.query(Transaction).limit(n).all()
    records = []

    for _ in range(n):
        source = random.choice(["user", "account", "transaction"])
        if source == "user":
            user = random.choice(users)
            records.append(generate_compliance_record(user=user))
        elif source == "account":
            account = random.choice(accounts)
            user = next((u for u in users if u.user_id == account.user_id), None)
            records.append(generate_compliance_record(user=user, account=account))
        else:
            tx = random.choice(transactions)
            user = next((u for u in users if u.user_id == tx.user_id), None)
            account = next((a for a in accounts if a.account_id == tx.account_id), None)
            records.append(generate_compliance_record(user=user, account=account, transaction=tx))

    session.bulk_save_objects(records)
    session.commit()
    print(f"{len(records)} compliance records berhasil dimasukkan.")

if __name__ == "__main__":
    insert_realistic_compliance()
