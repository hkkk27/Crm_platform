# from fastapi import APIRouter, HTTPException
# from app.schemas.schemas import LoginRequest
# from app.core.security import create_access_token, ROLE_PERMISSIONS
# from app.db.sqlite_client import fetch_one
# from app.services.audit_service import create_audit_log

# from datetime import datetime, timedelta
# import hashlib
# import random

# from fastapi import HTTPException
# from app.schemas.schemas import ForgotPasswordRequest, ResetPasswordRequest
# from app.core.config import settings
# from app.db.sqlite_client import fetch_one, execute_query
# from app.services.email_service import send_password_reset_email
# from app.services.audit_service import create_audit_log

# router = APIRouter(prefix="/auth", tags=["Authentication"])

# def _hash_reset_code(email: str, reset_code: str):
#     raw_value = f"{email.lower()}:{reset_code}:{settings.JWT_SECRET}"
#     return hashlib.sha256(raw_value.encode("utf-8")).hexdigest()

# @router.post("/login")
# def login(payload: LoginRequest):
#     user = fetch_one("""
#     SELECT email, password, role, status
#     FROM users
#     WHERE email = ?
#     """, (payload.email,))

#     if not user:
#         raise HTTPException(status_code=401, detail="Invalid email or password")

#     if user["password"] != payload.password:
#         raise HTTPException(status_code=401, detail="Invalid email or password")

#     # if user["status"] != "Active":
#     #     raise HTTPException(status_code=403, detail="User is inactive")

#     role = user["role"]

#     token = create_access_token(payload.email, role)

#     create_audit_log(
#         user_email=payload.email,
#         user_role=role,
#         action="Login",
#         object_type="User",
#         object_id=payload.email,
#         status="Allowed",
#         details="User logged in successfully"
#     )

#     return {
#         "success": True,
#         "access_token": token,
#         "token_type": "Bearer",
#         "user": {
#             "email": payload.email,
#             "role": role,
#             "allowed_modules": ROLE_PERMISSIONS[role]
#         }
#     }

# @router.post("/forgot-password/request")
# def request_forgot_password(payload: ForgotPasswordRequest):
#     email = payload.email.strip().lower()

#     user = fetch_one("""
#     SELECT email, role, status
#     FROM users
#     WHERE lower(email) = ?
#     """, (email,))

#     safe_response = {
#         "success": True,
#         "message": "If this email exists, a password reset code has been sent."
#     }

#     if not user:
#         return safe_response

#     if user["status"] != "Active":
#         raise HTTPException(status_code=403, detail="User is inactive")

#     reset_code = str(random.randint(100000, 999999))
#     code_hash = _hash_reset_code(email, reset_code)

#     expires_at = (
#         datetime.utcnow() + timedelta(minutes=settings.PASSWORD_RESET_EXPIRE_MINUTES)
#     ).isoformat()

#     execute_query("""
#     INSERT INTO password_reset_codes (email, code_hash, expires_at, used)
#     VALUES (?, ?, ?, 0)
#     """, (email, code_hash, expires_at))

#     send_password_reset_email(email, reset_code)

#     create_audit_log(
#         user_email=email,
#         user_role=user["role"],
#         action="Forgot Password Requested",
#         object_type="User",
#         object_id=email,
#         status="Allowed",
#         details="Password reset code generated"
#     )

#     return safe_response
# @router.post("/forgot-password/reset")
# def reset_forgot_password(payload: ResetPasswordRequest):
#     email = payload.email.strip().lower()
#     reset_code = payload.reset_code.strip()
#     new_password = payload.new_password.strip()

#     if len(new_password) < 8:
#         raise HTTPException(status_code=400, detail="Password must be at least 8 characters")

#     user = fetch_one("""
#     SELECT email, role, status
#     FROM users
#     WHERE lower(email) = ?
#     """, (email,))

#     if not user:
#         raise HTTPException(status_code=400, detail="Invalid or expired reset code")

#     code_hash = _hash_reset_code(email, reset_code)

#     reset_row = fetch_one("""
#     SELECT reset_id, expires_at, used
#     FROM password_reset_codes
#     WHERE lower(email) = ? AND code_hash = ?
#     ORDER BY reset_id DESC
#     LIMIT 1
#     """, (email, code_hash))

#     if not reset_row or reset_row["used"] == 1:
#         raise HTTPException(status_code=400, detail="Invalid or expired reset code")

#     if datetime.fromisoformat(reset_row["expires_at"]) < datetime.utcnow():
#         raise HTTPException(status_code=400, detail="Invalid or expired reset code")

#     execute_query("""
#     UPDATE users
#     SET password = ?
#     WHERE lower(email) = ?
#     """, (new_password, email))

#     execute_query("""
#     UPDATE password_reset_codes
#     SET used = 1
#     WHERE reset_id = ?
#     """, (reset_row["reset_id"],))

#     create_audit_log(
#         user_email=email,
#         user_role=user["role"],
#         action="Password Reset",
#         object_type="User",
#         object_id=email,
#         status="Allowed",
#         details="Password reset completed successfully"
#     )

