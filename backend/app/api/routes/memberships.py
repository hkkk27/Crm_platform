# # import uuid

# # from fastapi import APIRouter, Depends, HTTPException

# # from app.core.security import get_current_user, require_permission
# # from app.db.sqlite_client import execute_query, fetch_all, fetch_one
# # from app.services.audit_service import create_audit_log
# # from app.services.loyalty_service import (
# #     build_loyalty_customer,
# #     calculate_points_for_purchase,
# #     get_all_benefits,
# #     get_all_tier_rules,
# #     normalize_tier,
# # )
# # from app.services.cache_service import cache


# # router = APIRouter(
# #     prefix="/memberships",
# #     tags=["Memberships"],
# # )


# # CUSTOMER_LOYALTY_FIELDS = """
# #     customer_id,
# #     crm_customer_key,
# #     customer_name,
# #     phone_number,
# #     masked_phone_number,
# #     email,
# #     masked_email,
# #     customer_city,
# #     customer_state,
# #     product_category,
# #     primary_shopping_channel,
# #     membership_status,
# #     membership_tier,
# #     points_earned,
# #     points_redeemed,
# #     points_balance,
# #     membership_expiry_date,
# #     upgrade_eligibility,
# #     total_sales,
# #     total_transactions,
# #     total_items_purchased,
# #     avg_transaction_value,
# #     purchase_frequency,
# #     days_since_last_purchase,
# #     last_purchase_date,
# #     online_purchases,
# #     in_store_purchases,
# #     app_sessions_30d,
# #     website_visits,
# #     wishlist_count,
# #     repeat_purchase_flag,
# #     customer_segment,
# #     potential_member_score,
# #     churn_risk_level,
# #     estimated_clv,
# #     recommendation_reason_codes,
# #     whatsapp_consent,
# #     sms_consent,
# #     email_consent,
# #     app_notification_consent,
# #     personalization_consent,
# #     do_not_contact,
# #     preferred_campaign_channel
# # """


# # def get_customer_row(customer_id: str):
# #     return fetch_one(
# #         f"""
# #         SELECT
# #             {CUSTOMER_LOYALTY_FIELDS}
# #         FROM customers_360
# #         WHERE CAST(customer_id AS TEXT) = ?
# #         """,
# #         (str(customer_id),),
# #     )


# # def to_int(value, default=0):
# #     try:
# #         if value is None or value == "":
# #             return default
# #         return int(float(value))
# #     except (TypeError, ValueError):
# #         return default


# # def to_float(value, default=0.0):
# #     try:
# #         if value is None or value == "":
# #             return default
# #         return float(value)
# #     except (TypeError, ValueError):
# #         return default


# # # -------------------------------------------------------------------
# # # Fixed routes must remain above the dynamic /{customer_id} GET route.
# # # -------------------------------------------------------------------


# # @router.get("")
# # def get_membership_list(user=Depends(get_current_user)):
# #     require_permission(user, "loyalty")

# #     rows = fetch_all(
# #         f"""
# #         SELECT
# #             {CUSTOMER_LOYALTY_FIELDS}
# #         FROM customers_360
# #         ORDER BY
# #             CASE LOWER(
# #                 COALESCE(
# #                     membership_tier,
# #                     ''
# #                 )
# #             )
# #                 WHEN 'platinum' THEN 1
# #                 WHEN 'gold' THEN 2
# #                 WHEN 'silver' THEN 3
# #                 ELSE 4
# #             END,
# #             COALESCE(
# #                 estimated_clv,
# #                 0
# #             ) DESC
# #         LIMIT 100
# #         """
# #     )

# #     # data = [build_loyalty_customer(row) for row in rows]
# #     data = []

# #     for row in rows:
# #         try:
# #             data.append(
# #                 build_loyalty_customer(row)
# #             )
# #         except Exception as e:
# #             print("LOYALTY ERROR:", e)
# #             print("CUSTOMER:", row)
# #             raise

# #     create_audit_log(
# #         user_email=user["sub"],
# #         user_role=user["role"],
# #         action="View membership list",
# #         object_type="Membership",
# #         object_id="ALL",
# #         status="Allowed",
# #         details="Enhanced loyalty membership list viewed",
# #     )

# #     return {
# #         "success": True,
# #         "count": len(data),
# #         "data": data,
# #     }


# # # @router.get("/summary")
# # # def get_loyalty_summary(user=Depends(get_current_user)):
# # #     require_permission(user, "loyalty")

# # #     rows = fetch_all(
# # #         f"""
# # #         SELECT
# # #             {CUSTOMER_LOYALTY_FIELDS}
# # #         FROM customers_360
# # #         """
# # #     )

# # #     customers = [build_loyalty_customer(row) for row in rows]
# # #     total_customers = len(customers)

# # #     active_members = [
# # #         customer
# # #         for customer in customers
# # #         if customer.get("actual_membership_tier") != "Non-member"
# # #     ]

# # #     potential_members = [
# # #         customer
# # #         for customer in customers
# # #         if "Potential Member" in str(customer.get("loyalty_segment") or "")
# # #     ]

# # #     upgrade_recommended = [
# # #         customer
# # #         for customer in customers
# # #         if customer.get("recommendation_flag")
# # #         and customer.get("actual_membership_tier") in ["Silver", "Gold"]
# # #     ]

# # #     contactable_recommendations = [
# # #         customer
# # #         for customer in customers
# # #         if customer.get("recommendation_flag")
# # #         and customer.get("contact_allowed")
# # #     ]

# # #     total_points_earned = sum(
# # #         to_int(customer.get("points_earned")) for customer in customers
# # #     )
# # #     total_points_redeemed = sum(
# # #         to_int(customer.get("points_redeemed")) for customer in customers
# # #     )
# # #     total_points_balance = sum(
# # #         to_int(customer.get("points_balance")) for customer in customers
# # #     )
# # #     member_sales = sum(
# # #         to_float(customer.get("total_sales")) for customer in active_members
# # #     )

# # #     tier_distribution = {}
# # #     for customer in customers:
# # #         tier = customer.get("actual_membership_tier") or "Non-member"
# # #         tier_distribution[tier] = tier_distribution.get(tier, 0) + 1

# # #     return {
# # #         "success": True,
# # #         "summary": {
# # #             "total_customers": total_customers,
# # #             "active_members": len(active_members),
# # #             "non_members": total_customers - len(active_members),
# # #             "potential_members": len(potential_members),
# # #             "upgrade_recommended": len(upgrade_recommended),
# # #             "contactable_recommendations": len(contactable_recommendations),
# # #             "total_points_earned": total_points_earned,
# # #             "total_points_redeemed": total_points_redeemed,
# # #             "total_points_balance": total_points_balance,
# # #             "outstanding_points_value": round(total_points_balance * 0.10, 2),
# # #             "member_sales": round(member_sales, 2),
# # #         },
# # #         "tier_distribution": [
# # #             {"tier": tier, "count": count}
# # #             for tier, count in tier_distribution.items()
# # #         ],
# # #     }

# # @router.get("/summary")
# # def get_loyalty_summary(
# #     user=Depends(get_current_user),
# # ):
# #     require_permission(user, "loyalty")

# #     cached_response = cache.get(
# #         "loyalty:summary"
# #     )

# #     if cached_response is not None:
# #         return cached_response

# #     total_customers_row = fetch_one("""
# #     SELECT COUNT(*) AS count
# #     FROM customers_360
# #     """)

# #     total_customers = int(
# #         total_customers_row.get("count", 0)
# #     )

# #     active_members_row = fetch_one("""
# #     SELECT COUNT(*) AS count
# #     FROM customers_360
# #     WHERE LOWER(
# #         COALESCE(membership_tier, 'non-member')
# #     ) != 'non-member'
# #     """)

# #     active_members = int(
# #         active_members_row.get("count", 0)
# #     )

# #     potential_members_row = fetch_one("""
# #     SELECT COUNT(*) AS count
# #     FROM customers_360
# #     WHERE COALESCE(
# #         potential_member_score,
# #         0
# #     ) >= 50
# #     """)

# #     potential_members = int(
# #         potential_members_row.get("count", 0)
# #     )

# #     points_row = fetch_one("""
# #     SELECT
# #         COALESCE(
# #             SUM(points_earned),
# #             0
# #         ) AS earned,
# #         COALESCE(
# #             SUM(points_redeemed),
# #             0
# #         ) AS redeemed,
# #         COALESCE(
# #             SUM(points_balance),
# #             0
# #         ) AS balance
# #     FROM customers_360
# #     """)

# #     member_sales_row = fetch_one("""
# #     SELECT
# #         COALESCE(
# #             SUM(total_sales),
# #             0
# #         ) AS sales
# #     FROM customers_360
# #     WHERE LOWER(
# #         COALESCE(
# #             membership_tier,
# #             'non-member'
# #         )
# #     ) != 'non-member'
# #     """)

