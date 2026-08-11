# from app.db.sqlite_client import fetch_all, fetch_one


# VALID_TIERS = [
#     "Non-member",
#     "Silver",
#     "Gold",
#     "Platinum",
# ]


# def to_number(value, default=0):
#     """
#     Safely converts a value to float.
#     """

#     try:
#         if value is None or value == "":
#             return default

#         return float(value)

#     except (TypeError, ValueError):
#         return default


# def to_integer(value, default=0):
#     """
#     Safely converts a value to integer.
#     """

#     try:
#         if value is None or value == "":
#             return default

#         return int(float(value))

#     except (TypeError, ValueError):
#         return default


# def to_boolean(value):
#     """
#     Supports SQLite integers, booleans, and CSV text values.
#     """

#     if isinstance(value, str):
#         return value.strip().lower() in [
#             "1",
#             "true",
#             "yes",
#             "y",
#         ]

#     return value in [
#         True,
#         1,
#     ]


# def normalize_tier(tier):
#     """
#     Converts different tier spellings into the standard tier names.

#     Important:
#     Unknown or empty tiers are treated as Non-member.
#     """

#     value = str(
#         tier or "Non-member"
#     ).strip().lower()

#     tier_map = {
#         "non-member": "Non-member",
#         "non member": "Non-member",
#         "nonmember": "Non-member",
#         "potential": "Non-member",
#         "potential member": "Non-member",
#         "inactive": "Non-member",
#         "silver": "Silver",
#         "gold": "Gold",
#         "platinum": "Platinum",
#     }

#     return tier_map.get(
#         value,
#         "Non-member",
#     )


# def get_tier_rule(tier_name):
#     """
#     Returns the active configuration rule for one tier.
#     """

#     tier = normalize_tier(tier_name)

#     return fetch_one(
#         """
#         SELECT *
#         FROM loyalty_tier_rules
#         WHERE tier_name = ?
#           AND is_active = 1
#         """,
#         (tier,),
#     )


# def get_all_tier_rules():
#     """
#     Returns all active tier rules in membership order.
#     """

#     return fetch_all(
#         """
#         SELECT *
#         FROM loyalty_tier_rules
#         WHERE is_active = 1
#         ORDER BY
#             CASE tier_name
#                 WHEN 'Non-member' THEN 1
#                 WHEN 'Silver' THEN 2
#                 WHEN 'Gold' THEN 3
#                 WHEN 'Platinum' THEN 4
#                 ELSE 5
#             END
#         """
#     )


# def get_tier_benefits(tier_name):
#     """
#     Returns active benefits belonging to one tier.
#     """

#     tier = normalize_tier(tier_name)

#     return fetch_all(
#         """
#         SELECT *
#         FROM loyalty_benefits
#         WHERE tier_name = ?
#           AND is_active = 1
#         ORDER BY benefit_name
#         """,
#         (tier,),
#     )


# def get_all_benefits():
#     """
#     Returns all active benefits grouped in tier order.
#     """

#     return fetch_all(
#         """
#         SELECT *
#         FROM loyalty_benefits
#         WHERE is_active = 1
#         ORDER BY
#             CASE tier_name
#                 WHEN 'Non-member' THEN 1
#                 WHEN 'Silver' THEN 2
#                 WHEN 'Gold' THEN 3
#                 WHEN 'Platinum' THEN 4
#                 ELSE 5
#             END,
#             benefit_name
#         """
#     )


# def calculate_points_for_purchase(
#     tier_name,
#     order_amount,
# ):
#     """
#     Calculates reward points for one purchase.

#     Current rules from loyalty_tier_rules:

#     Non-member: 1 point per Rs. 1,000
#     Silver: 2 points per Rs. 1,000
#     Gold: 3 points per Rs. 1,000
#     Platinum: 4 points per Rs. 1,000
#     """

#     tier = normalize_tier(tier_name)
#     rule = get_tier_rule(tier)

#     spend_unit = 1000
#     multiplier = 1

