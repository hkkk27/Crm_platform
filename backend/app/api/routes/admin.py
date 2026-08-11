# import csv
# import io
# import uuid

# from fastapi import APIRouter, Depends, HTTPException, Query
# from fastapi.responses import StreamingResponse

# from app.core.security import get_current_user, require_permission
# from app.db.sqlite_client import execute_query, fetch_all, fetch_one
# from app.services.audit_service import create_audit_log

# router = APIRouter(prefix="/admin", tags=["Admin"])

# ALLOWED_USER_ROLES = {
#     "Admin",
#     "CRM Team",
#     "Store Team",
#     "Management",
#     "Customer Service",
#     "Security / IT",
# }
# ALLOWED_USER_STATUSES = {"Active", "Inactive"}
# ALLOWED_CAMPAIGN_STATUSES = {
#     "Draft", "Approved", "Running", "Active", "Paused", "Rejected",
#     "Completed", "Cancelled"
# }


# def _value(row, key, default=0):
#     if not row:
#         return default
#     value = row.get(key)
#     return default if value is None else value


# def _safe_page(page: int, page_size: int):
#     return max(page, 1), min(max(page_size, 1), 200)


# @router.get("/summary")
# def get_admin_summary(user=Depends(get_current_user)):
#     require_permission(user, "admin")

#     user_stats = fetch_one(
#         """
#         SELECT COUNT(*) AS total_users,
#                SUM(CASE WHEN LOWER(COALESCE(status, 'active')) = 'active' THEN 1 ELSE 0 END) AS active_users,
#                SUM(CASE WHEN LOWER(COALESCE(status, 'active')) != 'active' THEN 1 ELSE 0 END) AS inactive_users
#         FROM users
#         """
#     )
#     agent_stats = fetch_one(
#         """
#         SELECT COUNT(*) AS service_agents,
#                SUM(CASE WHEN LOWER(COALESCE(status, '')) IN ('available', 'online', 'active') THEN 1 ELSE 0 END) AS online_agents,
#                SUM(CASE WHEN LOWER(COALESCE(status, '')) NOT IN ('available', 'online', 'active') THEN 1 ELSE 0 END) AS offline_agents
#         FROM customer_service_agents
#         """
#     )
#     campaign_stats = fetch_one(
#         """
#         SELECT COUNT(*) AS crm_campaigns,
#                SUM(CASE WHEN LOWER(COALESCE(status, '')) IN ('active', 'running', 'approved') THEN 1 ELSE 0 END) AS active_campaigns,
#                SUM(CASE WHEN LOWER(COALESCE(status, '')) = 'draft' THEN 1 ELSE 0 END) AS draft_campaigns,
#                SUM(CASE WHEN LOWER(COALESCE(status, '')) = 'paused' THEN 1 ELSE 0 END) AS paused_campaigns
#         FROM crm_campaigns
#         """
#     )
#     ticket_stats = fetch_one(
#         """
#         SELECT SUM(CASE WHEN status NOT IN ('Resolved', 'Closed') THEN 1 ELSE 0 END) AS open_tickets,
#                SUM(CASE WHEN priority IN ('High', 'Critical') THEN 1 ELSE 0 END) AS high_priority_tickets
#         FROM customer_service_tickets
#         """
#     )
#     reset_stats = fetch_one(
#         """
#         SELECT COUNT(*) AS password_resets,
#                SUM(CASE WHEN COALESCE(used, 0) = 0 AND datetime(expires_at) > datetime('now') THEN 1 ELSE 0 END) AS pending_password_resets
#         FROM password_reset_codes
#         """
#     )
#     customer_stats = fetch_one(
#         """
#         SELECT COUNT(*) AS customer_360_records,
#                ROUND(AVG(COALESCE(data_quality_score, 0)), 2) AS data_quality_score
#         FROM customers_360
#         """
#     )

#     return {
#         "total_users": int(_value(user_stats, "total_users")),
#         "active_users": int(_value(user_stats, "active_users")),
#         "inactive_users": int(_value(user_stats, "inactive_users")),
#         "service_agents": int(_value(agent_stats, "service_agents")),
#         "online_agents": int(_value(agent_stats, "online_agents")),
#         "offline_agents": int(_value(agent_stats, "offline_agents")),
#         "crm_campaigns": int(_value(campaign_stats, "crm_campaigns")),
#         "active_campaigns": int(_value(campaign_stats, "active_campaigns")),
#         "draft_campaigns": int(_value(campaign_stats, "draft_campaigns")),
#         "paused_campaigns": int(_value(campaign_stats, "paused_campaigns")),
#         "open_tickets": int(_value(ticket_stats, "open_tickets")),
#         "high_priority_tickets": int(_value(ticket_stats, "high_priority_tickets")),
#         "password_resets": int(_value(reset_stats, "password_resets")),
#         "pending_password_resets": int(_value(reset_stats, "pending_password_resets")),
#         "customer_360_records": int(_value(customer_stats, "customer_360_records")),
#         "data_quality_score": float(_value(customer_stats, "data_quality_score", 0.0)),
#     }


