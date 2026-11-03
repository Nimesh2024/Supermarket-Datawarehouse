-- ========================================================================================
-- SUPERMARKET DATA WAREHOUSE (supermarket_dw) - 15 BUSINESS ANALYTICAL QUERIES
-- ========================================================================================
-- Database: supermarket_dw
-- Description: 15 distinct, meaningful business analytical queries designed for decision-making,
--              performance monitoring, customer retention, inventory management, and supplier evaluation.
-- ========================================================================================

USE supermarket_dw;

-- ========================================================================================
-- 1. REVENUE AND PROFIT CONTRIBUTION BY PRODUCT CATEGORY
-- Business Importance:
-- Identifies which product categories drive the highest sales revenue versus profit margin.
-- Helps retail executives optimize shelf-space allocation and inventory procurement budgets.
-- ========================================================================================
SELECT 
    p.category AS Category,
    SUM(f.quantity) AS Total_Units_Sold,
    ROUND(SUM(f.sales_amount), 2) AS Total_Revenue,
    ROUND(SUM(f.cost_amount), 2) AS Total_Cost,
    ROUND(SUM(f.profit_amount), 2) AS Total_Profit,
    ROUND((SUM(f.profit_amount) / SUM(f.sales_amount)) * 100, 2) AS Profit_Margin_Pct
FROM FactSales f
JOIN DimProduct p ON f.product_key = p.product_key
GROUP BY p.category
ORDER BY Total_Revenue DESC;


-- ========================================================================================
-- 2. TOP 5 BEST-SELLING PRODUCTS BY SALES REVENUE
-- Business Importance:
-- Highlights superstar products that generate the majority of store turnover. Ensures
-- procurement teams maintain priority safety stock to prevent expensive stock-outs.
-- ========================================================================================
SELECT 
    p.product_name AS Product_Name,
    p.category AS Category,
    SUM(f.quantity) AS Units_Sold,
    ROUND(SUM(f.sales_amount), 2) AS Total_Revenue,
    ROUND(SUM(f.profit_amount), 2) AS Total_Profit
FROM FactSales f
JOIN DimProduct p ON f.product_key = p.product_key
GROUP BY p.product_key, p.product_name, p.category
ORDER BY Total_Revenue DESC
LIMIT 5;


-- ========================================================================================
-- 3. BRANCH SALES AND PROFITABILITY RANKING
-- Business Importance:
-- Evaluates branch-level financial health and efficiency by measuring transaction volume,
-- total margin, and Average Transaction Value (ATV) to guide store manager KPI targets.
-- ========================================================================================
SELECT 
    b.branch_name AS Branch_Name,
    b.city AS City,
    COUNT(DISTINCT f.sale_id) AS Total_Transactions,
    ROUND(SUM(f.sales_amount), 2) AS Total_Revenue,
    ROUND(SUM(f.profit_amount), 2) AS Total_Profit,
    ROUND(SUM(f.sales_amount) / COUNT(DISTINCT f.sale_id), 2) AS Avg_Transaction_Value
FROM FactSales f
JOIN DimBranch b ON f.branch_key = b.branch_key
GROUP BY b.branch_key, b.branch_name, b.city
ORDER BY Total_Revenue DESC;


-- ========================================================================================
-- 4. MONTHLY SALES AND PROFIT GROWTH TREND
-- Business Importance:
-- Tracks time-series financial trends over months. Enables the business to forecast cash flow,
-- prepare for seasonal demand surges, and detect revenue slowdowns early.
-- ========================================================================================
SELECT 
    d.year_number AS Year,
    d.month_number AS Month_No,
    d.month_name AS Month_Name,
    COUNT(DISTINCT f.sale_id) AS Total_Transactions,
    ROUND(SUM(f.sales_amount), 2) AS Total_Revenue,
    ROUND(SUM(f.profit_amount), 2) AS Total_Profit
FROM FactSales f
JOIN DimDate d ON f.date_key = d.date_key
GROUP BY d.year_number, d.month_number, d.month_name
ORDER BY d.year_number, d.month_number;


-- ========================================================================================
-- 5. TOP HIGH-VALUE VIP CUSTOMERS BY TOTAL SPEND
-- Business Importance:
-- Uncovers the most loyal and highest-spending shoppers. Enables targeted VIP loyalty programs,
-- personalized discounts, and dedicated account retention initiatives.
-- ========================================================================================
SELECT 
    c.customer_name AS Customer_Name,
    c.city AS City,
    c.gender AS Gender,
    COUNT(DISTINCT f.sale_id) AS Total_Orders,
    SUM(f.quantity) AS Total_Items_Bought,
    ROUND(SUM(f.sales_amount), 2) AS Total_Spend,
    ROUND(SUM(f.profit_amount), 2) AS Total_Profit
