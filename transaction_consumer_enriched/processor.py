from db.models import Transaction, User, Device, IPAddress, Enrichment, Account, Merchant
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
from dateutil import parser
import decimal

def upsert_user(session: Session, event):
    if isinstance(event, str):
        import json
        event = json.loads(event)
    source_user_id = event.get('source_user_id')
    bank_id = event.get('bank_id')
    if not source_user_id or not bank_id:
        return None
    user = session.query(User).filter_by(source_user_id=source_user_id, source_bank_id=bank_id).first()
    if user:
        pass
    else:
        user = User(
            user_id=uuid.uuid4(),
            source_user_id=source_user_id,
            source_bank_id=bank_id,
        )
        session.add(user)
    session.commit()
    return user

def upsert_enrichment(session, event, user_id, transaction_id):
    if isinstance(event, str):
        import json
        event = json.loads(event)
    from db.models import Enrichment
    # Helper for casting
    def to_decimal(val):
        try:
            if val is None or val == '':
                return None
            return decimal.Decimal(str(val))
        except Exception:
            return None
    def to_int(val):
        try:
            return int(val)
        except (TypeError, ValueError):
            return None
    def to_bool(val):
        if isinstance(val, bool):
            return val
        if isinstance(val, str):
            return val.lower() == 'true'
        return False
    enrichment = session.query(Enrichment).filter_by(transaction_id=transaction_id, user_id=user_id).first()
    if enrichment:
        enrichment.amount_idr = to_decimal(event.get('amount_idr'))
        enrichment.hour_of_day = to_int(event.get('hour_of_day'))
        enrichment.day_of_week = to_int(event.get('day_of_week'))
        enrichment.is_weekend = to_bool(event.get('is_weekend'))
        enrichment.is_night = to_bool(event.get('is_night'))
        enrichment.ip_is_private = to_bool(event.get('ip_is_private'))
        enrichment.device_type_category = event.get('device_type_category')
        enrichment.txn_count_5min = to_int(event.get('txn_count_5min'))
        enrichment.txn_amount_sum_5min = to_decimal(event.get('txn_amount_sum_5min'))
        enrichment.is_fraud = to_bool(event.get('is_fraud'))
        enrichment.bscore = to_decimal(event.get('bscore'))
    else:
        enrichment = Enrichment(
            id=uuid.uuid4(),
            transaction_id=transaction_id,
            user_id=user_id,
            amount_idr=to_decimal(event.get('amount_idr')),
            hour_of_day=to_int(event.get('hour_of_day')),
            day_of_week=to_int(event.get('day_of_week')),
            is_weekend=to_bool(event.get('is_weekend')),
            is_night=to_bool(event.get('is_night')),
            ip_is_private=to_bool(event.get('ip_is_private')),
            device_type_category=event.get('device_type_category'),
            txn_count_5min=to_int(event.get('txn_count_5min')),
            txn_amount_sum_5min=to_decimal(event.get('txn_amount_sum_5min')),
            is_fraud=to_bool(event.get('is_fraud')),
            bscore=to_decimal(event.get('bscore')),
        )
        session.add(enrichment)
    session.commit()
    return enrichment

def upsert_account(session: Session, event, user_id):
    if isinstance(event, str):
        import json
        event = json.loads(event)
    def to_decimal(val):
        try:
            if val is None or val == '':
                return None
            return decimal.Decimal(str(val))
        except Exception:
            return None
    source_account_id = event.get('source_account_id')
    bank_id = event.get('bank_id')
    if not source_account_id or not bank_id or not user_id:
        return None
    account = session.query(Account).filter_by(account_number=source_account_id, bank_id=bank_id, user_id=user_id).first()
    if account:
        # Update fields if needed
        account.account_type = event.get('account_type')
        account.status = event.get('account_status')
        account.balance = to_decimal(event.get('balance', 0.0))
    else:
        account = Account(
            account_id=uuid.uuid4(),
            user_id=user_id,
            bank_id=bank_id,
            account_number=source_account_id,
            account_type=event.get('account_type'),
            status=event.get('account_status', 'active'),
            currency=event.get('currency', 'IDR'),
            balance=to_decimal(event.get('balance', 0.0))
        )
        session.add(account)
    session.commit()
    return account