# #     tier_distribution = fetch_all("""
# #     SELECT
# #         COALESCE(
# #             membership_tier,
# #             'Non-member'
# #         ) AS tier,
# #         COUNT(*) AS count
# #     FROM customers_360
# #     GROUP BY membership_tier
# #     ORDER BY count DESC
# #     """)

# #     return {
# #         "success": True,
# #         "summary": {
# #             "total_customers": total_customers,
# #             "active_members": active_members,
# #             "non_members":
# #                 total_customers - active_members,

# #             "potential_members":
# #                 potential_members,

# #             "upgrade_recommended": 0,

# #             "contactable_recommendations": 0,

# #             "total_points_earned":
# #                 int(points_row.get("earned", 0)),

# #             "total_points_redeemed":
# #                 int(points_row.get("redeemed", 0)),

# #             "total_points_balance":
# #                 int(points_row.get("balance", 0)),

# #             "outstanding_points_value":
# #                 round(
# #                     float(
# #                         points_row.get(
# #                             "balance",
# #                             0
# #                         )
# #                     ) * 0.10,
# #                     2
# #                 ),

# #             "member_sales":
# #                 round(
# #                     float(
# #                         member_sales_row.get(
# #                             "sales",
# #                             0
# #                         )
# #                     ),
# #                     2
# #                 )
# #         },
# #         "tier_distribution": tier_distribution
# #     }


# # # @router.get("/rules")
# # # def get_loyalty_rules(user=Depends(get_current_user)):
# # #     require_permission(user, "loyalty")
# # #     rules = get_all_tier_rules()
# # #     return {
# # #         "success": True,
# # #         "count": len(rules),
# # #         "data": rules,
# # #     }

# # @router.get("/rules")
# # def get_loyalty_rules(
# #     user=Depends(get_current_user),
# # ):
# #     require_permission(user, "loyalty")

# #     cached_response = cache.get(
# #         "loyalty:rules"
# #     )

# #     if cached_response is not None:
# #         return cached_response

# #     rules = get_all_tier_rules()

# #     response = {
# #         "success": True,
# #         "count": len(rules),
# #         "data": rules,
# #     }

# #     cache.set(
# #         "loyalty:rules",
# #         response,
# #         ttl_seconds=600,
# #     )

# #     return response

# # # @router.get("/benefits")
# # # def get_loyalty_benefits(user=Depends(get_current_user)):
# # #     require_permission(user, "loyalty")
# # #     benefits = get_all_benefits()
# # #     return {
# # #         "success": True,
# # #         "count": len(benefits),
# # #         "data": benefits,
# # #     }
# # @router.get("/rules")
# # def get_loyalty_rules(
# #     user=Depends(get_current_user),
# # ):
# #     require_permission(user, "loyalty")

# #     cached_response = cache.get(
# #         "loyalty:rules"
# #     )

# #     if cached_response is not None:
# #         return cached_response

# #     rules = get_all_tier_rules()

# #     response = {
# #         "success": True,
# #         "count": len(rules),
# #         "data": rules,
# #     }

# #     cache.set(
# #         "loyalty:rules",
# #         response,
# #         ttl_seconds=600,
# #     )

# #     return response

# # @router.get("/segments/potential-members")
# # def get_potential_members(user=Depends(get_current_user)):
# #     require_permission(user, "loyalty")

# #     rows = fetch_all(
# #         f"""
# #         SELECT
# #             {CUSTOMER_LOYALTY_FIELDS}
# #         FROM customers_360
# #         WHERE LOWER(TRIM(COALESCE(membership_status, ''))) IN (
# #             'non-member',
# #             'non member',
# #             ''
# #         )
# #         OR LOWER(TRIM(COALESCE(membership_tier, ''))) IN (
# #             'non-member',
# #             'non member',
# #             ''
# #         )
# #         ORDER BY COALESCE(potential_member_score, 0) DESC
# #         LIMIT 100
# #         """
# #     )

# #     data = [build_loyalty_customer(row) for row in rows]

# #     create_audit_log(
# #         user_email=user["sub"],
# #         user_role=user["role"],
# #         action="View potential members",
# #         object_type="Membership",
# #         object_id="POTENTIAL_MEMBERS",
# #         status="Allowed",
# #         details="Potential member recommendation list viewed",
# #     )

# #     return {
# #         "success": True,
# #         "count": len(data),
# #         "data": data,
# #     }


# # @router.get("/segments/upgrade-eligible")
# # def get_upgrade_recommended_customers(user=Depends(get_current_user)):
# #     require_permission(user, "loyalty")

# #     rows = fetch_all(
# #         f"""
# #         SELECT
# #             {CUSTOMER_LOYALTY_FIELDS}
# #         FROM customers_360
# #         WHERE LOWER(TRIM(COALESCE(membership_tier, ''))) IN (
# #             'silver',
# #             'gold'
# #         )
# #         LIMIT 50
# #         """
# #     )

# #     evaluated = [build_loyalty_customer(row) for row in rows]
# #     recommended = [
# #         customer
# #         for customer in evaluated
# #         if customer.get("recommendation_flag")
# #     ]
# #     recommended.sort(
# #         key=lambda customer: to_int(customer.get("tier_upgrade_score")),
# #         reverse=True,
# #     )

# #     create_audit_log(
# #         user_email=user["sub"],
# #         user_role=user["role"],
# #         action="View upgrade recommended customers",
# #         object_type="Membership",
# #         object_id="UPGRADE_RECOMMENDED",
# #         status="Allowed",
# #         details=(
# #             "Customers recommended for higher-tier membership advertising viewed"
# #         ),
# #     )

# #     return {
# #         "success": True,
# #         "count": len(recommended),
# #         "data": recommended,
# #     }


# # @router.get("/segments")
# # def get_loyalty_segments(user=Depends(get_current_user)):
# #     require_permission(user, "loyalty")

# #     rows = fetch_all(
# #         f"""
# #         SELECT
# #             {CUSTOMER_LOYALTY_FIELDS}
# #         FROM customers_360
# #         LIMIT 50
# #         """
# #     )

# #     customers = [build_loyalty_customer(row) for row in rows]
# #     segment_map = {}

# #     for customer in customers:
# #         segment = customer.get("loyalty_segment") or "Unclassified"

# #         if segment not in segment_map:
# #             segment_map[segment] = {
# #                 "segment_name": segment,
# #                 "customer_count": 0,
# #                 "contactable_count": 0,
# #                 "recommended_action": customer.get("recommended_action") or "",
# #             }

# #         segment_map[segment]["customer_count"] += 1

# #         if customer.get("contact_allowed"):
# #             segment_map[segment]["contactable_count"] += 1

# #     return {
# #         "success": True,
# #         "count": len(segment_map),
# #         "data": list(segment_map.values()),
# #     }


# # @router.get("/segments/{segment_name}/customers")
# # def get_customers_by_loyalty_segment(
# #     segment_name: str,
# #     user=Depends(get_current_user),
# # ):
# #     require_permission(user, "loyalty")

# #     rows = fetch_all(
# #         f"""
# #         SELECT
# #             {CUSTOMER_LOYALTY_FIELDS}
# #         FROM customers_360
# #         LIMIT 50
# #         """
# #     )

# #     selected_customers = []

# #     for row in rows:
# #         customer = build_loyalty_customer(row)
# #         if str(customer.get("loyalty_segment") or "").lower() == segment_name.lower():
# #             selected_customers.append(customer)

# #     return {
# #         "success": True,
# #         "segment_name": segment_name,
# #         "count": len(selected_customers),
# #         "data": selected_customers,
# #     }


# # # -------------------------------------------------------------------
# # # Customer actions: direct membership purchase, earn, and redeem.
# # # A customer may purchase any valid membership tier directly.
# # # Internal recommendation scores do not block purchase.
# # # -------------------------------------------------------------------


# # @router.post("/{customer_id}/purchase")
# # def purchase_membership(
# #     customer_id: str,
# #     payload: dict,
# #     user=Depends(get_current_user),
# # ):
# #     require_permission(user, "loyalty")

# #     customer = get_customer_row(customer_id)
# #     if not customer:
# #         raise HTTPException(status_code=404, detail="Customer not found")

# #     requested_tier = str(payload.get("tier") or "").strip()
# #     tier = normalize_tier(requested_tier)

# #     if tier not in ["Silver", "Gold", "Platinum"]:
# #         raise HTTPException(
# #             status_code=400,
# #             detail="Invalid membership tier. Use Silver, Gold, or Platinum.",
# #         )

# #     old_tier = normalize_tier(customer.get("membership_tier"))
# #     history_id = "LTH-" + str(uuid.uuid4())[:8].upper()
# #     reason = payload.get("reason") or f"Customer purchased {tier} membership"

# #     execute_query(
# #         """
# #         UPDATE customers_360
# #         SET
# #             membership_status = 'Active',
# #             membership_tier = ?,
# #             membership_expiry_date = DATE('now', '+1 year')
# #         WHERE CAST(customer_id AS TEXT) = ?
# #         """,
# #         (tier, str(customer_id)),
# #     )