# @router.get("/users")
# def get_admin_users(
#     page: int = Query(default=1, ge=1),
#     page_size: int = Query(default=50, ge=1, le=200),
#     user=Depends(get_current_user),
# ):
#     require_permission(user, "admin")
#     page, page_size = _safe_page(page, page_size)
#     total = int(_value(fetch_one("SELECT COUNT(*) AS count FROM users"), "count"))
#     offset = (page - 1) * page_size
#     items = fetch_all(
#         """
#         SELECT u.user_id, u.email, u.role, u.status,
#                (SELECT MAX(a.created_at) FROM audit_logs a WHERE LOWER(a.user_email) = LOWER(u.email)) AS last_activity
#         FROM users u
#         ORDER BY u.user_id
#         LIMIT ? OFFSET ?
#         """,
#         (page_size, offset),
#     )
#     return {"total": total, "page": page, "page_size": page_size, "items": items}


# @router.put("/users/{user_id}/role")
# def update_user_role(
#     user_id: int,
#     payload: dict,
#     user=Depends(get_current_user),
# ):
#     require_permission(user, "admin")
#     existing = fetch_one(
#         "SELECT user_id, email, role, status FROM users WHERE user_id = ?",
#         (user_id,),
#     )
#     if not existing:
#         raise HTTPException(status_code=404, detail="User not found")

#     role = str(payload.get("role") or existing.get("role")).strip()
#     status = str(payload.get("status") or existing.get("status")).strip()
#     if role not in ALLOWED_USER_ROLES:
#         raise HTTPException(status_code=400, detail="Invalid role")
#     if status not in ALLOWED_USER_STATUSES:
#         raise HTTPException(status_code=400, detail="Invalid user status")

#     if existing.get("email") == user.get("sub") and status == "Inactive":
#         raise HTTPException(status_code=400, detail="You cannot deactivate your own account")

#     execute_query(
#         "UPDATE users SET role = ?, status = ? WHERE user_id = ?",
#         (role, status, user_id),
#     )
#     details = (
#         f"Role changed from {existing.get('role')} to {role}; "
#         f"status changed from {existing.get('status')} to {status}"
#     )
#     create_audit_log(
#         user_email=user["sub"],
#         user_role=user["role"],
#         action="Updated user role and status",
#         object_type="users",
#         object_id=str(user_id),
#         status="Success",
#         details=details,
#     )
#     updated = fetch_one(
#         "SELECT user_id, email, role, status FROM users WHERE user_id = ?",
#         (user_id,),
#     )
#     return {"success": True, "message": "User updated successfully", "user": updated}


# @router.get("/agents")
# def get_admin_agents(
#     page: int = Query(default=1, ge=1),
#     page_size: int = Query(default=50, ge=1, le=200),
#     user=Depends(get_current_user),
# ):
#     require_permission(user, "admin")
#     page, page_size = _safe_page(page, page_size)
#     total = int(_value(fetch_one("SELECT COUNT(*) AS count FROM customer_service_agents"), "count"))
#     offset = (page - 1) * page_size
#     items = fetch_all(
#         """
#         SELECT a.agent_id, a.agent_name, a.agent_email, a.role, a.status,
#                COUNT(t.ticket_id) AS assigned_tickets,
#                ROUND(
#                    CASE WHEN COUNT(t.ticket_id) = 0 THEN 100.0
#                         ELSE 100.0 * SUM(CASE WHEN LOWER(COALESCE(t.sla_status, '')) IN ('met', 'on track', 'within sla') THEN 1 ELSE 0 END) / COUNT(t.ticket_id)
#                    END,
#                    2
#                ) AS sla_score
#         FROM customer_service_agents a
#         LEFT JOIN customer_service_tickets t ON t.assigned_agent_id = a.agent_id
#         GROUP BY a.agent_id, a.agent_name, a.agent_email, a.role, a.status
#         ORDER BY a.agent_name
#         LIMIT ? OFFSET ?
#         """,
#         (page_size, offset),
#     )
#     for item in items:
#         item["sla_score"] = f"{float(item.get('sla_score') or 0):.2f}%"
#     return {"total": total, "page": page, "page_size": page_size, "items": items}


