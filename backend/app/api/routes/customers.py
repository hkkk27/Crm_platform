

from fastapi import APIRouter, Depends, HTTPException
from app.db.sqlite_client import fetch_all, fetch_one, execute_query
from app.core.security import get_current_user, require_permission
from app.services.audit_service import create_audit_log
from app.services.customer_profile_service import (
    apply_customer_masking,
    build_customer_summary,
    build_membership_summary,
    build_purchase_summary,
    build_segmentation_summary,
)

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("")
def get_customers(user=Depends(get_current_user)):
    require_permission(user, "customers")

    rows = fetch_all("""
    SELECT
        customer_id,
        crm_customer_key,
        customer_name,
        phone_number,
        masked_phone_number,
        email,
        masked_email,
        customer_city,
        customer_state,
        product_category,
        membership_status,
        membership_tier,
        customer_segment,
        total_sales,
        estimated_clv,
        churn_risk_level,
        potential_member_score,
        whatsapp_consent,
        sms_consent,
        email_consent,
        app_notification_consent,
        personalization_consent,
        do_not_contact
    FROM customers_360
    LIMIT 500
    """)

    masked_rows = []

    for row in rows:
        masked_rows.append(apply_customer_masking(row, user["role"]))

    create_audit_log(
        user_email=user["sub"],
        user_role=user["role"],
        action="View customer list",
        object_type="Customer",
        object_id="ALL",
        status="Allowed",
        details="Customer list viewed"
    )

    return {
        "success": True,
        "count": len(masked_rows),
        "data": masked_rows
    }


@router.get("/{customer_id}/profile")
def get_customer_profile(customer_id: str, user=Depends(get_current_user)):
    require_permission(user, "customers")

    customer = fetch_one("""
    SELECT *
    FROM customers_360
    WHERE customer_id = ?
    """, (customer_id,))

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    consent = fetch_one("""
    SELECT *
    FROM consents
    WHERE customer_id = ?
    """, (customer_id,))

    app_activity = None

    campaign_history = fetch_all("""
    SELECT *
    FROM campaign_responses
    WHERE customer_id = ?
    LIMIT 20
    """, (customer_id,))

    masked_customer = apply_customer_masking(customer, user["role"])

    create_audit_log(
        user_email=user["sub"],
        user_role=user["role"],
        action="View customer profile",
        object_type="Customer",
        object_id=customer_id,
        status="Allowed",
        details="Customer 360 profile viewed"
    )

    return {
        "success": True,
        "customer_id": customer_id,
        "customer_summary": build_customer_summary(masked_customer),
        "purchase_summary": build_purchase_summary(customer),
        "membership_summary": build_membership_summary(customer),
        "segmentation_summary": build_segmentation_summary(customer),
        "consent": consent,
        "app_activity": app_activity,
        "campaign_history": campaign_history
    }


@router.put("/{customer_id}/profile")
def update_customer_profile(customer_id: str, payload: dict, user=Depends(get_current_user)):
    require_permission(user, "customers")

    allowed_update_fields = [
        "customer_name",
        "phone_number",
        "email",
        "customer_city",
        "customer_state",
        "preferred_category"
    ]

    update_data = {
        key: value
        for key, value in payload.items()
        if key in allowed_update_fields
    }

    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields provided for update")

    existing_customer = fetch_one("""
    SELECT customer_id
    FROM customers_360
    WHERE customer_id = ?
    """, (customer_id,))

    if not existing_customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    set_clause = ", ".join([f"{field} = ?" for field in update_data.keys()])
    values = list(update_data.values())
    values.append(customer_id)

    execute_query(
        f"""
        UPDATE customers_360
        SET {set_clause}
        WHERE customer_id = ?
        """,
        tuple(values)
    )

    create_audit_log(
        user_email=user["sub"],
        user_role=user["role"],
        action="Update customer profile",
        object_type="Customer",
        object_id=customer_id,
        status="Allowed",
        details=str(update_data)
    )

    return {
        "success": True,
        "message": "Customer profile updated successfully",
        "updated_fields": update_data
    }