#     if rule:
#         spend_unit = to_number(
#             rule.get("spend_unit"),
#             1000,
#         )

#         multiplier = to_integer(
#             rule.get("points_multiplier"),
#             1,
#         )

#     amount = to_number(
#         order_amount,
#         0,
#     )

#     if amount <= 0 or spend_unit <= 0:
#         return {
#             "tier": tier,
#             "order_amount": amount,
#             "spend_unit": spend_unit,
#             "points_multiplier": multiplier,
#             "base_units": 0,
#             "points_earned": 0,
#         }

#     base_units = int(
#         amount // spend_unit
#     )

#     points_earned = (
#         base_units * multiplier
#     )

#     return {
#         "tier": tier,
#         "order_amount": amount,
#         "spend_unit": spend_unit,
#         "points_multiplier": multiplier,
#         "base_units": base_units,
#         "points_earned": points_earned,
#     }


# def calculate_upgrade_score(customer):
#     """
#     Calculates an internal CRM recommendation score.

#     This score does not control whether a customer can purchase
#     membership.

#     The score is only used by the company to identify customers
#     who may respond well to membership or tier-upgrade campaigns.

#     Maximum score: 100
#     """

#     score = 0
#     reasons = []

#     total_sales = to_number(
#         customer.get("total_sales"),
#         0,
#     )

#     total_transactions = to_integer(
#         customer.get("total_transactions"),
#         0,
#     )

#     estimated_clv = to_number(
#         customer.get("estimated_clv"),
#         0,
#     )

#     days_since_last_purchase = to_integer(
#         customer.get("days_since_last_purchase"),
#         999,
#     )

#     app_sessions = to_integer(
#         customer.get("app_sessions_30d"),
#         0,
#     )

#     website_visits = to_integer(
#         customer.get("website_visits"),
#         0,
#     )

#     wishlist_count = to_integer(
#         customer.get("wishlist_count"),
#         0,
#     )

#     # -------------------------------------------------
#     # Total sales score: maximum 30 points
#     # -------------------------------------------------

#     if total_sales >= 50000:
#         score += 30
#         reasons.append(
#             "Very high total sales"
#         )

#     elif total_sales >= 20000:
#         score += 20
#         reasons.append(
#             "High total sales"
#         )

#     elif total_sales >= 10000:
#         score += 10
#         reasons.append(
#             "Good total sales"
#         )

#     # -------------------------------------------------
#     # Transaction frequency: maximum 20 points
#     # -------------------------------------------------

#     if total_transactions >= 20:
#         score += 20
#         reasons.append(
#             "Very frequent transactions"
#         )

#     elif total_transactions >= 10:
#         score += 12
#         reasons.append(
#             "Frequent transactions"
#         )

#     elif total_transactions >= 5:
#         score += 6
#         reasons.append(
#             "Regular transactions"
#         )

#     # -------------------------------------------------
#     # Customer lifetime value: maximum 20 points
#     # -------------------------------------------------

#     if estimated_clv >= 50000:
#         score += 20
#         reasons.append(
#             "Very high estimated CLV"
#         )

#     elif estimated_clv >= 20000:
#         score += 12
#         reasons.append(
#             "High estimated CLV"
#         )

#     elif estimated_clv >= 10000:
#         score += 6
#         reasons.append(
#             "Good estimated CLV"
#         )

#     # -------------------------------------------------
#     # Recent activity: maximum 10 points
#     # -------------------------------------------------

#     if days_since_last_purchase <= 30:
#         score += 10
#         reasons.append(
#             "Recently active"
#         )

#     elif days_since_last_purchase <= 90:
#         score += 5
#         reasons.append(
#             "Moderately recent purchase"
#         )

#     # -------------------------------------------------
#     # Repeat purchase: maximum 15 points
#     # -------------------------------------------------

#     if to_boolean(
#         customer.get("repeat_purchase_flag")
#     ):
#         score += 15
#         reasons.append(
#             "Repeat purchaser"
#         )

