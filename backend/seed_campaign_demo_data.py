import sqlite3
import json
from datetime import datetime

DB_NAME = "omnilink_crm.db"

conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()

# -------------------------------------------------
# Ensure campaign tables exist
# -------------------------------------------------

cur.execute("""
CREATE TABLE IF NOT EXISTS crm_campaigns (
    campaign_id TEXT PRIMARY KEY,
    campaign_name TEXT NOT NULL,
    campaign_type TEXT,
    business_channel TEXT,
    demo_platform TEXT DEFAULT 'discord',
    target_segment TEXT,
    template_id TEXT,
    status TEXT DEFAULT 'Draft',
    total_audience INTEGER DEFAULT 0,
    eligible_count INTEGER DEFAULT 0,
    removed_count INTEGER DEFAULT 0,
    sent_count INTEGER DEFAULT 0,
    failed_count INTEGER DEFAULT 0,
    created_by TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS crm_campaign_templates (
    template_id TEXT PRIMARY KEY,
    template_name TEXT NOT NULL,
    template_type TEXT,
    template_json TEXT NOT NULL,
    created_by TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS crm_campaign_runs (
    run_id TEXT PRIMARY KEY,
    campaign_id TEXT,
    run_status TEXT,
    total_audience INTEGER DEFAULT 0,
    eligible_count INTEGER DEFAULT 0,
    removed_count INTEGER DEFAULT 0,
    sent_count INTEGER DEFAULT 0,
    failed_count INTEGER DEFAULT 0,
    run_date TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS crm_campaign_message_logs (
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT,
    campaign_id TEXT,
    customer_id TEXT,
    customer_name TEXT,
    business_channel TEXT,
    demo_platform TEXT,
    sent_status TEXT,
    rendered_title TEXT,
    rendered_message TEXT,
    opened INTEGER DEFAULT 0,
    clicked INTEGER DEFAULT 0,
    converted INTEGER DEFAULT 0,
    revenue REAL DEFAULT 0,
    error_message TEXT,
    sent_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

# -------------------------------------------------
# Insert campaign templates
# -------------------------------------------------

templates = [
    {
        "template_id": "TPL-BIRTHDAY",
        "template_name": "Birthday Voucher Reminder",
        "template_type": "Birthday",
        "template_json": {
            "title": "Happy Birthday {{customer_name}}!",
            "body": "Hi {{customer_name}}, your birthday voucher is ready. Visit us or open the app to redeem your reward.",
            "cta_text": "Redeem Now",
            "footer": "OmniLink CRM Demo"
        }
    },
    {
        "template_id": "TPL-MEMBER-CONVERT",
        "template_name": "Potential Member Conversion",
        "template_type": "Membership",
        "template_json": {
            "title": "Join OmniLink Rewards, {{customer_name}}",
            "body": "You have shown strong purchase activity in {{preferred_category}}. Join our loyalty program and unlock exclusive member benefits.",
            "cta_text": "Join Now",
            "footer": "OmniLink CRM Demo"
        }
    },
    {
        "template_id": "TPL-UPGRADE",
        "template_name": "Silver to Gold Upgrade Reminder",
        "template_type": "Upgrade",
        "template_json": {
            "title": "Upgrade Opportunity for {{customer_name}}",
            "body": "You are currently a {{membership_tier}} member with {{points_balance}} points. You may be eligible for the next tier.",
            "cta_text": "Explore Benefits",
            "footer": "OmniLink CRM Demo"
        }
    },
    {
        "template_id": "TPL-WINBACK",
        "template_name": "Inactive Customer Winback",
        "template_type": "Winback",
        "template_json": {
            "title": "We miss you, {{customer_name}}",
            "body": "It has been a while since your last purchase. Come back and explore new offers in {{preferred_category}}.",
            "cta_text": "Shop Again",
            "footer": "OmniLink CRM Demo"
        }
    },
    {
        "template_id": "TPL-HIGH-VALUE",
        "template_name": "High Value Customer Preview",
        "template_type": "Exclusive",
        "template_json": {
            "title": "Exclusive Preview for {{customer_name}}",
            "body": "As one of our high value customers, you get early access to premium offers in {{preferred_category}}.",
            "cta_text": "View Preview",
            "footer": "OmniLink CRM Demo"
        }
    }
]

for template in templates:
    cur.execute("""
    INSERT OR REPLACE INTO crm_campaign_templates
    (template_id, template_name, template_type, template_json, created_by)
    VALUES (?, ?, ?, ?, ?)
    """, (
        template["template_id"],
        template["template_name"],
        template["template_type"],
        json.dumps(template["template_json"]),
        "system"
    ))

# -------------------------------------------------
# Insert demo campaign master rows
# -------------------------------------------------

campaigns = [
    {
        "campaign_id": "CMP-DEMO-001",
        "campaign_name": "Potential Member Conversion Campaign",
        "campaign_type": "Membership",
        "business_channel": "Email",
        "demo_platform": "discord",
        "target_segment": "Potential Member",
        "template_id": "TPL-MEMBER-CONVERT",
        "status": "Draft",
        "total_audience": 120,
        "eligible_count": 86,
        "removed_count": 34,
        "sent_count": 0,
        "failed_count": 0
    },
    {
        "campaign_id": "CMP-DEMO-002",
        "campaign_name": "Birthday Voucher Campaign",
        "campaign_type": "Birthday",
        "business_channel": "Email",
        "demo_platform": "discord",
        "target_segment": "Birthday Month",
        "template_id": "TPL-BIRTHDAY",
        "status": "Ready for Preview",
        "total_audience": 65,
        "eligible_count": 51,
        "removed_count": 14,
        "sent_count": 0,
        "failed_count": 0
    },
    {
        "campaign_id": "CMP-DEMO-003",
        "campaign_name": "Silver to Gold Upgrade Campaign",
        "campaign_type": "Upgrade",
        "business_channel": "WhatsApp",
        "demo_platform": "discord",
        "target_segment": "Silver-to-Gold Eligible",
        "template_id": "TPL-UPGRADE",
        "status": "Simulated Sent",
        "total_audience": 90,
        "eligible_count": 63,
        "removed_count": 27,
        "sent_count": 5,
        "failed_count": 0
    },
    {
        "campaign_id": "CMP-DEMO-004",
        "campaign_name": "Inactive Customer Winback Campaign",
        "campaign_type": "Winback",
        "business_channel": "SMS",
        "demo_platform": "discord",
        "target_segment": "Inactive Customer",
        "template_id": "TPL-WINBACK",
        "status": "Review",
        "total_audience": 140,
        "eligible_count": 92,
        "removed_count": 48,
        "sent_count": 0,
        "failed_count": 0
    },
    {
        "campaign_id": "CMP-DEMO-005",
        "campaign_name": "High Value Customer Exclusive Preview",
        "campaign_type": "Exclusive",
        "business_channel": "App",
        "demo_platform": "discord",
        "target_segment": "High Value Customer",
        "template_id": "TPL-HIGH-VALUE",
        "status": "Approved",
        "total_audience": 45,
        "eligible_count": 38,
        "removed_count": 7,
        "sent_count": 0,
        "failed_count": 0
    }
]

for campaign in campaigns:
    cur.execute("""
    INSERT OR REPLACE INTO crm_campaigns
    (
        campaign_id,
        campaign_name,
        campaign_type,
        business_channel,
        demo_platform,
        target_segment,
        template_id,
        status,
        total_audience,
        eligible_count,
        removed_count,
        sent_count,
        failed_count,
        created_by,
        updated_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (
        campaign["campaign_id"],
        campaign["campaign_name"],
        campaign["campaign_type"],
        campaign["business_channel"],
        campaign["demo_platform"],
        campaign["target_segment"],
        campaign["template_id"],
        campaign["status"],
        campaign["total_audience"],
        campaign["eligible_count"],
        campaign["removed_count"],
        campaign["sent_count"],
        campaign["failed_count"],
        "crm@omnilink.com"
    ))

# -------------------------------------------------
# Insert one completed run for demo campaign
# -------------------------------------------------

cur.execute("""
INSERT OR REPLACE INTO crm_campaign_runs
(
    run_id,
    campaign_id,
    run_status,
    total_audience,
    eligible_count,
    removed_count,
    sent_count,
    failed_count,
    run_date
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
""", (
    "RUN-DEMO-001",
    "CMP-DEMO-003",
    "Completed",
    90,
    63,
    27,
    5,
    0
))

cur.execute("""
SELECT
    customer_id,
    customer_name,
    product_category,
    membership_tier,
    points_balance
FROM customers_360
LIMIT 5
""")

sample_customers = cur.fetchall()

for index, customer in enumerate(sample_customers):
    customer_id = str(customer[0])
    customer_name = customer[1] or f"Customer {customer_id}"
    preferred_category = customer[2] or "your preferred category"
    membership_tier = customer[3] or "Silver"
    points_balance = customer[4] or 0



    rendered_title = f"Upgrade Opportunity for {customer_name}"
    rendered_message = (
        f"Hi {customer_name}, you are currently a {membership_tier} member "
        f"with {points_balance} points. You may be eligible for the next tier. "
        f"Explore offers related to {preferred_category}."
    )

    opened = 1 if index in [0, 1, 2] else 0
    clicked = 1 if index in [0, 2] else 0
    converted = 1 if index == 0 else 0
    revenue = 2499.00 if converted else 0

    cur.execute("""
    INSERT INTO crm_campaign_message_logs
    (
        run_id,
        campaign_id,
        customer_id,
        customer_name,
        business_channel,
        demo_platform,
        sent_status,
        rendered_title,
        rendered_message,
        opened,
        clicked,
        converted,
        revenue,
        error_message,
        sent_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (
        "RUN-DEMO-001",
        "CMP-DEMO-003",
        customer_id,
        customer_name,
        "WhatsApp",
        "discord",
        "simulated",
        rendered_title,
        rendered_message,
        opened,
        clicked,
        converted,
        revenue,
        ""
    ))

    cur.execute("""
    INSERT INTO campaign_responses
    (
        campaign_id,
        customer_id,
        sent_status,
        opened,
        clicked,
        converted,
        revenue
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        "CMP-DEMO-003",
        customer_id,
        "simulated",
        opened,
        clicked,
        converted,
        revenue
    ))

conn.commit()
conn.close()

print("Demo campaign data inserted successfully.")
print("Campaigns inserted: 5")
print("Templates inserted: 5")
print("Demo message logs inserted from real customers:", len(sample_customers))