# @router.post("/agents")
# def create_admin_agent(payload: dict, user=Depends(get_current_user)):
#     require_permission(user, "admin")
#     agent_name = str(payload.get("agent_name") or "").strip()
#     agent_email = str(payload.get("agent_email") or "").strip().lower()
#     role = str(payload.get("role") or "Support Agent").strip()
#     status = str(payload.get("status") or "Available").strip()
#     if not agent_name or not agent_email:
#         raise HTTPException(status_code=400, detail="agent_name and agent_email are required")
#     duplicate = fetch_one(
#         "SELECT agent_id FROM customer_service_agents WHERE LOWER(agent_email) = ?",
#         (agent_email,),
#     )
#     if duplicate:
#         raise HTTPException(status_code=409, detail="Agent email already exists")

#     agent_id = "AG-" + uuid.uuid4().hex[:8].upper()
#     execute_query(
#         """
#         INSERT INTO customer_service_agents (
#             agent_id, agent_name, agent_email, role, status
#         ) VALUES (?, ?, ?, ?, ?)
#         """,
#         (agent_id, agent_name, agent_email, role, status),
#     )
#     create_audit_log(
#         user_email=user["sub"],
#         user_role=user["role"],
#         action="Created customer service agent",
#         object_type="customer_service_agents",
#         object_id=agent_id,
#         status="Success",
#         details=f"Created agent {agent_name} ({agent_email})",
#     )
#     agent = fetch_one(
#         "SELECT agent_id, agent_name, agent_email, role, status FROM customer_service_agents WHERE agent_id = ?",
#         (agent_id,),
#     )
#     return {"success": True, "message": "Agent created successfully", "agent": agent}


# @router.get("/password-resets")
# def get_password_resets(
#     page: int = Query(default=1, ge=1),
#     page_size: int = Query(default=50, ge=1, le=200),
#     user=Depends(get_current_user),
# ):
#     require_permission(user, "admin")
#     page, page_size = _safe_page(page, page_size)
#     total = int(_value(fetch_one("SELECT COUNT(*) AS count FROM password_reset_codes"), "count"))
#     offset = (page - 1) * page_size
#     items = fetch_all(
#         """
#         SELECT reset_id, email, created_at, expires_at,
#                CASE WHEN COALESCE(used, 0) = 1 THEN 1 ELSE 0 END AS used
#         FROM password_reset_codes
#         ORDER BY created_at DESC, reset_id DESC
#         LIMIT ? OFFSET ?
#         """,
#         (page_size, offset),
#     )
#     return {"total": total, "page": page, "page_size": page_size, "items": items}


# @router.get("/campaigns")
# def get_admin_campaigns(
#     page: int = Query(default=1, ge=1),
#     page_size: int = Query(default=50, ge=1, le=200),
#     user=Depends(get_current_user),
# ):
#     require_permission(user, "admin")
#     page, page_size = _safe_page(page, page_size)
#     total = int(_value(fetch_one("SELECT COUNT(*) AS count FROM crm_campaigns"), "count"))
#     offset = (page - 1) * page_size
#     items = fetch_all(
#         """
#         SELECT campaign_id, campaign_name,
#                business_channel AS channel,
#                status,
#                COALESCE(total_audience, 0) AS audience,
#                COALESCE(sent_count, 0) AS sent,
#                COALESCE(failed_count, 0) AS failed,
#                created_by AS owner
#         FROM crm_campaigns
#         ORDER BY created_at DESC
#         LIMIT ? OFFSET ?
#         """,
#         (page_size, offset),
#     )
#     return {"total": total, "page": page, "page_size": page_size, "items": items}


# @router.put("/campaigns/{campaign_id}/status")
# def update_campaign_status(
#     campaign_id: str,
#     payload: dict,
#     user=Depends(get_current_user),
# ):
#     require_permission(user, "admin")
#     existing = fetch_one(
#         "SELECT campaign_id, campaign_name, status FROM crm_campaigns WHERE campaign_id = ?",
#         (campaign_id,),
#     )
#     if not existing:
#         raise HTTPException(status_code=404, detail="Campaign not found")
#     status = str(payload.get("status") or "").strip()
#     if status not in ALLOWED_CAMPAIGN_STATUSES:
#         raise HTTPException(status_code=400, detail="Invalid campaign status")

