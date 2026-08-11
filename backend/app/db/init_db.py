from app.db.sqlite_client import execute_query
from app.services.password_service import hash_password


# Replace the body of seed_users() with this version:
def seed_users():
    users = [
        ("admin@omnilink.com", "1234567890", "Admin", "Active"),
        ("crm@omnilink.com", "1234567890", "CRM Team", "Active"),
        ("store@omnilink.com", "1234567890", "Store Team", "Active"),
        ("management@omnilink.com", "1234567890", "Management", "Active"),
        ("service@omnilink.com", "1234567890", "Customer Service", "Active"),
        ("security@omnilink.com", "1234567890", "Security / IT", "Active"),
        ("priya.nair@omnilink.com", "1234567890", "Customer Service", "Active"),
        ("kabir.sethi@omnilink.com", "1234567890", "Customer Service", "Active"),
        ("rohan.shah@omnilink.com", "1234567890", "Customer Service", "Active"),
        ("ankit97963@gmail.com", "1234567890", "Admin", "Active"),
    ]

    for email, password, role, status in users:
        execute_query(
            """
            INSERT OR IGNORE INTO users (email, password, role, status)
            VALUES (?, ?, ?, ?)
            """,
            (email, hash_password(password), role, status),
        )



def init_database():
    # Users table
    execute_query("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        status TEXT DEFAULT 'Active'
    )
    """)

    # Customers table
    execute_query("""
    CREATE TABLE IF NOT EXISTS customers (
        customer_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        phone TEXT,
        email TEXT,
        city TEXT,
        birthday_month TEXT,
        status TEXT,
        preferred_category TEXT,
        total_spend REAL DEFAULT 0,
        average_order_value REAL DEFAULT 0,
        purchase_frequency INTEGER DEFAULT 0,
        last_purchase_date TEXT
    )
    """)

    # Memberships table
    execute_query("""
    CREATE TABLE IF NOT EXISTS memberships (
        membership_id TEXT PRIMARY KEY,
        customer_id TEXT,
        membership_status TEXT,
        tier TEXT,
        points_balance INTEGER DEFAULT 0,
        points_earned INTEGER DEFAULT 0,
        points_redeemed INTEGER DEFAULT 0,
        expiry_date TEXT,
        upgrade_eligibility INTEGER DEFAULT 0
    )
    """)

    # Consents table
    execute_query("""
    CREATE TABLE IF NOT EXISTS consents (
        consent_id TEXT PRIMARY KEY,
        customer_id TEXT,
        whatsapp_consent INTEGER DEFAULT 0,
        sms_consent INTEGER DEFAULT 0,
        email_consent INTEGER DEFAULT 0,
        app_notification_consent INTEGER DEFAULT 0,
        personalization_consent INTEGER DEFAULT 0,
        do_not_contact INTEGER DEFAULT 0,
        consent_source TEXT,
        consent_given_date TEXT,
        consent_withdrawn_date TEXT
    )
    """)

    # Campaigns table
    execute_query("""
    CREATE TABLE IF NOT EXISTS campaigns (
        campaign_id TEXT PRIMARY KEY,
        campaign_name TEXT NOT NULL,
        campaign_type TEXT,
        channel TEXT,
        target_segment TEXT,
        status TEXT DEFAULT 'Draft',
        audience_count INTEGER DEFAULT 0,
        eligible_count INTEGER DEFAULT 0,
        created_by TEXT,
        approved_by TEXT
    )
    """)

    # Campaign responses table
    execute_query("""
    CREATE TABLE IF NOT EXISTS campaign_responses (
        response_id INTEGER PRIMARY KEY AUTOINCREMENT,
        campaign_id TEXT,
        customer_id TEXT,
        sent_status TEXT DEFAULT 'simulated',
        opened INTEGER DEFAULT 0,
        clicked INTEGER DEFAULT 0,
        converted INTEGER DEFAULT 0,
        revenue REAL DEFAULT 0
    )
    """)
    execute_query("""
    CREATE TABLE IF NOT EXISTS password_reset_codes (
    reset_id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    code_hash TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    used INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Audit logs table
    execute_query("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        user_role TEXT,
        action TEXT,
        object_type TEXT,
        object_id TEXT,
        status TEXT,
        details TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    seed_users()
    seed_sample_data()


def seed_users():
    users = [
        ("admin@omnilink.com", "1234567890", "Admin", "Active"),
        ("crm@omnilink.com", "1234567890", "CRM Team", "Active"),
        ("store@omnilink.com", "1234567890", "Store Team", "Active"),
        ("management@omnilink.com", "1234567890", "Management", "Active"),
        ("service@omnilink.com", "1234567890", "Customer Service", "Active"),
        ("security@omnilink.com", "1234567890", "Security / IT", "Active"),

        # Customer Service employees
        ("priya.nair@omnilink.com", "1234567890", "Customer Service", "Active"),
        ("kabir.sethi@omnilink.com", "1234567890", "Customer Service", "Active"),
        ("rohan.shah@omnilink.com", "1234567890", "Customer Service", "Active"),

        # Optional showcase user
        ("ankit97963@gmail.com", "1234567890", "Admin", "Active")
    ]

    for email, password, role, status in users:
        execute_query("""
        INSERT OR IGNORE INTO users (email, password, role, status)
        VALUES (?, ?, ?, ?)
        """, (email, password, role, status))


def seed_sample_data():
    customers = [
        ("CUST-1001", "Riya Sharma", "9876543210", "riya@mail.com", "Mumbai", "August", "Member", "Premium Dresses", 23800, 3400, 7, "2026-06-14"),
        ("CUST-1002", "Aarav Mehta", "9765432122", "aarav@mail.com", "Pune", "December", "Non-member", "Footwear", 14500, 2900, 5, "2026-06-02"),
        ("CUST-1003", "Neha Iyer", "9988776678", "neha@mail.com", "Mumbai", "July", "Member", "Ethnic Wear", 52200, 4350, 12, "2026-06-18"),
        ("CUST-1004", "Kabir Khan", "9654321054", "kabir@mail.com", "Navi Mumbai", "March", "Member", "Casual Wear", 7200, 1800, 4, "2026-03-04"),
    ]

    for customer in customers:
        execute_query("""
        INSERT OR IGNORE INTO customers
        (customer_id, name, phone, email, city, birthday_month, status, preferred_category, total_spend, average_order_value, purchase_frequency, last_purchase_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, customer)

    memberships = [
        ("MEM-1001", "CUST-1001", "Active", "Silver", 1320, 2000, 680, "2027-06-14", 1),
        ("MEM-1002", "CUST-1002", "Non-member", "Non-member", 0, 0, 0, None, 1),
        ("MEM-1003", "CUST-1003", "Active", "Gold", 4100, 6000, 1900, "2027-06-18", 1),
        ("MEM-1004", "CUST-1004", "Active", "Silver", 410, 600, 190, "2027-03-04", 0),
    ]

    for membership in memberships:
        execute_query("""
        INSERT OR IGNORE INTO memberships
        (membership_id, customer_id, membership_status, tier, points_balance, points_earned, points_redeemed, expiry_date, upgrade_eligibility)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, membership)

    consents = [
        ("CON-1001", "CUST-1001", 1, 1, 1, 1, 1, 0, "Membership Form", "2026-06-01", None),
        ("CON-1002", "CUST-1002", 1, 0, 1, 0, 1, 0, "Website", "2026-06-02", None),
        ("CON-1003", "CUST-1003", 0, 0, 1, 1, 1, 0, "App", "2026-06-03", None),
        ("CON-1004", "CUST-1004", 0, 0, 0, 0, 0, 1, "Customer Service", "2026-06-04", None),
    ]

    for consent in consents:
        execute_query("""
        INSERT OR IGNORE INTO consents
        (consent_id, customer_id, whatsapp_consent, sms_consent, email_consent, app_notification_consent, personalization_consent, do_not_contact, consent_source, consent_given_date, consent_withdrawn_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, consent)