#     # -------------------------------------------------
#     # Digital engagement: maximum 5 points
#     # -------------------------------------------------

#     if (
#         app_sessions >= 10
#         or website_visits >= 20
#         or wishlist_count >= 5
#     ):
#         score += 5
#         reasons.append(
#             "Strong digital engagement"
#         )

#     return {
#         "score": min(score, 100),
#         "reasons": reasons,
#     }


# def get_contactability(customer):
#     """
#     Separates loyalty recommendations from communication permission.

#     A customer can be recommended for membership or upgrade even if
#     marketing contact is blocked.

#     Consent controls communication only.
#     """

#     do_not_contact = to_boolean(
#         customer.get("do_not_contact")
#     )

#     channels = []

#     if not do_not_contact:
#         if to_boolean(
#             customer.get("whatsapp_consent")
#         ):
#             channels.append("WhatsApp")

#         if to_boolean(
#             customer.get("sms_consent")
#         ):
#             channels.append("SMS")

#         if to_boolean(
#             customer.get("email_consent")
#         ):
#             channels.append("Email")

#         if to_boolean(
#             customer.get(
#                 "app_notification_consent"
#             )
#         ):
#             channels.append("App")

#     return {
#         "contact_allowed": (
#             not do_not_contact
#             and len(channels) > 0
#         ),
#         "do_not_contact": do_not_contact,
#         "available_channels": channels,
#     }


# def calculate_loyalty_recommendation(customer):
#     """
#     Calculates the internal CRM loyalty recommendation.

#     Actual membership:
#         Chosen or purchased by the customer.

#     Recommendation:
#         Used only by the company for segmentation and campaigns.
#     """

#     current_tier = normalize_tier(
#         customer.get("membership_tier")
#     )

#     membership_status = str(
#         customer.get("membership_status")
#         or "Non-member"
#     ).strip()

#     potential_member_score = to_integer(
#         customer.get("potential_member_score"),
#         0,
#     )

#     score_result = calculate_upgrade_score(
#         customer
#     )

#     upgrade_score = score_result["score"]
#     reasons = list(
#         score_result["reasons"]
#     )

#     contactability = get_contactability(
#         customer
#     )

#     rule = get_tier_rule(
#         current_tier
#     )

#     next_tier = (
#         rule.get("next_tier")
#         if rule
#         else None
#     )

#     # The actual database field is:
#     # minimum_recommendation_score
#     minimum_score = (
#         to_integer(
#             rule.get(
#                 "minimum_recommendation_score"
#             ),
#             100,
#         )
#         if rule
#         else 100
#     )

#     recommendation_flag = False
#     recommendation_label = ""
#     loyalty_segment = ""
#     recommended_action = ""

#     is_non_member = (
#         current_tier == "Non-member"
#         or membership_status.lower()
#         in [
#             "non-member",
#             "non member",
#             "nonmember",
#             "inactive",
#             "",
#         ]
#     )

#     # -------------------------------------------------
#     # Non-member recommendation
#     # -------------------------------------------------

#     if is_non_member:
#         if potential_member_score >= 70:
#             loyalty_segment = (
#                 "High Potential Member"
#             )

#             recommendation_flag = True

#             recommendation_label = (
#                 "Strong candidate for membership advertising"
#             )

#             recommended_action = (
#                 "Promote Silver, Gold or Platinum membership"
#             )

#         elif potential_member_score >= 50:
#             loyalty_segment = (
#                 "Medium Potential Member"
#             )

#             recommendation_flag = True

#             recommendation_label = (
#                 "Moderate membership conversion opportunity"
#             )

#             recommended_action = (
#                 "Send educational membership benefits"
#             )

#         else:
#             loyalty_segment = (
#                 "Low Potential Member"
#             )

#             recommendation_label = (
#                 "Low current membership propensity"
#             )

#             recommended_action = (
#                 "Continue engagement and monitor behaviour"
#             )

#     # -------------------------------------------------
#     # Silver recommendation
#     # -------------------------------------------------

