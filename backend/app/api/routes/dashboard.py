# from fastapi import APIRouter, Depends
# from app.core.security import get_current_user, require_permission
# from app.db.sqlite_client import fetch_all, fetch_one

# router = APIRouter(
#     prefix="/dashboard",
#     tags=["Dashboard"]
# )


# def safe_count(row, key="count"):
#     if not row:
#         return 0

#     value = row.get(key)

#     if value is None:
#         return 0

#     return int(value)


# def safe_number(row, key="value"):
#     if not row:
#         return 0

#     value = row.get(key)

#     if value is None:
#         return 0

#     return value


# @router.get("/summary")
# def get_dashboard_summary(user=Depends(get_current_user)):
#     require_permission(user, "dashboard")

#     # -------------------------------------------------
#     # Executive summary KPIs
#     # -------------------------------------------------

#     total_customers_row = fetch_one("""
#     SELECT COUNT(*) AS count
#     FROM customers_360
#     """)

#     members_row = fetch_one("""
#     SELECT COUNT(*) AS count
#     FROM customers_360
#     WHERE membership_status IS NOT NULL
#       AND TRIM(membership_status) != ''
#       AND LOWER(TRIM(membership_status)) NOT IN (
#           'non-member',
#           'non member',
#           'inactive'
#       )
#     """)

#     avg_clv_row = fetch_one("""
#     SELECT ROUND(AVG(COALESCE(estimated_clv, 0)), 2) AS value
#     FROM customers_360
#     """)

#     repeat_purchase_row = fetch_one("""
#     SELECT ROUND(
#         CASE
#             WHEN COUNT(*) = 0 THEN 0
#             ELSE
#                 100.0 * SUM(
#                     CASE
#                         WHEN COALESCE(repeat_purchase_flag, 0) = 1
#                         THEN 1
#                         ELSE 0
#                     END
#                 ) / COUNT(*)
#         END,
#         2
#     ) AS value
#     FROM customers_360
#     """)

#     high_churn_row = fetch_one("""
#     SELECT COUNT(*) AS count
#     FROM customers_360
#     WHERE LOWER(TRIM(churn_risk_level)) = 'high'
#     """)

#     campaign_eligible_row = fetch_one("""
#     SELECT COUNT(*) AS count
#     FROM customers_360
#     WHERE
#         COALESCE(campaign_eligible_whatsapp, 0) = 1
#         OR COALESCE(campaign_eligible_sms, 0) = 1
#         OR COALESCE(campaign_eligible_email, 0) = 1
#         OR COALESCE(campaign_eligible_app, 0) = 1
#     """)

#     total_sales_row = fetch_one("""
#     SELECT ROUND(SUM(COALESCE(total_sales, 0)), 2) AS value
#     FROM customers_360
#     """)

#     whatsapp_reachable_row = fetch_one("""
#     SELECT COUNT(*) AS count
#     FROM customers_360
#     WHERE COALESCE(whatsapp_consent, 0) = 1
#       AND COALESCE(do_not_contact, 0) = 0
#     """)

#     missing_emails_row = fetch_one("""
#     SELECT COUNT(*) AS count
#     FROM customers_360
#     WHERE email IS NULL
#        OR TRIM(email) = ''
#     """)

#     total_campaigns_row = fetch_one("""
#     SELECT COUNT(*) AS count
#     FROM crm_campaigns
#     """)

#     open_tickets_row = fetch_one("""
#     SELECT COUNT(*) AS count
#     FROM customer_service_tickets
#     WHERE status NOT IN ('Resolved', 'Closed')
#     """)

#     total_customers = safe_count(total_customers_row)
#     member_count = safe_count(members_row)

#     member_percentage = round(
#         (member_count / total_customers) * 100,
#         2
#     ) if total_customers else 0

#     # -------------------------------------------------
#     # Customer segmentation chart
#     # -------------------------------------------------

#     customer_segments = fetch_all("""
#     SELECT
#         COALESCE(NULLIF(TRIM(customer_segment), ''), 'Unknown') AS label,
#         COUNT(*) AS value
#     FROM customers_360
#     GROUP BY COALESCE(NULLIF(TRIM(customer_segment), ''), 'Unknown')
#     ORDER BY value DESC
#     LIMIT 10
#     """)

#     # -------------------------------------------------
#     # Churn distribution chart
#     # -------------------------------------------------

