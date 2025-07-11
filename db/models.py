from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, ForeignKey, DECIMAL, JSON, Index, UniqueConstraint, Date
)
from sqlalchemy.dialects.postgresql import UUID, INET, JSONB
from sqlalchemy.orm import relationship, declarative_base
import datetime
import uuid
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_user_id = Column(String, nullable=False)
    source_bank_id = Column(UUID(as_uuid=True), ForeignKey('banks.bank_id'), nullable=False)
    name = Column(String, nullable=True)
    email = Column(String, unique=False, nullable=True)
    phone = Column(String, unique=False, nullable=True)
    address = Column(String, nullable=True)
    job_title = Column(String, nullable=True)
    user_type = Column(String, default='normal')
    kyc_status = Column(String, default='pending')
    kyc_verified_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    is_fraud = Column(Boolean, default=False)
    registration_date = Column(DateTime, default=func.now())
    last_login = Column(DateTime, nullable=True)
    device_count = Column(Integer, default=0)
    ip_count = Column(Integer, default=0)
    risk_score = Column(Float, default=0.0)
    notes = Column(String, nullable=True)

    devices = relationship('Device', back_populates='user')
    transactions = relationship('Transaction', back_populates='user')
    accounts = relationship('Account', back_populates='user')
    device_usage_logs = relationship('DeviceUsageLog', back_populates='user')
    compliance_records = relationship('ComplianceRecord', back_populates='user')
    ip_addresses = relationship('IPAddress', back_populates='user')
    enrichments = relationship('Enrichment', back_populates='user')

    bank = relationship('Bank', back_populates='users')

    __table_args__ = (
        Index('idx_user_source_bank_id', 'source_bank_id'),
        Index('idx_user_source_user_id', 'source_user_id'),
        Index('idx_user_user_type', 'user_type'),
        Index('idx_user_is_fraud', 'is_fraud'),
        Index('idx_user_is_active', 'is_active'),
        Index('idx_user_kyc_status', 'kyc_status'),
        Index('idx_user_registration_date', 'registration_date'),
    )


class Device(Base):
    __tablename__ = 'devices'

    device_uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(String, nullable=False)
    source_bank_id = Column(UUID(as_uuid=True), ForeignKey('banks.bank_id'), nullable=False)

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False, index=True)

    device_type = Column(String(50), nullable=False)  # e.g. Android, iOS, Web
    os_version = Column(String(50), nullable=True)
    app_version = Column(String(50), nullable=True)
    is_emulator = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship('User', back_populates='devices')
    device_usage_logs = relationship('DeviceUsageLog', back_populates='device')
    transactions = relationship('Transaction', back_populates='device')
    bank = relationship('Bank', back_populates='devices')

    __table_args__ = (
        Index('idx_device_user_id', 'user_id'),
        Index('idx_device_device_id', 'device_id'),
        Index('idx_device_source_bank_id', 'source_bank_id'),
    )


class IPAddress(Base):
    __tablename__ = 'ip_addresses'

    ip_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey('transactions.id'), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=True)
    ip_address = Column(INET, nullable=False)
    location = Column(String, nullable=True)
    is_proxy = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    transaction = relationship('Transaction', back_populates='ip_addresses')
    user = relationship('User', back_populates='ip_addresses')


class Bank(Base):
    __tablename__ = 'banks'

    bank_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bank_name = Column(String, nullable=False)
    bank_code = Column(String, nullable=False, unique=True)
    swift_code = Column(String, nullable=True, unique=True) 
    api_key = Column(String, nullable=True)  
    address = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    accounts = relationship('Account', back_populates='bank')
    devices = relationship('Device', back_populates='bank')
    transactions = relationship('Transaction', back_populates='bank')
    users = relationship('User', back_populates='bank')

    __table_args__ = (
        UniqueConstraint('bank_code', name='uq_bank_code'),
        UniqueConstraint('swift_code', name='uq_swift_code'),
    )


class Account(Base):
    __tablename__ = 'accounts'

    account_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False) 
    bank_id = Column(UUID(as_uuid=True), ForeignKey('banks.bank_id'), nullable=False)  

    account_type = Column(String, nullable=True) 
    account_number = Column(String, nullable=True)  
    account_name = Column(String, nullable=True) 
    balance = Column(DECIMAL(18, 2), default=0.0)
    currency = Column(String(3), default='IDR')
    status = Column(String, default='active')     
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    is_fraud = Column(Boolean, default=False)
    
    user = relationship('User', back_populates='accounts')
    bank = relationship('Bank', back_populates='accounts')
    transactions = relationship('Transaction', back_populates='account')
    compliance_records = relationship('ComplianceRecord', back_populates='account')


