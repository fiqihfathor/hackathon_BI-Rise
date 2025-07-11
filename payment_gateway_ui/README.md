# Sample Streamlit UI for Payment Gateway

This microservice provides a simple Streamlit-based UI to:
- Display sample users from a Postgres database
- Send a payment request to the payment gateway

## Setup

1. Copy `.env.example` to `.env` and fill in your database and payment gateway details.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

## Environment Variables
- `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`: Postgres connection details
- `PAYMENT_GATEWAY_URL`: Base URL of the payment gateway API

## Notes
- The app expects a `users` table with at least `id`, `username`, and `email` fields.
- The payment endpoint is expected at `/pay` on the payment gateway.