#     churn_distribution = fetch_all("""
#     SELECT
#         COALESCE(NULLIF(TRIM(churn_risk_level), ''), 'Unknown') AS label,
#         COUNT(*) AS value
#     FROM customers_360
#     GROUP BY COALESCE(NULLIF(TRIM(churn_risk_level), ''), 'Unknown')
#     ORDER BY
#         CASE LOWER(label)
#             WHEN 'low' THEN 1
#             WHEN 'medium' THEN 2
#             WHEN 'high' THEN 3
#             ELSE 4
#         END
#     """)

#     # -------------------------------------------------
#     # Membership tier chart
#     # -------------------------------------------------

#     membership_tiers = fetch_all("""
#     SELECT
#         COALESCE(NULLIF(TRIM(membership_tier), ''), 'Non-member') AS label,
#         COUNT(*) AS value
#     FROM customers_360
#     GROUP BY COALESCE(NULLIF(TRIM(membership_tier), ''), 'Non-member')
#     ORDER BY value DESC
#     """)

#     # -------------------------------------------------
#     # Top cities chart
#     # -------------------------------------------------

#     top_cities = fetch_all("""
#     SELECT
#         COALESCE(NULLIF(TRIM(customer_city), ''), 'Unknown') AS label,
#         COUNT(*) AS value
#     FROM customers_360
#     GROUP BY COALESCE(NULLIF(TRIM(customer_city), ''), 'Unknown')
#     ORDER BY value DESC
#     LIMIT 10
#     """)

#     # -------------------------------------------------
#     # Consent reachability chart
#     # -------------------------------------------------

#     consent_reachability_row = fetch_one("""
#     SELECT
#         SUM(
#             CASE
#                 WHEN COALESCE(whatsapp_consent, 0) = 1
#                  AND COALESCE(do_not_contact, 0) = 0
#                 THEN 1 ELSE 0
#             END
#         ) AS whatsapp,

#         SUM(
#             CASE
#                 WHEN COALESCE(sms_consent, 0) = 1
#                  AND COALESCE(do_not_contact, 0) = 0
#                 THEN 1 ELSE 0
#             END
#         ) AS sms,

#         SUM(
#             CASE
#                 WHEN COALESCE(email_consent, 0) = 1
#                  AND COALESCE(do_not_contact, 0) = 0
#                 THEN 1 ELSE 0
#             END
#         ) AS email,

#         SUM(
#             CASE
#                 WHEN COALESCE(app_notification_consent, 0) = 1
#                  AND COALESCE(do_not_contact, 0) = 0
#                 THEN 1 ELSE 0
#             END
#         ) AS app
#     FROM customers_360
#     """)

#     consent_reachability = [
#         {
#             "label": "WhatsApp",
#             "value": safe_number(
#                 consent_reachability_row,
#                 "whatsapp"
#             )
#         },
#         {
#             "label": "SMS",
#             "value": safe_number(
#                 consent_reachability_row,
#                 "sms"
#             )
#         },
#         {
#             "label": "Email",
#             "value": safe_number(
#                 consent_reachability_row,
#                 "email"
#             )
#         },
#         {
#             "label": "App",
#             "value": safe_number(
#                 consent_reachability_row,
#                 "app"
#             )
#         }
#     ]

#     # -------------------------------------------------
#     # Campaign status chart
#     # -------------------------------------------------

#     campaign_status = fetch_all("""
#     SELECT
#         COALESCE(NULLIF(TRIM(status), ''), 'Unknown') AS label,
#         COUNT(*) AS value
#     FROM crm_campaigns
#     GROUP BY COALESCE(NULLIF(TRIM(status), ''), 'Unknown')
#     ORDER BY value DESC
#     """)

#     # -------------------------------------------------
#     # Campaign performance chart
#     # -------------------------------------------------

#     campaign_performance_row = fetch_one("""
#     SELECT
#         COUNT(*) AS total_messages,

#         SUM(
#             CASE
#                 WHEN COALESCE(opened, 0) = 1
#                 THEN 1 ELSE 0
#             END
#         ) AS opened,

#         SUM(
#             CASE
#                 WHEN COALESCE(clicked, 0) = 1
#                 THEN 1 ELSE 0
#             END
#         ) AS clicked,

#         SUM(
#             CASE
#                 WHEN COALESCE(converted, 0) = 1
#                 THEN 1 ELSE 0
#             END
#         ) AS converted,