#     execute_query(
#         "UPDATE crm_campaigns SET status = ? WHERE campaign_id = ?",
#         (status, campaign_id),
#     )
#     create_audit_log(
#         user_email=user["sub"],
#         user_role=user["role"],
#         action="Updated campaign status",
#         object_type="crm_campaigns",
#         object_id=campaign_id,
#         status="Success",
#         details=f"Campaign status changed from {existing.get('status')} to {status}",
#     )
#     return {
#         "success": True,
#         "message": "Campaign status updated successfully",
#         "campaign_id": campaign_id,
#         "status": status,
#     }


# def _build_data_health():
#     customer = fetch_one(
#         """
#         SELECT COUNT(*) AS records,
#                SUM(CASE WHEN COALESCE(duplicate_customer_flag, 0) = 1 THEN 1 ELSE 0 END) AS duplicate_count,
#                SUM(CASE WHEN COALESCE(missing_email_flag, 0) = 1 THEN 1 ELSE 0 END) AS missing_email_count,
#                SUM(CASE WHEN COALESCE(missing_phone_flag, 0) = 1 THEN 1 ELSE 0 END) AS missing_phone_count,
#                ROUND(AVG(COALESCE(data_quality_score, 0)), 2) AS quality_score
#         FROM customers_360
#         """
#     )
#     tickets = fetch_one(
#         """
#         SELECT COUNT(*) AS records,
#                SUM(CASE WHEN LOWER(COALESCE(sla_status, '')) IN ('breached', 'overdue') THEN 1 ELSE 0 END) AS issue_count
#         FROM customer_service_tickets
#         """
#     )
#     timeline = fetch_one(
#         """
#         SELECT COUNT(*) AS records,
#                SUM(CASE WHEN event_description IS NULL OR TRIM(event_description) = '' THEN 1 ELSE 0 END) AS issue_count
#         FROM customer_service_timeline
#         """
#     )
#     consent = fetch_one(
#         """
#         SELECT COUNT(*) AS records,
#                SUM(CASE WHEN COALESCE(do_not_contact, 0) = 1 THEN 1 ELSE 0 END) AS issue_count
#         FROM consents
#         """
#     )

#     customer_issue_count = max(
#         int(_value(customer, "duplicate_count")),
#         int(_value(customer, "missing_email_count")),
#         int(_value(customer, "missing_phone_count")),
#     )
#     customer_issue = "No major issue"
#     if customer_issue_count == int(_value(customer, "duplicate_count")) and customer_issue_count:
#         customer_issue = "Duplicate customer flags"
#     elif customer_issue_count == int(_value(customer, "missing_email_count")) and customer_issue_count:
#         customer_issue = "Missing email flags"
#     elif customer_issue_count:
#         customer_issue = "Missing phone flags"

#     def quality(records, issues):
#         records = int(records or 0)
#         issues = int(issues or 0)
#         return round(100.0 * max(records - issues, 0) / records, 2) if records else 100.0

#     return [
#         {
#             "area": "Customer 360",
#             "records": int(_value(customer, "records")),
#             "primary_issue": customer_issue,
#             "issue_count": customer_issue_count,
#             "quality_score": f"{float(_value(customer, 'quality_score', 0.0)):.2f}%",
#         },
#         {
#             "area": "Customer Service Tickets",
#             "records": int(_value(tickets, "records")),
#             "primary_issue": "SLA overdue or breached",
#             "issue_count": int(_value(tickets, "issue_count")),
#             "quality_score": f"{quality(_value(tickets, 'records'), _value(tickets, 'issue_count')):.2f}%",
#         },
#         {
#             "area": "Customer Service Timeline",
#             "records": int(_value(timeline, "records")),
#             "primary_issue": "Missing event descriptions",
#             "issue_count": int(_value(timeline, "issue_count")),
#             "quality_score": f"{quality(_value(timeline, 'records'), _value(timeline, 'issue_count')):.2f}%",
#         },
#         {
#             "area": "Consent Records",
#             "records": int(_value(consent, "records")),
#             "primary_issue": "Do-not-contact records",
#             "issue_count": int(_value(consent, "issue_count")),
#             "quality_score": f"{quality(_value(consent, 'records'), 0):.2f}%",
#         },
#     ]


# @router.get("/data-health")
# def get_data_health(user=Depends(get_current_user)):
#     require_permission(user, "admin")
#     return _build_data_health()


