import uuid
import json
from fastapi import APIRouter, Depends, HTTPException
from app.db.sqlite_client import fetch_all, fetch_one, execute_query
from app.core.security import get_current_user, require_permission
from app.services.audit_service import create_audit_log
from app.services.campaign_service import (
    get_campaign_audience,
    filter_audience_by_consent,
    render_template,
    get_template,
    build_campaign_metrics
)
from app.services.webhook_service import (
    get_discord_webhook_for_campaign_type,
    send_discord_message
)

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])


@router.get("")
def get_campaigns(user=Depends(get_current_user)):
    require_permission(user, "campaigns")

    rows = fetch_all("""
    SELECT *
    FROM crm_campaigns
    ORDER BY created_at DESC
    """)

    return {
        "success": True,
        "count": len(rows),
        "data": rows
    }


@router.get("/templates")
def get_campaign_templates(user=Depends(get_current_user)):
    require_permission(user, "campaigns")

    rows = fetch_all("""
    SELECT *
    FROM crm_campaign_templates
    ORDER BY created_at DESC
    """)

    parsed_rows = []

    for row in rows:
        parsed = dict(row)
        try:
            parsed["template_json"] = json.loads(parsed["template_json"])
        except Exception:
            pass
        parsed_rows.append(parsed)

    return {
        "success": True,
        "count": len(parsed_rows),
        "data": parsed_rows
    }


@router.post("/templates")
def create_campaign_template(payload: dict, user=Depends(get_current_user)):
    require_permission(user, "campaigns")

    template_id = "TPL-" + str(uuid.uuid4())[:8].upper()

    template_name = payload.get("template_name")
    template_type = payload.get("template_type", "General")
    template_json = payload.get("template_json")

    if not template_name or not template_json:
        raise HTTPException(status_code=400, detail="template_name and template_json are required")

    execute_query("""
    INSERT INTO crm_campaign_templates
    (template_id, template_name, template_type, template_json, created_by)
    VALUES (?, ?, ?, ?, ?)
    """, (
        template_id,
        template_name,
        template_type,
        json.dumps(template_json),
        user["sub"]
    ))

    create_audit_log(
        user_email=user["sub"],
        user_role=user["role"],
        action="Create campaign template",
        object_type="CampaignTemplate",
        object_id=template_id,
        status="Allowed",
        details=template_name
    )

    return {
        "success": True,
        "message": "Campaign template created successfully",
        "template_id": template_id
    }