FROM FactSales f
JOIN DimCustomer c ON f.customer_key = c.customer_key
GROUP BY c.customer_key, c.customer_name, c.city, c.gender
ORDER BY Total_Spend DESC
LIMIT 5;


-- ========================================================================================
-- 6. CUSTOMER DEMOGRAPHICS & SPENDING PATTERNS BY GENDER AND CITY
-- Business Importance:
-- Provides demographic segmentation across regional markets. Informs regional marketing
-- campaigns, personalized product bundling, and localized store merchandising.
-- ========================================================================================
SELECT 
    c.gender AS Gender,
    c.city AS City,
    COUNT(DISTINCT c.customer_key) AS Customer_Count,
    ROUND(SUM(f.sales_amount), 2) AS Total_Revenue,
    ROUND(SUM(f.sales_amount) / COUNT(DISTINCT c.customer_key), 2) AS Avg_Spend_Per_Customer
FROM FactSales f
JOIN DimCustomer c ON f.customer_key = c.customer_key
GROUP BY c.gender, c.city
ORDER BY Total_Revenue DESC;


-- ========================================================================================
-- 7. DISCOUNT IMPACT ANALYSIS ON REVENUE AND MARGIN
-- Business Importance:
-- Measures the trade-off between price discounts and net profit across product categories.
-- Helps merchandising teams eliminate discount erosion where margins are hurt without volume lift.
-- ========================================================================================
SELECT 
    p.category AS Category,
    ROUND(SUM(f.sales_amount + f.discount_amount), 2) AS Gross_Sales,
    ROUND(SUM(f.discount_amount), 2) AS Total_Discounts_Given,
    ROUND(SUM(f.sales_amount), 2) AS Net_Sales_Revenue,
    ROUND((SUM(f.discount_amount) / NULLIF(SUM(f.sales_amount + f.discount_amount), 0)) * 100, 2) AS Discount_Rate_Pct,
    ROUND(SUM(f.profit_amount), 2) AS Net_Profit
FROM FactSales f
JOIN DimProduct p ON f.product_key = p.product_key
GROUP BY p.category
ORDER BY Total_Discounts_Given DESC;


-- ========================================================================================
-- 8. INVENTORY HEALTH & STOCK DEPLETION RATIO
-- Business Importance:
-- Compares actual units sold against available inventory per category. Identifies categories
-- with rapid stock turnover versus those tying up working capital with dead stock.
-- ========================================================================================
SELECT 
    p.category AS Category,
    SUM(p.stock_quantity) AS Total_Stock_Available,
    COALESCE(SUM(f.quantity), 0) AS Total_Units_Sold,
    ROUND(COALESCE(SUM(f.quantity), 0) / NULLIF(SUM(p.stock_quantity), 0), 4) AS Stock_Depletion_Ratio
FROM DimProduct p
LEFT JOIN FactSales f ON p.product_key = f.product_key
GROUP BY p.category
ORDER BY Stock_Depletion_Ratio DESC;


-- ========================================================================================
-- 9. LOW STOCK ALERT FOR ACTIVE SELLING PRODUCTS
-- Business Importance:
-- Generates an automated early-warning system for inventory replenishment, mitigating
-- stock-outs and ensuring customer shopping satisfaction.
-- ========================================================================================
SELECT 
    p.product_name AS Product_Name,
    p.category AS Category,
    p.stock_quantity AS Remaining_Stock,
    COALESCE(SUM(f.quantity), 0) AS Total_Units_Sold,
    p.selling_price AS Selling_Price
FROM DimProduct p
LEFT JOIN FactSales f ON p.product_key = f.product_key
GROUP BY p.product_key, p.product_name, p.category, p.stock_quantity, p.selling_price
ORDER BY p.stock_quantity ASC
LIMIT 5;


-- ========================================================================================
-- 10. SUPPLIER SOURCING MARGIN & PRICE VARIANCE ANALYSIS
-- Business Importance:
-- Evaluates supplier contract competitiveness by comparing wholesale supply costs against
-- supermarket retail prices. Empowers procurement managers during contract renegotiations.
-- ========================================================================================
SELECT 
    s.supplier_name AS Supplier_Name,
    p.product_name AS Product_Name,
    p.category AS Category,
    ss.supply_price AS Supplier_Price,
    p.selling_price AS Retail_Selling_Price,
    ROUND((p.selling_price - ss.supply_price), 2) AS Gross_Margin_Amount,
    ROUND(((p.selling_price - ss.supply_price) / p.selling_price) * 100, 2) AS Gross_Margin_Pct
FROM FactSupplierSupply ss
JOIN DimSupplier s ON ss.supplier_key = s.supplier_key
JOIN DimProduct p ON ss.product_key = p.product_key
ORDER BY Gross_Margin_Pct DESC
LIMIT 5;