# @router.get("/data-health/export")
# def export_data_health(user=Depends(get_current_user)):
#     require_permission(user, "admin")
#     rows = _build_data_health()
#     stream = io.StringIO()
#     writer = csv.DictWriter(
#         stream,
#         fieldnames=["area", "records", "primary_issue", "issue_count", "quality_score"],
#     )
#     writer.writeheader()
#     writer.writerows(rows)
#     create_audit_log(
#         user_email=user["sub"],
#         user_role=user["role"],
#         action="Exported data health report",
#         object_type="customers_360",
#         object_id="DATA_HEALTH",
#         status="Success",
#         details="Admin downloaded the data-health CSV report",
#     )
#     return StreamingResponse(
#         iter([stream.getvalue()]),
#         media_type="text/csv",
#         headers={"Content-Disposition": "attachment; filename=data-health-report.csv"},
#     )
import csv
import io
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.core.security import get_current_user, require_permission
from app.db.sqlite_client import execute_query, fetch_all, fetch_one
from app.services.audit_service import create_audit_log
from app.services.cache_service import cache


router = APIRouter(prefix="/admin", tags=["Admin"])


ALLOWED_USER_ROLES = {
    "Admin",
    "CRM Team",
    "Store Team",
    "Management",
    "Customer Service",
    "Security / IT",
}

ALLOWED_USER_STATUSES = {
    "Active",
    "Inactive",
}

ALLOWED_CAMPAIGN_STATUSES = {
    "Draft",
    "Approved",
    "Running",
    "Active",
    "Paused",
    "Rejected",
    "Completed",
    "Cancelled",
}


def _value(row, key, default=0):
    if not row:
        return default

    value = row.get(key)

    return default if value is None else value


def _safe_page(page: int, page_size: int):
    return max(page, 1), min(max(page_size, 1), 200)


@router.get("/summary")
def get_admin_summary(user=Depends(get_current_user)):
    require_permission(user, "admin")

    cached_response = cache.get(
        "admin:summary"
    )

    if cached_response is not None:
        return cached_response

    user_stats = fetch_one(
        """
        SELECT COUNT(*) AS total_users,
               SUM(CASE WHEN LOWER(COALESCE(status, 'active')) = 'active' THEN 1 ELSE 0 END) AS active_users,
               SUM(CASE WHEN LOWER(COALESCE(status, 'active')) != 'active' THEN 1 ELSE 0 END) AS inactive_users
        FROM users
        """
    )

    agent_stats = fetch_one(
        """
        SELECT COUNT(*) AS service_agents,
               SUM(CASE WHEN LOWER(COALESCE(status, '')) IN ('available', 'online', 'active') THEN 1 ELSE 0 END) AS online_agents,
               SUM(CASE WHEN LOWER(COALESCE(status, '')) NOT IN ('available', 'online', 'active') THEN 1 ELSE 0 END) AS offline_agents
        FROM customer_service_agents
        """
    )

    campaign_stats = fetch_one(
        """
        SELECT COUNT(*) AS crm_campaigns,
               SUM(CASE WHEN LOWER(COALESCE(status, '')) IN ('active', 'running', 'approved') THEN 1 ELSE 0 END) AS active_campaigns,
               SUM(CASE WHEN LOWER(COALESCE(status, '')) = 'draft' THEN 1 ELSE 0 END) AS draft_campaigns,
               SUM(CASE WHEN LOWER(COALESCE(status, '')) = 'paused' THEN 1 ELSE 0 END) AS paused_campaigns
        FROM crm_campaigns
        """
    )

    ticket_stats = fetch_one(
        """
        SELECT SUM(CASE WHEN status NOT IN ('Resolved', 'Closed') THEN 1 ELSE 0 END) AS open_tickets,
               SUM(CASE WHEN priority IN ('High', 'Critical') THEN 1 ELSE 0 END) AS high_priority_tickets
        FROM customer_service_tickets
        """
    )

    reset_stats = fetch_one(
        """
        SELECT COUNT(*) AS password_resets,
               SUM(CASE WHEN COALESCE(used, 0) = 0 AND datetime(expires_at) > datetime('now') THEN 1 ELSE 0 END) AS pending_password_resets
        FROM password_reset_codes
        """
    )

    customer_stats = fetch_one(
        """
        SELECT COUNT(*) AS customer_360_records,
               ROUND(AVG(COALESCE(data_quality_score, 0)), 2) AS data_quality_score
        FROM customers_360
        """
    )

    response = {
        "total_users": int(_value(user_stats, "total_users")),
        "active_users": int(_value(user_stats, "active_users")),
        "inactive_users": int(_value(user_stats, "inactive_users")),
        "service_agents": int(_value(agent_stats, "service_agents")),
        "online_agents": int(_value(agent_stats, "online_agents")),
        "offline_agents": int(_value(agent_stats, "offline_agents")),
        "crm_campaigns": int(_value(campaign_stats, "crm_campaigns")),
        "active_campaigns": int(_value(campaign_stats, "active_campaigns")),
        "draft_campaigns": int(_value(campaign_stats, "draft_campaigns")),
        "paused_campaigns": int(_value(campaign_stats, "paused_campaigns")),
        "open_tickets": int(_value(ticket_stats, "open_tickets")),
        "high_priority_tickets": int(_value(ticket_stats, "high_priority_tickets")),
        "password_resets": int(_value(reset_stats, "password_resets")),
        "pending_password_resets": int(_value(reset_stats, "pending_password_resets")),
        "customer_360_records": int(_value(customer_stats, "customer_360_records")),
        "data_quality_score": float(_value(customer_stats, "data_quality_score", 0.0)),
    }

    cache.set(
        "admin:summary",
        response,
        ttl_seconds=30,
    )

    return response


