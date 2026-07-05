-- Cleans the raw Online Retail transactions table.
-- Removes: cancelled invoices (InvoiceNo starting with 'C'), rows with
-- no CustomerID, non-positive quantities, and non-positive prices.

DROP TABLE IF EXISTS clean_transactions;

CREATE TABLE clean_transactions AS
SELECT
    InvoiceNo,
    StockCode,
    Description,
    Quantity,
    InvoiceDate,
    UnitPrice,
    CAST(CustomerID AS INTEGER) AS CustomerID,
    Country,
    Quantity * UnitPrice AS LineRevenue
FROM raw_transactions
WHERE CustomerID IS NOT NULL
  AND InvoiceNo NOT LIKE 'C%'
  AND Quantity > 0
  AND UnitPrice > 0;
