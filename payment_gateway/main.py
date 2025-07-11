from fastapi import FastAPI, HTTPException
from datetime import datetime, timezone, timedelta
import uuid
from utils.schema import TransactionRequestFromBank
from utils.producer import send_transaction
from utils.redis_cache import get_currency_rate_from_cache, set_currency_rate_to_cache
from utils.config import get_db
from utils.services import get_currency_rate_from_db, validate_api_key
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from pydantic import validator

app = FastAPI()

@validator("transaction_time")
def validate_tx_time(cls, v):
    if v > datetime.utcnow() + timedelta(minutes=5):
        raise ValueError("transaction_time cannot be in the future")
    return v

@app.post("/transactions")
async def create_transaction(tx_req: TransactionRequestFromBank, bank = Depends(validate_api_key), db: AsyncSession = Depends(get_db)):
    try:
        if "transaction_time" in tx_req:
            tx_req.transaction_time = validate_tx_time(tx_req.transaction_time)

        if tx_req.amount <= 0:
            raise HTTPException(status_code=400, detail="Amount must be greater than 0")

        rate = await get_currency_rate_from_cache(tx_req.currency)
        if rate is None:
            rate = await get_currency_rate_from_db(tx_req.currency, db)
            if rate is None:
                rate = 1.0
            else:
                await set_currency_rate_to_cache(tx_req.currency, rate, expire_seconds=3600)

        transaction_event = tx_req.dict()
        transaction_event.update({
            "transaction_id": str(uuid.uuid4()),
            "received_time": datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
            "bank_id": str(bank.bank_id),
            "currency_exchange_rate": rate,
        })

        dt = transaction_event["transaction_time"]
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        transaction_event["transaction_time"] = dt.isoformat(timespec="milliseconds").replace("+00:00", "Z")

        send_transaction(transaction_event)
        
        return {
            "status": "success",
            "transaction_id": transaction_event["transaction_id"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
