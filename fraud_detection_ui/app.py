import streamlit as st
import redis
import json
import os

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_KEY = "fraud_alerts"

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

st.set_page_config(page_title="Fraud Monitoring Dashboard", layout="wide")
tabs = st.tabs(["Fraud Alert Monitoring", "Tab 2", "Tab 3"])

# Tab 1: Fraud Alert Monitoring
with tabs[0]:
    st.header("Fraud Alert Monitoring")
    alerts = r.lrange(REDIS_KEY, 0, 99)  # show latest 100 alerts
    alerts = [json.loads(a) for a in alerts]
    st.write(f"Total alerts cached: {r.llen(REDIS_KEY)}")
    if alerts:
        st.dataframe(alerts)
    else:
        st.info("No alerts found in Redis cache.")

# Tab 2 & 3: Kosong
with tabs[1]:
    st.header("Tab 2 (Coming Soon)")
with tabs[2]:
    st.header("Tab 3 (Coming Soon)")