# #     execute_query(
# #         """
# #         INSERT INTO loyalty_tier_history (
# #             history_id,
# #             customer_id,
# #             old_tier,
# #             new_tier,
# #             change_type,
# #             change_reason,
# #             recommendation_score,
# #             changed_by
# #         )
# #         VALUES (?, ?, ?, ?, ?, ?, ?, ?)
# #         """,
# #         (
# #             history_id,
# #             str(customer_id),
# #             old_tier,
# #             tier,
# #             "Purchased",
# #             reason,
# #             0,
# #             user["sub"],
# #         ),
# #     )

# #     create_audit_log(
# #         user_email=user["sub"],
# #         user_role=user["role"],
# #         action="Purchase membership",
# #         object_type="Membership",
# #         object_id=str(customer_id),
# #         status="Allowed",
# #         details=f"Membership changed from {old_tier} to {tier}",
# #     )

# #     updated_customer = get_customer_row(customer_id)

# #     return {
# #         "success": True,
# #         "message": f"{tier} membership activated successfully",
# #         "history_id": history_id,
# #         "data": build_loyalty_customer(updated_customer),
# #     }


# # @router.post("/{customer_id}/earn")
# # def earn_loyalty_points(
# #     customer_id: str,
# #     payload: dict,
# #     user=Depends(get_current_user),
# # ):
# #     require_permission(user, "loyalty")

# #     customer = get_customer_row(customer_id)
# #     if not customer:
# #         raise HTTPException(status_code=404, detail="Customer not found")

# #     order_amount = to_float(payload.get("order_amount"))
# #     if order_amount <= 0:
# #         raise HTTPException(
# #             status_code=400,
# #             detail="order_amount must be greater than 0",
# #         )

# #     calculation = calculate_points_for_purchase(
# #         customer.get("membership_tier"),
# #         order_amount,
# #     )
# #     points_earned = to_int(calculation.get("points_earned"))
# #     balance_before = to_int(customer.get("points_balance"))
# #     balance_after = balance_before + points_earned
# #     transaction_id = "LPT-" + str(uuid.uuid4())[:8].upper()

# #     source_reference_id = (
# #         payload.get("order_id")
# #         or payload.get("source_reference_id")
# #         or ""
# #     )

# #     execute_query(
# #         """
# #         UPDATE customers_360
# #         SET
# #             points_earned = COALESCE(points_earned, 0) + ?,
# #             points_balance = ?
# #         WHERE CAST(customer_id AS TEXT) = ?
# #         """,
# #         (points_earned, balance_after, str(customer_id)),
# #     )

# #     execute_query(
# #         """
# #         INSERT INTO loyalty_point_transactions (
# #             transaction_id,
# #             customer_id,
# #             transaction_type,
# #             source_type,
# #             source_reference_id,
# #             order_amount,
# #             points_change,
# #             balance_before,
# #             balance_after,
# #             description,
# #             created_by
# #         )
# #         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
# #         """,
# #         (
# #             transaction_id,
# #             str(customer_id),
# #             "Earn",
# #             "Purchase",
# #             source_reference_id,
# #             order_amount,
# #             points_earned,
# #             balance_before,
# #             balance_after,
# #             f"Earned {points_earned} points for purchase of Rs. {order_amount}",
# #             user["sub"],
# #         ),
# #     )

# #     create_audit_log(
# #         user_email=user["sub"],
# #         user_role=user["role"],
# #         action="Earn loyalty points",
# #         object_type="LoyaltyPoints",
# #         object_id=transaction_id,
# #         status="Allowed",
# #         details=f"Customer {customer_id} earned {points_earned} points",
# #     )

# #     return {
# #         "success": True,
# #         "message": "Points added successfully",
# #         "transaction_id": transaction_id,
# #         "calculation": calculation,
# #         "balance_before": balance_before,
# #         "balance_after": balance_after,
# #     }


# # @router.post("/{customer_id}/redeem")
# # def redeem_loyalty_points(
# #     customer_id: str,
# #     payload: dict,
# #     user=Depends(get_current_user),
# # ):
# #     require_permission(user, "loyalty")

# #     customer = get_customer_row(customer_id)
# #     if not customer:
# #         raise HTTPException(status_code=404, detail="Customer not found")

# #     points = to_int(payload.get("points"))
# #     if points < 100:
# #         raise HTTPException(
# #             status_code=400,
# #             detail="Minimum redemption is 100 points",
# #         )

# #     balance_before = to_int(customer.get("points_balance"))
# #     if points > balance_before:
# #         raise HTTPException(status_code=400, detail="Insufficient points balance")

# #     # Conversion rule: 100 points = Rs. 10.
# #     discount_value = round(points * 0.10, 2)
# #     order_amount = to_float(payload.get("order_amount"))

# #     if order_amount > 0 and discount_value > order_amount * 0.20:
# #         raise HTTPException(
# #             status_code=400,
# #             detail="Point redemption cannot exceed 20 percent of order value",
# #         )

# #     balance_after = balance_before - points
# #     redemption_id = "LRD-" + str(uuid.uuid4())[:8].upper()
# #     transaction_id = "LPT-" + str(uuid.uuid4())[:8].upper()
# #     order_id = payload.get("order_id") or ""

# #     execute_query(
# #         """
# #         UPDATE customers_360
# #         SET
# #             points_redeemed = COALESCE(points_redeemed, 0) + ?,
# #             points_balance = ?
# #         WHERE CAST(customer_id AS TEXT) = ?
# #         """,
# #         (points, balance_after, str(customer_id)),
# #     )

# #     execute_query(
# #         """
# #         INSERT INTO loyalty_redemptions (
# #             redemption_id,
# #             customer_id,
# #             points_redeemed,
# #             discount_value,
# #             order_id,
# #             status,
# #             processed_by
# #         )
# #         VALUES (?, ?, ?, ?, ?, ?, ?)
# #         """,
# #         (
# #             redemption_id,
# #             str(customer_id),
# #             points,
# #             discount_value,
# #             order_id,
# #             "Completed",
# #             user["sub"],
# #         ),
# #     )

# #     execute_query(
# #         """
# #         INSERT INTO loyalty_point_transactions (
# #             transaction_id,
# #             customer_id,
# #             transaction_type,
# #             source_type,
# #             source_reference_id,
# #             order_amount,
# #             points_change,
# #             balance_before,
# #             balance_after,
# #             description,
# #             created_by
# #         )
# #         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
# #         """,
# #         (
# #             transaction_id,
# #             str(customer_id),
# #             "Redeem",
# #             "Order Discount",
# #             order_id,
# #             order_amount,
# #             -points,
# #             balance_before,
# #             balance_after,
# #             f"Redeemed {points} points for Rs. {discount_value} discount",
# #             user["sub"],
# #         ),
# #     )

# #     create_audit_log(
# #         user_email=user["sub"],
# #         user_role=user["role"],
# #         action="Redeem loyalty points",
# #         object_type="LoyaltyRedemption",
# #         object_id=redemption_id,
# #         status="Allowed",
# #         details=f"Customer {customer_id} redeemed {points} points",
# #     )

# #     return {
# #         "success": True,
# #         "message": "Points redeemed successfully",
# #         "redemption_id": redemption_id,
# #         "transaction_id": transaction_id,
# #         "points_redeemed": points,
# #         "discount_value": discount_value,
# #         "balance_before": balance_before,
# #         "balance_after": balance_after,
# #     }


# # # -------------------------------------------------------------------
# # # Dynamic GET route must stay last so it does not capture /summary,
# # # /rules, /benefits, or /segments paths as customer IDs.
# # # -------------------------------------------------------------------


# # @router.get("/{customer_id}")
# # def get_customer_membership(
# #     customer_id: str,
# #     user=Depends(get_current_user),
# # ):
# #     require_permission(user, "loyalty")

# #     customer = get_customer_row(customer_id)
# #     if not customer:
# #         raise HTTPException(
# #             status_code=404,
# #             detail="Membership record not found",
# #         )

# #     loyalty_data = build_loyalty_customer(customer)

# #     transactions = fetch_all(
# #         """
# #         SELECT *
# #         FROM loyalty_point_transactions
# #         WHERE customer_id = ?
# #         ORDER BY created_at DESC
# #         LIMIT 100
# #         """,
# #         (str(customer_id),),
# #     )

# #     redemptions = fetch_all(
# #         """
# #         SELECT *
# #         FROM loyalty_redemptions
# #         WHERE customer_id = ?
# #         ORDER BY created_at DESC
# #         LIMIT 100
# #         """,
# #         (str(customer_id),),
# #     )

# #     tier_history = fetch_all(
# #         """
# #         SELECT *
# #         FROM loyalty_tier_history
# #         WHERE customer_id = ?
# #         ORDER BY changed_at DESC
# #         LIMIT 100
# #         """,
# #         (str(customer_id),),
# #     )

