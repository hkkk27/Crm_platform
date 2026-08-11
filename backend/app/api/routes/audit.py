from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.security import get_current_user, require_permission
from app.db.sqlite_client import fetch_all, fetch_one
from app.services.audit_service import derive_audit_risk

router = APIRouter(prefix="/audit", tags=["Audit Logs"])


def _normalize_status(status: str) -> str:
    value = str(status or "").strip().lower()
    if value in {"allowed", "success", "successful", "completed", "sent"}:
        return "Success"
    if value in {"denied", "failed", "failure", "error", "blocked"}:
        return "Failed"
    return str(status or "Unknown")


def _serialize_log(row: dict) -> dict:
    item = dict(row)
    normalized_status = _normalize_status(item.get("status"))
    return {
        "audit_id": item.get("audit_id"),
        "time": item.get("created_at"),
        "created_at": item.get("created_at"),
        "user_email": item.get("user_email") or "System",
        "user_role": item.get("user_role") or "System",
        "action": item.get("action") or "Unknown action",
        "object_type": item.get("object_type") or "Unknown",
        "module": item.get("object_type") or "Unknown",
        "object_id": item.get("object_id") or "",
        "status": normalized_status,
        "raw_status": item.get("status") or "",
        "risk": derive_audit_risk(
            item.get("action"), item.get("object_type"), item.get("status")
        ),
        "details": item.get("details") or "",
    }


@router.get("/summary")
def get_audit_summary(user=Depends(get_current_user)):
    require_permission(user, "audit")

    rows = fetch_all(
        """
        SELECT audit_id, user_email, user_role, action, object_type,
               object_id, status, details, created_at
        FROM audit_logs
        """
    )
    items = [_serialize_log(row) for row in rows]
    successful = sum(1 for item in items if item["status"] == "Success")
    failed = sum(1 for item in items if item["status"] == "Failed")
    high_risk = sum(1 for item in items if item["risk"] == "High")

    activity = {}
    for item in items:
        email = item["user_email"]
        activity[email] = activity.get(email, 0) + 1

    most_active_user = (
        max(activity, key=activity.get) if activity else None
    )

    return {
        "total_events": len(items),
        "successful_actions": successful,
        "failed_actions": failed,
        "high_risk_events": high_risk,
        "most_active_user": most_active_user,
    }


@router.get("/logs")
def get_audit_logs(
    search: str = Query(default=""),
    role: str = Query(default=""),
    module: str = Query(default=""),
    status: str = Query(default=""),
    risk: str = Query(default=""),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    user=Depends(get_current_user),
):
    require_permission(user, "audit")

    rows = fetch_all(
        """
        SELECT audit_id, user_email, user_role, action, object_type,
               object_id, status, details, created_at
        FROM audit_logs
        ORDER BY created_at DESC, audit_id DESC
        """
    )
    items = [_serialize_log(row) for row in rows]

    search_value = search.strip().lower()
    role_value = role.strip().lower()
    module_value = module.strip().lower()
    status_value = status.strip().lower()
    risk_value = risk.strip().lower()

    if search_value:
        items = [
            item for item in items
            if search_value in " ".join(
                str(item.get(key) or "")
                for key in [
                    "user_email", "user_role", "action", "object_type",
                    "object_id", "details"
                ]
            ).lower()
        ]
    if role_value:
        items = [item for item in items if item["user_role"].lower() == role_value]
    if module_value:
        items = [item for item in items if item["object_type"].lower() == module_value]
    if status_value:
        items = [item for item in items if item["status"].lower() == status_value]
    if risk_value:
        items = [item for item in items if item["risk"].lower() == risk_value]

    total = len(items)
    start = (page - 1) * page_size
    paged_items = items[start:start + page_size]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": paged_items,
    }


@router.get("/logs/{audit_id}")
def get_audit_log_detail(
    audit_id: int,
    user=Depends(get_current_user),
):
    require_permission(user, "audit")

    row = fetch_one(
        """
        SELECT audit_id, user_email, user_role, action, object_type,
               object_id, status, details, created_at
        FROM audit_logs
        WHERE audit_id = ?
        """,
        (audit_id,),
    )
    if not row:
        raise HTTPException(status_code=404, detail="Audit log not found")
    return _serialize_log(row)
