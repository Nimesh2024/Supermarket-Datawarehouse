
import os
import sys
import sqlite3
from pathlib import Path
from datetime import datetime
from decimal import Decimal

import pandas as pd
import requests
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, URL

import dns.resolver
from pymongo import MongoClient

# Configure public DNS servers to prevent local router timeouts on MongoDB SRV records
try:
    _dns_resolver = dns.resolver.Resolver()
    _dns_resolver.nameservers = ["8.8.8.8", "1.1.1.1"] + _dns_resolver.nameservers
    dns.resolver.default_resolver = _dns_resolver
except Exception:
    pass

# --------------------------------------------------
# 1. CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def required_env(name, default=None):
    value = os.getenv(name, default)
    if value is None or not value.strip():
        raise ValueError(f"Missing environment variable: {name}")
    return value


def mysql_engine(prefix, database):
    return create_engine(
        URL.create(
            "mysql+pymysql",
            username=required_env(f"{prefix}_DB_USER"),
            password=os.getenv(f"{prefix}_DB_PASSWORD", ""),
            host=required_env(f"{prefix}_DB_HOST", "127.0.0.1"),
            port=int(required_env(f"{prefix}_DB_PORT", "3306")),
            database=database,
        ),
        pool_pre_ping=True,
        connect_args={"connect_timeout": 10},
    )


source_engine = mysql_engine(
    "SOURCE", required_env("SOURCE_DB_NAME", "supermarket_pos")
)

dw_engine = mysql_engine(
    "DW", required_env("DW_DB_NAME", "supermarket_dw")
)

SQLITE_PATH = BASE_DIR / required_env(
    "SQLITE_PATH", "customer_branch.db"
)
CSV_PATH = BASE_DIR / required_env(
    "PRODUCTS_CSV_PATH", "products.csv"
)
API_URL = required_env(
    "SUPPLIER_API_URL",
    "http://127.0.0.1:5001/api/suppliers",
)

# --------------------------------------------------
# 2. EXTRACT: MYSQL POS
# --------------------------------------------------

def extract_pos():
    print("Extracting MySQL POS data...")

    with source_engine.connect() as conn:
        sales = pd.read_sql(
            text("""
                SELECT sale_id, sale_datetime, customer_id,
                       branch_id, payment_method, status
                FROM pos_sales
            """),
            conn,
        )

        items = pd.read_sql(
            text("""
                SELECT sale_item_id, sale_id, product_id,
                       quantity, unit_price, discount_amount
                FROM pos_sale_items
            """),
            conn,
        )

    return sales, items


# --------------------------------------------------
# 3. EXTRACT: SQLITE CUSTOMERS AND BRANCHES
# --------------------------------------------------

def extract_sqlite():
    print("Extracting SQLite data...")

    if not SQLITE_PATH.exists():
        raise FileNotFoundError(
            f"SQLite database not found: {SQLITE_PATH}"
        )

    with sqlite3.connect(SQLITE_PATH) as conn:
        customers = pd.read_sql_query(
            "SELECT customer_id, customer_name, city, gender "
            "FROM customers",
            conn,
        )

        branches = pd.read_sql_query(
            "SELECT branch_id, branch_name, city, address "
            "FROM branches",
            conn,
        )

    return customers, branches


# --------------------------------------------------
# 4. EXTRACT: CSV PRODUCT DATA
# --------------------------------------------------

def extract_products():
    print("Extracting product CSV...")

    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV not found: {CSV_PATH}")

    products = pd.read_csv(CSV_PATH)

    required = {
        "product_id", "product_name", "category",
        "unit_cost", "selling_price", "stock_quantity",
    }

    missing = required - set(products.columns)
    if missing:
        raise ValueError(f"CSV missing columns: {sorted(missing)}")

    return products


# --------------------------------------------------
# 5. EXTRACT: REST API
# --------------------------------------------------

