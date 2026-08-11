import jwt
from datetime import datetime, timedelta
from fastapi import Header, HTTPException
from app.core.config import settings
from fastapi.security import HTTPBearer
from fastapi.security import HTTPAuthorizationCredentials
from fastapi import Depends

bearer_scheme = HTTPBearer()


ROLE_PERMISSIONS = {
    "Admin": [
        "dashboard",
        "customers",
        "loyalty",
        "consent",
        "campaigns",
        "kpi",
        "audit",
        "customer_service",
        "admin"
    ],
    "CRM Team": [
        "dashboard",
        "customers",
        "loyalty",
        "consent",
        "campaigns",
        "kpi"
    ],
    "Store Team": [
        "dashboard",
        "customers",
        "loyalty"
    ],
    "Management": [
        "dashboard",
        "kpi"
    ],
    "Customer Service": [
        "dashboard",
        "customers",
        "consent",
        "customer_service",
        "audit"
    ],
    "Security / IT": [
        "settings",
        "audit",
        "admin"
    ],
}


def create_access_token(user_email: str, role: str):
    payload = {
        "sub": user_email,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=8)
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )


def decode_token(token: str):
    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    token = credentials.credentials
    return decode_token(token)


def require_permission(user: dict, module: str):
    role = user.get("role")
    allowed_modules = ROLE_PERMISSIONS.get(role, [])

    if module not in allowed_modules:
        raise HTTPException(
            status_code=403,
            detail=f"Role '{role}' cannot access {module}"
        )

    return True