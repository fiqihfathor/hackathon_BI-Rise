import redis
import json
from db.models import Rule

def load_rules_to_redis(session, redis_client, redis_key="rules:all"):
    """
    Query semua rule aktif dari DB, simpan ke Redis sebagai JSON list.
    """
    rules = session.query(Rule).filter(Rule.active == True).all()
    rules_data = [
        {
            "id": str(rule.rule_id),
            "rule_name": rule.rule_name,
            "rule_dsl": rule.rule_dsl,
            "description": rule.description,
            "source": rule.source,
            "created_at": str(rule.created_at)
        }
        for rule in rules
    ]
    redis_client.set(redis_key, json.dumps(rules_data))