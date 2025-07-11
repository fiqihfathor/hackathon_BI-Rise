import streamlit as st
import psycopg2
import requests
import os
import uuid
import random
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import json

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5433")
DB_NAME = os.getenv("DB_NAME", "hacketon_fraud")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

PAYMENT_GATEWAY_URL = os.getenv("PAYMENT_GATEWAY_URL", "http://localhost:8000")

@st.cache_data(show_spinner=False)
def get_users():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cur = conn.cursor()
        cur.execute("SELECT user_id, source_user_id, name, email, source_bank_id FROM users LIMIT 100;")
        users = cur.fetchall()
        cur.close()
        conn.close()
        return users
    except Exception as e:
        st.error(f"Error fetching users: {e}")
        return []

def get_bank_api_key(source_bank_id):
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cur = conn.cursor()
        cur.execute("SELECT api_key FROM banks WHERE bank_id = %s;", (source_bank_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            return row[0]
        return None
    except Exception as e:
        st.error(f"Error fetching bank API key: {e}")
        return None

def normalize_transaction_time(v):
    """Normalize transaction_time to ISO8601 with milliseconds and trailing Z for UTC."""
    if hasattr(v, "isoformat"):
        iso = v.isoformat(timespec="milliseconds")
        # If datetime is naive (no tzinfo), treat as UTC and add Z
        if v.tzinfo is None:
            iso += "Z"
        else:
            # If tzinfo present and not UTC, convert to UTC string
            if v.utcoffset() != timedelta(0):
                # Convert to UTC
                iso = v.astimezone(tz=None).isoformat(timespec="milliseconds").replace("+00:00", "Z")
            else:
                if not iso.endswith("Z"):
                    iso += "Z"
        return iso
    elif isinstance(v, str):
        try:
            # Parse string, remove trailing Z for parsing
            dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
            return dt.isoformat(timespec="milliseconds").replace("+00:00", "Z")
        except Exception:
            # fallback: just ensure endswith Z
            return v if v.endswith("Z") else v + "Z"
    else:
        return str(v)

def send_transaction(transaction_data, bank_api_key):
    if "transaction_time" in transaction_data:
        transaction_data["transaction_time"] = normalize_transaction_time(transaction_data["transaction_time"])
    try:
        response = requests.post(
            f"{PAYMENT_GATEWAY_URL}/transactions",
            json=transaction_data,
            headers={"X-API-KEY": bank_api_key}
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Status {response.status_code}: {response.text}"}
    except Exception as e:
        return {"error": str(e)}

def generate_random_ip():
    # Generate a random public IPv4 address avoiding private/reserved ranges (simplified)
    # Avoid 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16
    first_octet = random.choice(
        [i for i in range(1, 256)
         if i != 10 and not (172 <= i <= 172) and i != 192]
    )
    second_octet = random.randint(0, 255)
    third_octet = random.randint(0, 255)
    fourth_octet = random.randint(1, 254)
    return f"{first_octet}.{second_octet}.{third_octet}.{fourth_octet}"

def generate_random_transaction(user):
    transaction_types = ["debit", "credit", "transfer"]
    device_types = ["Android", "iOS", "Web"]
    source_transaction_id = f"src-{uuid.uuid4().hex[:8]}"
    source_account_id = f"acc-{uuid.uuid4().hex[:6]}"
    source_merchant_code = f"merch-{random.randint(100,999)}"
    amount = round(random.uniform(1000, 1000000), 2)
    currency = "IDR"
    transaction_type = random.choice(transaction_types)
    transaction_time = datetime.utcnow().isoformat(timespec="milliseconds") + "Z"
    location = random.choice(["Jakarta, Indonesia", "Bandung, Indonesia", "Surabaya, Indonesia"])
    device_id = f"device-{uuid.uuid4().hex[:8]}"
    device_type = random.choice(device_types)
    os_version = random.choice(["12", "13", "14"])
    app_version = random.choice(["4.0.2", "4.1.0", "4.2.1"])
    is_emulator = random.choice([False, False, False, True])
    ip_address = generate_random_ip()
    ip_location = "Indonesia"
    is_proxy = random.choice([False, False, True])
    notes = random.choice(["Test transaction", ""])

    transaction = {
        "source_user_id": user[1],
        "source_transaction_id": source_transaction_id,
        "source_account_id": source_account_id,
        "source_merchant_code": source_merchant_code,
        "amount": amount,
        "currency": currency,
        "transaction_type": transaction_type,
        "transaction_time": transaction_time,
        "location": location,
        "device_id": device_id,
        "device_type": device_type,
        "os_version": os_version,
        "app_version": app_version,
        "is_emulator": is_emulator,
        "ip_address": ip_address,
        "ip_location": ip_location,
        "is_proxy": is_proxy,
        "notes": notes if notes else None
    }

    return {k: v for k, v in transaction.items() if v is not None}
