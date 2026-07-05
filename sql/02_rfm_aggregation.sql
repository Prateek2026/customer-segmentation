-- Computes Recency, Frequency, Monetary per customer from clean_transactions.
-- Snapshot date = one day after the last invoice date in the dataset,
-- so Recency for the most recent purchaser is >= 1.

DROP TABLE IF EXISTS customer_rfm;

CREATE TABLE customer_rfm AS
WITH snapshot AS (
    SELECT DATE(MAX(InvoiceDate), '+1 day') AS snapshot_date
    FROM clean_transactions
)
SELECT
    CustomerID,
    CAST(JULIANDAY((SELECT snapshot_date FROM snapshot)) - JULIANDAY(MAX(InvoiceDate)) AS INTEGER) AS Recency,
    COUNT(DISTINCT InvoiceNo) AS Frequency,
    ROUND(SUM(LineRevenue), 2) AS Monetary
FROM clean_transactions
GROUP BY CustomerID;