def extract_suppliers():
    print("Extracting supplier API data...")

    response = requests.get(API_URL, timeout=15)
    response.raise_for_status()

    data = response.json()

    if not isinstance(data, list):
        raise ValueError("Supplier API must return a JSON list.")

    suppliers = pd.DataFrame(data)

    required = {
        "supplier_id", "supplier_name", "city",
        "product_id", "supply_price",
    }

    if suppliers.empty:
        raise ValueError("Supplier API returned no records.")

    missing = required - set(suppliers.columns)
    if missing:
        raise ValueError(
            f"API response missing fields: {sorted(missing)}"
        )

    return suppliers


# --------------------------------------------------
# 6. TRANSFORM AND VALIDATE
# --------------------------------------------------

def clean_dimensions(customers, branches, products, suppliers):
    customers = customers.copy()
    branches = branches.copy()
    products = products.copy()
    suppliers = suppliers.copy()

    # Remove duplicate dimension/source keys
    customers = customers.drop_duplicates(subset=["customer_id"], keep="last")
    branches = branches.drop_duplicates(subset=["branch_id"], keep="last")
    products = products.drop_duplicates(subset=["product_id"], keep="last")
    suppliers = suppliers.drop_duplicates(subset=["supplier_id"], keep="last")

    for df, key, name in [
        (customers, "customer_id", "customers"),
        (branches, "branch_id", "branches"),
        (products, "product_id", "products"),
        (suppliers, "supplier_id", "suppliers"),
    ]:
        if df[key].isna().any():
            raise ValueError(f"Missing {key} in {name}")

    # Clean text fields
    for df, columns in [
        (customers, ["customer_name", "city", "gender"]),
        (branches, ["branch_name", "city", "address"]),
        (products, ["product_name", "category"]),
        (suppliers, ["supplier_name", "city"]),
    ]:
        for col in columns:
            df[col] = df[col].astype("string").str.strip()
            df[col] = df[col].replace("", pd.NA)

    if customers["customer_name"].isna().any():
        raise ValueError("Customer name cannot be empty.")

    if branches["branch_name"].isna().any():
        raise ValueError("Branch name cannot be empty.")

    if products["product_name"].isna().any():
        raise ValueError("Product name cannot be empty.")

    # Convert identifiers and numeric fields
    for df, columns in [
        (customers, ["customer_id"]),
        (branches, ["branch_id"]),
        (products, ["product_id", "stock_quantity"]),
        (suppliers, ["supplier_id", "product_id"]),
    ]:
        for col in columns:
            df[col] = pd.to_numeric(df[col], errors="raise")
            if df[col].isna().any():
                raise ValueError(f"Missing numeric value: {col}")
            if (df[col] % 1 != 0).any():
                raise ValueError(f"Non-integer ID/count: {col}")
            df[col] = df[col].astype("int64")

    for col in ["unit_cost", "selling_price"]:
        products[col] = pd.to_numeric(
            products[col], errors="raise"
        )

    suppliers["supply_price"] = pd.to_numeric(
        suppliers["supply_price"], errors="raise"
    )

    for col in ["unit_cost", "selling_price"]:
        if (products[col] < 0).any():
            raise ValueError(f"Negative values in {col}")

    if (products["stock_quantity"] < 0).any():
        raise ValueError("Negative stock quantity.")

    if (suppliers["supply_price"] < 0).any():
        raise ValueError("Negative supplier price.")

    if suppliers.duplicated(
        subset=["supplier_id", "product_id"]
    ).any():
        raise ValueError("Duplicate supplier/product pairs in API.")

    # Every supplier product must exist in the product source.
    product_ids = set(products["product_id"])
    if not set(suppliers["product_id"]).issubset(product_ids):
        raise ValueError(
            "Supplier API contains product IDs missing from products.csv."
        )

    return customers, branches, products, suppliers


