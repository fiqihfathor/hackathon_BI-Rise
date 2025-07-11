from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from pydantic import validator
from datetime import datetime, timedelta, timezone

class TransactionRequestFromBank(BaseModel):
    source_transaction_id: str          # ID transaksi asli dari bank A
    source_user_id: str                 # user_id asli dari bank A
    source_account_id: str              # account_id asli dari bank A
    source_merchant_code: Optional[str] = None

    amount: float
    currency: str = "IDR"
    transaction_type: str               # debit / credit / transfer / etc
    transaction_time: Optional[datetime] = None
    location: Optional[str] = None

    device_id: Optional[str] = None     # ID perangkat asli
    device_type: Optional[str] = None   # Android/iOS/Web
    os_version: Optional[str] = None
    app_version: Optional[str] = None
    is_emulator: Optional[bool] = None

    ip_address: Optional[str] = None
    ip_location: Optional[str] = None
    is_proxy: Optional[bool] = None

    notes: Optional[str] = None
    
    @validator("transaction_time")
    def validate_tx_time(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            raise ValueError("transaction_time must be timezone-aware")
        
        v_utc = v.astimezone(timezone.utc)

        now_utc = datetime.now(timezone.utc)
        if v_utc > now_utc + timedelta(minutes=5):
            raise ValueError("transaction_time cannot be in the future")

        return v_utc