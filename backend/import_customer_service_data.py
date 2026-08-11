import sqlite3
import pandas as pd

DB_NAME = "omnilink_crm.db"

TICKETS_CSV = r"C:\Users\tres1454\hks-vscode\data\updated_customer_360_customer_service_tickets.csv"
TIMELINE_CSV = r"C:\Users\tres1454\hks-vscode\data\updated_customer_360_customer_service_timeline.csv"

AGENT_MAP = {
    "Priya Nair": "AGT-001",
    "Kabir Sethi": "AGT-002",
    "Rohan Shah": "AGT-003",
    "Ankit Kumar": "AGT-004",
    "Harshit Sharma": "AGT-005",
    "Sneha Rao": "AGT-006"
}

conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS customer_service_tickets")
cur.execute("DROP TABLE IF EXISTS customer_service_timeline")
cur.execute("DROP TABLE IF EXISTS customer_service_agents")

cur.execute("""
CREATE TABLE customer_service_agents (
    agent_id TEXT PRIMARY KEY,
    agent_name TEXT,
    agent_email TEXT,
    role TEXT DEFAULT 'Customer Service Agent',
    status TEXT DEFAULT 'Active'
)
""")

cur.execute("""
CREATE TABLE customer_service_tickets (
    ticket_id TEXT PRIMARY KEY,
    customer_id TEXT,
    crm_customer_key TEXT,
    customer_name TEXT,
    linked_order_id TEXT,
    issue_category TEXT,
    query_type TEXT,
    priority TEXT,
    status TEXT,
    assigned_agent_id TEXT,
    assigned_to TEXT,
    created_on TEXT,
    sla_due TEXT,
    last_updated TEXT,
    channel TEXT,
    sla_status TEXT,
    escalation_level TEXT,
    escalated_to TEXT,
    membership_tier TEXT,
    masked_phone_number TEXT,
    masked_email TEXT,
    customer_city TEXT,
    customer_segment TEXT,
    churn_risk_level TEXT,
    product_id TEXT,
    product_name TEXT,
    product_category TEXT,
    transaction_date TEXT,
    order_value REAL,
    payment_method TEXT,
    delivery_status TEXT,
    return_refund_status TEXT,
    description TEXT,
    internal_notes TEXT,
    resolution_summary TEXT,
    call_review TEXT DEFAULT '',
    contact_result TEXT DEFAULT 'Not Contacted',
    follow_up_required TEXT DEFAULT 'No',
    follow_up_date TEXT DEFAULT '',
    follow_up_note TEXT DEFAULT '',
    completed_on TEXT DEFAULT '',
    last_action_by TEXT DEFAULT ''
)
""")

cur.execute("""
CREATE TABLE customer_service_timeline (
    timeline_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id TEXT,
    event_type TEXT,
    event_title TEXT,
    event_description TEXT,
    old_status TEXT,
    new_status TEXT,
    old_priority TEXT,
    new_priority TEXT,
    assigned_from TEXT,
    assigned_to TEXT,
    escalation_level TEXT,
    escalated_to TEXT,
    sla_status TEXT,
    created_by TEXT,
    created_at TEXT
)
""")

agents = [
    ("AGT-001", "Priya Nair", "priya.nair@omnilink.com"),
    ("AGT-002", "Kabir Sethi", "kabir.sethi@omnilink.com"),
    ("AGT-003", "Rohan Shah", "rohan.shah@omnilink.com"),
    ("AGT-004", "Ankit Kumar", "ankit.service@omnilink.com"),
    ("AGT-005", "Harshit Sharma", "harshit.service@omnilink.com"),
    ("AGT-006", "Sneha Rao", "sneha.rao@omnilink.com")
]

for agent_id, agent_name, email in agents:
    cur.execute("""
    INSERT INTO customer_service_agents
    (agent_id, agent_name, agent_email)
    VALUES (?, ?, ?)
    """, (agent_id, agent_name, email))

tickets_df = pd.read_csv(TICKETS_CSV)

for _, row in tickets_df.iterrows():
    assigned_to = str(row.get("assigned_to", "")).strip()
    assigned_agent_id = AGENT_MAP.get(assigned_to, "AGT-000")

    order_value = row.get("order_value", 0)

    try:
        order_value = float(order_value)
    except Exception:
        order_value = 0

    cur.execute("""
    INSERT INTO customer_service_tickets (
        ticket_id,
        customer_id,
        crm_customer_key,
        customer_name,
        linked_order_id,
        issue_category,
        query_type,
        priority,
        status,
        assigned_agent_id,
        assigned_to,
        created_on,
        sla_due,
        last_updated,
        channel,
        sla_status,
        escalation_level,
        escalated_to,
        membership_tier,
        masked_phone_number,
        masked_email,
        customer_city,
        customer_segment,
        churn_risk_level,
        product_id,
        product_name,
        product_category,
        transaction_date,
        order_value,
        payment_method,
        delivery_status,
        return_refund_status,
        description,
        internal_notes,
        resolution_summary
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        row.get("ticket_id"),
        str(row.get("customer_id")),
        row.get("crm_customer_key"),
        row.get("customer_name"),
        str(row.get("linked_order_id")),
        row.get("issue_category"),
        row.get("query_type"),
        row.get("priority"),
        row.get("status"),
        assigned_agent_id,
        assigned_to,
        row.get("created_on"),
        row.get("sla_due"),
        row.get("last_updated"),
        row.get("channel"),
        row.get("sla_status"),
        row.get("escalation_level"),
        row.get("escalated_to"),
        row.get("membership_tier"),
        row.get("masked_phone_number"),
        row.get("masked_email"),
        row.get("customer_city"),
        row.get("customer_segment"),
        row.get("churn_risk_level"),
        str(row.get("product_id")),
        row.get("product_name"),
        row.get("product_category"),
        row.get("transaction_date"),
        order_value,
        row.get("payment_method"),
        row.get("delivery_status"),
        row.get("return_refund_status"),
        row.get("description"),
        row.get("internal_notes"),
        row.get("resolution_summary")
    ))

timeline_df = pd.read_csv(TIMELINE_CSV)

for _, row in timeline_df.iterrows():
    cur.execute("""
    INSERT INTO customer_service_timeline (
        ticket_id,
        event_type,
        event_title,
        event_description,
        old_status,
        new_status,
        old_priority,
        new_priority,
        assigned_from,
        assigned_to,
        escalation_level,
        escalated_to,
        sla_status,
        created_by,
        created_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        row.get("ticket_id"),
        row.get("event_type"),
        row.get("event_title"),
        row.get("event_description"),
        row.get("old_status"),
        row.get("new_status"),
        row.get("old_priority"),
        row.get("new_priority"),
        row.get("assigned_from"),
        row.get("assigned_to"),
        row.get("escalation_level"),
        row.get("escalated_to"),
        row.get("sla_status"),
        row.get("created_by"),
        row.get("created_at")
    ))

conn.commit()
conn.close()

print("Customer service tables created and data imported successfully.")
print("Tickets imported:", len(tickets_df))
print("Timeline events imported:", len(timeline_df))