def clean_sales(sales, items, customers, branches, products):
    sales = sales.copy()
    items = items.copy()

    sales["sale_datetime"] = pd.to_datetime(
        sales["sale_datetime"], errors="raise"
    )

    for col in ["sale_id", "customer_id", "branch_id"]:
        sales[col] = pd.to_numeric(sales[col], errors="raise")
        if sales[col].isna().any():
            raise ValueError(f"Missing sales field: {col}")
        if (sales[col] % 1 != 0).any():
            raise ValueError(f"Invalid integer values: {col}")
        sales[col] = sales[col].astype("int64")

    for col in [
        "sale_item_id", "sale_id", "product_id", "quantity"
    ]:
        items[col] = pd.to_numeric(items[col], errors="raise")
        if items[col].isna().any():
            raise ValueError(f"Missing item field: {col}")
        if (items[col] % 1 != 0).any():
            raise ValueError(f"Invalid integer values: {col}")
        items[col] = items[col].astype("int64")

    for col in ["unit_price", "discount_amount"]:
        items[col] = pd.to_numeric(items[col], errors="raise")

    if sales["sale_id"].duplicated().any():
        raise ValueError("Duplicate sale IDs in POS source.")

    if items["sale_item_id"].duplicated().any():
        raise ValueError("Duplicate sale item IDs in POS source.")

    if (items["quantity"] <= 0).any():
        raise ValueError("Sale item quantity must be positive.")

    if (items["unit_price"] < 0).any():
        raise ValueError("Sale item price cannot be negative.")

    if (items["discount_amount"] < 0).any():
        raise ValueError("Discount cannot be negative.")

    if (
        items["discount_amount"]
        > items["quantity"] * items["unit_price"]
    ).any():
        raise ValueError("Discount exceeds the line amount.")

    # Only completed sales are included in FactSales.
    sales = sales[
        sales["status"].astype(str).str.upper().eq("COMPLETED")
    ].copy()

    # Validate source relationships before loading facts.
    if not set(items["sale_id"]).issubset(set(sales["sale_id"])):
        raise ValueError(
            "Sale items refer to missing or non-completed sales."
        )

    if not set(sales["customer_id"]).issubset(
        set(customers["customer_id"])
    ):
        raise ValueError("POS contains unknown customer IDs.")

    if not set(sales["branch_id"]).issubset(
        set(branches["branch_id"])
    ):
        raise ValueError("POS contains unknown branch IDs.")

    if not set(items["product_id"]).issubset(
        set(products["product_id"])
    ):
        raise ValueError("POS contains unknown product IDs.")

    return sales, items


# --------------------------------------------------
# 7. HELPER: MYSQL UPSERT
# --------------------------------------------------

def upsert(conn, table, columns, rows, key_columns):
    if not rows:
        return

    # Table and column names are constants authored in this script.
    col_sql = ", ".join(f"`{c}`" for c in columns)
    placeholders = ", ".join(f":{c}" for c in columns)

    update_columns = [
        c for c in columns if c not in key_columns
    ]

    if update_columns:
        update_sql = ", ".join(
            f"`{c}` = VALUES(`{c}`)" for c in update_columns
        )
        suffix = f"ON DUPLICATE KEY UPDATE {update_sql}"
    else:
        suffix = "ON DUPLICATE KEY UPDATE " + ", ".join(
            f"`{c}` = VALUES(`{c}`)" for c in key_columns
        )

    statement = text(
        f"INSERT INTO `{table}` ({col_sql}) "
        f"VALUES ({placeholders}) {suffix}"
    )

    conn.execute(statement, rows)


def records(df):
    return df.astype(object).where(pd.notna(df), None).to_dict(
        orient="records"
    )


# --------------------------------------------------
# 8. TRANSFORM: BUILD DIMENSIONS AND FACTS
# --------------------------------------------------

def build_date_dimension(sales):
    dates = pd.to_datetime(sales["sale_datetime"]).dt.normalize()
    unique_dates = sorted(dates.unique())

    rows = []
    for value in unique_dates:
        date = pd.Timestamp(value).date()

        rows.append({
            "date_key": int(date.strftime("%Y%m%d")),
            "full_date": date,
            "day_number": date.day,
            "month_number": date.month,
            "month_name": date.strftime("%B"),
            "quarter_number": (date.month - 1) // 3 + 1,
            "year_number": date.year,
        })

    return pd.DataFrame(rows)


