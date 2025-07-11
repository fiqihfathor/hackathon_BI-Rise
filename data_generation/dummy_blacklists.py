import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import uuid
import random
import datetime
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.models import Base, Blacklist, User, Merchant, Device, Account
from db.config import SYNC_DATABASE_URL

fake = Faker()

engine = create_engine(SYNC_DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(engine)

def generate_dummy_blacklist(n=20):
    blacklist_entries = []

    users = session.query(User).all()
    merchants = session.query(Merchant).all()
    devices = session.query(Device).all()
    accounts = session.query(Account).all()

    entity_pool = [
        ('user', users),
        ('merchant', merchants),
        ('device', devices),
        ('account', accounts)
    ]

    reasons = [
        "multiple fraud alerts",
        "manual review flagged",
        "associated with fraudulent transactions",
        "using emulator or proxy",
        "linked to suspended account"
    ]

    for _ in range(n):
        entity_type, entity_list = fake.random_element(entity_pool)
        if not entity_list:
            continue  # skip if no data
        entity = fake.random_element(entity_list)

        added_at = fake.date_time_between(start_date='-1y', end_date='now')
        removed_at = None if fake.boolean(chance_of_getting_true=80) else fake.date_time_between(start_date=added_at, end_date='now')

        entry = Blacklist(
            id=uuid.uuid4(),
            entity_type=entity_type,
            entity_id=getattr(entity, f"{entity_type}_id"),
            reason=fake.random_element(reasons),
            added_at=added_at,
            removed_at=removed_at,
            added_by=fake.name(),
            active=removed_at is None
        )
        blacklist_entries.append(entry)

    return blacklist_entries

def insert_blacklist(entries):
    session.query(Blacklist).delete()
    session.commit()
    session.bulk_save_objects(entries)
    session.commit()

if __name__ == "__main__":
    entries = generate_dummy_blacklist(100)
    insert_blacklist(entries)
    print("30 blacklist entries berhasil ditambahkan.")
