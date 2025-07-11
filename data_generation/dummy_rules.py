import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import uuid
import datetime
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.models import Base, Rule
from db.config import SYNC_DATABASE_URL

fake = Faker()
engine = create_engine(SYNC_DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(engine)

def generate_dummy_rules():
    rules = []

    predefined_rules = [
        {
            "rule_name": "high_amount_night_transfer",
            "description": "Transfer di atas 10 juta antara pukul 00:00 - 04:00",
            "dsl": {
                "field": "amount",
                "operator": ">",
                "value": 10000000,
                "and": {
                    "field": "transaction_time",
                    "operator": "between_hour",
                    "value": [0, 4]
                }
            },
            "source": "manual"
        },
        {
            "rule_name": "suspicious_ip_country",
            "description": "Transaksi dari negara dengan risiko tinggi",
            "dsl": {
                "field": "ip_country",
                "operator": "in",
                "value": ["North Korea", "Iran", "Syria"]
            },
            "source": "manual"
        },
        {
            "rule_name": "multiple_accounts_same_device",
            "description": "Lebih dari 3 akun aktif menggunakan 1 device dalam 24 jam",
            "dsl": {
                "field": "device_id_usage_count",
                "operator": ">",
                "value": 3,
                "time_range": "24h"
            },
            "source": "AI-generated"
        },
        {
            "rule_name": "kyc_not_verified_high_risk",
            "description": "User belum KYC tapi user_type-nya high_risk",
            "dsl": {
                "field": "kyc_status",
                "operator": "!=",
                "value": "verified",
                "and": {
                    "field": "user_type",
                    "operator": "==",
                    "value": "high_risk"
                }
            },
            "source": "manual"
        },
        {
            "rule_name": "frequent_failed_login_device",
            "description": "Lebih dari 5 kali gagal login dari device yang sama dalam 1 jam",
            "dsl": {
                "field": "login_failed_count",
                "operator": ">",
                "value": 5,
                "time_range": "1h"
            },
            "source": "AI-generated"
        }
    ]

    for rule in predefined_rules:
        r = Rule(
            rule_id=uuid.uuid4(),
            rule_name=rule["rule_name"],
            rule_dsl=rule["dsl"],
            description=rule["description"],
            source=rule["source"],
            active=True,
            created_at=datetime.datetime.utcnow()
        )
        rules.append(r)

    return rules

def insert_rules(rules):
    session.query(Rule).delete()
    session.commit()
    session.bulk_save_objects(rules)
    session.commit()

if __name__ == "__main__":
    dummy_rules = generate_dummy_rules()
    insert_rules(dummy_rules)
    print(f"{len(dummy_rules)} dummy rules berhasil ditambahkan.")