-- ========================================================================================
-- 11. PRODUCT CUSTOMER SATISFACTION & RATING OVERVIEW
-- Business Importance:
-- Merges transactional intelligence with customer sentiment data. Identifies top-rated
-- consumer favorites for promotional spotlights and marketing endorsements.
-- ========================================================================================
SELECT 
    p.product_name AS Product_Name,
    p.category AS Category,
    COUNT(fb.review_id) AS Total_Reviews,
    ROUND(AVG(fb.rating), 2) AS Avg_Customer_Rating,
    MIN(fb.rating) AS Lowest_Rating,
    MAX(fb.rating) AS Highest_Rating
FROM FactFeedback fb
JOIN DimProduct p ON fb.product_key = p.product_key
GROUP BY p.product_key, p.product_name, p.category
ORDER BY Avg_Customer_Rating DESC, Total_Reviews DESC
LIMIT 5;


-- ========================================================================================
-- 12. UNDERPERFORMING PRODUCTS WITH LOW CUSTOMER RATINGS (Rating < 3.0)
-- Business Importance:
-- Detects quality issues, packaging defects, or negative consumer perceptions early. Allows
-- quality assurance teams to intervene, replace defective batches, or discontinue suppliers.
-- ========================================================================================
SELECT 
    p.product_name AS Product_Name,
    p.category AS Category,
    ROUND(AVG(fb.rating), 2) AS Avg_Rating,
    COUNT(fb.review_id) AS Total_Feedback_Count
FROM FactFeedback fb
JOIN DimProduct p ON fb.product_key = p.product_key
GROUP BY p.product_key, p.product_name, p.category
HAVING AVG(fb.rating) < 3.0
ORDER BY Avg_Rating ASC;


-- ========================================================================================
-- 13. CUSTOMER SATISFACTION ACROSS PRODUCT CATEGORIES
-- Business Importance:
-- Evaluates brand perception and quality consistency across entire departments (Dairy, Bakery, etc.).
-- Enables management to detect category-wide customer dissatisfaction drivers.
-- ========================================================================================
SELECT 
    p.category AS Category,
    COUNT(fb.review_id) AS Total_Reviews,
    ROUND(AVG(fb.rating), 2) AS Avg_Category_Rating,
    SUM(CASE WHEN fb.rating >= 4 THEN 1 ELSE 0 END) AS Positive_Reviews,
    SUM(CASE WHEN fb.rating <= 2 THEN 1 ELSE 0 END) AS Negative_Reviews
FROM FactFeedback fb
JOIN DimProduct p ON fb.product_key = p.product_key
GROUP BY p.category
ORDER BY Avg_Category_Rating DESC;


-- ========================================================================================
-- 14. BRANCH CROSS-CITY CUSTOMER FLOW (LOCAL VS OUT-OF-TOWN SHOPPERS)
-- Business Importance:
-- Analyzes customer mobility by comparing customer home cities against branch locations.
-- Guides billboard advertising, regional delivery hubs, and new store location planning.
-- ========================================================================================
SELECT 
    b.branch_name AS Branch_Name,
    b.city AS Branch_City,
    c.city AS Customer_City,
    CASE WHEN b.city = c.city THEN 'Local Resident' ELSE 'Out-of-Town Visitor' END AS Customer_Origin_Type,
    COUNT(DISTINCT f.sale_id) AS Transaction_Count,
    ROUND(SUM(f.sales_amount), 2) AS Total_Sales
FROM FactSales f
JOIN DimBranch b ON f.branch_key = b.branch_key
JOIN DimCustomer c ON f.customer_key = c.customer_key
GROUP BY b.branch_name, b.city, c.city
ORDER BY Total_Sales DESC
LIMIT 5;


-- ========================================================================================
-- 15. QUARTERLY BUSINESS PERFORMANCE SUMMARY
-- Business Importance:
-- Synthesizes executive-level quarterly KPIs (Order Volume, Units Sold, Gross Revenue,
-- Net Profit, and Profit Margin %). Essential for quarterly board meetings and strategic planning.
-- ========================================================================================
SELECT 
    d.year_number AS Year,
    CONCAT('Q', d.quarter_number) AS Quarter,
    COUNT(DISTINCT f.sale_id) AS Total_Orders,
    SUM(f.quantity) AS Total_Units_Sold,
    ROUND(SUM(f.sales_amount), 2) AS Total_Revenue,
    ROUND(SUM(f.profit_amount), 2) AS Total_Profit,
    ROUND((SUM(f.profit_amount) / SUM(f.sales_amount)) * 100, 2) AS Profit_Margin_Pct
FROM FactSales f
JOIN DimDate d ON f.date_key = d.date_key
GROUP BY d.year_number, d.quarter_number
ORDER BY d.year_number, d.quarter_number;