#         ROUND(
#             SUM(COALESCE(revenue, 0)),
#             2
#         ) AS revenue
#     FROM crm_campaign_message_logs
#     """)

#     campaign_performance = [
#         {
#             "label": "Opened",
#             "value": safe_number(
#                 campaign_performance_row,
#                 "opened"
#             )
#         },
#         {
#             "label": "Clicked",
#             "value": safe_number(
#                 campaign_performance_row,
#                 "clicked"
#             )
#         },
#         {
#             "label": "Converted",
#             "value": safe_number(
#                 campaign_performance_row,
#                 "converted"
#             )
#         },
#         {
#             "label": "Revenue",
#             "value": safe_number(
#                 campaign_performance_row,
#                 "revenue"
#             )
#         }
#     ]

#     # -------------------------------------------------
#     # Recent campaigns table
#     # -------------------------------------------------

#     recent_campaigns = fetch_all("""
#     SELECT
#         c.campaign_id,
#         c.campaign_name,
#         c.campaign_type,
#         c.business_channel,
#         c.demo_platform,
#         c.target_segment,
#         c.status,
#         c.total_audience,
#         c.eligible_count,
#         c.sent_count,
#         c.failed_count,
#         c.created_by,
#         c.created_at,

#         ROUND(
#             COALESCE(
#                 (
#                     SELECT SUM(COALESCE(l.revenue, 0))
#                     FROM crm_campaign_message_logs l
#                     WHERE l.campaign_id = c.campaign_id
#                 ),
#                 0
#             ),
#             2
#         ) AS revenue

#     FROM crm_campaigns c
#     ORDER BY c.created_at DESC
#     LIMIT 5
#     """)

#     # -------------------------------------------------
#     # Service ticket status chart
#     # -------------------------------------------------

#     ticket_status = fetch_all("""
#     SELECT
#         COALESCE(NULLIF(TRIM(status), ''), 'Unknown') AS label,
#         COUNT(*) AS value
#     FROM customer_service_tickets
#     GROUP BY COALESCE(NULLIF(TRIM(status), ''), 'Unknown')
#     ORDER BY value DESC
#     """)

#     # -------------------------------------------------
#     # Service SLA distribution
#     # -------------------------------------------------

#     sla_distribution = fetch_all("""
#     SELECT
#         COALESCE(NULLIF(TRIM(sla_status), ''), 'Unknown') AS label,
#         COUNT(*) AS value
#     FROM customer_service_tickets
#     GROUP BY COALESCE(NULLIF(TRIM(sla_status), ''), 'Unknown')
#     ORDER BY value DESC
#     """)

#     sla_summary_row = fetch_one("""
#     SELECT
#         COUNT(*) AS total,

#         SUM(
#             CASE
#                 WHEN LOWER(TRIM(COALESCE(sla_status, '')))
#                      IN ('within sla', 'on track', 'met')
#                 THEN 1
#                 ELSE 0
#             END
#         ) AS compliant
#     FROM customer_service_tickets
#     """)

#     total_sla_tickets = safe_count(
#         sla_summary_row,
#         "total"
#     )

#     compliant_sla_tickets = safe_count(
#         sla_summary_row,
#         "compliant"
#     )

#     sla_compliance_percentage = round(
#         (compliant_sla_tickets / total_sla_tickets) * 100,
#         2
#     ) if total_sla_tickets else 0

#     # -------------------------------------------------
#     # Ticket trend
#     # Converts DD-MM-YYYY and YYYY-MM-DD formats
#     # -------------------------------------------------

#     ticket_trend = fetch_all("""
#     SELECT
#         normalized_date AS label,
#         SUM(created_count) AS created,
#         SUM(resolved_count) AS resolved,
#         SUM(escalated_count) AS escalated
#     FROM (
#         SELECT
#             CASE
#                 WHEN created_on GLOB '??-??-????*'
#                 THEN
#                     SUBSTR(created_on, 7, 4)
#                     || '-'
#                     || SUBSTR(created_on, 4, 2)
#                     || '-'
#                     || SUBSTR(created_on, 1, 2)
#                 ELSE SUBSTR(created_on, 1, 10)
#             END AS normalized_date,

#             1 AS created_count,

#             CASE
#                 WHEN status IN ('Resolved', 'Closed')
#                 THEN 1
#                 ELSE 0
#             END AS resolved_count,

