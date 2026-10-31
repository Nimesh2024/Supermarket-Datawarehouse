
import sqlite3

# Create or connect to the SQLite database
connection = sqlite3.connect("customer_branch.db")
cursor = connection.cursor()

# 1. Create Customers table
cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY,
    customer_name TEXT NOT NULL,
    city TEXT,
    gender TEXT
)
""")

# 2. Create Branches table
cursor.execute("""
CREATE TABLE IF NOT EXISTS branches (
    branch_id INTEGER PRIMARY KEY,
    branch_name TEXT NOT NULL,
    city TEXT,
    address TEXT
)
""")

# 3. Insert sample customers
cursor.executemany("""
INSERT OR IGNORE INTO customers
(customer_id, customer_name, city, gender)
VALUES (?, ?, ?, ?)
""", [
    (1, "Kamal Perera", "Colombo", "Male"),
    (2, "Nimali Silva", "Galle", "Female"),
    (3, "Amal Fernando", "Matara", "Male"),
    (4, "Saman Kumara", "Colombo", "Male"),
    (5, "Tharushi Jayasinghe", "Galle", "Female")
])

# 4. Insert sample branches
cursor.executemany("""
INSERT OR IGNORE INTO branches
(branch_id, branch_name, city, address)
VALUES (?, ?, ?, ?)
""", [
    (101, "Colombo Main Branch", "Colombo", "Colombo 03"),
    (102, "Galle Branch", "Galle", "Galle Town"),
    (103, "Matara Branch", "Matara", "Matara Town")
])

# Save changes
connection.commit()

# 5. Display customers
print("\nCUSTOMERS")
for row in cursor.execute("SELECT * FROM customers"):
    print(row)

# 6. Display branches
print("\nBRANCHES")
for row in cursor.execute("SELECT * FROM branches"):
    print(row)

connection.close()

print("\nSQLite database created successfully!")
