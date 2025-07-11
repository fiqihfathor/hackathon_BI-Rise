import logging
import threading
import time
from rule_loader import load_rules_to_redis
from db.models import Blacklist

def start_rule_refresh_scheduler(session, redis_client, interval_sec=300):
    """
    Scheduler thread untuk refresh rules ke Redis setiap interval_sec detik.
    """

    def refresh_loop():
        while True:
            try:
                load_rules_to_redis(session, redis_client)
                logging.info("[Scheduler] Successfully refreshed rules to Redis.")
            except Exception as e:
                logging.error(f"[Scheduler] Error refreshing rules: {e}")
            time.sleep(interval_sec)

    thread = threading.Thread(target=refresh_loop, daemon=True)
    thread.start()
    return thread



def start_blacklist_refresh_scheduler(session, redis_client, interval_sec=300):
    """
    Scheduler thread untuk refresh blacklist user/device ke Redis setiap interval_sec detik.
    """
    def refresh_blacklist_loop():
        while True:
            try:
                load_blacklists_to_redis(session, redis_client)
                logging.info("[Scheduler] Successfully refreshed blacklist to Redis.")
            except Exception as e:
                print(f"[Scheduler] Error refreshing blacklist: {e}")
            time.sleep(interval_sec)

    thread = threading.Thread(target=refresh_blacklist_loop, daemon=True)
    thread.start()
    return thread


def load_blacklists_to_redis(db_session, redis_client, ttl=24*3600):
    """
    Ambil semua blacklist user & device dari DB, simpan ke Redis.
    """
    # User blacklist
    user_blacklist = db_session.query(Blacklist).filter_by(
        entity_type="user", active=True
    ).all()
    for entry in user_blacklist:
        redis_key = f"blacklist:user:{entry.entity_id}:{entry.source_bank_id}"
        redis_client.set(redis_key, "1", ex=ttl)

    # Device blacklist
    device_blacklist = db_session.query(Blacklist).filter_by(
        entity_type="device", active=True
    ).all()
    for entry in device_blacklist:
        redis_key = f"blacklist:device:{entry.entity_id}:{entry.source_bank_id}"
        redis_client.set(redis_key, "1", ex=ttl)

    logging.info(f"Loaded {len(user_blacklist)} user blacklist & {len(device_blacklist)} device blacklist to Redis.")