#             CASE
#                 WHEN status = 'Escalated'
#                 THEN 1
#                 ELSE 0
#             END AS escalated_count

#         FROM customer_service_tickets
#         WHERE created_on IS NOT NULL
#           AND TRIM(created_on) != ''
#     )
#     GROUP BY normalized_date
#     ORDER BY normalized_date DESC
#     LIMIT 7
#     """)

#     ticket_trend.reverse()

#     # -------------------------------------------------
#     # Recent service tickets table
#     # -------------------------------------------------

#     recent_tickets = fetch_all("""
#     SELECT
#         ticket_id,
#         customer_id,
#         customer_name,
#         linked_order_id,
#         issue_category,
#         priority,
#         status,
#         assigned_agent_id,
#         assigned_to,
#         sla_status,
#         sla_due,
#         channel,
#         created_on,
#         last_updated
#     FROM customer_service_tickets
#     ORDER BY last_updated DESC, created_on DESC
#     LIMIT 5
#     """)

#     # -------------------------------------------------
#     # High churn customers table
#     # -------------------------------------------------

#     high_churn_customers = fetch_all("""
#     SELECT
#         customer_id,
#         crm_customer_key,
#         customer_name,
#         membership_tier,
#         customer_segment,
#         churn_risk_level,
#         ROUND(COALESCE(total_sales, 0), 2) AS total_sales,
#         ROUND(COALESCE(estimated_clv, 0), 2) AS estimated_clv
#     FROM customers_360
#     WHERE LOWER(TRIM(churn_risk_level)) IN ('high', 'medium')
#     ORDER BY
#         CASE LOWER(TRIM(churn_risk_level))
#             WHEN 'high' THEN 1
#             WHEN 'medium' THEN 2
#             ELSE 3
#         END,
#         estimated_clv DESC
#     LIMIT 10
#     """)

#     # -------------------------------------------------
#     # Data quality
#     # -------------------------------------------------

#     data_quality_row = fetch_one("""
#     SELECT
#         COUNT(*) AS total_records,

#         SUM(
#             CASE
#                 WHEN email IS NULL OR TRIM(email) = ''
#                 THEN 1 ELSE 0
#             END
#         ) AS missing_email,

#         SUM(
#             CASE
#                 WHEN phone_number IS NULL
#                   OR TRIM(phone_number) = ''
#                 THEN 1 ELSE 0
#             END
#         ) AS missing_phone,

#         SUM(
#             CASE
#                 WHEN email IS NOT NULL
#                  AND TRIM(email) != ''
#                  AND phone_number IS NOT NULL
#                  AND TRIM(phone_number) != ''
#                  AND customer_name IS NOT NULL
#                  AND TRIM(customer_name) != ''
#                 THEN 1 ELSE 0
#             END
#         ) AS good_records
#     FROM customers_360
#     """)

#     total_quality_records = safe_count(
#         data_quality_row,
#         "total_records"
#     )

#     missing_email_count = safe_count(
#         data_quality_row,
#         "missing_email"
#     )

#     missing_phone_count = safe_count(
#         data_quality_row,
#         "missing_phone"
#     )

#     good_records_count = safe_count(
#         data_quality_row,
#         "good_records"
#     )

#     average_data_quality = round(
#         (good_records_count / total_quality_records) * 100,
#         2
#     ) if total_quality_records else 0

#     data_quality = [
#         {
#             "label": "Missing Email",
#             "value": missing_email_count
#         },
#         {
#             "label": "Missing Phone",
#             "value": missing_phone_count
#         },
#         {
#             "label": "Good Records",
#             "value": good_records_count
#         }
#     ]

#     # -------------------------------------------------
#     # Loyalty points
#     # Uses points_balance from customers_360.
#     # Add points_earned/redeemed later if available.
#     # -------------------------------------------------

#     loyalty_points_row = fetch_one("""
#     SELECT
#         SUM(COALESCE(points_balance, 0)) AS points_balance
#     FROM customers_360
#     """)

#     # -------------------------------------------------
#     # Final response
#     # -------------------------------------------------

#     return {
#         "success": True,