#     return {
#         "success": True,
#         "message": "Password updated successfully. Please login again."
#     }
import hashlib
import random
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.core.security import ROLE_PERMISSIONS, create_access_token
from app.db.sqlite_client import execute_query, fetch_one
from app.schemas.schemas import (
    ForgotPasswordRequest,
    LoginRequest,
    ResetPasswordRequest,
)
from app.services.audit_service import create_audit_log
from app.services.email_service import send_password_reset_email
from app.services.password_service import (
    hash_password,
    is_password_hash,
    plaintext_matches,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _hash_reset_code(email: str, reset_code: str) -> str:
    raw_value = f"{email.lower()}:{reset_code}:{settings.JWT_SECRET}"
    return hashlib.sha256(raw_value.encode("utf-8")).hexdigest()


def _verify_login_password(
    email: str,
    submitted_password: str,
    stored_password: str,
) -> bool:
    """
    Verify modern hashes and safely migrate legacy plaintext passwords.

    Legacy compatibility can be removed after every users.password value
    begins with 'pbkdf2_sha256$'.
    """
    if is_password_hash(stored_password):
        return verify_password(submitted_password, stored_password)

    if not plaintext_matches(submitted_password, stored_password):
        return False

    # One-time automatic migration after a successful legacy login.
    execute_query(
        """
        UPDATE users
        SET password = ?
        WHERE lower(email) = lower(?)
        """,
        (hash_password(submitted_password), email),
    )
    return True


@router.post("/login")
def login(payload: LoginRequest):
    email = payload.email.strip().lower()

    user = fetch_one(
        """
        SELECT email, password, role, status
        FROM users
        WHERE lower(email) = ?
        """,
        (email,),
    )

    if not user or not _verify_login_password(
        email,
        payload.password,
        user.get("password"),
    ):
        create_audit_log(
            user_email=email,
            user_role=user.get("role") if user else "Unknown",
            action="Login",
            object_type="User",
            object_id=email,
            status="Denied",
            details="Invalid email or password",
        )
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if str(user.get("status") or "").strip().lower() != "active":
        create_audit_log(
            user_email=email,
            user_role=user.get("role") or "Unknown",
            action="Login",
            object_type="User",
            object_id=email,
            status="Denied",
            details="Inactive user attempted to log in",
        )
        raise HTTPException(status_code=403, detail="User is inactive")

    role = user.get("role")
    if role not in ROLE_PERMISSIONS:
        raise HTTPException(status_code=403, detail="User role is not configured")

    token = create_access_token(email, role)

    create_audit_log(
        user_email=email,
        user_role=role,
        action="Login",
        object_type="User",
        object_id=email,
        status="Allowed",
        details="User logged in successfully",
    )

    return {
        "success": True,
        "access_token": token,
        "token_type": "Bearer",
        "user": {
            "email": email,
            "role": role,
            "allowed_modules": ROLE_PERMISSIONS.get(role, []),
        },
    }


@router.post("/forgot-password/request")
def request_forgot_password(payload: ForgotPasswordRequest):
    email = payload.email.strip().lower()
    user = fetch_one(
        """
        SELECT email, role, status
        FROM users
        WHERE lower(email) = ?
        """,
        (email,),
    )

    safe_response = {
        "success": True,
        "message": "If this email exists, a password reset code has been sent.",
    }

    if not user:
        return safe_response

    if str(user.get("status") or "").strip().lower() != "active":
        return safe_response

    # Invalidate older unused codes for this account.
    execute_query(
        """
        UPDATE password_reset_codes
        SET used = 1
        WHERE lower(email) = ? AND used = 0
        """,
        (email,),
    )

    reset_code = str(random.SystemRandom().randint(100000, 999999))
    code_hash = _hash_reset_code(email, reset_code)
    expires_at = (
        datetime.utcnow()
        + timedelta(minutes=settings.PASSWORD_RESET_EXPIRE_MINUTES)
    ).isoformat()

    execute_query(
        """
        INSERT INTO password_reset_codes (
            email,
            code_hash,
            expires_at,
            used
        )
        VALUES (?, ?, ?, 0)
        """,
        (email, code_hash, expires_at),
    )

    send_password_reset_email(email, reset_code)

    create_audit_log(
        user_email=email,
        user_role=user.get("role") or "Unknown",
        action="Forgot Password Requested",
        object_type="User",
        object_id=email,
        status="Allowed",
        details="Password reset code generated",
    )

    return safe_response


@router.post("/forgot-password/reset")
def reset_forgot_password(payload: ResetPasswordRequest):
    email = payload.email.strip().lower()
    reset_code = payload.reset_code.strip()
    new_password = payload.new_password

    if len(new_password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters",
        )

    user = fetch_one(
        """
        SELECT email, role, status
        FROM users
        WHERE lower(email) = ?
        """,
        (email,),
    )

    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset code")

    code_hash = _hash_reset_code(email, reset_code)
    reset_row = fetch_one(
        """
        SELECT reset_id, expires_at, used
        FROM password_reset_codes
        WHERE lower(email) = ? AND code_hash = ?
        ORDER BY reset_id DESC
        LIMIT 1
        """,
        (email, code_hash),
    )

    if not reset_row or int(reset_row.get("used") or 0) == 1:
        raise HTTPException(status_code=400, detail="Invalid or expired reset code")

    try:
        expires_at = datetime.fromisoformat(reset_row.get("expires_at"))
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid or expired reset code")

    if expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired reset code")

    password_hash = hash_password(new_password)

    execute_query(
        """
        UPDATE users
        SET password = ?
        WHERE lower(email) = ?
        """,
        (password_hash, email),
    )

    execute_query(
        """
        UPDATE password_reset_codes
        SET used = 1
        WHERE reset_id = ?
        """,
        (reset_row.get("reset_id"),),
    )

    create_audit_log(
        user_email=email,
        user_role=user.get("role") or "Unknown",
        action="Password Reset",
        object_type="User",
        object_id=email,
        status="Allowed",
        details="Password reset completed successfully using a secure hash",
    )

    return {
        "success": True,
        "message": "Password updated successfully. Please login again.",
    }