# #     create_audit_log(
# #         user_email=user["sub"],
# #         user_role=user["role"],
# #         action="View customer membership",
# #         object_type="Membership",
# #         object_id=str(customer_id),
# #         status="Allowed",
# #         details="Enhanced customer loyalty detail viewed",
# #     )

# #     response = {
# #         "success": True,
# #         "summary": {
# #             "total_customers": total_customers,
# #             "active_members": active_members,
# #             "non_members":
# #                 total_customers - active_members,
# #             "potential_members":
# #                 potential_members,
# #             "total_points_earned":
# #                 int(points_row.get("earned", 0)),
# #             "total_points_redeemed":
# #                 int(points_row.get("redeemed", 0)),
# #             "total_points_balance":
# #                 int(points_row.get("balance", 0)),
# #             "outstanding_points_value":
# #                 round(
# #                     float(
# #                         points_row.get("balance", 0)
# #                     ) * 0.10,
# #                     2,
# #                 ),
# #             "member_sales":
# #                 round(
# #                     float(
# #                         member_sales_row.get(
# #                             "sales",
# #                             0,
# #                         )
# #                     ),
# #                     2,
# #                 ),
# #         },
# #         "tier_distribution":
# #             tier_distribution,
# #     }

# #     cache.set(
# #         "loyalty:summary",
# #         response,
# #         ttl_seconds=60,
# #     )

# #     return response
# import uuid

# from fastapi import APIRouter, Depends, HTTPException

# from app.core.security import get_current_user, require_permission
# from app.db.sqlite_client import execute_query, fetch_all, fetch_one
# from app.services.audit_service import create_audit_log
# from app.services.loyalty_service import (
#     build_loyalty_customer,
#     calculate_points_for_purchase,
#     get_all_benefits,
#     get_all_tier_rules,
#     normalize_tier,
# )
# from app.services.cache_service import cache


# router = APIRouter(
#     prefix="/memberships",
#     tags=["Memberships"],
# )


# CUSTOMER_LOYALTY_FIELDS = """
#     customer_id,
#     crm_customer_key,
#     customer_name,
#     phone_number,
#     masked_phone_number,
#     email,
#     masked_email,
#     customer_city,
#     customer_state,
#     product_category,
#     primary_shopping_channel,
#     membership_status,
#     membership_tier,
#     points_earned,
#     points_redeemed,
#     points_balance,
#     membership_expiry_date,
#     upgrade_eligibility,
#     total_sales,
#     total_transactions,
#     total_items_purchased,
#     avg_transaction_value,
#     purchase_frequency,
#     days_since_last_purchase,
#     last_purchase_date,
#     online_purchases,
#     in_store_purchases,
#     app_sessions_30d,
#     website_visits,
#     wishlist_count,
#     repeat_purchase_flag,
#     customer_segment,
#     potential_member_score,
#     churn_risk_level,
#     estimated_clv,
#     recommendation_reason_codes,
#     whatsapp_consent,
#     sms_consent,
#     email_consent,
#     app_notification_consent,
#     personalization_consent,
#     do_not_contact,
#     preferred_campaign_channel
# """


# def get_customer_row(customer_id: str):
#     return fetch_one(
#         f"""
#         SELECT
#             {CUSTOMER_LOYALTY_FIELDS}
#         FROM customers_360
#         WHERE CAST(customer_id AS TEXT) = ?
#         """,
#         (str(customer_id),),
#     )


# def to_int(value, default=0):
#     try:
#         if value is None or value == "":
#             return default
#         return int(float(value))
#     except (TypeError, ValueError):
#         return default


# def to_float(value, default=0.0):
#     try:
#         if value is None or value == "":
#             return default
#         return float(value)
#     except (TypeError, ValueError):
#         return default


# # -------------------------------------------------------------------
# # Fixed routes must remain above the dynamic /{customer_id} GET route.
# # -------------------------------------------------------------------


# @router.get("")
# def get_membership_list(user=Depends(get_current_user)):
#     require_permission(user, "loyalty")

#     rows = fetch_all(
#         f"""
#         SELECT
#             {CUSTOMER_LOYALTY_FIELDS}
#         FROM customers_360
#         ORDER BY
#             CASE LOWER(
#                 COALESCE(
#                     membership_tier,
#                     ''
#                 )
#             )
#                 WHEN 'platinum' THEN 1
#                 WHEN 'gold' THEN 2
#                 WHEN 'silver' THEN 3
#                 ELSE 4
#             END,
#             COALESCE(
#                 estimated_clv,
#                 0
#             ) DESC
#         LIMIT 100
#         """
#     )

#     data = []

#     for row in rows:
#         try:
#             data.append(
#                 build_loyalty_customer(row)
#             )
#         except Exception as error:
#             print("LOYALTY ERROR:", error)
#             print("CUSTOMER:", row)
#             raise

#     create_audit_log(
#         user_email=user["sub"],
#         user_role=user["role"],
#         action="View membership list",
#         object_type="Membership",
#         object_id="ALL",
#         status="Allowed",
#         details="Enhanced loyalty membership list viewed",
#     )

#     return {
#         "success": True,
#         "count": len(data),
#         "data": data,
#     }


# @router.get("/summary")
# def get_loyalty_summary(
#     user=Depends(get_current_user),
# ):
#     require_permission(user, "loyalty")

#     cached_response = cache.get(
#         "loyalty:summary"
#     )

#     if cached_response is not None:
#         return cached_response

#     total_customers_row = fetch_one("""
#     SELECT COUNT(*) AS count
#     FROM customers_360
#     """)

#     total_customers = int(
#         total_customers_row.get("count", 0)
#     )

#     active_members_row = fetch_one("""
#     SELECT COUNT(*) AS count
#     FROM customers_360
#     WHERE LOWER(
#         COALESCE(membership_tier, 'non-member')
#     ) != 'non-member'
#     """)

#     active_members = int(
#         active_members_row.get("count", 0)
#     )

#     potential_members_row = fetch_one("""
#     SELECT COUNT(*) AS count
#     FROM customers_360
#     WHERE COALESCE(
#         potential_member_score,
#         0
#     ) >= 50
#     """)

#     potential_members = int(
#         potential_members_row.get("count", 0)
#     )

#     points_row = fetch_one("""
#     SELECT
#         COALESCE(
#             SUM(points_earned),
#             0
#         ) AS earned,
#         COALESCE(
#             SUM(points_redeemed),
#             0
#         ) AS redeemed,
#         COALESCE(
#             SUM(points_balance),
#             0
#         ) AS balance
#     FROM customers_360
#     """)

#     member_sales_row = fetch_one("""
#     SELECT
#         COALESCE(
#             SUM(total_sales),
#             0
#         ) AS sales
#     FROM customers_360
#     WHERE LOWER(
#         COALESCE(
#             membership_tier,
#             'non-member'
#         )
#     ) != 'non-member'
#     """)

#     tier_distribution = fetch_all("""
#     SELECT
#         COALESCE(
#             membership_tier,
#             'Non-member'
#         ) AS tier,
#         COUNT(*) AS count
#     FROM customers_360
#     GROUP BY membership_tier
#     ORDER BY count DESC
#     """)

#     response = {
#         "success": True,
#         "summary": {
#             "total_customers": total_customers,
#             "active_members": active_members,
#             "non_members": total_customers - active_members,
#             "potential_members": potential_members,
#             "upgrade_recommended": 0,
#             "contactable_recommendations": 0,
#             "total_points_earned": int(
#                 points_row.get("earned", 0)
#             ),
#             "total_points_redeemed": int(
#                 points_row.get("redeemed", 0)
#             ),
#             "total_points_balance": int(
#                 points_row.get("balance", 0)
#             ),
#             "outstanding_points_value": round(
#                 float(
#                     points_row.get("balance", 0)
#                 ) * 0.10,
#                 2,
#             ),
#             "member_sales": round(
#                 float(
#                     member_sales_row.get(
#                         "sales",
#                         0,
#                     )
#                 ),
#                 2,
#             ),
#         },
#         "tier_distribution": tier_distribution,
#     }

#     cache.set(
#         "loyalty:summary",
#         response,
#         ttl_seconds=60,
#     )

#     return response


# @router.get("/rules")
# def get_loyalty_rules(
#     user=Depends(get_current_user),
# ):
#     require_permission(user, "loyalty")

#     cached_response = cache.get(
#         "loyalty:rules"
#     )

#     if cached_response is not None:
#         return cached_response

#     rules = get_all_tier_rules()

#     response = {
#         "success": True,
#         "count": len(rules),
#         "data": rules,
#     }

#     cache.set(
#         "loyalty:rules",
#         response,
#         ttl_seconds=600,
#     )

#     return response


# @router.get("/benefits")
# def get_loyalty_benefits(
#     user=Depends(get_current_user),
# ):
#     require_permission(user, "loyalty")

#     cached_response = cache.get(
#         "loyalty:benefits"
#     )

#     if cached_response is not None:
#         return cached_response

