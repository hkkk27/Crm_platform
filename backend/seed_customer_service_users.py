from app.db.sqlite_client import execute_query

execute_query("""
INSERT OR IGNORE INTO users (email, password, role, status)
VALUES (?, ?, ?, ?)
""", ("priya.nair@omnilink.com", "1234567890", "Customer Service", "Active"))

execute_query("""
INSERT OR IGNORE INTO users (email, password, role, status)
VALUES (?, ?, ?, ?)
""", ("kabir.sethi@omnilink.com", "1234567890", "Customer Service", "Active"))

execute_query("""
INSERT OR IGNORE INTO users (email, password, role, status)
VALUES (?, ?, ?, ?)
""", ("rohan.shah@omnilink.com", "1234567890", "Customer Service", "Active"))

print("Customer Service users inserted successfully.")