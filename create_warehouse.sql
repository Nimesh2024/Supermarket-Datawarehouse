CREATE DATABASE IF NOT EXISTS supermarket_dw
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE supermarket_dw;

CREATE TABLE IF NOT EXISTS DimDate (
    date_key INT PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    day_number TINYINT NOT NULL,
    month_number TINYINT NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    quarter_number TINYINT NOT NULL,
    year_number SMALLINT NOT NULL
);

CREATE TABLE IF NOT EXISTS DimProduct (
    product_key INT PRIMARY KEY,
    product_name VARCHAR(150) NOT NULL,
    category VARCHAR(100),
    unit_cost DECIMAL(12,2) NOT NULL,
    selling_price DECIMAL(12,2) NOT NULL,
    stock_quantity INT NOT NULL
);

CREATE TABLE IF NOT EXISTS DimCustomer (
    customer_key INT PRIMARY KEY,
    customer_name VARCHAR(150) NOT NULL,
    city VARCHAR(100),
    gender VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS DimBranch (
    branch_key INT PRIMARY KEY,
    branch_name VARCHAR(150) NOT NULL,
    city VARCHAR(100),
    address VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS DimSupplier (
    supplier_key INT PRIMARY KEY,
    supplier_name VARCHAR(150) NOT NULL,
    city VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS FactSales (
    fact_sales_key BIGINT AUTO_INCREMENT PRIMARY KEY,
    sale_id INT NOT NULL,
    sale_item_id INT NOT NULL,
    date_key INT NOT NULL,
    product_key INT NOT NULL,
    customer_key INT NOT NULL,
    branch_key INT NOT NULL,
    quantity INT NOT NULL,
    unit_selling_price DECIMAL(12,2) NOT NULL,
    discount_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    sales_amount DECIMAL(14,2) NOT NULL,
    cost_amount DECIMAL(14,2) NOT NULL,
    profit_amount DECIMAL(14,2) NOT NULL,

    UNIQUE KEY uq_sale_item (sale_id, sale_item_id),

    FOREIGN KEY (date_key) REFERENCES DimDate(date_key),
    FOREIGN KEY (product_key) REFERENCES DimProduct(product_key),
    FOREIGN KEY (customer_key) REFERENCES DimCustomer(customer_key),
    FOREIGN KEY (branch_key) REFERENCES DimBranch(branch_key)
);

CREATE TABLE IF NOT EXISTS FactSupplierSupply (
    supplier_key INT NOT NULL,
    product_key INT NOT NULL,
    supply_price DECIMAL(12,2) NOT NULL,
    PRIMARY KEY (supplier_key, product_key),
    FOREIGN KEY (supplier_key) REFERENCES DimSupplier(supplier_key),
    FOREIGN KEY (product_key) REFERENCES DimProduct(product_key)
);

CREATE TABLE IF NOT EXISTS FactFeedback (
    review_id VARCHAR(100) PRIMARY KEY,
    date_key INT NOT NULL,
    customer_key INT NOT NULL,
    product_key INT NOT NULL,
    rating TINYINT NOT NULL,
    review_text TEXT,
    FOREIGN KEY (date_key) REFERENCES DimDate(date_key),
    FOREIGN KEY (customer_key) REFERENCES DimCustomer(customer_key),
    FOREIGN KEY (product_key) REFERENCES DimProduct(product_key)
);

CREATE TABLE IF NOT EXISTS ETLRunLog (
    run_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    started_at DATETIME NOT NULL,
    completed_at DATETIME NULL,
    run_status VARCHAR(20) NOT NULL,
    message TEXT
);
