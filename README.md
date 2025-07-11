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