#     benefits = get_all_benefits()

#     response = {
#         "success": True,
#         "count": len(benefits),
#         "data": benefits,
#     }

#     cache.set(
#         "loyalty:benefits",
#         response,
#         ttl_seconds=600,
#     )

#     return response


# @router.get("/segments/potential-members")
# def get_potential_members(user=Depends(get_current_user)):
#     require_permission(user, "loyalty")

#     rows = fetch_all(
#         f"""
#         SELECT
#             {CUSTOMER_LOYALTY_FIELDS}
#         FROM customers_360
#         WHERE LOWER(TRIM(COALESCE(membership_status, ''))) IN (
#             'non-member',
#             'non member',
#             ''
#         )
#         OR LOWER(TRIM(COALESCE(membership_tier, ''))) IN (
#             'non-member',
#             'non member',
#             ''
#         )
#         ORDER BY COALESCE(potential_member_score, 0) DESC
#         LIMIT 100
#         """
#     )

#     data = [build_loyalty_customer(row) for row in rows]

#     create_audit_log(
#         user_email=user["sub"],
#         user_role=user["role"],
#         action="View potential members",
#         object_type="Membership",
#         object_id="POTENTIAL_MEMBERS",
#         status="Allowed",
#         details="Potential member recommendation list viewed",
#     )

#     return {
#         "success": True,
#         "count": len(data),
#         "data": data,
#     }


# @router.get("/segments/upgrade-eligible")
# def get_upgrade_recommended_customers(user=Depends(get_current_user)):
#     require_permission(user, "loyalty")

#     rows = fetch_all(
#         f"""
#         SELECT
#             {CUSTOMER_LOYALTY_FIELDS}
#         FROM customers_360
#         WHERE LOWER(TRIM(COALESCE(membership_tier, ''))) IN (
#             'silver',
#             'gold'
#         )
#         LIMIT 50
#         """
#     )

#     evaluated = [build_loyalty_customer(row) for row in rows]

#     recommended = [
#         customer
#         for customer in evaluated
#         if customer.get("recommendation_flag")
#     ]

#     recommended.sort(
#         key=lambda customer: to_int(
#             customer.get("tier_upgrade_score")
#         ),
#         reverse=True,
#     )

#     create_audit_log(
#         user_email=user["sub"],
#         user_role=user["role"],
#         action="View upgrade recommended customers",
#         object_type="Membership",
#         object_id="UPGRADE_RECOMMENDED",
#         status="Allowed",
#         details=(
#             "Customers recommended for higher-tier membership advertising viewed"
#         ),
#     )

#     return {
#         "success": True,
#         "count": len(recommended),
#         "data": recommended,
#     }


# @router.get("/segments")
# def get_loyalty_segments(user=Depends(get_current_user)):
#     require_permission(user, "loyalty")

#     rows = fetch_all(
#         f"""
#         SELECT
#             {CUSTOMER_LOYALTY_FIELDS}
#         FROM customers_360
#         LIMIT 50
#         """
#     )

#     customers = [build_loyalty_customer(row) for row in rows]

#     segment_map = {}

#     for customer in customers:
#         segment = customer.get("loyalty_segment") or "Unclassified"

#         if segment not in segment_map:
#             segment_map[segment] = {
#                 "segment_name": segment,
#                 "customer_count": 0,
#                 "contactable_count": 0,
#                 "recommended_action": customer.get("recommended_action") or "",
#             }

#         segment_map[segment]["customer_count"] += 1

#         if customer.get("contact_allowed"):
#             segment_map[segment]["contactable_count"] += 1

#     return {
#         "success": True,
#         "count": len(segment_map),
#         "data": list(segment_map.values()),
#     }


# @router.get("/segments/{segment_name}/customers")
# def get_customers_by_loyalty_segment(
#     segment_name: str,
#     user=Depends(get_current_user),
# ):
#     require_permission(user, "loyalty")

#     rows = fetch_all(
#         f"""
#         SELECT
#             {CUSTOMER_LOYALTY_FIELDS}
#         FROM customers_360
#         LIMIT 50
#         """
#     )

#     selected_customers = []

#     for row in rows:
#         customer = build_loyalty_customer(row)

#         if str(
#             customer.get("loyalty_segment") or ""
#         ).lower() == segment_name.lower():
#             selected_customers.append(customer)

#     return {
#         "success": True,
#         "segment_name": segment_name,
#         "count": len(selected_customers),
#         "data": selected_customers,
#     }


# # -------------------------------------------------------------------
# # Customer actions: direct membership purchase, earn, and redeem.
# # A customer may purchase any valid membership tier directly.
# # Internal recommendation scores do not block purchase.
# # -------------------------------------------------------------------


# @router.post("/{customer_id}/purchase")
# def purchase_membership(
#     customer_id: str,
#     payload: dict,
#     user=Depends(get_current_user),
# ):
#     require_permission(user, "loyalty")

#     customer = get_customer_row(customer_id)

#     if not customer:
#         raise HTTPException(
#             status_code=404,
#             detail="Customer not found",
#         )

#     requested_tier = str(
#         payload.get("tier") or ""
#     ).strip()

#     tier = normalize_tier(requested_tier)

#     if tier not in ["Silver", "Gold", "Platinum"]:
#         raise HTTPException(
#             status_code=400,
#             detail="Invalid membership tier. Use Silver, Gold, or Platinum.",
#         )

#     old_tier = normalize_tier(
#         customer.get("membership_tier")
#     )

#     history_id = "LTH-" + str(uuid.uuid4())[:8].upper()

#     reason = (
#         payload.get("reason")
#         or f"Customer purchased {tier} membership"
#     )

#     execute_query(
#         """
#         UPDATE customers_360
#         SET
#             membership_status = 'Active',
#             membership_tier = ?,
#             membership_expiry_date = DATE('now', '+1 year')
#         WHERE CAST(customer_id AS TEXT) = ?
#         """,
#         (
#             tier,
#             str(customer_id),
#         ),
#     )

#     execute_query(
#         """
#         INSERT INTO loyalty_tier_history (
#             history_id,
#             customer_id,
#             old_tier,
#             new_tier,
#             change_type,
#             change_reason,
#             recommendation_score,
#             changed_by
#         )
#         VALUES (?, ?, ?, ?, ?, ?, ?, ?)
#         """,
#         (
#             history_id,
#             str(customer_id),
#             old_tier,
#             tier,
#             "Purchased",
#             reason,
#             0,
#             user["sub"],
#         ),
#     )

#     create_audit_log(
#         user_email=user["sub"],
#         user_role=user["role"],
#         action="Purchase membership",
#         object_type="Membership",
#         object_id=str(customer_id),
#         status="Allowed",
#         details=f"Membership changed from {old_tier} to {tier}",
#     )

#     cache.delete(
#         "loyalty:summary"
#     )

#     cache.delete_prefix(
#         "loyalty:customers"
#     )

#     cache.delete_prefix(
#         f"loyalty:customer:{customer_id}"
#     )

#     cache.delete(
#         "dashboard:summary"
#     )

#     updated_customer = get_customer_row(customer_id)

#     return {
#         "success": True,
#         "message": f"{tier} membership activated successfully",
#         "history_id": history_id,
#         "data": build_loyalty_customer(updated_customer),
#     }


# @router.post("/{customer_id}/earn")
# def earn_loyalty_points(
#     customer_id: str,
#     payload: dict,
#     user=Depends(get_current_user),
# ):
#     require_permission(user, "loyalty")

#     customer = get_customer_row(customer_id)

#     if not customer:
#         raise HTTPException(
#             status_code=404,
#             detail="Customer not found",
#         )

#     order_amount = to_float(
#         payload.get("order_amount")
#     )

#     if order_amount <= 0:
#         raise HTTPException(
#             status_code=400,
#             detail="order_amount must be greater than 0",
#         )

#     calculation = calculate_points_for_purchase(
#         customer.get("membership_tier"),
#         order_amount,
#     )

#     points_earned = to_int(
#         calculation.get("points_earned")
#     )

#     balance_before = to_int(
#         customer.get("points_balance")
#     )

#     balance_after = balance_before + points_earned

#     transaction_id = "LPT-" + str(uuid.uuid4())[:8].upper()

#     source_reference_id = (
#         payload.get("order_id")
#         or payload.get("source_reference_id")
#         or ""
#     )

#     execute_query(
#         """
#         UPDATE customers_360
#         SET
#             points_earned = COALESCE(points_earned, 0) + ?,
#             points_balance = ?
#         WHERE CAST(customer_id AS TEXT) = ?
#         """,
#         (
#             points_earned,
#             balance_after,
#             str(customer_id),
#         ),
#     )

