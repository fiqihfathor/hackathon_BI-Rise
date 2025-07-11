import streamlit as st
import random
import time
from utils import get_users, get_bank_api_key, generate_random_transaction, send_transaction

def bulk_transaction_page():
    st.title("🔁 Auto Transaction Generator")

    users = get_users()
    user_options = {
        f"{name} ({email})": (user_id, source_user_id, name, email, source_bank_id)
        for user_id, source_user_id, name, email, source_bank_id in users
    }

    selected = st.multiselect("Select users", list(user_options.keys()))
    if not selected:
        st.stop()

    selected_user_tuples = [user_options[k] for k in selected]

    col1, col2 = st.columns(2)
    with col1:
        min_amount = st.number_input(
            "Min Amount", 
            min_value=1000, 
            value=st.session_state.get("min_amount", 100000), 
            step=1000, 
            key="min_amount"
        )
        st.caption(f"Min: Rp {min_amount:,.0f}".replace(",", "."))  # Format 1000000 → 1.000.000

    with col2:
        max_default = max(min_amount, st.session_state.get("max_amount", 1000000))
        max_amount = st.number_input(
            "Max Amount", 
            min_value=min_amount, 
            value=max_default, 
            step=1000, 
            key="max_amount"
        )
        st.caption(f"Max: Rp {max_amount:,.0f}".replace(",", "."))

    sleep_seconds = st.number_input("Delay between transactions (sec)", min_value=0.1, value=1.0, step=0.1)

    # Init session state
    if "bulk_running" not in st.session_state:
        st.session_state.bulk_running = False
    if "last_user_idx" not in st.session_state:
        st.session_state.last_user_idx = 0
    if "tx_logs" not in st.session_state:
        st.session_state.tx_logs = []

    # Start / Stop buttons
    if st.button("▶ Start Auto"):
        st.session_state.bulk_running = True
        st.rerun()

    if st.button("⏹ Stop"):
        st.session_state.bulk_running = False
        st.success("Stopped loop.")
        return

    if st.session_state.bulk_running:
        st.warning("🔄 Loop is running... Click STOP to stop.")

        user = selected_user_tuples[st.session_state.last_user_idx]
        user_id = user[0]
        source_bank_id = user[4]

        bank_api_key = get_bank_api_key(source_bank_id)
        if not bank_api_key:
            log = f"❌ {user_id}: API key not found"
        else:
            tx = generate_random_transaction(user)
            tx["amount"] = round(random.uniform(min_amount, max_amount), 2)
            result = send_transaction(tx, bank_api_key)

            if "error" in result:
                log = f"❌ {user_id}: {result['error']}"
            else:
                log = f"✅ {user_id}: Sent tx {result.get('transaction_id', '')}"

        # Save log
        st.session_state.tx_logs.append(log)
        st.session_state.tx_logs = st.session_state.tx_logs[-100:]  # Limit last 100

        # Next user index
        st.session_state.last_user_idx = (st.session_state.last_user_idx + 1) % len(selected_user_tuples)

        # Show log
        st.subheader("📜 Transaction Logs")
        for entry in reversed(st.session_state.tx_logs):
            st.write(entry)

        # Sleep + rerun
        time.sleep(sleep_seconds)
        st.rerun()
