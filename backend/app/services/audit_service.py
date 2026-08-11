# from app.db.sqlite_client import execute_query


# def create_audit_log(
#     user_email: str,
#     user_role: str,
#     action: str,
#     object_type: str,
#     object_id: str,
#     status: str = "Allowed",
#     details: str = ""
# ):
#     execute_query("""
#     INSERT INTO audit_logs
#     (user_email, user_role, action, object_type, object_id, status, details)
#     VALUES (?, ?, ?, ?, ?, ?, ?)
#     """, (
#         user_email,
#         user_role,
#         action,
#         object_type,
#         object_id,
#         status,
#         details
#     ))
from app.db.sqlite_client import execute_query


def create_audit_log(
    user_email: str,
    user_role: str,
    action: str,
    object_type: str,
    object_id: str,
    status: str = "Allowed",
    details: str = "",
):
    """Insert one immutable application audit event."""
    execute_query(
        """
        INSERT INTO audit_logs (
            user_email,
            user_role,
            action,
            object_type,
            object_id,
            status,
            details
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_email,
            user_role,
            action,
            object_type,
            str(object_id or ""),
            status,
            details,
        ),
    )


def derive_audit_risk(action: str, object_type: str, status: str = "") -> str:
    """Derive Low, Medium, or High risk without adding a DB column."""
    action_value = str(action or "").strip().lower()
    object_value = str(object_type or "").strip().lower()
    status_value = str(status or "").strip().lower()
    combined = f"{object_value} {action_value} {status_value}"

    high_terms = [
        "delete",
        "deactivate",
        "disable",
        "role",
        "permission",
        "password reset",
        "forgot password",
        "withdraw",
        "do not contact",
        "dnc",
        "export",
        "approve",
        "reject",
    ]
    high_objects = {"users", "user", "password_reset_codes"}

    if any(term in combined for term in high_terms):
        return "High"
    if object_value in high_objects and any(
        term in action_value for term in ["update", "change", "reset"]
    ):
        return "High"

    medium_terms = [
        "campaign",
        "run",
        "failed",
        "escalat",
        "sla breach",
        "points",
        "redeem",
        "membership",
        "tier",
        "ticket update",
        "status changed",
    ]
    if any(term in combined for term in medium_terms):
        return "Medium"

    return "Low"
