import sqlite3
from pathlib import Path

db_path = Path(__file__).parent / "customer_branch.db"

# Create or connect to the SQLite database
connection = sqlite3.connect(db_path)
cursor = connection.cursor()

# Reset tables for clean generation
cursor.execute("DROP TABLE IF EXISTS customers")
cursor.execute("DROP TABLE IF EXISTS branches")

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

# 3. Insert customers (30 realistic customer profiles)
customers_data = [
    (1, "Kamal Perera", "Colombo", "Male"),
    (2, "Nimali Silva", "Galle", "Female"),
    (3, "Amal Fernando", "Matara", "Male"),
    (4, "Saman Kumara", "Colombo", "Male"),
    (5, "Tharushi Jayasinghe", "Galle", "Female"),
    (6, "Dinesh Bandara", "Kandy", "Male"),
    (7, "Sanduni Wickramasinghe", "Colombo", "Female"),
    (8, "Kasun Rajapaksha", "Kurunegala", "Male"),
    (9, "Chathurika Senanayake", "Negombo", "Female"),
    (10, "Nuwan Pradeep", "Gampaha", "Male"),
    (11, "Dilini Madushani", "Kandy", "Female"),
    (12, "Ruwan Gunawardena", "Kalutara", "Male"),
    (13, "Ishara Kavindi", "Colombo", "Female"),
    (14, "Asanka Weerasinghe", "Ratnapura", "Male"),
    (15, "Hashini Anuradha", "Galle", "Female"),
    (16, "Chaminda Pushpakumara", "Matara", "Male"),
    (17, "Nadeesha Sewwandi", "Negombo", "Female"),
    (18, "Mahesh Dissanayake", "Anuradhapura", "Male"),
    (19, "Oshadi Wijerathne", "Colombo", "Female"),
    (20, "Roshan Alwis", "Kandy", "Male"),
    (21, "Kaveesha De Silva", "Galle", "Female"),
    (22, "Supun Jayawardena", "Kurunegala", "Male"),
    (23, "Sachini Perera", "Colombo", "Female"),
    (24, "Janaka Rathnayake", "Gampaha", "Male"),
    (25, "Hiruni Fonseka", "Kalutara", "Female"),
    (26, "Lahiru Thilina", "Matara", "Male"),
    (27, "Rashmi Malshani", "Kandy", "Female"),
    (28, "Gehan Mendis", "Colombo", "Male"),
    (29, "Bhagya Hettiarachchi", "Negombo", "Female"),
    (30, "Vimukthi Sandaruwan", "Galle", "Male")
]

cursor.executemany("""
INSERT INTO customers (customer_id, customer_name, city, gender)
VALUES (?, ?, ?, ?)
""", customers_data)

# 4. Insert branches (8 supermarket branches across Sri Lanka)
branches_data = [
    (101, "Colombo Main Branch", "Colombo", "Colombo 03"),
    (102, "Galle Branch", "Galle", "Galle Town"),
    (103, "Matara Branch", "Matara", "Matara Town"),
    (104, "Kandy City Branch", "Kandy", "Dalada Veediya"),
    (105, "Negombo Coastal Branch", "Negombo", "Beach Road"),
    (106, "Kurunegala Metro Branch", "Kurunegala", "Colombo Road"),
    (107, "Gampaha Branch", "Gampaha", "Station Road"),
    (108, "Kalutara Riverside Branch", "Kalutara", "Main Street")
]

cursor.executemany("""
INSERT INTO branches (branch_id, branch_name, city, address)
VALUES (?, ?, ?, ?)
""", branches_data)

# Save changes
connection.commit()

# Verify counts
customer_count = cursor.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
branch_count = cursor.execute("SELECT COUNT(*) FROM branches").fetchone()[0]

print(f"SQLite database created successfully!")
print(f"Total customers: {customer_count}")
print(f"Total branches: {branch_count}")

connection.close()
