import json
import requests
import os
from dotenv import load_dotenv
import time
load_dotenv()

SCHEMA_REGISTRY_URL = os.getenv("SCHEMA_REGISTRY_URL")

SUBJECT = "transactions_raw-value"  # biasanya topic + "-value"
SCHEMA_FILE = "kafka_manager/schema/transaction_raw.avsc"

def register_schema(schema_registry_url, subject, schema_file, max_retries=5, delay=3):
    with open(schema_file, "r") as f:
        schema_str = f.read()
    
    payload = {
        "schema": json.dumps(json.loads(schema_str))
    }
    url = f"{schema_registry_url}/subjects/{subject}/versions"
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers={"Content-Type": "application/vnd.schemaregistry.v1+json"}, json=payload)
            if response.status_code == 200:
                print(f"Schema registered with id: {response.json()['id']}")
                return
            else:
                print(f"Failed to register schema: {response.status_code} {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt+1} failed: {e}")
        
        print(f"Retrying in {delay} seconds...")
        time.sleep(delay)
    
    raise Exception("Failed to register schema after multiple retries")

if __name__ == "__main__":
    register_schema(SCHEMA_REGISTRY_URL, SUBJECT, SCHEMA_FILE)
    time.sleep(2)