#         "summary": {
#             "total_customers": total_customers,
#             "members": member_count,
#             "member_percentage": member_percentage,
#             "avg_clv": safe_number(avg_clv_row),
#             "repeat_purchase_rate": safe_number(
#                 repeat_purchase_row
#             ),
#             "high_churn_customers": safe_count(
#                 high_churn_row
#             ),
#             "campaign_eligible_customers": safe_count(
#                 campaign_eligible_row
#             ),
#             "total_sales": safe_number(
#                 total_sales_row
#             ),
#             "open_service_tickets": safe_count(
#                 open_tickets_row
#             ),
#             "total_campaigns": safe_count(
#                 total_campaigns_row
#             ),
#             "whatsapp_reachable": safe_count(
#                 whatsapp_reachable_row
#             ),
#             "missing_emails": missing_email_count,
#             "average_data_quality": average_data_quality,
#             "sla_compliance_percentage": sla_compliance_percentage
#         },

#         "charts": {
#             "customer_segments": customer_segments,
#             "churn_distribution": churn_distribution,
#             "membership_tiers": membership_tiers,
#             "top_cities": top_cities,
#             "consent_reachability": consent_reachability,
#             "campaign_status": campaign_status,
#             "campaign_performance": campaign_performance,
#             "ticket_status": ticket_status,
#             "ticket_trend": ticket_trend,
#             "sla_distribution": sla_distribution,
#             "data_quality": data_quality
#         },

#         "loyalty": {
#             "points_balance": safe_number(
#                 loyalty_points_row,
#                 "points_balance"
#             )
#         },

#         "tables": {
#             "recent_campaigns": recent_campaigns,
#             "recent_tickets": recent_tickets,
#             "high_churn_customers": high_churn_customers
#         },

#         "metadata": {
#             "age_chart_available": False,
#             "age_chart_reason": (
#                 "Age, date_of_birth, or age_group is not available "
#                 "in the confirmed customers_360 schema."
#             ),
#             "data_source": "SQLite",
#             "live": True
#         }
#     }

from fastapi import APIRouter, Depends
from app.core.security import get_current_user, require_permission
from app.db.sqlite_client import fetch_all, fetch_one
from app.services.cache_service import cache
 
router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)
 
 
def safe_count(row, key="count"):
    if not row:
        return 0
 
    value = row.get(key)
 
    if value is None:
        return 0
 
    return int(value)
 
 
def safe_number(row, key="value"):
    if not row:
        return 0
 
    value = row.get(key)
 
    if value is None:
        return 0
 
    return value
 
 