#     elif current_tier == "Silver":
#         if upgrade_score >= minimum_score:
#             loyalty_segment = (
#                 "Silver-to-Gold Recommended"
#             )

#             recommendation_flag = True

#             recommendation_label = (
#                 "Recommended for Gold membership campaign"
#             )

#             recommended_action = (
#                 "Promote Gold benefits and early access"
#             )

#         else:
#             loyalty_segment = (
#                 "Silver Member"
#             )

#             recommendation_label = (
#                 "Continue Silver member engagement"
#             )

#             recommended_action = (
#                 "Promote Silver benefits and points usage"
#             )

#     # -------------------------------------------------
#     # Gold recommendation
#     # -------------------------------------------------

#     elif current_tier == "Gold":
#         if upgrade_score >= minimum_score:
#             loyalty_segment = (
#                 "Gold-to-Platinum Recommended"
#             )

#             recommendation_flag = True

#             recommendation_label = (
#                 "Recommended for Platinum membership campaign"
#             )

#             recommended_action = (
#                 "Promote Platinum pre-launch and premium benefits"
#             )

#         else:
#             loyalty_segment = (
#                 "Gold Member"
#             )

#             recommendation_label = (
#                 "Continue Gold member engagement"
#             )

#             recommended_action = (
#                 "Promote Gold benefits and bonus points"
#             )

#     # -------------------------------------------------
#     # Platinum recommendation
#     # -------------------------------------------------

#     elif current_tier == "Platinum":
#         loyalty_segment = (
#             "Top-Tier Platinum"
#         )

#         recommendation_label = (
#             "Top membership tier"
#         )

#         recommended_action = (
#             "Focus on retention, premium service and VIP access"
#         )

#     # -------------------------------------------------
#     # Retention override
#     #
#     # A current member with high churn risk should be
#     # prioritized for retention.
#     # -------------------------------------------------

#     churn_risk = str(
#         customer.get("churn_risk_level")
#         or ""
#     ).strip().lower()

#     if (
#         current_tier != "Non-member"
#         and churn_risk == "high"
#     ):
#         loyalty_segment = (
#             "Loyal but High Churn Risk"
#         )

#         recommended_action = (
#             "Prioritize retention and customer service outreach"
#         )

#         reasons.append(
#             "High churn risk"
#         )

#     # -------------------------------------------------
#     # Communication status
#     # -------------------------------------------------

#     if contactability["do_not_contact"]:
#         communication_status = (
#             "Recommendation available but marketing contact blocked"
#         )

#     elif not contactability[
#         "available_channels"
#     ]:
#         communication_status = (
#             "No approved communication channel"
#         )

#     else:
#         communication_status = (
#             "Contact allowed through approved channels"
#         )

#     return {
#         "actual_membership_tier":
#             current_tier,

#         "potential_member_score":
#             potential_member_score,

#         "tier_upgrade_score":
#             upgrade_score,

#         "recommendation_score_required":
#             minimum_score,

#         "recommendation_flag":
#             recommendation_flag,

#         "recommended_tier":
#             next_tier,

#         "recommendation_label":
#             recommendation_label,

#         "loyalty_segment":
#             loyalty_segment,

#         "recommended_action":
#             recommended_action,

#         "score_reasons":
#             reasons,

#         "contact_allowed":
#             contactability[
#                 "contact_allowed"
#             ],

#         "do_not_contact":
#             contactability[
#                 "do_not_contact"
#             ],

#         "available_channels":
#             contactability[
#                 "available_channels"
#             ],

#         "communication_status":
#             communication_status,
#     }


# def build_loyalty_customer(customer):
#     """
#     Builds the final customer object returned to the Loyalty frontend.
#     """

#     if not customer:
#         return None

#     recommendation = (
#         calculate_loyalty_recommendation(
#             customer
#         )
#     )

#     tier = recommendation[
#         "actual_membership_tier"
#     ]

#     # rule = get_tier_rule(tier)
#     # benefits = get_tier_benefits(tier)
#     rule = None
#     benefits = []