#     execute_query(
#         """
#         INSERT INTO loyalty_point_transactions (
#             transaction_id,
#             customer_id,
#             transaction_type,
#             source_type,
#             source_reference_id,
#             order_amount,
#             points_change,
#             balance_before,
#             balance_after,
#             description,
#             created_by
#         )
#         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#         """,
#         (
#             transaction_id,
#             str(customer_id),
#             "Earn",
#             "Purchase",
#             source_reference_id,
#             order_amount,
#             points_earned,
#             balance_before,
#             balance_after,
#             f"Earned {points_earned} points for purchase of Rs. {order_amount}",
#             user["sub"],
#         ),
#     )

#     create_audit_log(
#         user_email=user["sub"],
#         user_role=user["role"],
#         action="Earn loyalty points",
#         object_type="LoyaltyPoints",
#         object_id=transaction_id,
#         status="Allowed",
#         details=f"Customer {customer_id} earned {points_earned} points",
#     )

#     cache.delete(
#         "loyalty:summary"
#     )

#     cache.delete_prefix(
#         f"loyalty:customer:{customer_id}"
#     )

#     cache.delete(
#         "dashboard:summary"
#     )

#     return {
#         "success": True,
#         "message": "Points added successfully",
#         "transaction_id": transaction_id,
#         "calculation": calculation,
#         "balance_before": balance_before,
#         "balance_after": balance_after,
#     }


# @router.post("/{customer_id}/redeem")
# def redeem_loyalty_points(
#     customer_id: str,
#     payload: dict,
#     user=Depends(get_current_user),
# ):
#     require_permission(user, "loyalty")

#     customer = get_customer_row(customer_id)

#     if not customer:
#         raise HTTPException(
#             status_code=404,
#             detail="Customer not found",
#         )

#     points = to_int(
#         payload.get("points")
#     )

#     if points < 100:
#         raise HTTPException(
#             status_code=400,
#             detail="Minimum redemption is 100 points",
#         )

#     balance_before = to_int(
#         customer.get("points_balance")
#     )

#     if points > balance_before:
#         raise HTTPException(
#             status_code=400,
#             detail="Insufficient points balance",
#         )

#     # Conversion rule: 100 points = Rs. 10.
#     discount_value = round(
#         points * 0.10,
#         2,
#     )

#     order_amount = to_float(
#         payload.get("order_amount")
#     )

#     if order_amount > 0 and discount_value > order_amount * 0.20:
#         raise HTTPException(
#             status_code=400,
#             detail="Point redemption cannot exceed 20 percent of order value",
#         )

#     balance_after = balance_before - points

#     redemption_id = "LRD-" + str(uuid.uuid4())[:8].upper()
#     transaction_id = "LPT-" + str(uuid.uuid4())[:8].upper()

#     order_id = payload.get("order_id") or ""

#     execute_query(
#         """
#         UPDATE customers_360
#         SET
#             points_redeemed = COALESCE(points_redeemed, 0) + ?,
#             points_balance = ?
#         WHERE CAST(customer_id AS TEXT) = ?
#         """,
#         (
#             points,
#             balance_after,
#             str(customer_id),
#         ),
#     )

#     execute_query(
#         """
#         INSERT INTO loyalty_redemptions (
#             redemption_id,
#             customer_id,
#             points_redeemed,
#             discount_value,
#             order_id,
#             status,
#             processed_by
#         )
#         VALUES (?, ?, ?, ?, ?, ?, ?)
#         """,
#         (
#             redemption_id,
#             str(customer_id),
#             points,
#             discount_value,
#             order_id,
#             "Completed",
#             user["sub"],
#         ),
#     )

#     execute_query(
#         """
#         INSERT INTO loyalty_point_transactions (
#             transaction_id,
#             customer_id,
#             transaction_type,
#             source_type,
#             source_reference_id,
#             order_amount,
#             points_change,
#             balance_before,
#             balance_after,
#             description,
#             created_by
#         )
#         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#         """,
#         (
#             transaction_id,
#             str(customer_id),
#             "Redeem",
#             "Order Discount",
#             order_id,
#             order_amount,
#             -points,
#             balance_before,
#             balance_after,
#             f"Redeemed {points} points for Rs. {discount_value} discount",
#             user["sub"],
#         ),
#     )

#     create_audit_log(
#         user_email=user["sub"],
#         user_role=user["role"],
#         action="Redeem loyalty points",
#         object_type="LoyaltyRedemption",
#         object_id=redemption_id,
#         status="Allowed",
#         details=f"Customer {customer_id} redeemed {points} points",
#     )

#     cache.delete(
#         "loyalty:summary"
#     )

#     cache.delete_prefix(
#         f"loyalty:customer:{customer_id}"
#     )

#     cache.delete(
#         "dashboard:summary"
#     )

#     return {
#         "success": True,
#         "message": "Points redeemed successfully",
#         "redemption_id": redemption_id,
#         "transaction_id": transaction_id,
#         "points_redeemed": points,
#         "discount_value": discount_value,
#         "balance_before": balance_before,
#         "balance_after": balance_after,
#     }


# # -------------------------------------------------------------------
# # Dynamic GET route must stay last so it does not capture /summary,
# # /rules, /benefits, or /segments paths as customer IDs.
# # -------------------------------------------------------------------


# @router.get("/{customer_id}")
# def get_customer_membership(
#     customer_id: str,
#     user=Depends(get_current_user),
# ):
#     require_permission(user, "loyalty")

#     customer = get_customer_row(customer_id)

#     if not customer:
#         raise HTTPException(
#             status_code=404,
#             detail="Membership record not found",
#         )

#     loyalty_data = build_loyalty_customer(customer)

#     transactions = fetch_all(
#         """
#         SELECT *
#         FROM loyalty_point_transactions
#         WHERE customer_id = ?
#         ORDER BY created_at DESC
#         LIMIT 100
#         """,
#         (str(customer_id),),
#     )

#     redemptions = fetch_all(
#         """
#         SELECT *
#         FROM loyalty_redemptions
#         WHERE customer_id = ?
#         ORDER BY created_at DESC
#         LIMIT 100
#         """,
#         (str(customer_id),),
#     )

#     tier_history = fetch_all(
#         """
#         SELECT *
#         FROM loyalty_tier_history
#         WHERE customer_id = ?
#         ORDER BY changed_at DESC
#         LIMIT 100
#         """,
#         (str(customer_id),),
#     )

#     create_audit_log(
#         user_email=user["sub"],
#         user_role=user["role"],
#         action="View customer membership",
#         object_type="Membership",
#         object_id=str(customer_id),
#         status="Allowed",
#         details="Enhanced customer loyalty detail viewed",
#     )

#     return {
#         "success": True,
#         "data": loyalty_data,
#         "transactions": transactions,
#         "redemptions": redemptions,
#         "tier_history": tier_history,
#     }

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.security import get_current_user, require_permission
from app.db.sqlite_client import execute_query, fetch_all, fetch_one
from app.services.audit_service import create_audit_log
from app.services.cache_service import cache
from app.services.loyalty_service import (
    build_benefit_map,
    build_loyalty_customer,
    build_rule_map,
    calculate_points_for_purchase,
    get_all_benefits,
    get_all_tier_rules,
    normalize_tier,
    to_float,
    to_integer,
)

router = APIRouter(prefix="/memberships", tags=["Memberships"])

CUSTOMER_LOYALTY_FIELDS = """
    customer_id, crm_customer_key, customer_name, phone_number,
    masked_phone_number, email, masked_email, customer_city,
    customer_state, product_category, primary_shopping_channel,
    membership_status, membership_tier, points_earned, points_redeemed,
    points_balance, membership_expiry_date, upgrade_eligibility,
    total_sales, total_transactions, total_items_purchased,
    avg_transaction_value, purchase_frequency, days_since_last_purchase,
    last_purchase_date, online_purchases, in_store_purchases,
    app_sessions_30d, website_visits, wishlist_count,
    repeat_purchase_flag, customer_segment, potential_member_score,
    churn_risk_level, estimated_clv, recommendation_reason_codes,
    whatsapp_consent, sms_consent, email_consent,
    app_notification_consent, personalization_consent, do_not_contact,
    preferred_campaign_channel
"""


def get_customer_row(customer_id: str):
    return fetch_one(
        f"SELECT {CUSTOMER_LOYALTY_FIELDS} FROM customers_360 WHERE CAST(customer_id AS TEXT) = ?",
        (str(customer_id),),
    )


def _load_rules():
    return get_all_tier_rules(), build_rule_map()


def _invalidate_customer(customer_id: str):
    cache.delete("loyalty:summary")
    cache.delete_prefix("loyalty:list:")
    cache.delete_prefix("loyalty:segments")
    cache.delete(f"loyalty:customer:{customer_id}")
    cache.delete("dashboard:summary")
    cache.delete("admin:summary")


