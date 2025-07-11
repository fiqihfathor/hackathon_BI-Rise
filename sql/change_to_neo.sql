WITH user_features AS (
    SELECT
        u.user_id,
        COUNT(t.transaction_id) AS total_transactions,
        AVG(t.amount) AS avg_transaction_amount,
        COUNT(DISTINCT t.merchant_id) AS unique_merchants,
        SUM(CASE WHEN d.is_emulator THEN 1 ELSE 0 END) AS emulator_device_count,
        SUM(CASE WHEN ip.is_proxy THEN 1 ELSE 0 END) AS proxy_ip_count,
        COUNT(a.alert_id) AS alert_count,
        AVG(a.score) AS avg_alert_score,
        COUNT(cr.record_id) AS compliance_record_count
    FROM users u
    LEFT JOIN transactions t ON u.user_id = t.user_id
    LEFT JOIN devices d ON u.user_id = d.user_id
    LEFT JOIN ip_addresses ip ON u.user_id = ip.user_id
    LEFT JOIN alerts a ON a.transaction_id = t.id 
    LEFT JOIN compliance_records cr ON u.user_id = cr.user_id
    GROUP BY u.user_id
)
SELECT
    -- FROM node: User
    u.user_id AS from_user_id,
    u.name AS from_user_name,
    u.email AS from_user_email,
    u.phone AS from_user_phone,
    u.job_title AS from_user_job,
    u.user_type AS from_user_type,
--    u.is_fraud AS from_user_is_fraud,
    -- TO node: Merchant
    m.merchant_id AS to_merchant_id,
    m.name AS to_merchant_name,
    m.category AS to_merchant_category,
    m.location AS to_merchant_location,
    m.risk_level AS to_merchant_risk_level,
    -- Edge / Relationship
    t.transaction_id,
    t.amount,
    t.transaction_time,
    t.transaction_type,
    t.location AS transaction_location,
    -- ⛳ Rule-based fraud flag (per transaksi, diturunkan dari user)
    CASE
        WHEN 
            uf.total_transactions > 50 AND uf.avg_transaction_amount < 10000
            OR uf.emulator_device_count >= 2
            OR uf.proxy_ip_count >= 3
            OR uf.alert_count >= 3 AND uf.avg_alert_score > 70
            OR uf.unique_merchants >= 10 AND uf.total_transactions > 20
            OR uf.compliance_record_count >= 2
        THEN 1 ELSE 0
    END AS transaction_is_fraud_flag
FROM transactions t
JOIN users u ON t.user_id = u.user_id
JOIN merchants m ON t.merchant_id = m.merchant_id
LEFT JOIN user_features uf ON uf.user_id = u.user_id
WHERE t.transaction_time::date = CURRENT_DATE - INTERVAL '1 day'