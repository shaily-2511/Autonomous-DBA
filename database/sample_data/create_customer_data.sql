-- ============================================================
-- CORRECTED: Sample Data Generation with Forced Statistics Update
-- PostgreSQL Conference 2026
-- Table: customer_data
-- ============================================================

-- Step 1: Drop existing table to start fresh
DROP TABLE IF EXISTS customer_data CASCADE;

-- Step 2: Create the customer_data table
CREATE TABLE customer_data (
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(50),
    state VARCHAR(2),
    zip_code VARCHAR(10),
    account_status VARCHAR(20) NOT NULL,
    total_purchases DECIMAL(10,2) DEFAULT 0.00,
    last_purchase_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Step 3: Insert initial sample data (10,000 customers)
INSERT INTO customer_data (first_name, last_name, email, phone, address, city, state, zip_code, account_status, total_purchases, last_purchase_date)
SELECT
    'FirstName' || gs as first_name,
    'LastName' || gs as last_name,
    'customer' || gs || '@example.com' as email,
    '555-' || LPAD((random() * 9999)::TEXT, 4, '0') as phone,
    (random() * 9999)::INTEGER || ' Main Street' as address,
    'City' || (random() * 100)::INTEGER as city,
    CASE (random() * 5)::INTEGER
        WHEN 0 THEN 'CA'
        WHEN 1 THEN 'NY'
        WHEN 2 THEN 'TX'
        WHEN 3 THEN 'FL'
        ELSE 'WA'
    END as state,
    LPAD((random() * 99999)::TEXT, 5, '0') as zip_code,
    CASE (random() * 3)::INTEGER
        WHEN 0 THEN 'active'
        WHEN 1 THEN 'inactive'
        ELSE 'pending'
    END as account_status,
    (random() * 5000 + 100)::DECIMAL(10,2) as total_purchases,
    CURRENT_TIMESTAMP - (random() * 180 || ' days')::INTERVAL as last_purchase_date
FROM generate_series(1, 10000) gs;

-- Step 4: Force statistics collection after initial insert
ANALYZE customer_data;

-- Step 5: Create bloat by performing multiple UPDATE operations
-- Update 1: Change account status for 35% of customers
UPDATE customer_data
SET account_status = 'active', updated_at = CURRENT_TIMESTAMP
WHERE customer_id IN (
    SELECT customer_id FROM customer_data
    WHERE account_status = 'pending'
    LIMIT 3500
);

-- Update 2: Update email addresses for 30% of customers
UPDATE customer_data
SET email = 'updated_' || email, updated_at = CURRENT_TIMESTAMP
WHERE customer_id IN (
    SELECT customer_id FROM customer_data
    ORDER BY random()
    LIMIT 3000
);

-- Update 3: Update total purchases for 25% of customers
UPDATE customer_data
SET total_purchases = total_purchases * 1.15,
    last_purchase_date = CURRENT_TIMESTAMP,
    updated_at = CURRENT_TIMESTAMP
WHERE customer_id IN (
    SELECT customer_id FROM customer_data
    ORDER BY random()
    LIMIT 2500
);

-- Update 4: Update addresses for 20% of customers
UPDATE customer_data
SET address = 'Updated Address ' || customer_id,
    city = 'NewCity' || (random() * 50)::INTEGER,
    updated_at = CURRENT_TIMESTAMP
WHERE customer_id IN (
    SELECT customer_id FROM customer_data
    ORDER BY random()
    LIMIT 2000
);

-- Update 5: Update phone numbers for 15% of customers
UPDATE customer_data
SET phone = '555-' || LPAD((random() * 9999)::TEXT, 4, '0'),
    updated_at = CURRENT_TIMESTAMP
WHERE customer_id IN (
    SELECT customer_id FROM customer_data
    ORDER BY random()
    LIMIT 1500
);

-- Step 6: Delete some records to create more dead tuples
DELETE FROM customer_data
WHERE customer_id IN (
    SELECT customer_id FROM customer_data
    WHERE account_status = 'inactive'
    LIMIT 600
);

-- Step 7: CRITICAL - Force PostgreSQL to update statistics
-- This makes the dead tuples visible in pg_stat_user_tables
ANALYZE customer_data;

-- Step 8: Wait a moment for statistics to propagate
SELECT pg_sleep(2);

-- Step 9: Verify the bloat
SELECT
    schemaname,
    relname as tablename,
    n_live_tup as live_tuples,
    n_dead_tup as dead_tuples,
    ROUND(n_dead_tup * 100.0 / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_tuple_percent,
    CASE
        WHEN n_dead_tup * 100.0 / NULLIF(n_live_tup + n_dead_tup, 0) > 20 THEN 'VACUUM REQUIRED'
        ELSE 'OK'
    END as recommendation
FROM pg_stat_user_tables
WHERE relname = 'customer_data';

-- Step 10: Show detailed table statistics
SELECT
    pg_size_pretty(pg_total_relation_size('customer_data')) as total_size,
    pg_size_pretty(pg_relation_size('customer_data')) as table_size,
    pg_size_pretty(pg_indexes_size('customer_data')) as indexes_size;

-- Step 11: Additional verification
SELECT
    COUNT(*) as total_records,
    COUNT(CASE WHEN account_status = 'active' THEN 1 END) as active_customers,
    COUNT(CASE WHEN account_status = 'pending' THEN 1 END) as pending_customers,
    ROUND(AVG(total_purchases), 2) as avg_purchase_amount
FROM customer_data;