@router.get("/{customer_id}/timeline")
def get_customer_timeline(customer_id: str, user=Depends(get_current_user)):
    require_permission(user, "customers")

    customer = fetch_one("""
    SELECT *
    FROM customers_360
    WHERE customer_id = ?
    """, (customer_id,))

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    campaign_events = fetch_all("""
    SELECT
        campaign_id,
        sent_status,
        opened,
        clicked,
        converted,
        revenue
    FROM campaign_responses
    WHERE customer_id = ?
    LIMIT 20
    """, (customer_id,))

    audit_events = fetch_all("""
    SELECT
        action,
        user_email,
        user_role,
        created_at,
        details
    FROM audit_logs
    WHERE object_id = ?
    ORDER BY created_at DESC
    LIMIT 20
    """, (customer_id,))

    timeline = []

    if customer.get("last_purchase_date"):
        timeline.append({
            "type": "Purchase",
            "date": customer.get("last_purchase_date"),
            "description": f"Last purchase recorded. Category: {customer.get('product_category')}"
        })

    if customer.get("membership_status"):
        timeline.append({
            "type": "Membership",
            "date": customer.get("membership_expiry_date"),
            "description": f"Membership status: {customer.get('membership_status')}, Tier: {customer.get('membership_tier')}"
        })

    if customer.get("consent_given_date"):
        timeline.append({
            "type": "Consent",
            "date": customer.get("consent_given_date"),
            "description": f"Consent source: {customer.get('consent_source')}"
        })

    for event in campaign_events:
        timeline.append({
            "type": "Campaign",
            "date": "N/A",
            "description": (
                f"Campaign {event.get('campaign_id')} - "
                f"Status: {event.get('sent_status')}, "
                f"Opened: {event.get('opened')}, "
                f"Clicked: {event.get('clicked')}, "
                f"Converted: {event.get('converted')}, "
                f"Revenue: {event.get('revenue')}"
            )
        })

    for event in audit_events:
        timeline.append({
            "type": "Audit",
            "date": event.get("created_at"),
            "description": f"{event.get('action')} by {event.get('user_email')} ({event.get('user_role')})"
        })

    create_audit_log(
        user_email=user["sub"],
        user_role=user["role"],
        action="View customer timeline",
        object_type="Customer",
        object_id=customer_id,
        status="Allowed",
        details="Customer timeline viewed"
    )

    return {
        "success": True,
        "customer_id": customer_id,
        "timeline_count": len(timeline),
        "timeline": timeline
    }
    require_permission(user, "customers")

    customer = fetch_one("""
    SELECT *
    FROM customers_360
    WHERE customer_id = ?
    """, (customer_id,))

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    campaign_events = fetch_all("""
    SELECT
        campaign_id,
        campaign_name,
        channel,
        sent_status,
        opened,
        clicked,
        converted,
        campaign_revenue,
        event_date
    FROM campaign_responses
    WHERE customer_id = ?
    LIMIT 20
    """, (customer_id,))

    audit_events = fetch_all("""
    SELECT
        action,
        user_email,
        user_role,
        created_at,
        details
    FROM audit_logs
    WHERE object_id = ?
    ORDER BY created_at DESC
    LIMIT 20
    """, (customer_id,))

    timeline = []

    if customer.get("last_purchase_date"):
        timeline.append({
            "type": "Purchase",
            "date": customer.get("last_purchase_date"),
            "description": f"Last purchase recorded. Category: {customer.get('product_category')}"
        })

    if customer.get("membership_status"):
        timeline.append({
            "type": "Membership",
            "date": customer.get("membership_expiry_date"),
            "description": f"Membership tier: {customer.get('membership_tier')}"
        })

    for event in campaign_events:
        timeline.append({
            "type": "Campaign",
            "date": event.get("event_date"),
            "description": f"{event.get('campaign_name')} via {event.get('channel')} - {event.get('sent_status')}"
        })

    for event in audit_events:
        timeline.append({
            "type": "Audit",
            "date": event.get("created_at"),
            "description": f"{event.get('action')} by {event.get('user_email')}"
        })

    create_audit_log(
        user_email=user["sub"],
        user_role=user["role"],
        action="View customer timeline",
        object_type="Customer",
        object_id=customer_id,
        status="Allowed",
        details="Customer timeline viewed"
    )

    return {
        "success": True,
        "customer_id": customer_id,
        "timeline": timeline
    }