class Merchant(Base):
    __tablename__ = 'merchants'
    merchant_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_bank_id = Column(UUID(as_uuid=True), ForeignKey('banks.bank_id'), nullable=False)
    merchant_code = Column(String, nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)
    location = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    risk_level = Column(String, default='low')
    status = Column(String, default='active')
    registered_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_transaction_date = Column(DateTime, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    transactions = relationship('Transaction', back_populates='merchant')

    __table_args__ = (
        UniqueConstraint('source_bank_id', 'merchant_code', name='uq_bank_merchant_code'),
    )


class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = Column(String, nullable=False)
    bank_id = Column(UUID(as_uuid=True), ForeignKey('banks.bank_id'), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=True)
    account_id = Column(UUID(as_uuid=True), ForeignKey('accounts.account_id'), nullable=True)
    device_uuid = Column(UUID(as_uuid=True), ForeignKey('devices.device_uuid'), nullable=True)

    amount = Column(DECIMAL(18, 2), nullable=False)
    transaction_time = Column(DateTime, default=datetime.datetime.utcnow)
    merchant_id = Column(UUID(as_uuid=True), ForeignKey('merchants.merchant_id'), nullable=True)
    location = Column(String, nullable=True)
    transaction_type = Column(String, nullable=False)
    currency_exchange_rate = Column(Float, nullable=True)

    user = relationship('User', back_populates='transactions')
    account = relationship('Account', back_populates='transactions')
    bank = relationship('Bank', back_populates='transactions')
    merchant = relationship('Merchant', back_populates='transactions')
    device = relationship('Device', back_populates='transactions')
    ip_addresses = relationship('IPAddress', back_populates='transaction')
    alerts = relationship('Alert', back_populates='transaction')
    compliance_records = relationship('ComplianceRecord', back_populates='transaction')
    enrichments = relationship('Enrichment', back_populates='transaction')

    __table_args__ = (
        UniqueConstraint('transaction_id', 'bank_id', name='uq_transaction_bank'),
    )

class Enrichment(Base):
    __tablename__ = 'transaction_enrichments'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey('transactions.id'))
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    amount_idr = Column(Float, nullable=True)
    hour_of_day = Column(Integer, nullable=True)
    day_of_week = Column(Integer, nullable=True)
    is_weekend = Column(Boolean, nullable=True)
    is_night = Column(Boolean, nullable=True)
    ip_is_private = Column(Boolean, nullable=True)
    device_type_category = Column(String, nullable=True)
    txn_count_5min = Column(Integer, nullable=True)
    txn_amount_sum_5min = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    is_fraud = Column(Boolean, default=False)
    rule_result = Column(JSONB, nullable=True)
    bscore = Column(Float, nullable=True)

    transaction = relationship('Transaction', back_populates='enrichments')
    user = relationship('User', back_populates='enrichments')


class Alert(Base):
    __tablename__ = 'alerts'

    alert_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey('transactions.id'))

    alert_type = Column(String, nullable=True)
    rule_name = Column(String, nullable=True)
    score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default='open')

    transaction = relationship('Transaction', back_populates='alerts')


class Rule(Base):
    __tablename__ = 'rules'

    rule_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_name = Column(String, unique=True)
    rule_dsl = Column(JSON, nullable=True)
    description = Column(String, nullable=True)
    source = Column(String)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class DeviceUsageLog(Base):
    __tablename__ = 'device_usage_logs'

    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    device_uuid = Column(UUID(as_uuid=True), ForeignKey('devices.device_uuid'))
    ip_address = Column(INET, nullable=True)
    login_time = Column(DateTime, default=datetime.datetime.utcnow)
    location = Column(String, nullable=True)

    user = relationship('User', back_populates='device_usage_logs')
    device = relationship('Device', back_populates='device_usage_logs')


class ComplianceRecord(Base):
    __tablename__ = 'compliance_records'

    record_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=True)
    account_id = Column(UUID(as_uuid=True), ForeignKey('accounts.account_id'), nullable=True)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey('transactions.id'), nullable=True)
    compliance_type = Column(String)
    status = Column(String)
    notes = Column(String, nullable=True)
    checked_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship('User', back_populates='compliance_records')
    account = relationship('Account', back_populates='compliance_records')
    transaction = relationship('Transaction', back_populates='compliance_records')


class Blacklist(Base):
    __tablename__ = 'blacklist'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(String, nullable=False)
    entity_id = Column(String, nullable=False)
    source_bank_id = Column(UUID(as_uuid=True), ForeignKey('banks.bank_id'), nullable=False)
    reason = Column(String, nullable=True)
    added_at = Column(DateTime, default=datetime.datetime.utcnow)
    removed_at = Column(DateTime, nullable=True)
    added_by = Column(String, nullable=True)
    active = Column(Boolean, default=True)


class CurrencyRate(Base):
    __tablename__ = 'currency_rates'

    currency = Column(String(3), nullable=False, index=True, primary_key=True)
    rate_to_idr = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    source = Column(String, nullable=True)

    __table_args__ = (
        Index('idx_currency_rate_date', 'date'),
        Index('idx_currency_rate_currency', 'currency'),
    )