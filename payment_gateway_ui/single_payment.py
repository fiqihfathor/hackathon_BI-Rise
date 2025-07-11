import streamlit as st
from utils import get_users, send_transaction, get_bank_api_key, generate_random_transaction
import psycopg2
import os

# Helper to fetch more user details (for preview)
def get_user_details(user_id):
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5433")
    DB_NAME = os.getenv("DB_NAME", "hacketon_fraud")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cur = conn.cursor()
        cur.execute("""
            SELECT name, email, user_type, kyc_status, risk_score, is_fraud
            FROM users WHERE user_id = %s LIMIT 1;
        """, (user_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            return {
                "name": row[0],
                "email": row[1],
                "user_type": row[2],
                "kyc_status": row[3],
                "risk_score": row[4],
                "is_fraud": row[5],
            }
        return None
    except Exception as e:
        return None

def single_payment_page():
    st.header("Send Single Payment")
    users = get_users()
    # --- 1. User Search/Filter ---
    search = st.text_input("Search user by name or email", "")
    # Adjust filter and options for 5-field user tuples
    filtered_users = [u for u in users if search.lower() in u[2].lower() or search.lower() in u[3].lower()]
    user_options = {f"{name} ({email})": (user_id, source_user_id, name, email, source_bank_id) for user_id, source_user_id, name, email, source_bank_id in filtered_users}
    if not user_options:
        st.warning("No users match your search.")
        return
    selected = st.selectbox("Select a user", list(user_options.keys()), key="single_user")
    user_tuple = user_options[selected]
    user_id = user_tuple[0]
    source_user_id = user_tuple[1]
    source_bank_id = user_tuple[4]

    # --- 2. User Detail Preview ---
    details = get_user_details(user_id)
    if details:
        with st.expander("Show user details"):
            st.write(f"**Name:** {details['name']}")
            st.write(f"**Email:** {details['email']}")
            st.write(f"**KYC Status:** {details['kyc_status']}")
            st.write(f"**User Type:** {details['user_type']}")
            st.write(f"**Risk Score:** {details['risk_score']}")
            st.write(f"**Is Fraud:** {'Yes' if details['is_fraud'] else 'No'}")
            if details['is_fraud'] or (details['risk_score'] and details['risk_score'] >= 0.7):
                st.warning("⚠️ This user is flagged as high risk or fraud.")

    # --- 4. Payment Amount ---
    amount = st.number_input("Payment Amount", min_value=1000, step=1000, value=100000, key="single_amount")
    note = st.text_input("Payment Note (optional)", "")

    # --- 5. Payment Button with Loading ---
    pay_btn = st.button("Send Payment", key="send_payment_btn")
    if pay_btn:
        with st.spinner("Sending payment..."):
            bank_api_key = get_bank_api_key(source_bank_id)
            if not bank_api_key:
                st.error("Could not find API key for user's bank.")
                return
            tx = generate_random_transaction(user_tuple)
            tx["amount"] = amount
            if note:
                tx["notes"] = note
            with st.expander("Show Transaction Data"):
                st.json(tx)
            result = send_transaction(tx, bank_api_key)
        # --- 6. Feedback Card ---
        if "error" in result:
            st.error(result["error"])
        else:
            st.success("Payment sent!")
            st.json(result)
            st.info(f"Amount: {amount} | Note: {note if note else '-'} | User: {details['name']} ({details['email']})")

