import sys
import os
import uuid
import datetime
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.models import Base, Bank
from db.config import SYNC_DATABASE_URL

fake = Faker('id_ID')

engine = create_engine(SYNC_DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Pastikan tabel-tabel dibuat
Base.metadata.create_all(engine)

def generate_dummy_banks(n=20):
    banks = []
    now = datetime.datetime.utcnow()
    used_bank_codes = set()
    used_swift_codes = set()

    bank_name_prefixes = [chr(i) for i in range(ord('A'), ord('A') + n)]
    idx = 0

    while len(banks) < n:
        bank_name = f"{bank_name_prefixes[idx]} Bank"
        bank_code = fake.unique.bothify(text='???###').upper()
        swift_code = fake.unique.bothify(text='??????##').upper()

        if bank_code in used_bank_codes or swift_code in used_swift_codes:
            continue

        used_bank_codes.add(bank_code)
        used_swift_codes.add(swift_code)

        bank = Bank(
            bank_id=uuid.uuid4(),
            bank_name=bank_name,
            bank_code=bank_code,
            swift_code=swift_code,
            api_key=uuid.uuid4().hex,
            address=fake.address().replace('\n', ', '),
            contact_phone=fake.phone_number(),
            contact_email=fake.company_email(),
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        banks.append(bank)
        idx += 1

    return banks

def insert_banks(banks):
    session.query(Bank).delete()  # Kosongkan dulu isi tabel Bank
    session.commit()

    session.bulk_save_objects(banks)
    session.commit()

if __name__ == "__main__":
    dummy_banks = generate_dummy_banks(20)
    insert_banks(dummy_banks)
    print("✅ 20 dummy bank records berhasil dimasukkan ke database dengan API key.")