@router.get("/users")
def get_admin_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    user=Depends(get_current_user),
):
    require_permission(user, "admin")

    page, page_size = _safe_page(page, page_size)

    total = int(
        _value(
            fetch_one("SELECT COUNT(*) AS count FROM users"),
            "count",
        )
    )

    offset = (page - 1) * page_size

    items = fetch_all(
        """
        SELECT u.user_id, u.email, u.role, u.status,
               (SELECT MAX(a.created_at) FROM audit_logs a WHERE LOWER(a.user_email) = LOWER(u.email)) AS last_activity
        FROM users u
        ORDER BY u.user_id
        LIMIT ? OFFSET ?
        """,
        (page_size, offset),
    )

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items,
    }


@router.put("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    payload: dict,
    user=Depends(get_current_user),
):
    require_permission(user, "admin")

    existing = fetch_one(
        "SELECT user_id, email, role, status FROM users WHERE user_id = ?",
        (user_id,),
    )

    if not existing:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    role = str(
        payload.get("role") or existing.get("role")
    ).strip()

    status = str(
        payload.get("status") or existing.get("status")
    ).strip()

    if role not in ALLOWED_USER_ROLES:
        raise HTTPException(
            status_code=400,
            detail="Invalid role",
        )

    if status not in ALLOWED_USER_STATUSES:
        raise HTTPException(
            status_code=400,
            detail="Invalid user status",
        )

    if existing.get("email") == user.get("sub") and status == "Inactive":
        raise HTTPException(
            status_code=400,
            detail="You cannot deactivate your own account",
        )

    execute_query(
        "UPDATE users SET role = ?, status = ? WHERE user_id = ?",
        (role, status, user_id),
    )

    details = (
        f"Role changed from {existing.get('role')} to {role}; "
        f"status changed from {existing.get('status')} to {status}"
    )

    create_audit_log(
        user_email=user["sub"],
        user_role=user["role"],
        action="Updated user role and status",
        object_type="users",
        object_id=str(user_id),
        status="Success",
        details=details,
    )

    cache.delete(
        "admin:summary"
    )

    cache.delete_prefix(
        "admin:users"
    )

    updated = fetch_one(
        "SELECT user_id, email, role, status FROM users WHERE user_id = ?",
        (user_id,),
    )

    return {
        "success": True,
        "message": "User updated successfully",
        "user": updated,
    }


@router.get("/agents")
def get_admin_agents(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    user=Depends(get_current_user),
):
    require_permission(user, "admin")

    page, page_size = _safe_page(page, page_size)

    total = int(
        _value(
            fetch_one(
                "SELECT COUNT(*) AS count FROM customer_service_agents"
            ),
            "count",
        )
    )

    offset = (page - 1) * page_size

    items = fetch_all(
        """
        SELECT a.agent_id, a.agent_name, a.agent_email, a.role, a.status,
               COUNT(t.ticket_id) AS assigned_tickets,
               ROUND(
                   CASE WHEN COUNT(t.ticket_id) = 0 THEN 100.0
                        ELSE 100.0 * SUM(CASE WHEN LOWER(COALESCE(t.sla_status, '')) IN ('met', 'on track', 'within sla') THEN 1 ELSE 0 END) / COUNT(t.ticket_id)
                   END,
                   2
               ) AS sla_score
        FROM customer_service_agents a
        LEFT JOIN customer_service_tickets t ON t.assigned_agent_id = a.agent_id
        GROUP BY a.agent_id, a.agent_name, a.agent_email, a.role, a.status
        ORDER BY a.agent_name
        LIMIT ? OFFSET ?
        """,
        (page_size, offset),
    )

    for item in items:
        item["sla_score"] = f"{float(item.get('sla_score') or 0):.2f}%"

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items,
    }


