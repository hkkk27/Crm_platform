import json
from app.db.sqlite_client import fetch_all, fetch_one


def get_consent_column_for_channel(channel: str):
    channel = (channel or "").lower()

    channel_map = {
        "whatsapp": "whatsapp_consent",
        "sms": "sms_consent",
        "email": "email_consent",
        "app": "app_notification_consent",
        "app notification": "app_notification_consent"
    }

    return channel_map.get(channel)


def build_segment_where_clause(target_segment: str):
    target_segment = target_segment or ""
    normalized_segment = target_segment.strip().lower()

    if normalized_segment == "all customers":
        return "1 = 1", ()

    if normalized_segment == "birthday month":
        return "month_of_year IS NOT NULL", ()

    if normalized_segment == "potential member":
        return """
        (
            customer_segment = ?
            OR membership_status = 'Non-member'
            OR potential_member_score >= 60
        )
        """, ("Potential Member",)

    if normalized_segment == "silver-to-gold eligible":
        return """
        (
            customer_segment = ?
            OR membership_tier = 'Silver'
            OR upgrade_eligibility IN (1, '1', 'Yes', 'yes', 'TRUE', 'true')
        )
        """, ("Silver-to-Gold Eligible",)

    if normalized_segment == "gold-to-platinum eligible":
        return """
        (
            customer_segment = ?
            OR membership_tier = 'Gold'
            OR upgrade_eligibility IN (1, '1', 'Yes', 'yes', 'TRUE', 'true')
        )
        """, ("Gold-to-Platinum Eligible",)

    if normalized_segment == "inactive customer":
        return """
        (
            customer_segment = ?
            OR customer_segment LIKE '%Inactive%'
            OR churn_risk_level = 'High'
            OR days_since_last_purchase >= 90
        )
        """, ("Inactive Customer",)

    if normalized_segment == "high value customer":
        return """
        (
            customer_segment = ?
            OR customer_segment LIKE '%High%'
            OR estimated_clv >= 50000
            OR total_sales >= 50000
        )
        """, ("High Value Customer",)

    if normalized_segment == "discount sensitive customer":
        return """
        (
            customer_segment = ?
            OR customer_segment LIKE '%Discount%'
            OR avg_discount_used > 0
        )
        """, ("Discount Sensitive Customer",)

    if normalized_segment == "electronics buyer":
        return """
        (
            customer_segment = ?
            OR product_category = 'Electronics'
        )
        """, ("Electronics Buyer",)

    if normalized_segment == "clothing buyer":
        return """
        (
            customer_segment = ?
            OR product_category = 'Clothing'
        )
        """, ("Clothing Buyer",)

    if normalized_segment == "groceries buyer":
        return """
        (
            customer_segment = ?
            OR product_category = 'Groceries'
        )
        """, ("Groceries Buyer",)

    return "customer_segment = ?", (target_segment,)


def get_campaign_audience(campaign: dict):
    where_clause, params = build_segment_where_clause(campaign.get("target_segment"))

    query = f"""
    SELECT
        customer_id,
        crm_customer_key,
        customer_name,
        email,
        phone_number,
        customer_city,
        product_category,
        product_category AS preferred_category,
        membership_status,
        membership_tier,
        points_balance,
        customer_segment,
        potential_member_score,
        recommendation_reason_codes,
        whatsapp_consent,
        sms_consent,
        email_consent,
        app_notification_consent,
        personalization_consent,
        do_not_contact
    FROM customers_360
    WHERE {where_clause}
    LIMIT 1000
    """

    return fetch_all(query, params)


def filter_audience_by_consent(customers: list, business_channel: str):
    consent_column = get_consent_column_for_channel(business_channel)

    eligible = []
    removed = []

    for customer in customers:
        if customer.get("do_not_contact") in [1, "1", True]:
            removed.append({
                **customer,
                "removed_reason": "Do Not Contact"
            })
            continue

        if not consent_column:
            eligible.append(customer)
            continue

        if customer.get(consent_column) in [1, "1", True]:
            eligible.append(customer)
        else:
            removed.append({
                **customer,
                "removed_reason": f"No {business_channel} consent"
            })

    return eligible, removed


def render_template(template_json_text: str, customer: dict, campaign: dict):
    try:
        template = json.loads(template_json_text)
    except Exception:
        template = {
            "title": "Campaign Message",
            "body": template_json_text,
            "cta_text": "Learn More",
            "footer": "OmniLink CRM Demo"
        }

    replacements = {
        "{{customer_id}}": str(customer.get("customer_id", "")),
        "{{customer_name}}": str(customer.get("customer_name", "Customer")),
        "{{membership_tier}}": str(customer.get("membership_tier", "Non-member")),
        "{{points_balance}}": str(customer.get("points_balance", 0)),
        "{{preferred_category}}": str(
            customer.get("preferred_category")
            or customer.get("product_category")
            or "your favorite category"
        ),
        "{{customer_segment}}": str(customer.get("customer_segment", "")),
        "{{campaign_id}}": str(campaign.get("campaign_id", "")),
        "{{campaign_name}}": str(campaign.get("campaign_name", ""))
    }

    rendered = {}

    for key, value in template.items():
        if isinstance(value, str):
            rendered_value = value
            for placeholder, replacement in replacements.items():
                rendered_value = rendered_value.replace(placeholder, replacement)
            rendered[key] = rendered_value
        else:
            rendered[key] = value

    return rendered


def get_template(template_id: str):
    return fetch_one("""
    SELECT *
    FROM crm_campaign_templates
    WHERE template_id = ?
    """, (template_id,))


def build_campaign_metrics(campaign_id: str):
    total = fetch_one("""
    SELECT COUNT(*) as count
    FROM crm_campaign_message_logs
    WHERE campaign_id = ?
    """, (campaign_id,))

    sent = fetch_one("""
    SELECT COUNT(*) as count
    FROM crm_campaign_message_logs
    WHERE campaign_id = ? AND sent_status = 'sent'
    """, (campaign_id,))

    failed = fetch_one("""
    SELECT COUNT(*) as count
    FROM crm_campaign_message_logs
    WHERE campaign_id = ? AND sent_status = 'failed'
    """, (campaign_id,))

    simulated = fetch_one("""
    SELECT COUNT(*) as count
    FROM crm_campaign_message_logs
    WHERE campaign_id = ? AND sent_status = 'simulated'
    """, (campaign_id,))

    clicked = fetch_one("""
    SELECT COUNT(*) as count
    FROM crm_campaign_message_logs
    WHERE campaign_id = ? AND clicked = 1
    """, (campaign_id,))

    converted = fetch_one("""
    SELECT COUNT(*) as count
    FROM crm_campaign_message_logs
    WHERE campaign_id = ? AND converted = 1
    """, (campaign_id,))

    revenue = fetch_one("""
    SELECT ROUND(SUM(revenue), 2) as value
    FROM crm_campaign_message_logs
    WHERE campaign_id = ?
    """, (campaign_id,))

    return {
        "total_logs": total["count"] if total else 0,
        "sent_count": sent["count"] if sent else 0,
        "failed_count": failed["count"] if failed else 0,
        "simulated_count": simulated["count"] if simulated else 0,
        "clicked_count": clicked["count"] if clicked else 0,
        "converted_count": converted["count"] if converted else 0,
        "revenue": revenue["value"] if revenue and revenue["value"] else 0
    }