@router.post("")
def create_campaign(payload: dict, user=Depends(get_current_user)):
    require_permission(user, "campaigns")

    campaign_id = "CMP-" + str(uuid.uuid4())[:8].upper()

    campaign_name = payload.get("campaign_name")
    campaign_type = payload.get("campaign_type")
    business_channel = payload.get("business_channel")
    target_segment = payload.get("target_segment")
    template_id = payload.get("template_id")
    demo_platform = payload.get("demo_platform", "discord")

    if not campaign_name:
        raise HTTPException(status_code=400, detail="campaign_name is required")

    if not business_channel:
        raise HTTPException(status_code=400, detail="business_channel is required")

    if not target_segment:
        raise HTTPException(status_code=400, detail="target_segment is required")

    if not template_id:
        raise HTTPException(status_code=400, detail="template_id is required")

    template = get_template(template_id)

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    execute_query("""
    INSERT INTO crm_campaigns
    (campaign_id, campaign_name, campaign_type, business_channel, demo_platform, target_segment, template_id, status, created_by)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        campaign_id,
        campaign_name,
        campaign_type,
        business_channel,
        demo_platform,
        target_segment,
        template_id,
        "Draft",
        user["sub"]
    ))

    create_audit_log(
        user_email=user["sub"],
        user_role=user["role"],
        action="Create campaign",
        object_type="Campaign",
        object_id=campaign_id,
        status="Allowed",
        details=campaign_name
    )

    return {
        "success": True,
        "message": "Campaign created successfully",
        "campaign_id": campaign_id
    }


@router.get("/{campaign_id}")
def get_campaign_detail(campaign_id: str, user=Depends(get_current_user)):
    require_permission(user, "campaigns")

    campaign = fetch_one("""
    SELECT *
    FROM crm_campaigns
    WHERE campaign_id = ?
    """, (campaign_id,))

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    metrics = build_campaign_metrics(campaign_id)

    return {
        "success": True,
        "campaign": campaign,
        "metrics": metrics
    }


@router.post("/{campaign_id}/audience-preview")
def campaign_audience_preview(campaign_id: str, user=Depends(get_current_user)):
    require_permission(user, "campaigns")

    campaign = fetch_one("""
    SELECT *
    FROM crm_campaigns
    WHERE campaign_id = ?
    """, (campaign_id,))

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    audience = get_campaign_audience(campaign)
    eligible, removed = filter_audience_by_consent(audience, campaign.get("business_channel"))

    execute_query("""
    UPDATE crm_campaigns
    SET total_audience = ?, eligible_count = ?, removed_count = ?, updated_at = CURRENT_TIMESTAMP
    WHERE campaign_id = ?
    """, (
        len(audience),
        len(eligible),
        len(removed),
        campaign_id
    ))

    return {
        "success": True,
        "campaign_id": campaign_id,
        "target_segment": campaign.get("target_segment"),
        "business_channel": campaign.get("business_channel"),
        "total_audience": len(audience),
        "eligible_after_consent": len(eligible),
        "removed_due_to_consent_or_dnc": len(removed),
        "sample_eligible_customers": eligible[:10],
        "sample_removed_customers": removed[:10]
    }


@router.post("/{campaign_id}/simulate-send")
def simulate_campaign_send(campaign_id: str, payload: dict = None, user=Depends(get_current_user)):
    require_permission(user, "campaigns")

    payload = payload or {}
    max_send_count = int(payload.get("max_send_count", 5))

    campaign = fetch_one("""
    SELECT *
    FROM crm_campaigns
    WHERE campaign_id = ?
    """, (campaign_id,))

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    template = get_template(campaign.get("template_id"))

    if not template:
        raise HTTPException(status_code=404, detail="Campaign template not found")

    audience = get_campaign_audience(campaign)
    eligible, removed = filter_audience_by_consent(audience, campaign.get("business_channel"))

    customers_to_send = eligible[:max_send_count]

    run_id = "RUN-" + str(uuid.uuid4())[:8].upper()

    execute_query("""
    INSERT INTO crm_campaign_runs
    (run_id, campaign_id, run_status, total_audience, eligible_count, removed_count)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        run_id,
        campaign_id,
        "Running",
        len(audience),
        len(eligible),
        len(removed)
    ))

    sent_count = 0
    failed_count = 0

    webhook_url = get_discord_webhook_for_campaign_type(campaign.get("campaign_type"))

    for customer in customers_to_send:
        rendered = render_template(template["template_json"], customer, campaign)

        title = rendered.get("title", campaign.get("campaign_name"))
        body = rendered.get("body", "")
        footer = rendered.get("footer", "OmniLink CRM Demo")

        send_result = send_discord_message(
            webhook_url=webhook_url,
            title=title,
            body=body,
            footer=footer
        )

        sent_status = send_result.get("status")

        if send_result.get("success"):
            sent_count += 1
        else:
            failed_count += 1

        execute_query("""
        INSERT INTO crm_campaign_message_logs
        (run_id, campaign_id, customer_id, customer_name, business_channel, demo_platform, sent_status, rendered_title, rendered_message, error_message)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            run_id,
            campaign_id,
            str(customer.get("customer_id")),
            customer.get("customer_name"),
            campaign.get("business_channel"),
            campaign.get("demo_platform"),
            sent_status,
            title,
            body,
            send_result.get("message", "")
        ))

        execute_query("""
        INSERT INTO campaign_responses
        (campaign_id, customer_id, sent_status, opened, clicked, converted, revenue)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            campaign_id,
            str(customer.get("customer_id")),
            sent_status,
            0,
            0,
            0,
            0
        ))

    execute_query("""
    UPDATE crm_campaign_runs
    SET run_status = ?, sent_count = ?, failed_count = ?
    WHERE run_id = ?
    """, (
        "Completed",
        sent_count,
        failed_count,
        run_id
    ))

    execute_query("""
    UPDATE crm_campaigns
    SET
        status = ?,
        total_audience = ?,
        eligible_count = ?,
        removed_count = ?,
        sent_count = ?,
        failed_count = ?,
        updated_at = CURRENT_TIMESTAMP
    WHERE campaign_id = ?
    """, (
        "Simulated Sent",
        len(audience),
        len(eligible),
        len(removed),
        sent_count,
        failed_count,
        campaign_id
    ))

    create_audit_log(
        user_email=user["sub"],
        user_role=user["role"],
        action="Simulate campaign send",
        object_type="Campaign",
        object_id=campaign_id,
        status="Allowed",
        details=f"Run ID: {run_id}, Sent: {sent_count}, Failed: {failed_count}"
    )

    return {
        "success": True,
        "message": "Campaign send simulation completed",
        "campaign_id": campaign_id,
        "run_id": run_id,
        "total_audience": len(audience),
        "eligible_after_consent": len(eligible),
        "removed_due_to_consent_or_dnc": len(removed),
        "attempted_send_count": len(customers_to_send),
        "sent_count": sent_count,
        "failed_count": failed_count
    }