@router.post("/agents")
def create_admin_agent(
    payload: dict,
    user=Depends(get_current_user),
):
    require_permission(user, "admin")

    agent_name = str(
        payload.get("agent_name") or ""
    ).strip()

    agent_email = str(
        payload.get("agent_email") or ""
    ).strip().lower()

    role = str(
        payload.get("role") or "Support Agent"
    ).strip()

    status = str(
        payload.get("status") or "Available"
    ).strip()

    if not agent_name or not agent_email:
        raise HTTPException(
            status_code=400,
            detail="agent_name and agent_email are required",
        )

    duplicate = fetch_one(
        "SELECT agent_id FROM customer_service_agents WHERE LOWER(agent_email) = ?",
        (agent_email,),
    )

    if duplicate:
        raise HTTPException(
            status_code=409,
            detail="Agent email already exists",
        )

    agent_id = "AG-" + uuid.uuid4().hex[:8].upper()

    execute_query(
        """
        INSERT INTO customer_service_agents (
            agent_id, agent_name, agent_email, role, status
        ) VALUES (?, ?, ?, ?, ?)
        """,
        (
            agent_id,
            agent_name,
            agent_email,
            role,
            status,
        ),
    )

    create_audit_log(
        user_email=user["sub"],
        user_role=user["role"],
        action="Created customer service agent",
        object_type="customer_service_agents",
        object_id=agent_id,
        status="Success",
        details=f"Created agent {agent_name} ({agent_email})",
    )

    cache.delete(
        "admin:summary"
    )

    cache.delete_prefix(
        "admin:agents"
    )

    agent = fetch_one(
        "SELECT agent_id, agent_name, agent_email, role, status FROM customer_service_agents WHERE agent_id = ?",
        (agent_id,),
    )

    return {
        "success": True,
        "message": "Agent created successfully",
        "agent": agent,
    }


@router.get("/password-resets")
def get_password_resets(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    user=Depends(get_current_user),
):
    require_permission(user, "admin")

    page, page_size = _safe_page(page, page_size)

    total = int(
        _value(
            fetch_one(
                "SELECT COUNT(*) AS count FROM password_reset_codes"
            ),
            "count",
        )
    )

    offset = (page - 1) * page_size

    items = fetch_all(
        """
        SELECT reset_id, email, created_at, expires_at,
               CASE WHEN COALESCE(used, 0) = 1 THEN 1 ELSE 0 END AS used
        FROM password_reset_codes
        ORDER BY created_at DESC, reset_id DESC
        LIMIT ? OFFSET ?
        """,
        (page_size, offset),
    )

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items,
    }


@router.get("/campaigns")
def get_admin_campaigns(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    user=Depends(get_current_user),
):
    require_permission(user, "admin")

    page, page_size = _safe_page(page, page_size)

    total = int(
        _value(
            fetch_one("SELECT COUNT(*) AS count FROM crm_campaigns"),
            "count",
        )
    )

    offset = (page - 1) * page_size

    items = fetch_all(
        """
        SELECT campaign_id, campaign_name,
               business_channel AS channel,
               status,
               COALESCE(total_audience, 0) AS audience,
               COALESCE(sent_count, 0) AS sent,
               COALESCE(failed_count, 0) AS failed,
               created_by AS owner
        FROM crm_campaigns
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
        """,
        (page_size, offset),
    )

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items,
    }


@router.put("/campaigns/{campaign_id}/status")
def update_campaign_status(
    campaign_id: str,
    payload: dict,
    user=Depends(get_current_user),
):
    require_permission(user, "admin")

    existing = fetch_one(
        "SELECT campaign_id, campaign_name, status FROM crm_campaigns WHERE campaign_id = ?",
        (campaign_id,),
    )

    if not existing:
        raise HTTPException(
            status_code=404,
            detail="Campaign not found",
        )

    status = str(
        payload.get("status") or ""
    ).strip()

    if status not in ALLOWED_CAMPAIGN_STATUSES:
        raise HTTPException(
            status_code=400,
            detail="Invalid campaign status",
        )

    execute_query(
        "UPDATE crm_campaigns SET status = ? WHERE campaign_id = ?",
        (status, campaign_id),
    )

    create_audit_log(
        user_email=user["sub"],
        user_role=user["role"],
        action="Updated campaign status",
        object_type="crm_campaigns",
        object_id=campaign_id,
        status="Success",
        details=f"Campaign status changed from {existing.get('status')} to {status}",
    )

    cache.delete(
        "admin:summary"
    )

    cache.delete_prefix(
        "admin:campaigns"
    )

    cache.delete(
        "dashboard:summary"
    )

    return {
        "success": True,
        "message": "Campaign status updated successfully",
        "campaign_id": campaign_id,
        "status": status,
    }