#     points_earned = to_integer(
#         customer.get("points_earned"),
#         0,
#     )

#     points_redeemed = to_integer(
#         customer.get("points_redeemed"),
#         0,
#     )

#     points_balance = to_integer(
#         customer.get("points_balance"),
#         0,
#     )

#     # Current conversion rule:
#     # 100 points = Rs. 10.
#     # Therefore, one point = Rs. 0.10.
#     redeemable_value = round(
#         points_balance * 0.10,
#         2,
#     )

#     result = dict(customer)

#     result.update(
#         recommendation
#     )

#     result.update(
#         {
#             "points_earned":
#                 points_earned,

#             "points_redeemed":
#                 points_redeemed,

#             "points_balance":
#                 points_balance,

#             "redeemable_value":
#                 redeemable_value,

#             "tier_rule":
#                 rule,

#             "benefits":
#                 benefits,
#         }
#     )

#     return result

from app.db.sqlite_client import fetch_all, fetch_one

VALID_TIERS = ["Non-member", "Silver", "Gold", "Platinum"]


def to_number(value, default=0):
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def to_integer(value, default=0):
    try:
        if value is None or value == "":
            return default
        return int(float(value))
    except (TypeError, ValueError):
        return default


def to_boolean(value):
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y"}
    return value in {True, 1}


def normalize_tier(tier):
    value = str(tier or "Non-member").strip().lower()
    return {
        "non-member": "Non-member",
        "non member": "Non-member",
        "nonmember": "Non-member",
        "potential": "Non-member",
        "potential member": "Non-member",
        "inactive": "Non-member",
        "silver": "Silver",
        "gold": "Gold",
        "platinum": "Platinum",
    }.get(value, "Non-member")


def get_tier_rule(tier_name):
    return fetch_one(
        """
        SELECT *
        FROM loyalty_tier_rules
        WHERE tier_name = ? AND is_active = 1
        """,
        (normalize_tier(tier_name),),
    )


def get_all_tier_rules():
    return fetch_all(
        """
        SELECT *
        FROM loyalty_tier_rules
        WHERE is_active = 1
        ORDER BY CASE tier_name
            WHEN 'Non-member' THEN 1
            WHEN 'Silver' THEN 2
            WHEN 'Gold' THEN 3
            WHEN 'Platinum' THEN 4
            ELSE 5
        END
        """
    )


def get_tier_benefits(tier_name):
    return fetch_all(
        """
        SELECT *
        FROM loyalty_benefits
        WHERE tier_name = ? AND is_active = 1
        ORDER BY benefit_name
        """,
        (normalize_tier(tier_name),),
    )


def get_all_benefits():
    return fetch_all(
        """
        SELECT *
        FROM loyalty_benefits
        WHERE is_active = 1
        ORDER BY CASE tier_name
            WHEN 'Non-member' THEN 1
            WHEN 'Silver' THEN 2
            WHEN 'Gold' THEN 3
            WHEN 'Platinum' THEN 4
            ELSE 5
        END, benefit_name
        """
    )


def build_rule_map(rules=None):
    rows = rules if rules is not None else get_all_tier_rules()
    return {normalize_tier(row.get("tier_name")): row for row in rows}


def build_benefit_map(benefits=None):
    rows = benefits if benefits is not None else get_all_benefits()
    result = {tier: [] for tier in VALID_TIERS}
    for row in rows:
        result.setdefault(normalize_tier(row.get("tier_name")), []).append(row)
    return result