def load_payment_mapping(conn):
    mapping = {"cash": 1, "card": 2, "credit card": 2, "debit card": 3, "mobile pay": 4}
    try:
        df = pd.read_sql(
            text("SELECT payment_method_key, payment_method_name, payment_category FROM DimPaymentMethod"),
            conn,
        )
        for _, row in df.iterrows():
            pm_name = str(row["payment_method_name"]).strip().lower()
            pm_cat = str(row["payment_category"]).strip().lower()
            key = int(row["payment_method_key"])
            mapping[pm_name] = key
            if pm_cat not in mapping:
                mapping[pm_cat] = key
    except Exception:
        pass
    return mapping


def build_fact_sales(sales, items, products, payment_mapping=None):
    # Product cost comes from the CSV source.
    product_costs = products[
        ["product_id", "unit_cost"]
    ].copy()

    joined = items.merge(
        sales,
        on="sale_id",
        how="inner",
        validate="many_to_one",
    )

    joined = joined.merge(
        product_costs,
        on="product_id",
        how="left",
        validate="many_to_one",
    )

    if joined["unit_cost"].isna().any():
        raise ValueError("Product cost missing for a sale item.")

    joined["date_key"] = pd.to_datetime(
        joined["sale_datetime"]
    ).dt.strftime("%Y%m%d").astype("int64")

    joined["sales_amount"] = (
        joined["quantity"] * joined["unit_price"]
        - joined["discount_amount"]
    ).round(2)

    joined["cost_amount"] = (
        joined["quantity"] * joined["unit_cost"]
    ).round(2)

    joined["profit_amount"] = (
        joined["sales_amount"] - joined["cost_amount"]
    ).round(2)

    if payment_mapping is not None and "payment_method" in joined.columns:
        joined["payment_method_key"] = (
            joined["payment_method"]
            .astype(str)
            .str.strip()
            .str.lower()
            .map(payment_mapping)
            .fillna(1)
            .astype("int64")
        )

    joined = joined.rename(
        columns={
            "product_id": "product_key",
            "customer_id": "customer_key",
            "branch_id": "branch_key",
            "unit_price": "unit_selling_price",
        }
    )

    columns = [
        "sale_id", "sale_item_id", "date_key",
        "product_key", "customer_key", "branch_key",
        "quantity", "unit_selling_price", "discount_amount",
        "sales_amount", "cost_amount", "profit_amount",
    ]
    if "payment_method_key" in joined.columns:
        columns.append("payment_method_key")

    return joined[columns]


# --------------------------------------------------
# 9. LOAD: CENTRAL DATA WAREHOUSE
# --------------------------------------------------

def load_warehouse(
    customers, branches, products, suppliers,
    sales, items
):
    print("Transforming and loading data...")

    date_dim = build_date_dimension(sales)

    customer_dim = customers.rename(
        columns={"customer_id": "customer_key"}
    )[["customer_key", "customer_name", "city", "gender"]]

    branch_dim = branches.rename(
        columns={"branch_id": "branch_key"}
    )[["branch_key", "branch_name", "city", "address"]]

    product_dim = products.rename(
        columns={"product_id": "product_key"}
    )[[
        "product_key", "product_name", "category",
        "unit_cost", "selling_price", "stock_quantity",
    ]]

    supplier_dim = suppliers[
        ["supplier_id", "supplier_name", "city"]
    ].drop_duplicates(subset=["supplier_id"]).rename(
        columns={"supplier_id": "supplier_key"}
    )

    supplier_facts = suppliers.rename(
        columns={
            "supplier_id": "supplier_key",
            "product_id": "product_key",
        }
    )[["supplier_key", "product_key", "supply_price"]]

    # One transaction for all warehouse changes.
    # If any load fails, all changes in this transaction roll back.
    with dw_engine.begin() as conn:
        payment_mapping = load_payment_mapping(conn)
        facts = build_fact_sales(sales, items, products, payment_mapping=payment_mapping)

        upsert(
            conn, "DimDate",
            [
                "date_key", "full_date", "day_number",
                "month_number", "month_name",
                "quarter_number", "year_number",
            ],
            records(date_dim), ["date_key"],
        )

        upsert(
            conn, "DimProduct",
            [
                "product_key", "product_name", "category",
                "unit_cost", "selling_price", "stock_quantity",
            ],
            records(product_dim), ["product_key"],
        )

        upsert(
            conn, "DimCustomer",
            ["customer_key", "customer_name", "city", "gender"],
            records(customer_dim), ["customer_key"],
        )

        upsert(
            conn, "DimBranch",
            ["branch_key", "branch_name", "city", "address"],
            records(branch_dim), ["branch_key"],
        )

        upsert(
            conn, "DimSupplier",
            ["supplier_key", "supplier_name", "city"],
            records(supplier_dim), ["supplier_key"],
        )

        fact_cols = [
            "sale_id", "sale_item_id", "date_key",
            "product_key", "customer_key", "branch_key",
            "quantity", "unit_selling_price",
            "discount_amount", "sales_amount",
            "cost_amount", "profit_amount",
        ]
        if "payment_method_key" in facts.columns:
            try:
                table_cols = [r[0] for r in conn.execute(text("DESCRIBE FactSales")).fetchall()]
                if "payment_method_key" in table_cols:
                    fact_cols.append("payment_method_key")
            except Exception:
                pass

        upsert(
            conn, "FactSales",
            fact_cols,
            records(facts[fact_cols]), ["sale_id", "sale_item_id"],
        )

        upsert(
            conn, "FactSupplierSupply",
            ["supplier_key", "product_key", "supply_price"],
            records(supplier_facts),
            ["supplier_key", "product_key"],
        )

    print("Warehouse transaction committed successfully.")


