## Project Description

This project is a fraud detection system that leverages BSCORE, a probability score generated using Logistic Regression, to identify and prioritize potentially fraudulent transactions. The system is designed to support data ingestion, risk scoring, and result visualization, enabling faster and more accurate fraud detection for financial or transactional data.

---

## Tech Stack
- **Backend:** Python, FastAPI (or Flask)
- **Machine Learning:** scikit-learn (Logistic Regression), pandas, numpy
- **Database:** PostgreSQL, SQL (with migration scripts)
- **Object Storage:** MinIO
- **Messaging/Streaming:** Kafka, Apache Flink
- **Frontend Dashboard:** React.js (with Vite), JavaScript, Power BI
- **Others:** Redis, Docker (optional for deployment)

## Features
- BSCORE calculation using Logistic Regression
- Transaction risk scoring and prioritization
- Data ingestion and preprocessing pipeline
- Dashboard for fraud monitoring and investigation (React.js & Power BI)
- Integration with databases, message brokers, object storage, and Redis cache
- Real-time stream processing with Apache Flink
- Rule-based AI agent for automated fraud pattern detection and decision support
- Integrated chatbot for user interaction and support

## Dataset
Table : User
Column Name | Data Type | Description
--- | --- | ---
user_id | UUID | Primary key
source_user_id | String | Source user ID
source_bank_id | UUID | Source bank ID
name | String | User name
email | String | User email
phone | String | User phone
address | String | User address
job_title | String | User job title
user_type | String | User type
kyc_status | String | KYC status
kyc_verified_at | DateTime | KYC verified at
is_active | Boolean | Is active
is_fraud | Boolean | Is fraud
registration_date | DateTime | Registration date
last_login | DateTime | Last login
device_count | Integer | Device count
ip_count | Integer | IP count
risk_score | Float | Risk score
notes | String | Notes

Table : Device
Column Name | Data Type | Description
--- | --- | ---
device_uuid | UUID | Primary key
device_id | String | Device ID
source_bank_id | UUID | Source bank ID
user_id | UUID | User ID
device_type | String | Device type
os_version | String | OS version
app_version | String | App version
is_emulator | Boolean | Is emulator

Table : IP Address
Column Name | Data Type | Description
--- | --- | ---
ip_id | UUID | Primary key
transaction_id | UUID | Transaction ID
user_id | UUID | User ID
ip_address | String | IP address
location | String | Location
is_proxy | Boolean | Is proxy
created_at | DateTime | Created at

Table : Bank
Column Name | Data Type | Description
--- | --- | ---
bank_id | UUID | Primary key
bank_name | String | Bank name
bank_code | String | Bank code
swift_code | String | Swift code
api_key | String | API key
address | String | Address
contact_phone | String | Contact phone
contact_email | String | Contact email
is_active | Boolean | Is active
created_at | DateTime | Created at
updated_at | DateTime | Updated at

Table : Account
Column Name | Data Type | Description
--- | --- | ---
account_id | UUID | Primary key
user_id | UUID | User ID
bank_id | UUID | Bank ID
account_type | String | Account type
account_number | String | Account number
account_name | String | Account name
balance | DECIMAL | Balance
currency | String | Currency
status | String | Status
created_at | DateTime | Created at
updated_at | DateTime | Updated at
is_fraud | Boolean | Is fraud

Table : Merchant
Column Name | Data Type | Description
--- | --- | ---
merchant_id | UUID | Primary key
source_bank_id | UUID | Source bank ID
merchant_code | String | Merchant code
name | String | Merchant name
category | String | Merchant category
location | String | Merchant location
phone | String | Merchant phone
email | String | Merchant email
risk_level | String | Merchant risk level
status | String | Merchant status
registered_at | DateTime | Merchant registered at
last_transaction_date | DateTime | Merchant last transaction date
notes | String | Merchant notes
created_at | DateTime | Merchant created at

Table : Transaction
Column Name | Data Type | Description
--- | --- | ---
id | UUID | Primary key
transaction_id | String | Transaction ID
bank_id | UUID | Bank ID
user_id | UUID | User ID
merchant_id | UUID | Merchant ID
amount | DECIMAL | Transaction amount
currency | String | Transaction currency
status | String | Transaction status
created_at | DateTime | Transaction created at
updated_at | DateTime | Transaction updated at

Table : Enrichment
Column Name | Data Type | Description
--- | --- | ---
id | UUID | Primary key
transaction_id | UUID | Transaction ID
user_id | UUID | User ID
amount_idr | Float | Amount in IDR
hour_of_day | Integer | Hour of day
day_of_week | Integer | Day of week
is_weekend | Boolean | Is weekend
is_night | Boolean | Is night
ip_is_private | Boolean | Is IP private
device_type_category | String | Device type category
txn_count_5min | Integer | Transaction count in 5 minutes
txn_amount_sum_5min | Float | Transaction amount sum in 5 minutes
created_at | DateTime | Enrichment created at
updated_at | DateTime | Enrichment updated at
is_fraud | Boolean | Is fraud
rule_result | JSONB | Rule result
bscore | Float | Bscore

Table : Alert
Column Name | Data Type | Description
--- | --- | ---
alert_id | UUID | Primary key
transaction_id | UUID | Transaction ID
alert_type | String | Alert type
rule_name | String | Rule name
score | Float | Alert score
created_at | DateTime | Alert created at
status | String | Alert status

Table : Rule
Column Name | Data Type | Description
--- | --- | ---
rule_id | UUID | Primary key
rule_name | String | Rule name
rule_type | String | Rule type
rule_description | String | Rule description
rule_threshold | Float | Rule threshold
rule_weight | Float | Rule weight
created_at | DateTime | Rule created at
updated_at | DateTime | Rule updated at

Table : DeviceUsageLog
Column Name | Data Type | Description
--- | --- | ---
log_id | UUID | Primary key
user_id | UUID | User ID
device_uuid | UUID | Device UUID
ip_address | String | IP address
login_time | DateTime | Login time
location | String | Location

Table : ComplianceRecord
Column Name | Data Type | Description
--- | --- | ---
record_id | UUID | Primary key
user_id | UUID | User ID
account_id | UUID | Account ID
transaction_id | UUID | Transaction ID
compliance_type | String | Compliance type
status | String | Compliance status
notes | String | Compliance notes
checked_at | DateTime | Compliance checked at

Table : Blacklist
Column Name | Data Type | Description
--- | --- | ---
id | UUID | Primary key
entity_type | String | Entity type
entity_id | String | Entity ID
source_bank_id | UUID | Source bank ID
reason | String | Reason
added_at | DateTime | Added at
removed_at | DateTime | Removed at
added_by | String | Added by
active | Boolean | Active

Table : CurrencyRate
Column Name | Data Type | Description
--- | --- | ---
currency | String | Currency
rate_to_idr | Float | Rate to IDR
date | Date | Date
source | String | Source



