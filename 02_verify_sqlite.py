
import sqlite3
from pathlib import Path

db_path = Path(__file__).parent / "customer_branch.db"

if not db_path.exists():
    print("ERROR: customer_branch.db not found.")
    print("Run 02_create_sqlite.py first.")
    raise SystemExit(1)

connection = sqlite3.connect(db_path)
cursor = connection.cursor()

tables = cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
      AND name NOT LIKE 'sqlite_%'
    ORDER BY name
""").fetchall()

print("Database:", db_path.resolve())
print("Tables:", [table[0] for table in tables])

for table in ("customers", "branches"):
    if table not in [item[0] for item in tables]:
        print(f"ERROR: Missing table {table}")
        continue

    count = cursor.execute(
        f"SELECT COUNT(*) FROM {table}"
    ).fetchone()[0]

    print(f"{table}: {count} rows")
    print(cursor.execute(
        f"SELECT * FROM {table} LIMIT 5"
    ).fetchall())

connection.close()