def upsert_merchant(session: Session, event, bank_id):
    if isinstance(event, str):
        import json
        event = json.loads(event)
    merchant_code = event.get('source_merchant_code')
    if not merchant_code or not bank_id:
        return None
    merchant = session.query(Merchant).filter_by(merchant_code=merchant_code, source_bank_id=bank_id).first()
    if merchant:
        merchant.name = event.get('merchant_name')
        merchant.category = event.get('merchant_category')
        merchant.location = event.get('location')
        merchant.phone = event.get('merchant_phone')
        merchant.email = event.get('merchant_email')
    else:
        merchant = Merchant(
            merchant_id=uuid.uuid4(),
            source_bank_id=bank_id,
            merchant_code=merchant_code,
            name=event.get('merchant_name', merchant_code),
            category=event.get('merchant_category'),
            location=event.get('location'),
            phone=event.get('merchant_phone'),
            email=event.get('merchant_email')
        )
        session.add(merchant)
    session.commit()
    return merchant

def upsert_device(session: Session, event, user_id):
    if isinstance(event, str):
        import json
        event = json.loads(event)
    def to_bool(val):
        if isinstance(val, bool):
            return val
        if isinstance(val, str):
            return val.lower() == 'true'
        return False
    device_id = event.get('device_id')
    bank_id = event.get('bank_id')
    if not device_id or not bank_id or not user_id:
        return None
    device = session.query(Device).filter_by(device_id=device_id, source_bank_id=bank_id, user_id=user_id).first()
    if device:
        device.device_type = event.get('device_type')
        device.os_version = event.get('os_version')
        device.app_version = event.get('app_version')
        device.is_emulator = to_bool(event.get('is_emulator'))
    else:
        device = Device(
            device_uuid=uuid.uuid4(),
            device_id=device_id,
            source_bank_id=bank_id,
            user_id=user_id,
            device_type=event.get('device_type') or 'unknown',
            os_version=event.get('os_version'),
            app_version=event.get('app_version'),
            is_emulator=to_bool(event.get('is_emulator'))
        )
        session.add(device)
    session.commit()
    return device

def upsert_ipaddress(session: Session, event, user_id):
    if isinstance(event, str):
        import json
        event = json.loads(event)
    def to_bool(val):
        if isinstance(val, bool):
            return val
        if isinstance(val, str):
            return val.lower() == 'true'
        return False
    ip_addr = event.get('ip_address')
    if not ip_addr or not user_id:
        return None
    ip = session.query(IPAddress).filter_by(ip_address=ip_addr, user_id=user_id).first()
    if ip:
        ip.is_proxy = to_bool(event.get('is_proxy'))
        ip.location = event.get('ip_location')
    else:
        ip = IPAddress(
            ip_id=uuid.uuid4(),
            ip_address=ip_addr,
            user_id=user_id,
            is_proxy=to_bool(event.get('is_proxy')),
            location=event.get('ip_location')
        )
        session.add(ip)
    session.commit()
    return ip

def dict_to_transaction(event, user=None, device=None, account=None, merchant=None):
    if isinstance(event, str):
        import json
        event = json.loads(event)
    txn_time = event.get('transaction_time')
    if txn_time:
        try:
            txn_time = parser.parse(txn_time)
        except Exception:
            txn_time = None
    else:
        txn_time = None
    def to_decimal(val):
        try:
            if val is None or val == '':
                return None
            return decimal.Decimal(str(val))
        except Exception:
            return None
    def to_bool(val):
        if isinstance(val, bool):
            return val
        if isinstance(val, str):
            return val.lower() == 'true'
        return False
    return Transaction(
        transaction_id=event.get('transaction_id'),
        bank_id=event.get('bank_id'),
        user_id=user.user_id if user else event.get('user_id'),
        account_id=account.account_id if account else event.get('account_id'),
        device_uuid=device.device_uuid if device else event.get('device_uuid'),
        amount=to_decimal(event.get('amount')),
        transaction_time=txn_time,
        merchant_id=merchant.merchant_id if merchant else event.get('merchant_id'),
        location=event.get('location'),
        transaction_type=event.get('transaction_type'),
        currency_exchange_rate=to_decimal(event.get('currency_exchange_rate'))
    )

def upsert_transaction(session: Session, txn: Transaction):
    existing = session.query(Transaction).filter_by(transaction_id=txn.transaction_id, bank_id=txn.bank_id).first()
    if existing:
        for attr in [
            'user_id', 'account_id', 'device_uuid', 'amount', 'transaction_time',
            'merchant_id', 'location', 'transaction_type', 'currency_exchange_rate']:
            setattr(existing, attr, getattr(txn, attr))
    else:
        session.add(txn)
    session.commit()
