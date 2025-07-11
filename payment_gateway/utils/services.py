
from fastapi import Header, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from utils.config import get_db
from sqlalchemy import text

async def get_currency_rate_from_db(currency: str, db_session):
    query = text("SELECT rate_to_idr FROM currency_rates WHERE currency = :currency ORDER BY date DESC LIMIT 1")
    result = await db_session.execute(query, {"currency": currency})
    row = result.fetchone()
    if row:
        return row[0]
    return None


async def validate_api_key(
    session: AsyncSession = Depends(get_db),
    x_api_key: str = Header(...),
):
    query = text("SELECT * FROM banks WHERE api_key = :api_key AND is_active = True")
    async with session:
        result = await session.execute(query, {"api_key": x_api_key})
        row = result.first()
        if not row:
            raise HTTPException(status_code=401, detail="Invalid or inactive API key")
        return row