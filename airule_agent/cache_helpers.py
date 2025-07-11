import json
from redis import Redis

def get_redis():
    return Redis.from_url(os.getenv("REDIS_URL"), encoding="utf8", decode_responses=True)

def get_set_from_redis(redis_client, key):
    """
    Ambil set (atau string/boolean) dari Redis. Return None jika key tidak ada.
    Jika value adalah JSON list/set, return set. Jika string/boolean, return string.
    """
    val = redis_client.get(key)
    if val is None:
        return None
    try:
        # Coba parse JSON, fallback ke string
        return set(json.loads(val))
    except Exception:
        return val  # fallback: string (misal untuk cache boolean "1"/"0")

def set_set_to_redis(redis_client, key, data, expire=300):
    """
    Simpan set/list ke Redis sebagai JSON. Data juga bisa string/boolean.
    """
    if isinstance(data, (set, list)):
        redis_client.set(key, json.dumps(list(data)), ex=expire)
    else:
        redis_client.set(key, str(data), ex=expire)