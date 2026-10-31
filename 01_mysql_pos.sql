
CREATE DATABASE IF NOT EXISTS supermarket_pos;
USE supermarket_pos;

-- 1. Sales transaction table
CREATE TABLE IF NOT EXISTS pos_sales (
    sale_id INT PRIMARY KEY,
    sale_datetime DATETIME NOT NULL,
    customer_id INT NOT NULL,
    branch_id INT NOT NULL,
    payment_method VARCHAR(30),
    status VARCHAR(20) DEFAULT 'COMPLETED'
);

-- 2. Sales item details table
CREATE TABLE IF NOT EXISTS pos_sale_items (
    sale_item_id INT PRIMARY KEY,
    sale_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0,

    CONSTRAINT fk_pos_sale
        FOREIGN KEY (sale_id)
        REFERENCES pos_sales(sale_id),

    CONSTRAINT chk_quantity
        CHECK (quantity > 0),

    CONSTRAINT chk_unit_price
        CHECK (unit_price >= 0),

    CONSTRAINT chk_discount
        CHECK (discount_amount >= 0)
);

-- 3. Sample sales transactions
INSERT INTO pos_sales
(sale_id, sale_datetime, customer_id, branch_id,
 payment_method, status)
VALUES
(1001, '2026-01-05 10:30:00', 1, 101, 'Cash', 'COMPLETED'),
(1002, '2026-01-05 11:15:00', 2, 102, 'Card', 'COMPLETED'),
(1003, '2026-01-06 14:20:00', 3, 101, 'Cash', 'COMPLETED'),
(1004, '2026-01-07 16:45:00', 1, 103, 'Card', 'COMPLETED'),
(1005, '2026-02-02 09:30:00', 4, 102, 'Cash', 'COMPLETED'),
(1006, '2026-02-10 12:10:00', 5, 101, 'Card', 'COMPLETED'),
(1007, '2026-02-12 17:00:00', 2, 103, 'Cash', 'COMPLETED'),
(1008, '2026-03-01 13:25:00', 3, 102, 'Card', 'COMPLETED');

-- 4. Sample sale item details
INSERT INTO pos_sale_items
(sale_item_id, sale_id, product_id, quantity,
 unit_price, discount_amount)
VALUES
(1, 1001, 1001, 2, 250.00, 0),
(2, 1001, 1002, 1, 450.00, 50),
(3, 1002, 1003, 3, 180.00, 0),
(4, 1002, 1001, 1, 250.00, 0),
(5, 1003, 1004, 2, 1200.00, 100),
(6, 1004, 1002, 4, 450.00, 0),
(7, 1005, 1003, 5, 180.00, 0),
(8, 1005, 1005, 2, 350.00, 0),
(9, 1006, 1001, 4, 250.00, 0),
(10, 1006, 1004, 1, 1200.00, 0),
(11, 1007, 1005, 3, 350.00, 50),
(12, 1008, 1003, 2, 180.00, 0);

-- 5. Verify the source data
SELECT * FROM pos_sales;
SELECT * FROM pos_sale_items;

-- 6. Calculate sales totals
SELECT
    s.sale_id,
    s.sale_datetime,
    SUM(i.quantity * i.unit_price
        - i.discount_amount) AS total_sales
FROM pos_sales s
JOIN pos_sale_items i ON s.sale_id = i.sale_id
WHERE s.status = 'COMPLETED'
GROUP BY s.sale_id, s.sale_datetime
ORDER BY s.sale_datetime;



SHOW DATABASES LIKE 'supermarket_pos';

USE supermarket_pos;

SHOW TABLES;

SELECT COUNT(*) AS total_sales
FROM pos_sales;

SELECT COUNT(*) AS total_sale_items
FROM pos_sale_items;