
import pandas as pd
from pathlib import Path

file_path = Path(__file__).parent / "products.csv"

if not file_path.exists():
    raise FileNotFoundError(
        "products.csv not found in the project folder."
    )

df = pd.read_csv(file_path)

required_columns = [
    "product_id",
    "product_name",
    "category",
    "unit_cost",
    "selling_price",
    "stock_quantity"
]

missing = set(required_columns) - set(df.columns)

if missing:
    raise ValueError(f"Missing columns: {missing}")

if df["product_id"].duplicated().any():
    raise ValueError("Duplicate product IDs found.")

if df[required_columns].isnull().any().any():
    raise ValueError("Missing values found in required columns.")

if (df["unit_cost"] < 0).any() or (
    df["selling_price"] < 0
).any() or (df["stock_quantity"] < 0).any():
    raise ValueError("Negative cost, price, or stock found.")

print("CSV validation successful!")
print("Total products:", len(df))
print(df.to_string(index=False))
