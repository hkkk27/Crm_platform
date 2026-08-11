from fastapi import APIRouter, Depends, HTTPException
from app.db.sqlite_client import fetch_all, fetch_one, execute_query
from app.core.security import get_current_user, require_permission
from app.services.audit_service import create_audit_log

router = APIRouter(prefix="/consents", tags=["Consents"])


@router.get("")
def get_consent_list(user=Depends(get_current_user)):
    require_permission(user, "consent")

    rows = fetch_all("""
    SELECT
        customer_id,
        crm_customer_key,
        customer_name,
        whatsapp_consent,
        sms_consent,
        email_consent,
        app_notification_consent,
        personalization_consent,
        do_not_contact,
        consent_source,
        consent_given_date,
        consent_withdrawn_date,
        preferred_campaign_channel
    FROM customers_360
    LIMIT 500
    """)

    create_audit_log(
        user_email=user["sub"],
        user_role=user["role"],
        action="View consent list",
        object_type="Consent",
        object_id="ALL",
        status="Allowed",
        details="Consent list viewed"
    )

    return {
        "success": True,
        "count": len(rows),
        "data": rows
    }


@router.get("/{customer_id}")
def get_customer_consent(customer_id: str, user=Depends(get_current_user)):
    require_permission(user, "consent")

    consent = fetch_one("""
    SELECT
        customer_id,
        crm_customer_key,
        customer_name,
        whatsapp_consent,
        sms_consent,
        email_consent,
        app_notification_consent,
        personalization_consent,
        do_not_contact,
        consent_source,
        consent_given_date,
        consent_withdrawn_date,
        preferred_campaign_channel
    FROM customers_360
    WHERE customer_id = ?
    """, (customer_id,))

    if not consent:
        raise HTTPException(status_code=404, detail="Consent record not found")

    create_audit_log(
        user_email=user["sub"],
        user_role=user["role"],
        action="View customer consent",
        object_type="Consent",
        object_id=customer_id,
        status="Allowed",
        details="Customer consent viewed"
    )

    return {
        "success": True,
        "data": consent
    }


@router.put("/{customer_id}")
def update_customer_consent(customer_id: str, payload: dict, user=Depends(get_current_user)):
    require_permission(user, "consent")

    allowed_fields = [
        "whatsapp_consent",
        "sms_consent",
        "email_consent",
        "app_notification_consent",
        "personalization_consent",
        "do_not_contact",
        "consent_source",
        "consent_withdrawn_date",
        "preferred_campaign_channel"
    ]

    update_data = {
        key: value
        for key, value in payload.items()
        if key in allowed_fields
    }

    if not update_data:
        raise HTTPException(status_code=400, detail="No valid consent fields provided")

    existing = fetch_one("""
    SELECT customer_id
    FROM customers_360
    WHERE customer_id = ?
    """, (customer_id,))

    if not existing:
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
        action="Update customer consent",
        object_type="Consent",
        object_id=customer_id,
        status="Allowed",
        details=str(update_data)
    )

    return {
        "success": True,
        "message": "Consent updated successfully",
        "updated_fields": update_data
    }


@router.put("/{customer_id}/withdraw")
def withdraw_customer_consent(customer_id: str, user=Depends(get_current_user)):
    require_permission(user, "consent")

    existing = fetch_one("""
    SELECT customer_id
    FROM customers_360
    WHERE customer_id = ?
    """, (customer_id,))

    if not existing:
        raise HTTPException(status_code=404, detail="Customer not found")

    execute_query("""
    UPDATE customers_360
    SET
        whatsapp_consent = 0,
        sms_consent = 0,
        email_consent = 0,
        app_notification_consent = 0,
        personalization_consent = 0,
        do_not_contact = 1,
        consent_withdrawn_date = DATE('now')
    WHERE customer_id = ?
    """, (customer_id,))

    create_audit_log(
        user_email=user["sub"],
        user_role=user["role"],
        action="Withdraw all customer consent",
        object_type="Consent",
        object_id=customer_id,
        status="Allowed",
        details="All communication consent withdrawn and Do Not Contact enabled"
    )

    return {
        "success": True,
        "message": "Consent withdrawn successfully and customer marked as Do Not Contact"
    }


@router.put("/{customer_id}/withdraw-channel/{channel}")
def withdraw_channel_consent(customer_id: str, channel: str, user=Depends(get_current_user)):
    require_permission(user, "consent")

    existing = fetch_one("""
    SELECT customer_id
    FROM customers_360
    WHERE customer_id = ?
    """, (customer_id,))

    if not existing:
        raise HTTPException(status_code=404, detail="Customer not found")

    channel_map = {
        "whatsapp": "whatsapp_consent",
        "sms": "sms_consent",
        "email": "email_consent",
        "app": "app_notification_consent",
        "personalization": "personalization_consent"
    }

    channel_key = channel.lower()

    if channel_key not in channel_map:
        raise HTTPException(
            status_code=400,
            detail="Invalid channel. Use whatsapp, sms, email, app, or personalization."
        )

    column_name = channel_map[channel_key]

    execute_query(
        f"""
        UPDATE customers_360
        SET {column_name} = 0
        WHERE customer_id = ?
        """,
        (customer_id,)
    )

    create_audit_log(
        user_email=user["sub"],
        user_role=user["role"],
        action=f"Withdraw {channel_key} consent",
        object_type="Consent",
        object_id=customer_id,
        status="Allowed",
        details=f"{channel_key} consent withdrawn only"
    )

    return {
        "success": True,
        "message": f"{channel_key} consent withdrawn successfully",
        "customer_id": customer_id,
        "withdrawn_channel": channel_key
    }