@router.get("")
def get_membership_list(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    tier: str = Query(default=""),
    search: str = Query(default=""),
    user=Depends(get_current_user),
):
    require_permission(user, "loyalty")
    cache_key = f"loyalty:list:{page}:{page_size}:{tier.lower()}:{search.lower()}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    where = []
    values = []
    if tier:
        where.append("LOWER(COALESCE(membership_tier, 'non-member')) = LOWER(?)")
        values.append(normalize_tier(tier))
    if search:
        pattern = f"%{search.strip()}%"
        where.append("(CAST(customer_id AS TEXT) LIKE ? OR customer_name LIKE ? OR email LIKE ?)")
        values.extend([pattern, pattern, pattern])

    where_sql = " WHERE " + " AND ".join(where) if where else ""
    total_row = fetch_one(f"SELECT COUNT(*) AS count FROM customers_360{where_sql}", tuple(values))
    offset = (page - 1) * page_size
    rows = fetch_all(
        f"""
        SELECT {CUSTOMER_LOYALTY_FIELDS}
        FROM customers_360
        {where_sql}
        ORDER BY CASE LOWER(COALESCE(membership_tier, ''))
            WHEN 'platinum' THEN 1 WHEN 'gold' THEN 2 WHEN 'silver' THEN 3 ELSE 4
        END, COALESCE(estimated_clv, 0) DESC
        LIMIT ? OFFSET ?
        """,
        tuple(values + [page_size, offset]),
    )
    _, rule_map = _load_rules()
    items = [build_loyalty_customer(row, rule_map=rule_map) for row in rows]
    response = {
        "success": True,
        "total": to_integer(total_row.get("count") if total_row else 0),
        "page": page,
        "page_size": page_size,
        "items": items,
        "data": items,
    }
    cache.set(cache_key, response, ttl_seconds=60)
    return response


@router.get("/summary")
def get_loyalty_summary(user=Depends(get_current_user)):
    require_permission(user, "loyalty")
    cached = cache.get("loyalty:summary")
    if cached is not None:
        return cached

    base = fetch_one(
        """
        SELECT COUNT(*) AS total_customers,
               SUM(CASE WHEN LOWER(TRIM(COALESCE(membership_tier, 'non-member'))) NOT IN ('non-member', 'non member', '') THEN 1 ELSE 0 END) AS active_members,
               SUM(CASE WHEN LOWER(TRIM(COALESCE(membership_tier, 'non-member'))) IN ('non-member', 'non member', '') AND COALESCE(potential_member_score, 0) >= 50 THEN 1 ELSE 0 END) AS potential_members,
               COALESCE(SUM(points_earned), 0) AS total_points_earned,
               COALESCE(SUM(points_redeemed), 0) AS total_points_redeemed,
               COALESCE(SUM(points_balance), 0) AS total_points_balance,
               COALESCE(SUM(CASE WHEN LOWER(TRIM(COALESCE(membership_tier, 'non-member'))) NOT IN ('non-member', 'non member', '') THEN total_sales ELSE 0 END), 0) AS member_sales
        FROM customers_360
        """
    )
    tier_distribution = fetch_all(
        """
        SELECT COALESCE(NULLIF(TRIM(membership_tier), ''), 'Non-member') AS tier,
               COUNT(*) AS count
        FROM customers_360
        GROUP BY COALESCE(NULLIF(TRIM(membership_tier), ''), 'Non-member')
        ORDER BY count DESC
        """
    )

    # Calculate recommendation counts without benefit queries.
    candidate_rows = fetch_all(
        f"""
        SELECT {CUSTOMER_LOYALTY_FIELDS}
        FROM customers_360
        WHERE LOWER(TRIM(COALESCE(membership_tier, ''))) IN ('silver', 'gold')
           OR COALESCE(potential_member_score, 0) >= 50
        """
    )
    _, rule_map = _load_rules()
    candidates = [build_loyalty_customer(row, rule_map=rule_map) for row in candidate_rows]
    upgrade_recommended = sum(
        1 for item in candidates
        if item.get("recommendation_flag") and item.get("actual_membership_tier") in {"Silver", "Gold"}
    )
    contactable_recommendations = sum(
        1 for item in candidates
        if item.get("recommendation_flag") and item.get("contact_allowed")
    )

    total = to_integer(base.get("total_customers") if base else 0)
    active = to_integer(base.get("active_members") if base else 0)
    balance = to_integer(base.get("total_points_balance") if base else 0)
    response = {
        "success": True,
        "summary": {
            "total_customers": total,
            "active_members": active,
            "non_members": total - active,
            "potential_members": to_integer(base.get("potential_members") if base else 0),
            "upgrade_recommended": upgrade_recommended,
            "contactable_recommendations": contactable_recommendations,
            "total_points_earned": to_integer(base.get("total_points_earned") if base else 0),
            "total_points_redeemed": to_integer(base.get("total_points_redeemed") if base else 0),
            "total_points_balance": balance,
            "outstanding_points_value": round(balance * 0.10, 2),
            "member_sales": round(to_float(base.get("member_sales") if base else 0), 2),
        },
        "tier_distribution": tier_distribution,
    }
    cache.set("loyalty:summary", response, ttl_seconds=60)
    return response


@router.get("/rules")
def get_loyalty_rules(user=Depends(get_current_user)):
    require_permission(user, "loyalty")
    cached = cache.get("loyalty:rules")
    if cached is not None:
        return cached
    rows = get_all_tier_rules()
    response = {"success": True, "count": len(rows), "data": rows}
    cache.set("loyalty:rules", response, ttl_seconds=600)
    return response


@router.get("/benefits")
def get_loyalty_benefits(user=Depends(get_current_user)):
    require_permission(user, "loyalty")
    cached = cache.get("loyalty:benefits")
    if cached is not None:
        return cached
    rows = get_all_benefits()
    response = {"success": True, "count": len(rows), "data": rows}
    cache.set("loyalty:benefits", response, ttl_seconds=600)
    return response


@router.get("/segments")
def get_loyalty_segments(user=Depends(get_current_user)):
    require_permission(user, "loyalty")
    cached = cache.get("loyalty:segments")
    if cached is not None:
        return cached
    rows = fetch_all(f"SELECT {CUSTOMER_LOYALTY_FIELDS} FROM customers_360")
    _, rule_map = _load_rules()
    segment_map = {}
    for row in rows:
        item = build_loyalty_customer(row, rule_map=rule_map)
        name = item.get("loyalty_segment") or "Unclassified"
        segment = segment_map.setdefault(name, {
            "segment_name": name,
            "customer_count": 0,
            "contactable_count": 0,
            "recommended_action": item.get("recommended_action") or "",
        })
        segment["customer_count"] += 1
        if item.get("contact_allowed"):
            segment["contactable_count"] += 1
    response = {"success": True, "count": len(segment_map), "data": list(segment_map.values())}
    cache.set("loyalty:segments", response, ttl_seconds=60)
    return response


@router.get("/segments/potential-members")
def get_potential_members(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    user=Depends(get_current_user),
):
    require_permission(user, "loyalty")
    offset = (page - 1) * page_size
    condition = "LOWER(TRIM(COALESCE(membership_tier, 'non-member'))) IN ('non-member', 'non member', '')"
    total = fetch_one(f"SELECT COUNT(*) AS count FROM customers_360 WHERE {condition}")
    rows = fetch_all(
        f"SELECT {CUSTOMER_LOYALTY_FIELDS} FROM customers_360 WHERE {condition} ORDER BY COALESCE(potential_member_score, 0) DESC LIMIT ? OFFSET ?",
        (page_size, offset),
    )
    _, rule_map = _load_rules()
    items = [build_loyalty_customer(row, rule_map=rule_map) for row in rows]
    return {"success": True, "total": to_integer(total.get("count") if total else 0), "page": page, "page_size": page_size, "items": items, "data": items}


# @router.get("/segments/upgrade-eligible")
# def get_upgrade_recommended_customers(user=Depends(get_current_user)):
#     require_permission(user, "loyalty")
#     rows = fetch_all(
#         f"SELECT {CUSTOMER_LOYALTY_FIELDS} FROM customers_360 WHERE LOWER(TRIM(COALESCE(membership_tier, ''))) IN ('silver', 'gold')"
#     )
#     _, rule_map = _load_rules()
#     items = [build_loyalty_customer(row, rule_map=rule_map) for row in rows]
#     recommended = [item for item in items if item.get("recommendation_flag")]
#     recommended.sort(key=lambda item: to_integer(item.get("tier_upgrade_score")), reverse=True)
#     return {"success": True, "count": len(recommended), "data": recommended}
@router.get("/segments/upgrade-eligible")
def get_upgrade_recommended_customers(
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    user=Depends(get_current_user),
):
    require_permission(user, "loyalty")

    cache_key = f"loyalty:upgrade-recommended:{limit}"

    cached_response = cache.get(cache_key)

    if cached_response is not None:
        return cached_response

    # SQL first restricts the candidate pool.
    # The scoring engine then evaluates only the strongest
    # Silver and Gold candidates instead of the full table.
    candidate_limit = min(
        max(limit * 10, 100),
        1000,
    )

    rows = fetch_all(
        f"""
        SELECT
            {CUSTOMER_LOYALTY_FIELDS}
        FROM customers_360
        WHERE LOWER(
            TRIM(
                COALESCE(
                    membership_tier,
                    ''
                )
            )
        ) IN (
            'silver',
            'gold'
        )
        ORDER BY
            COALESCE(total_sales, 0) DESC,
            COALESCE(estimated_clv, 0) DESC,
            COALESCE(total_transactions, 0) DESC
        LIMIT ?
        """,
        (candidate_limit,),
    )

    _, rule_map = _load_rules()

    evaluated = [
        build_loyalty_customer(
            row,
            rule_map=rule_map,
        )
        for row in rows
    ]

    recommended = [
        customer
        for customer in evaluated
        if customer.get("recommendation_flag")
    ]

    recommended.sort(
        key=lambda customer: to_integer(
            customer.get("tier_upgrade_score")
        ),
        reverse=True,
    )

    preview = recommended[:limit]

    response = {
        "success": True,
        "count": len(preview),
        "evaluated_candidates": len(evaluated),
        "data": preview,
    }

    cache.set(
        cache_key,
        response,
        ttl_seconds=60,
    )

    return response


