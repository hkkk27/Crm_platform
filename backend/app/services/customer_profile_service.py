def pick(row: dict, possible_keys: list, default=None):
    """
    Safely pick first available column from a row.
    Useful because CSV column names may differ slightly.
    """
    if not row:
        return default

    for key in possible_keys:
        if key in row and row[key] not in [None, "", "nan"]:
            return row[key]

    return default


def mask_phone(phone):
    if not phone:
        return None

    phone = str(phone)

    if len(phone) < 4:
        return "xxxx"

    return phone[:2] + "xxxxxx" + phone[-2:]


def mask_email(email):
    if not email:
        return None

    email = str(email)

    if "@" not in email:
        return "restricted"

    first = email[0]
    domain = email.split("@")[-1]

    return first + "*****@" + domain


def apply_customer_masking(customer: dict, role: str):
    """
    Store Team and Management should not see full personal data.
    """
    if not customer:
        return customer

    masked_customer = dict(customer)

    if role in ["Store Team", "Management"]:
        if "phone_number" in masked_customer:
            masked_customer["phone_number"] = mask_phone(masked_customer.get("phone_number"))

        if "email" in masked_customer:
            masked_customer["email"] = mask_email(masked_customer.get("email"))

        if "customer_name" in masked_customer:
            masked_customer["customer_name"] = masked_customer.get("customer_name")

    return masked_customer


def build_membership_summary(customer: dict):
    return {
        "membership_status": pick(customer, ["membership_status", "loyalty_program"], "Unknown"),
        "membership_tier": pick(customer, ["membership_tier"], "Unknown"),
        "points_earned": pick(customer, ["points_earned"], 0),
        "points_redeemed": pick(customer, ["points_redeemed"], 0),
        "points_balance": pick(customer, ["points_balance"], 0),
        "membership_expiry_date": pick(customer, ["membership_expiry_date"], None),
        "upgrade_eligibility": pick(customer, ["upgrade_eligibility"], False),
    }


def build_customer_summary(customer: dict):
    return {
        "customer_id": pick(customer, ["customer_id"]),
        "crm_customer_key": pick(customer, ["crm_customer_key"]),
        "name": pick(customer, ["customer_name", "name"]),
        "phone": pick(customer, ["phone_number", "phone"]),
        "masked_phone": pick(customer, ["masked_phone_number"]),
        "email": pick(customer, ["email"]),
        "masked_email": pick(customer, ["masked_email"]),
        "age": pick(customer, ["age"]),
        "age_group": pick(customer, ["age_group"]),
        "gender": pick(customer, ["gender"]),
        "income_bracket": pick(customer, ["income_bracket"]),
        "city": pick(customer, ["customer_city", "city"]),
        "state": pick(customer, ["customer_state", "state"]),
        "city_tier": pick(customer, ["customer_city_tier"]),
        "preferred_category": pick(customer, ["preferred_category", "product_category"]),
        "primary_shopping_channel": pick(customer, ["primary_shopping_channel"]),
    }


def build_purchase_summary(customer: dict):
    return {
        "total_sales": pick(customer, ["total_sales"], 0),
        "total_transactions": pick(customer, ["total_transactions"], 0),
        "total_items_purchased": pick(customer, ["total_items_purchased"], 0),
        "average_order_value": pick(customer, ["average_order_value", "avg_transaction_value", "avg_purchase_value"], 0),
        "purchase_frequency": pick(customer, ["purchase_frequency"]),
        "last_purchase_date": pick(customer, ["last_purchase_date", "last_purchase_date_parsed"]),
        "days_since_last_purchase": pick(customer, ["days_since_last_purchase"]),
        "online_purchases": pick(customer, ["online_purchases"], 0),
        "in_store_purchases": pick(customer, ["in_store_purchases"], 0),
        "estimated_clv": pick(customer, ["estimated_clv"], 0),
        "churn_risk_level": pick(customer, ["churn_risk_level"], "Unknown"),
    }


def build_segmentation_summary(customer: dict):
    return {
        "customer_segment": pick(customer, ["customer_segment"], "General Customer"),
        "potential_member_score": pick(customer, ["potential_member_score"], 0),
        "recommendation_reason_codes": pick(customer, ["recommendation_reason_codes"], ""),
        "repeat_purchase_flag": pick(customer, ["repeat_purchase_flag"], False),
        "campaign_eligible_whatsapp": pick(customer, ["campaign_eligible_whatsapp"], False),
        "campaign_eligible_sms": pick(customer, ["campaign_eligible_sms"], False),
        "campaign_eligible_email": pick(customer, ["campaign_eligible_email"], False),
        "campaign_eligible_app": pick(customer, ["campaign_eligible_app"], False),
    }