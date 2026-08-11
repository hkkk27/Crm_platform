# import sqlite3

# conn = sqlite3.connect("omnilink_crm.db")
# cur = conn.cursor()

# cur.execute("PRAGMA table_info(campaign_responses)")

# for row in cur.fetchall():
#     print(row)

# conn.close()
import sqlite3

# Connect to database
conn = sqlite3.connect("omnilink_crm.db")

# Return rows as dictionary-like objects
conn.row_factory = sqlite3.Row

cursor = conn.cursor()

# Get first 5 users
cursor.execute("""
    SELECT *
    FROM users
    LIMIT 5
""")

users = cursor.fetchall()

print("\nFirst 5 Users:\n")

for user in users:
    print(dict(user))

conn.close()