# --------------------------------------------------
# 10. ETL LOGGING AND EXECUTION
# --------------------------------------------------

def log_start():
    with dw_engine.begin() as conn:
        result = conn.execute(
            text("""
                INSERT INTO ETLRunLog
                    (started_at, run_status, message)
                VALUES (:started, 'RUNNING', :message)
            """),
            {
                "started": datetime.now(),
                "message": "ETL started",
            },
        )
        return result.lastrowid


def log_finish(run_id, status, message):
    with dw_engine.begin() as conn:
        conn.execute(
            text("""
                UPDATE ETLRunLog
                SET completed_at = :completed,
                    run_status = :status,
                    message = :message
                WHERE run_id = :run_id
            """),
            {
                "completed": datetime.now(),
                "status": status,
                "message": message[:60000],
                "run_id": run_id,
            },
        )

# ----------------------------------------------- Mongodb data ----------------------------------------------------

def extract_mongodb_reviews():
    print("Extracting MongoDB customer reviews...")

    uri = required_env("MONGODB_URI")
    database_name = required_env("MONGODB_DATABASE")
    collection_name = required_env("MONGODB_COLLECTION")

    with MongoClient(
        uri,
        serverSelectionTimeoutMS=5000
    ) as client:

        # Check MongoDB connection
        client.admin.command("ping")

        collection = (
            client[database_name][collection_name]
        )

        documents = list(
            collection.find({}, {"_id": 0})
        )

    if not documents:
        raise ValueError(
            "MongoDB reviews collection is empty."
        )

    reviews = pd.DataFrame(documents)

    required = {
        "review_id",
        "customer_id",
        "product_id",
        "rating",
        "review_text",
        "review_date",
    }

    missing = required - set(reviews.columns)

    if missing:
        raise ValueError(
            f"MongoDB reviews missing: {sorted(missing)}"
        )

    reviews["rating"] = pd.to_numeric(
        reviews["rating"], errors="raise"
    )

    if not reviews["rating"].between(1, 5).all():
        raise ValueError("Review rating must be 1 to 5.")

    reviews["review_date"] = pd.to_datetime(
        reviews["review_date"], errors="raise"
    ).dt.date

    reviews["review_text"] = (
        reviews["review_text"].fillna("").astype(str).str.strip()
    )

    reviews["review_id"] = (
        reviews["review_id"].astype(str).str.strip()
    )

    if reviews["review_id"].eq("").any():
        raise ValueError("Review ID cannot be empty.")

    if reviews["review_id"].duplicated().any():
        raise ValueError("Duplicate review IDs found.")

    for col in ["customer_id", "product_id"]:
        reviews[col] = pd.to_numeric(
            reviews[col], errors="raise"
        )

        if (
            reviews[col].isna().any()
            or (reviews[col] % 1 != 0).any()
        ):
            raise ValueError(
                f"Invalid MongoDB field: {col}"
            )

        reviews[col] = reviews[col].astype("int64")

    return reviews