@router.get("/summary")
def get_dashboard_summary(user=Depends(get_current_user)):
    require_permission(user, "dashboard")
    # Cache lookup
    cached_response = cache.get(
        "dashboard:summary"
    )


    if cached_response is not None:
        return cached_response
 
    total_customers_row = fetch_one("""
    SELECT COUNT(*) AS count
    FROM customers_360
    """)
 
    members_row = fetch_one("""
    SELECT COUNT(*) AS count
    FROM customers_360
    WHERE membership_status IS NOT NULL
      AND TRIM(membership_status) != ''
      AND LOWER(TRIM(membership_status)) NOT IN (
          'non-member',
          'non member',
          'inactive'
      )
    """)
 
    avg_clv_row = fetch_one("""
    SELECT ROUND(AVG(COALESCE(estimated_clv, 0)), 2) AS value
    FROM customers_360
    """)
 
    repeat_purchase_row = fetch_one("""
    SELECT ROUND(
        CASE
            WHEN COUNT(*) = 0 THEN 0
            ELSE
                100.0 * SUM(
                    CASE
                        WHEN COALESCE(repeat_purchase_flag, 0) = 1
                        THEN 1
                        ELSE 0
                    END
                ) / COUNT(*)
        END,
        2
    ) AS value
    FROM customers_360
    """)
 
    high_churn_row = fetch_one("""
    SELECT COUNT(*) AS count
    FROM customers_360
    WHERE LOWER(TRIM(churn_risk_level)) = 'high'
    """)
 
    campaign_eligible_row = fetch_one("""
    SELECT COUNT(*) AS count
    FROM customers_360
    WHERE
        COALESCE(campaign_eligible_whatsapp, 0) = 1
        OR COALESCE(campaign_eligible_sms, 0) = 1
        OR COALESCE(campaign_eligible_email, 0) = 1
        OR COALESCE(campaign_eligible_app, 0) = 1
    """)
 
    total_sales_row = fetch_one("""
    SELECT ROUND(SUM(COALESCE(total_sales, 0)), 2) AS value
    FROM customers_360
    """)
 
    whatsapp_reachable_row = fetch_one("""
    SELECT COUNT(*) AS count
    FROM customers_360
    WHERE COALESCE(whatsapp_consent, 0) = 1
      AND COALESCE(do_not_contact, 0) = 0
    """)
 
    missing_emails_row = fetch_one("""
    SELECT COUNT(*) AS count
    FROM customers_360
    WHERE email IS NULL
       OR TRIM(email) = ''
    """)
 
    total_campaigns_row = fetch_one("""
    SELECT COUNT(*) AS count
    FROM crm_campaigns
    """)
 
    open_tickets_row = fetch_one("""
    SELECT COUNT(*) AS count
    FROM customer_service_tickets
    WHERE status NOT IN ('Resolved', 'Closed')
    """)
 
    total_customers = safe_count(total_customers_row)
    member_count = safe_count(members_row)
 
    member_percentage = round(
        (member_count / total_customers) * 100,
        2
    ) if total_customers else 0
 
    customer_segments = fetch_all("""
    SELECT
        COALESCE(NULLIF(TRIM(customer_segment), ''), 'Unknown') AS label,
        COUNT(*) AS value
    FROM customers_360
    GROUP BY COALESCE(NULLIF(TRIM(customer_segment), ''), 'Unknown')
    ORDER BY value DESC
    LIMIT 10
    """)
 
    churn_distribution = fetch_all("""
    SELECT
        COALESCE(NULLIF(TRIM(churn_risk_level), ''), 'Unknown') AS label,
        COUNT(*) AS value
    FROM customers_360
    GROUP BY COALESCE(NULLIF(TRIM(churn_risk_level), ''), 'Unknown')
    ORDER BY
        CASE LOWER(label)
            WHEN 'low' THEN 1
            WHEN 'medium' THEN 2
            WHEN 'high' THEN 3
            ELSE 4
        END
    """)
 
    membership_tiers = fetch_all("""
    SELECT
        COALESCE(NULLIF(TRIM(membership_tier), ''), 'Non-member') AS label,
        COUNT(*) AS value
    FROM customers_360
    GROUP BY COALESCE(NULLIF(TRIM(membership_tier), ''), 'Non-member')
    ORDER BY value DESC
    """)
 
    top_cities = fetch_all("""
    SELECT
        COALESCE(NULLIF(TRIM(customer_city), ''), 'Unknown') AS label,
        COUNT(*) AS value
    FROM customers_360
    GROUP BY COALESCE(NULLIF(TRIM(customer_city), ''), 'Unknown')
    ORDER BY value DESC
    LIMIT 10
    """)
 
    consent_reachability_row = fetch_one("""
    SELECT
        SUM(
            CASE
                WHEN COALESCE(whatsapp_consent, 0) = 1
                 AND COALESCE(do_not_contact, 0) = 0
                THEN 1 ELSE 0
            END
        ) AS whatsapp,
 
        SUM(
            CASE
                WHEN COALESCE(sms_consent, 0) = 1
                 AND COALESCE(do_not_contact, 0) = 0
                THEN 1 ELSE 0
            END
        ) AS sms,
 
        SUM(
            CASE
                WHEN COALESCE(email_consent, 0) = 1
                 AND COALESCE(do_not_contact, 0) = 0
                THEN 1 ELSE 0
            END
        ) AS email,
 
        SUM(
            CASE
                WHEN COALESCE(app_notification_consent, 0) = 1
                 AND COALESCE(do_not_contact, 0) = 0
                THEN 1 ELSE 0
            END
        ) AS app
    FROM customers_360
    """)
 
    consent_reachability = [
        {"label": "WhatsApp", "value": safe_number(consent_reachability_row, "whatsapp")},
        {"label": "SMS", "value": safe_number(consent_reachability_row, "sms")},
        {"label": "Email", "value": safe_number(consent_reachability_row, "email")},
        {"label": "App", "value": safe_number(consent_reachability_row, "app")}
    ]
 
    campaign_status = fetch_all("""
    SELECT
        COALESCE(NULLIF(TRIM(status), ''), 'Unknown') AS label,
        COUNT(*) AS value
    FROM crm_campaigns
    GROUP BY COALESCE(NULLIF(TRIM(status), ''), 'Unknown')
    ORDER BY value DESC
    """)
 
    campaign_performance_row = fetch_one("""
    SELECT
        COUNT(*) AS total_messages,
 
        SUM(
            CASE
                WHEN COALESCE(opened, 0) = 1
                THEN 1 ELSE 0
            END
        ) AS opened,
 
        SUM(
            CASE
                WHEN COALESCE(clicked, 0) = 1
                THEN 1 ELSE 0
            END
        ) AS clicked,
 
        SUM(
            CASE
                WHEN COALESCE(converted, 0) = 1
                THEN 1 ELSE 0
            END
        ) AS converted,
 
        ROUND(
            SUM(COALESCE(revenue, 0)),
            2
        ) AS revenue
    FROM crm_campaign_message_logs
    """)
 
    campaign_performance = [
        {"label": "Opened", "value": safe_number(campaign_performance_row, "opened")},
        {"label": "Clicked", "value": safe_number(campaign_performance_row, "clicked")},
        {"label": "Converted", "value": safe_number(campaign_performance_row, "converted")},
        {"label": "Revenue", "value": safe_number(campaign_performance_row, "revenue")}
    ]
 
    recent_campaigns = fetch_all("""
    SELECT
        c.campaign_id,
        c.campaign_name,
        c.campaign_type,
        c.business_channel,
        c.demo_platform,
        c.target_segment,
        c.status,
        c.total_audience,
        c.eligible_count,
        c.sent_count,
        c.failed_count,
        c.created_by,
        c.created_at,
 
        ROUND(
            COALESCE(
                (
                    SELECT SUM(COALESCE(l.revenue, 0))
                    FROM crm_campaign_message_logs l
                    WHERE l.campaign_id = c.campaign_id
                ),
                0
            ),
            2
        ) AS revenue
 
    FROM crm_campaigns c
    ORDER BY c.created_at DESC
    LIMIT 5
    """)
 
    ticket_status = fetch_all("""
    SELECT
        COALESCE(NULLIF(TRIM(status), ''), 'Unknown') AS label,
        COUNT(*) AS value
    FROM customer_service_tickets
    GROUP BY COALESCE(NULLIF(TRIM(status), ''), 'Unknown')
    ORDER BY value DESC
    """)
 
    sla_distribution = fetch_all("""
    SELECT
        COALESCE(NULLIF(TRIM(sla_status), ''), 'Unknown') AS label,
        COUNT(*) AS value
    FROM customer_service_tickets
    GROUP BY COALESCE(NULLIF(TRIM(sla_status), ''), 'Unknown')
    ORDER BY value DESC
    """)
 
    sla_summary_row = fetch_one("""
    SELECT
        COUNT(*) AS total,
 
        SUM(
            CASE
                WHEN LOWER(TRIM(COALESCE(sla_status, '')))
                     IN ('within sla', 'on track', 'met')
                THEN 1
                ELSE 0
            END
        ) AS compliant
    FROM customer_service_tickets
    """)
 
    total_sla_tickets = safe_count(sla_summary_row, "total")
    compliant_sla_tickets = safe_count(sla_summary_row, "compliant")
 
    sla_compliance_percentage = round(
        (compliant_sla_tickets / total_sla_tickets) * 100,
        2
    ) if total_sla_tickets else 0
 
    ticket_trend = fetch_all("""
    SELECT
        normalized_date AS label,
        SUM(created_count) AS created,
        SUM(resolved_count) AS resolved,
        SUM(escalated_count) AS escalated
    FROM (
        SELECT
            CASE
                WHEN created_on GLOB '??-??-????'
                THEN
                    SUBSTR(created_on, 7, 4)
                    || '-'
                    || SUBSTR(created_on, 4, 2)
                    || '-'
                    || SUBSTR(created_on, 1, 2)
                ELSE SUBSTR(created_on, 1, 10)
            END AS normalized_date,
 
            1 AS created_count,
 
            CASE
                WHEN status IN ('Resolved', 'Closed')
                THEN 1
                ELSE 0
            END AS resolved_count,
 
            CASE
                WHEN status = 'Escalated'
                THEN 1
                ELSE 0
            END AS escalated_count
 
        FROM customer_service_tickets
        WHERE created_on IS NOT NULL
          AND TRIM(created_on) != ''
    )
    GROUP BY normalized_date
    ORDER BY normalized_date DESC
    LIMIT 7
    """)
 
    ticket_trend.reverse()
 
    recent_tickets = fetch_all("""
    SELECT
        ticket_id,
        customer_id,
        customer_name,
        linked_order_id,
        issue_category,
        priority,
        status,
        assigned_agent_id,
        assigned_to,
        sla_status,
        sla_due,
        channel,
        created_on,
        last_updated
    FROM customer_service_tickets
    ORDER BY last_updated DESC, created_on DESC
    LIMIT 5
    """)
 
    high_churn_customers = fetch_all("""
    SELECT
        customer_id,
        crm_customer_key,
        customer_name,
        membership_tier,
        customer_segment,
        churn_risk_level,
        ROUND(COALESCE(total_sales, 0), 2) AS total_sales,
        ROUND(COALESCE(estimated_clv, 0), 2) AS estimated_clv
    FROM customers_360
    WHERE LOWER(TRIM(churn_risk_level)) IN ('high', 'medium')
    ORDER BY
        CASE LOWER(TRIM(churn_risk_level))
            WHEN 'high' THEN 1
            WHEN 'medium' THEN 2
            ELSE 3
        END,
        estimated_clv DESC
    LIMIT 10
    """)
 
    data_quality_row = fetch_one("""
    SELECT
        COUNT(*) AS total_records,
 
        SUM(
            CASE
                WHEN email IS NULL OR TRIM(email) = ''
                THEN 1 ELSE 0
            END
        ) AS missing_email,
 
        SUM(
            CASE
                WHEN phone_number IS NULL
                  OR TRIM(phone_number) = ''
                THEN 1 ELSE 0
            END
        ) AS missing_phone,
 
        SUM(
            CASE
                WHEN email IS NOT NULL
                 AND TRIM(email) != ''
                 AND phone_number IS NOT NULL
                 AND TRIM(phone_number) != ''
                 AND customer_name IS NOT NULL
                 AND TRIM(customer_name) != ''
                THEN 1 ELSE 0
            END
        ) AS good_records
    FROM customers_360
    """)
 
    total_quality_records = safe_count(data_quality_row, "total_records")
    missing_email_count = safe_count(data_quality_row, "missing_email")
    missing_phone_count = safe_count(data_quality_row, "missing_phone")
    good_records_count = safe_count(data_quality_row, "good_records")
 
    average_data_quality = round(
        (good_records_count / total_quality_records) * 100,
        2
    ) if total_quality_records else 0
 
    data_quality = [
        {"label": "Missing Email", "value": missing_email_count},
        {"label": "Missing Phone", "value": missing_phone_count},
        {"label": "Good Records", "value": good_records_count}
    ]
 
    loyalty_points_row = fetch_one("""
    SELECT
        SUM(COALESCE(points_balance, 0)) AS points_balance
    FROM customers_360
    """)
 
    response = {
        "success": True,
        "summary": {
            "total_customers": total_customers,
            "members": member_count,
            "member_percentage": member_percentage,
            "avg_clv": safe_number(avg_clv_row),
            "repeat_purchase_rate": safe_number(repeat_purchase_row),
            "high_churn_customers": safe_count(high_churn_row),
            "campaign_eligible_customers": safe_count(campaign_eligible_row),
            "total_sales": safe_number(total_sales_row),
            "open_service_tickets": safe_count(open_tickets_row),
            "total_campaigns": safe_count(total_campaigns_row),
            "whatsapp_reachable": safe_count(whatsapp_reachable_row),
            "missing_emails": missing_email_count,
            "average_data_quality": average_data_quality,
            "sla_compliance_percentage": sla_compliance_percentage
        },
        "charts": {
            "customer_segments": customer_segments,
            "churn_distribution": churn_distribution,
            "membership_tiers": membership_tiers,
            "top_cities": top_cities,
            "consent_reachability": consent_reachability,
            "campaign_status": campaign_status,
            "campaign_performance": campaign_performance,
            "ticket_status": ticket_status,
            "ticket_trend": ticket_trend,
            "sla_distribution": sla_distribution,
            "data_quality": data_quality
        },
        "loyalty": {
            "points_balance": safe_number(
                loyalty_points_row,
                "points_balance"
            )
        },
        "tables": {
            "recent_campaigns": recent_campaigns,
            "recent_tickets": recent_tickets,
            "high_churn_customers": high_churn_customers
        },
        "metadata": {
            "age_chart_available": False,
            "age_chart_reason": (
                "Age, date_of_birth, or age_group is not available "
                "in the confirmed customers_360 schema."
            ),
            "data_source": "SQLite",
            "live": True
        }
    }

    cache.set(
        "dashboard:summary",
        response,
        ttl_seconds=60
    )

    return response