@router.get("/segments/{segment_name}/customers")
def get_customers_by_loyalty_segment(
    segment_name: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    user=Depends(get_current_user),
):
    require_permission(user, "loyalty")
    rows = fetch_all(f"SELECT {CUSTOMER_LOYALTY_FIELDS} FROM customers_360")
    _, rule_map = _load_rules()
    matched = []
    for row in rows:
        item = build_loyalty_customer(row, rule_map=rule_map)
        if str(item.get("loyalty_segment") or "").lower() == segment_name.lower():
            matched.append(item)
    start = (page - 1) * page_size
    items = matched[start:start + page_size]
    return {"success": True, "segment_name": segment_name, "total": len(matched), "page": page, "page_size": page_size, "items": items, "data": items}


@router.post("/{customer_id}/purchase")
def purchase_membership(customer_id: str, payload: dict, user=Depends(get_current_user)):
    require_permission(user, "loyalty")
    customer = get_customer_row(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    tier = normalize_tier(payload.get("tier"))
    if tier not in {"Silver", "Gold", "Platinum"}:
        raise HTTPException(status_code=400, detail="Use Silver, Gold, or Platinum")

    old_tier = normalize_tier(customer.get("membership_tier"))
    history_id = "LTH-" + uuid.uuid4().hex[:8].upper()
    reason = payload.get("reason") or f"Customer purchased {tier} membership"
    execute_query(
        """
        UPDATE customers_360
        SET membership_status = 'Active', membership_tier = ?,
            membership_expiry_date = DATE('now', '+1 year')
        WHERE CAST(customer_id AS TEXT) = ?
        """,
        (tier, str(customer_id)),
    )
    execute_query(
        """
        INSERT INTO loyalty_tier_history (
            history_id, customer_id, old_tier, new_tier, change_type,
            change_reason, recommendation_score, changed_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (history_id, str(customer_id), old_tier, tier, "Purchased", reason, 0, user["sub"]),
    )
    create_audit_log(user["sub"], user["role"], "Purchase membership", "Membership", str(customer_id), "Allowed", f"Membership changed from {old_tier} to {tier}")
    _invalidate_customer(customer_id)
    updated = get_customer_row(customer_id)
    rules, rule_map = _load_rules()
    benefit_map = build_benefit_map()
    return {"success": True, "message": f"{tier} membership activated successfully", "history_id": history_id, "data": build_loyalty_customer(updated, rule_map, benefit_map, True)}


@router.post("/{customer_id}/earn")
def earn_loyalty_points(customer_id: str, payload: dict, user=Depends(get_current_user)):
    require_permission(user, "loyalty")
    customer = get_customer_row(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    order_amount = to_float(payload.get("order_amount"))
    if order_amount <= 0:
        raise HTTPException(status_code=400, detail="order_amount must be greater than 0")

    rule = get_all_tier_rules()
    rule_map = build_rule_map(rule)
    tier = normalize_tier(customer.get("membership_tier"))
    calculation = calculate_points_for_purchase(tier, order_amount, rule_map.get(tier))
    points = to_integer(calculation.get("points_earned"))
    before = to_integer(customer.get("points_balance"))
    after = before + points
    transaction_id = "LPT-" + uuid.uuid4().hex[:8].upper()
    reference = payload.get("order_id") or payload.get("source_reference_id") or ""

    execute_query("UPDATE customers_360 SET points_earned = COALESCE(points_earned, 0) + ?, points_balance = ? WHERE CAST(customer_id AS TEXT) = ?", (points, after, str(customer_id)))
    execute_query(
        """
        INSERT INTO loyalty_point_transactions (
            transaction_id, customer_id, transaction_type, source_type,
            source_reference_id, order_amount, points_change, balance_before,
            balance_after, description, created_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (transaction_id, str(customer_id), "Earn", "Purchase", reference, order_amount, points, before, after, f"Earned {points} points for purchase of Rs. {order_amount}", user["sub"]),
    )
    create_audit_log(user["sub"], user["role"], "Earn loyalty points", "LoyaltyPoints", transaction_id, "Allowed", f"Customer {customer_id} earned {points} points")
    _invalidate_customer(customer_id)
    return {"success": True, "message": "Points added successfully", "transaction_id": transaction_id, "calculation": calculation, "balance_before": before, "balance_after": after}


@router.post("/{customer_id}/redeem")
def redeem_loyalty_points(customer_id: str, payload: dict, user=Depends(get_current_user)):
    require_permission(user, "loyalty")
    customer = get_customer_row(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    points = to_integer(payload.get("points"))
    if points < 100:
        raise HTTPException(status_code=400, detail="Minimum redemption is 100 points")
    before = to_integer(customer.get("points_balance"))
    if points > before:
        raise HTTPException(status_code=400, detail="Insufficient points balance")

    discount_value = round(points * 0.10, 2)
    order_amount = to_float(payload.get("order_amount"))
    if order_amount > 0 and discount_value > order_amount * 0.20:
        raise HTTPException(status_code=400, detail="Point redemption cannot exceed 20 percent of order value")

    after = before - points
    redemption_id = "LRD-" + uuid.uuid4().hex[:8].upper()
    transaction_id = "LPT-" + uuid.uuid4().hex[:8].upper()
    order_id = payload.get("order_id") or ""
    execute_query("UPDATE customers_360 SET points_redeemed = COALESCE(points_redeemed, 0) + ?, points_balance = ? WHERE CAST(customer_id AS TEXT) = ?", (points, after, str(customer_id)))
    execute_query("INSERT INTO loyalty_redemptions (redemption_id, customer_id, points_redeemed, discount_value, order_id, status, processed_by) VALUES (?, ?, ?, ?, ?, ?, ?)", (redemption_id, str(customer_id), points, discount_value, order_id, "Completed", user["sub"]))
    execute_query(
        """
        INSERT INTO loyalty_point_transactions (
            transaction_id, customer_id, transaction_type, source_type,
            source_reference_id, order_amount, points_change, balance_before,
            balance_after, description, created_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (transaction_id, str(customer_id), "Redeem", "Order Discount", order_id, order_amount, -points, before, after, f"Redeemed {points} points for Rs. {discount_value} discount", user["sub"]),
    )
    create_audit_log(user["sub"], user["role"], "Redeem loyalty points", "LoyaltyRedemption", redemption_id, "Allowed", f"Customer {customer_id} redeemed {points} points")
    _invalidate_customer(customer_id)
    return {"success": True, "message": "Points redeemed successfully", "redemption_id": redemption_id, "transaction_id": transaction_id, "points_redeemed": points, "discount_value": discount_value, "balance_before": before, "balance_after": after}


@router.get("/{customer_id}")
def get_customer_membership(customer_id: str, user=Depends(get_current_user)):
    require_permission(user, "loyalty")
    cache_key = f"loyalty:customer:{customer_id}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    customer = get_customer_row(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Membership record not found")

    rules = get_all_tier_rules()
    benefits = get_all_benefits()
    data = build_loyalty_customer(customer, build_rule_map(rules), build_benefit_map(benefits), True)
    transactions = fetch_all("SELECT * FROM loyalty_point_transactions WHERE customer_id = ? ORDER BY created_at DESC LIMIT 100", (str(customer_id),))
    redemptions = fetch_all("SELECT * FROM loyalty_redemptions WHERE customer_id = ? ORDER BY created_at DESC LIMIT 100", (str(customer_id),))
    history = fetch_all("SELECT * FROM loyalty_tier_history WHERE customer_id = ? ORDER BY changed_at DESC LIMIT 100", (str(customer_id),))
    response = {
        "success": True,
        "data": data,
        "point_transactions": transactions,
        "transactions": transactions,
        "redemptions": redemptions,
        "tier_history": history,
    }
    cache.set(cache_key, response, ttl_seconds=30)
    create_audit_log(user["sub"], user["role"], "View customer membership", "Membership", str(customer_id), "Allowed", "Enhanced customer loyalty detail viewed")
    return response