def build_feedback_facts(reviews, customers, products):
    # Check that every review refers to existing entities.
    customer_ids = set(customers["customer_id"])
    product_ids = set(products["product_id"])

    if not set(reviews["customer_id"]).issubset(customer_ids):
        raise ValueError(
            "Reviews contain unknown customer IDs."
        )

    if not set(reviews["product_id"]).issubset(product_ids):
        raise ValueError(
            "Reviews contain unknown product IDs."
        )

    facts = reviews.copy()

    facts["date_key"] = pd.to_datetime(
        facts["review_date"]
    ).dt.strftime("%Y%m%d").astype("int64")

    facts = facts.rename(
        columns={
            "customer_id": "customer_key",
            "product_id": "product_key",
        }
    )

    return facts[[
        "review_id",
        "date_key",
        "customer_key",
        "product_key",
        "rating",
        "review_text",
    ]]


def load_feedback(reviews, customers, products):
    feedback_facts = build_feedback_facts(
        reviews, customers, products
    )

    with dw_engine.begin() as conn:
        # Ensure review dates exist in DimDate.
        dates = pd.to_datetime(
            reviews["review_date"]
        )

        date_dim = pd.DataFrame({
            "date_key": dates.dt.strftime(
                "%Y%m%d"
            ).astype("int64"),
            "full_date": dates.dt.date,
            "day_number": dates.dt.day,
            "month_number": dates.dt.month,
            "month_name": dates.dt.strftime("%B"),
            "quarter_number": (
                (dates.dt.month - 1) // 3 + 1
            ),
            "year_number": dates.dt.year,
        }).drop_duplicates(subset=["date_key"])

        upsert(
            conn,
            "DimDate",
            [
                "date_key", "full_date", "day_number",
                "month_number", "month_name",
                "quarter_number", "year_number",
            ],
            records(date_dim),
            ["date_key"],
        )

        upsert(
            conn,
            "FactFeedback",
            [
                "review_id", "date_key", "customer_key",
                "product_key", "rating", "review_text",
            ],
            records(feedback_facts),
            ["review_id"],
        )

    print(
        f"Loaded {len(feedback_facts)} customer reviews."
    )



def main():
    run_id = None

    try:
        # Check that the warehouse schema exists.
        with dw_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            conn.execute(text("SELECT 1 FROM ETLRunLog LIMIT 1"))

        run_id = log_start()

        # Extract from all four sources.
        sales, items = extract_pos()
        customers, branches = extract_sqlite()
        products = extract_products()
        suppliers = extract_suppliers()
        reviews = extract_mongodb_reviews()

        # Clean and validate dimension data.
        customers, branches, products, suppliers = clean_dimensions(
            customers, branches, products, suppliers
        )

        # Clean sales and validate cross-source IDs.
        sales, items = clean_sales(
            sales, items, customers, branches, products
        )

        # Load dimensions and fact tables.
        load_warehouse(
            customers, branches, products, suppliers,
            sales, items,
        )

        load_feedback(reviews, customers, products)

        message = (
            f"Success. Sales={len(sales)}, "
            f"sale_items={len(items)}, "
            f"customers={len(customers)}, "
            f"branches={len(branches)}, "
            f"products={len(products)}, "
            f"suppliers={len(suppliers)}"
        )

        log_finish(run_id, "SUCCESS", message)
        print("\nETL completed successfully!")
        print(message)


    except Exception as exc:
        message = f"{type(exc).__name__}: {exc}"
        print("\nETL FAILED:", message, file=sys.stderr)

        if run_id is not None:
            try:
                log_finish(run_id, "FAILED", message)
            except Exception as log_error:
                print(
                    "Could not update ETL log:",
                    log_error,
                    file=sys.stderr,
                )

        raise

    finally:
        source_engine.dispose()
        dw_engine.dispose()


if __name__ == "__main__":
    main()
