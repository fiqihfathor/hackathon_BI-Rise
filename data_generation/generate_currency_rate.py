import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import requests
import datetime
from db.models import CurrencyRate
from sqlalchemy.orm import Session

def fetch_idr_rates_all():
    """
    Fetch all available currency rates to IDR from open.er-api.com (no API key needed).
    Returns dict: {currency: rate_to_idr}
    """
    url = "https://open.er-api.com/v6/latest/IDR"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if resp.status_code != 200 or "rates" not in data:
            print(f"API error: {data}")
            return {}
        rates = data["rates"]
        # rates: {CUR: rate_idr_to_cur}, so we need to invert to get cur_to_idr
        idr_rates = {cur: (1/rate if rate else None) for cur, rate in rates.items() if rate and cur != "IDR"}
        return idr_rates
    except Exception as e:
        print(f"Failed to fetch all currency rates: {e}")
        return {}

def generate_currency_rates(session: Session, date=None):
    """
    Generate CurrencyRate rows for today (or given date) using live rates for ALL currencies.
    """
    if date is None:
        date = datetime.date.today()
    rates = fetch_idr_rates_all()
    count = 0
    for currency, rate in rates.items():
        if rate is None:
            continue
        row = CurrencyRate(
            currency=currency,
            rate_to_idr=rate,
            date=date,
            source="exchangerate.host"
        )
        session.merge(row)
        count += 1
    session.commit()
    print(f"Inserted/updated rates for {count} currencies on {date}")

if __name__ == "__main__":
    from db.config import SessionLocal
    session = SessionLocal()
    generate_currency_rates(session)
    session.close()