def _build_data_health():
    customer = fetch_one(
        """
        SELECT COUNT(*) AS records,
               SUM(CASE WHEN COALESCE(duplicate_customer_flag, 0) = 1 THEN 1 ELSE 0 END) AS duplicate_count,
               SUM(CASE WHEN COALESCE(missing_email_flag, 0) = 1 THEN 1 ELSE 0 END) AS missing_email_count,
               SUM(CASE WHEN COALESCE(missing_phone_flag, 0) = 1 THEN 1 ELSE 0 END) AS missing_phone_count,
               ROUND(AVG(COALESCE(data_quality_score, 0)), 2) AS quality_score
        FROM customers_360
        """
    )

    tickets = fetch_one(
        """
        SELECT COUNT(*) AS records,
               SUM(CASE WHEN LOWER(COALESCE(sla_status, '')) IN ('breached', 'overdue') THEN 1 ELSE 0 END) AS issue_count
        FROM customer_service_tickets
        """
    )

    timeline = fetch_one(
        """
        SELECT COUNT(*) AS records,
               SUM(CASE WHEN event_description IS NULL OR TRIM(event_description) = '' THEN 1 ELSE 0 END) AS issue_count
        FROM customer_service_timeline
        """
    )

    consent = fetch_one(
        """
        SELECT COUNT(*) AS records,
               SUM(CASE WHEN COALESCE(do_not_contact, 0) = 1 THEN 1 ELSE 0 END) AS issue_count
        FROM consents
        """
    )

    customer_issue_count = max(
        int(_value(customer, "duplicate_count")),
        int(_value(customer, "missing_email_count")),
        int(_value(customer, "missing_phone_count")),
    )

    customer_issue = "No major issue"

    if customer_issue_count == int(_value(customer, "duplicate_count")) and customer_issue_count:
        customer_issue = "Duplicate customer flags"
    elif customer_issue_count == int(_value(customer, "missing_email_count")) and customer_issue_count:
        customer_issue = "Missing email flags"
    elif customer_issue_count:
        customer_issue = "Missing phone flags"

    def quality(records, issues):
        records = int(records or 0)
        issues = int(issues or 0)

        return round(
            100.0 * max(records - issues, 0) / records,
            2,
        ) if records else 100.0

    return [
        {
            "area": "Customer 360",
            "records": int(_value(customer, "records")),
            "primary_issue": customer_issue,
            "issue_count": customer_issue_count,
            "quality_score": f"{float(_value(customer, 'quality_score', 0.0)):.2f}%",
        },
        {
            "area": "Customer Service Tickets",
            "records": int(_value(tickets, "records")),
            "primary_issue": "SLA overdue or breached",
            "issue_count": int(_value(tickets, "issue_count")),
            "quality_score": f"{quality(_value(tickets, 'records'), _value(tickets, 'issue_count')):.2f}%",
        },
        {
            "area": "Customer Service Timeline",
            "records": int(_value(timeline, "records")),
            "primary_issue": "Missing event descriptions",
            "issue_count": int(_value(timeline, "issue_count")),
            "quality_score": f"{quality(_value(timeline, 'records'), _value(timeline, 'issue_count')):.2f}%",
        },
        {
            "area": "Consent Records",
            "records": int(_value(consent, "records")),
            "primary_issue": "Do-not-contact records",
            "issue_count": int(_value(consent, "issue_count")),
            "quality_score": f"{quality(_value(consent, 'records'), 0):.2f}%",
        },
    ]


@router.get("/data-health")
def get_data_health(
    user=Depends(get_current_user),
):
    require_permission(user, "admin")

    cached_response = cache.get(
        "admin:data-health"
    )

    if cached_response is not None:
        return cached_response

    response = _build_data_health()

    cache.set(
        "admin:data-health",
        response,
        ttl_seconds=60,
    )

    return response


@router.get("/data-health/export")
def export_data_health(user=Depends(get_current_user)):
    require_permission(user, "admin")

    rows = _build_data_health()

    stream = io.StringIO()

    writer = csv.DictWriter(
        stream,
        fieldnames=[
            "area",
            "records",
            "primary_issue",
            "issue_count",
            "quality_score",
        ],
    )

    writer.writeheader()
    writer.writerows(rows)

    create_audit_log(
        user_email=user["sub"],
        user_role=user["role"],
        action="Exported data health report",
        object_type="customers_360",
        object_id="DATA_HEALTH",
        status="Success",
        details="Admin downloaded the data-health CSV report",
    )

    return StreamingResponse(
        iter([stream.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=data-health-report.csv"
        },
    )