@router.get("/{campaign_id}/responses")
def get_campaign_responses(campaign_id: str, user=Depends(get_current_user)):
    require_permission(user, "campaigns")

    rows = fetch_all("""
    SELECT *
    FROM crm_campaign_message_logs
    WHERE campaign_id = ?
    ORDER BY sent_at DESC
    """, (campaign_id,))

    return {
        "success": True,
        "campaign_id": campaign_id,
        "count": len(rows),
        "data": rows
    }


@router.get("/{campaign_id}/responders")
def get_campaign_responders(campaign_id: str, user=Depends(get_current_user)):
    require_permission(user, "campaigns")

    rows = fetch_all("""
    SELECT *
    FROM crm_campaign_message_logs
    WHERE campaign_id = ?
    AND (opened = 1 OR clicked = 1 OR converted = 1)
    ORDER BY sent_at DESC
    """, (campaign_id,))

    return {
        "success": True,
        "campaign_id": campaign_id,
        "count": len(rows),
        "data": rows
    }


@router.get("/{campaign_id}/metrics")
def get_campaign_metrics(campaign_id: str, user=Depends(get_current_user)):
    require_permission(user, "campaigns")

    campaign = fetch_one("""
    SELECT *
    FROM crm_campaigns
    WHERE campaign_id = ?
    """, (campaign_id,))

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    metrics = build_campaign_metrics(campaign_id)

    return {
        "success": True,
        "campaign_id": campaign_id,
        "campaign": campaign,
        "metrics": metrics
    }


@router.get("/summary/daily")
def get_daily_campaign_summary(user=Depends(get_current_user)):
    require_permission(user, "campaigns")

    summary = fetch_one("""
    SELECT
        COUNT(*) as messages_today,
        SUM(CASE WHEN sent_status = 'sent' THEN 1 ELSE 0 END) as sent_today,
        SUM(CASE WHEN sent_status = 'simulated' THEN 1 ELSE 0 END) as simulated_today,
        SUM(CASE WHEN sent_status = 'failed' THEN 1 ELSE 0 END) as failed_today,
        SUM(CASE WHEN opened = 1 THEN 1 ELSE 0 END) as opened_today,
        SUM(CASE WHEN clicked = 1 THEN 1 ELSE 0 END) as clicked_today,
        SUM(CASE WHEN converted = 1 THEN 1 ELSE 0 END) as converted_today,
        ROUND(SUM(revenue), 2) as revenue_today
    FROM crm_campaign_message_logs
    WHERE DATE(sent_at) = DATE('now')
    """)

    campaigns_today = fetch_all("""
    SELECT *
    FROM crm_campaigns
    WHERE DATE(created_at) = DATE('now')
    ORDER BY created_at DESC
    """)

    return {
        "success": True,
        "summary": summary,
        "campaigns_created_today": len(campaigns_today),
        "campaigns": campaigns_today
    }