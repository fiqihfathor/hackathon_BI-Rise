import re
import datetime
from typing import Any
from cache_helpers import get_set_from_redis, set_set_to_redis
from db.models import Blacklist, DeviceUsageLog, User

redis_client = 'redis://redis:6379/0'
def eval_operator(actual: Any, operator: str, value: Any) -> bool:
    if actual is None:
        return False
    if operator == '>':
        return actual > value
    elif operator == '>=':
        return actual >= value
    elif operator == '<':
        return actual < value
    elif operator == '<=':
        return actual <= value
    elif operator == '==':
        return actual == value
    elif operator == '!=':
        return actual != value
    elif operator == 'in':
        return actual in value
    elif operator == 'not_in':
        return actual not in value
    elif operator == 'between_hour':
        if not isinstance(actual, datetime.datetime):
            return False
        hour = actual.hour
        return value[0] <= hour <= value[1]
    else:
        raise ValueError(f"Operator '{operator}' belum diimplementasikan")

def eval_condition(cond: dict, tx: dict, context: dict) -> bool:
    if isinstance(cond, str):
        raise ValueError(f"Invalid condition format: got string '{cond}'")

    if 'and' in cond:
        return all(eval_condition(c, tx, context) for c in cond['and'])
    if 'or' in cond:
        return any(eval_condition(c, tx, context) for c in cond['or'])

    if 'function' in cond:
        fn_name = cond['function']
        params = cond.get('params', {})
        fn = context.get('functions', {}).get(fn_name)
        if not fn:
            raise ValueError(f"Function '{fn_name}' tidak ditemukan di context")
        return fn(tx, **params)

    field = cond.get('field')
    operator = cond.get('operator')
    value = cond.get('value')

    actual = tx.get(field)
    # Patch: auto-cast string to float/int for numeric ops
    numeric_ops = {'>', '<', '>=', '<=', '==', '!='}
    if operator in numeric_ops:
        try:
            if isinstance(actual, str):
                try:
                    actual = float(actual)
                except Exception:
                    pass
            if isinstance(value, str):
                try:
                    value = float(value)
                except Exception:
                    pass
        except Exception:
            pass
    return eval_operator(actual, operator, value)

def evaluate_rule(rule_dsl: dict, tx: dict, context: dict = {}) -> bool:
    if not isinstance(rule_dsl, dict):
        raise ValueError("Rule DSL harus berupa dictionary")
    return eval_condition(rule_dsl, tx, context)


def user_kyc_status(tx, required_status='verified', db_session=None, **kwargs):
    """
    True jika status KYC user di DB sesuai required_status.
    """
    user_id = tx.get('source_user_id')
    bank_id = tx.get('source_bank_id')

    redis_key=f"user_kyc_status:{user_id}:{bank_id}"
    cached_status = get_set_from_redis(redis_client, redis_key)
    if cached_status is not None:
        return cached_status.decode() == required_status
    
    if not db_session or not user_id or not bank_id:
        return False
    user = db_session.query(User).filter_by(source_user_id=user_id, source_bank_id=bank_id).first()

    if user:
        set_set_to_redis(redis_client, redis_key, user.kyc_status)
    return user and getattr(user, "kyc_status", None) == required_status

def is_blacklisted_user(tx, **kwargs)->bool:
    """
    True jika user_id ada di blacklist. Redis sebagai cache, DB fallback.
    """
    user_id = tx.get('source_user_id')
    bank_id = tx.get('source_bank_id')
    redis_key=f"blacklist:user:{user_id}:{bank_id}"
    return get_set_from_redis(redis_client, redis_key) is not None

def device_blacklisted(tx: dict, **kwargs) -> bool:
    """
    True jika device_id ada di device_blacklist.
    """
    device_id = tx.get('device_id')
    redis_key=f"blacklist:device:{device_id}"
    return get_set_from_redis(redis_client, redis_key) is not None

# Registry fungsi untuk DSL
PREDEFINED_FUNCTIONS = {
    "is_blacklisted_user": is_blacklisted_user,
    "user_kyc_status": user_kyc_status,
    "device_blacklisted": device_blacklisted,
}

def get_context():
    """
    Context berisi registry fungsi DSL untuk evaluasi rule.
    """
    return {"functions": PREDEFINED_FUNCTIONS}
