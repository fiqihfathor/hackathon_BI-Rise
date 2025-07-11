from redis.asyncio import Redis
import json
import os
from dotenv import load_dotenv

load_dotenv()
redis = None

async def get_redis():
    global redis
    if redis is None:
        redis = await Redis.from_url(os.getenv("REDIS_URL"), encoding="utf8", decode_responses=True)
    return redis

async def get_currency_rate_from_cache(currency: str):
    redis = await get_redis()
    rate_json = await redis.get(f"currency_rate:{currency}")
    if rate_json:
        return float(rate_json)
    return None

async def set_currency_rate_to_cache(currency: str, rate: float, expire_seconds: int = 3600):
    redis = await get_redis()
    await redis.set(f"currency_rate:{currency}", str(rate), ex=expire_seconds)