def calculate_points_for_purchase(tier_name, order_amount, rule=None):
    tier = normalize_tier(tier_name)
    selected_rule = rule if rule is not None else get_tier_rule(tier)
    spend_unit = to_number(selected_rule.get("spend_unit"), 1000) if selected_rule else 1000
    multiplier = to_integer(selected_rule.get("points_multiplier"), 1) if selected_rule else 1
    amount = to_number(order_amount, 0)

    if amount <= 0 or spend_unit <= 0:
        return {
            "tier": tier,
            "order_amount": amount,
            "spend_unit": spend_unit,
            "points_multiplier": multiplier,
            "base_units": 0,
            "points_earned": 0,
        }

    base_units = int(amount // spend_unit)
    return {
        "tier": tier,
        "order_amount": amount,
        "spend_unit": spend_unit,
        "points_multiplier": multiplier,
        "base_units": base_units,
        "points_earned": base_units * multiplier,
    }


def calculate_upgrade_score(customer):
    score = 0
    reasons = []
    total_sales = to_number(customer.get("total_sales"))
    total_transactions = to_integer(customer.get("total_transactions"))
    estimated_clv = to_number(customer.get("estimated_clv"))
    days_since_last_purchase = to_integer(customer.get("days_since_last_purchase"), 999)
    app_sessions = to_integer(customer.get("app_sessions_30d"))
    website_visits = to_integer(customer.get("website_visits"))
    wishlist_count = to_integer(customer.get("wishlist_count"))

    if total_sales >= 50000:
        score += 30
        reasons.append("Very high total sales")
    elif total_sales >= 20000:
        score += 20
        reasons.append("High total sales")
    elif total_sales >= 10000:
        score += 10
        reasons.append("Good total sales")

    if total_transactions >= 20:
        score += 20
        reasons.append("Very frequent transactions")
    elif total_transactions >= 10:
        score += 12
        reasons.append("Frequent transactions")
    elif total_transactions >= 5:
        score += 6
        reasons.append("Regular transactions")

    if estimated_clv >= 50000:
        score += 20
        reasons.append("Very high estimated CLV")
    elif estimated_clv >= 20000:
        score += 12
        reasons.append("High estimated CLV")
    elif estimated_clv >= 10000:
        score += 6
        reasons.append("Good estimated CLV")

    if days_since_last_purchase <= 30:
        score += 10
        reasons.append("Recently active")
    elif days_since_last_purchase <= 90:
        score += 5
        reasons.append("Moderately recent purchase")

    if to_boolean(customer.get("repeat_purchase_flag")):
        score += 15
        reasons.append("Repeat purchaser")

    if app_sessions >= 10 or website_visits >= 20 or wishlist_count >= 5:
        score += 5
        reasons.append("Strong digital engagement")

    return {"score": min(score, 100), "reasons": reasons}


def get_contactability(customer):
    do_not_contact = to_boolean(customer.get("do_not_contact"))
    channels = []
    if not do_not_contact:
        if to_boolean(customer.get("whatsapp_consent")):
            channels.append("WhatsApp")
        if to_boolean(customer.get("sms_consent")):
            channels.append("SMS")
        if to_boolean(customer.get("email_consent")):
            channels.append("Email")
        if to_boolean(customer.get("app_notification_consent")):
            channels.append("App")
    return {
        "contact_allowed": not do_not_contact and bool(channels),
        "do_not_contact": do_not_contact,
        "available_channels": channels,
    }


def calculate_loyalty_recommendation(customer, rule=None):
    current_tier = normalize_tier(customer.get("membership_tier"))
    membership_status = str(customer.get("membership_status") or "Non-member").strip()
    potential_score = to_integer(customer.get("potential_member_score"))
    score_result = calculate_upgrade_score(customer)
    upgrade_score = score_result["score"]
    reasons = list(score_result["reasons"])
    contactability = get_contactability(customer)

    selected_rule = rule if rule is not None else get_tier_rule(current_tier)
    next_tier = selected_rule.get("next_tier") if selected_rule else None
    minimum_score = (
        to_integer(selected_rule.get("minimum_recommendation_score"), 100)
        if selected_rule else 100
    )

    recommendation_flag = False
    recommendation_label = ""
    loyalty_segment = ""
    recommended_action = ""
    is_non_member = current_tier == "Non-member" or membership_status.lower() in {
        "non-member", "non member", "nonmember", "inactive", ""
    }

    if is_non_member:
        if potential_score >= 70:
            loyalty_segment = "High Potential Member"
            recommendation_flag = True
            recommendation_label = "Strong candidate for membership advertising"
            recommended_action = "Promote Silver, Gold or Platinum membership"
        elif potential_score >= 50:
            loyalty_segment = "Medium Potential Member"
            recommendation_flag = True
            recommendation_label = "Moderate membership conversion opportunity"
            recommended_action = "Send educational membership benefits"
        else:
            loyalty_segment = "Low Potential Member"
            recommendation_label = "Low current membership propensity"
            recommended_action = "Continue engagement and monitor behaviour"
    elif current_tier == "Silver":
        if upgrade_score >= minimum_score:
            loyalty_segment = "Silver-to-Gold Recommended"
            recommendation_flag = True
            recommendation_label = "Recommended for Gold membership campaign"
            recommended_action = "Promote Gold benefits and early access"
        else:
            loyalty_segment = "Silver Member"
            recommendation_label = "Continue Silver member engagement"
            recommended_action = "Promote Silver benefits and points usage"
    elif current_tier == "Gold":
        if upgrade_score >= minimum_score:
            loyalty_segment = "Gold-to-Platinum Recommended"
            recommendation_flag = True
            recommendation_label = "Recommended for Platinum membership campaign"
            recommended_action = "Promote Platinum pre-launch and premium benefits"
        else:
            loyalty_segment = "Gold Member"
            recommendation_label = "Continue Gold member engagement"
            recommended_action = "Promote Gold benefits and bonus points"
    else:
        loyalty_segment = "Top-Tier Platinum"
        recommendation_label = "Top membership tier"
        recommended_action = "Focus on retention, premium service and VIP access"

    if current_tier != "Non-member" and str(customer.get("churn_risk_level") or "").lower() == "high":
        loyalty_segment = "Loyal but High Churn Risk"
        recommended_action = "Prioritize retention and customer service outreach"
        reasons.append("High churn risk")

    if contactability["do_not_contact"]:
        communication_status = "Recommendation available but marketing contact blocked"
    elif not contactability["available_channels"]:
        communication_status = "No approved communication channel"
    else:
        communication_status = "Contact allowed through approved channels"

    return {
        "actual_membership_tier": current_tier,
        "potential_member_score": potential_score,
        "tier_upgrade_score": upgrade_score,
        "recommendation_score_required": minimum_score,
        "recommendation_flag": recommendation_flag,
        "recommended_tier": next_tier,
        "recommendation_label": recommendation_label,
        "loyalty_segment": loyalty_segment,
        "recommended_action": recommended_action,
        "score_reasons": reasons,
        "contact_allowed": contactability["contact_allowed"],
        "do_not_contact": contactability["do_not_contact"],
        "available_channels": contactability["available_channels"],
        "communication_status": communication_status,
    }


def build_loyalty_customer(
    customer,
    rule_map=None,
    benefit_map=None,
    include_tier_details=False,
):
    if not customer:
        return None

    tier = normalize_tier(customer.get("membership_tier"))
    rule = rule_map.get(tier) if rule_map is not None else None
    recommendation = calculate_loyalty_recommendation(customer, rule=rule)
    points_earned = to_integer(customer.get("points_earned"))
    points_redeemed = to_integer(customer.get("points_redeemed"))
    points_balance = to_integer(customer.get("points_balance"))

    result = dict(customer)
    result.update(recommendation)
    result.update({
        "points_earned": points_earned,
        "points_redeemed": points_redeemed,
        "points_balance": points_balance,
        "redeemable_value": round(points_balance * 0.10, 2),
    })

    if include_tier_details:
        if rule is None:
            rule = get_tier_rule(tier)
        benefits = (
            benefit_map.get(tier, [])
            if benefit_map is not None
            else get_tier_benefits(tier)
        )
        result["tier_rule"] = rule
        result["benefits"] = benefits

    return result


def to_float(value, default=0.0):
    return to_number(value, default)
