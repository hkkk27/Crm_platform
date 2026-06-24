Web Framework & Server
	• fastapi: A modern, high-performance web framework used to build APIs with Python.
	• uvicorn[standard]: The lightning-fast server that actually runs your FastAPI application.
Data Validation & Configuration
	• pydantic: Checks and validates incoming API data to ensure it matches your required format.
	• pydantic-settings: Manages your application's settings and environment variables safely.
	• python-dotenv: Reads secret keys and credentials from a hidden .env file into your app.
Database & Security
	• supabase: The official client used to connect your Python app to a Supabase database.
	• PyJWT: Generates and verifies JSON Web Tokens to securely log users in and out.
How They Work Together
When a user logs into your app, python-dotenv loads your supabase credentials. The user sends their login info, which pydantic validates. Your app checks the details against supabase, and PyJWT generates a secure login token. This entire process is served to the web instantly by fastapi running on uvicorn.

omnilink-backend/
│
├── app/
│   ├── main.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   │
│   ├── db/
│   │   └── supabase_client.py
│   │
│   ├── schemas/
│   │   └── schemas.py
│   │
│   ├── api/
│   │   └── routes/
│   │       ├── health.py
│   │       ├── auth.py
│   │       ├── customers.py
│   │       ├── memberships.py
│   │       ├── consents.py
│   │       ├── campaigns.py
│   │       ├── audit.py
│   │       └── kpi.py
│   │
│   └── services/
│       ├── audit_service.py
│       ├── consent_service.py
│       └── segmentation_service.py
│
├── .env
├── requirements.txt
└── README.md

venv\Scripts\activate

  created_at TIMESTAMPTZ DEFAULT NOW()


GSM Gateway

-Perfect Harshit — we’ll start backend setup first. I’ll guide you exactly like: which folder to make, which file to create, what code to put, and how to run it.
We’ll build Phase 1 backend foundation:

FastAPI backend
Supabase connection
Swagger UI
Login simulation
Role-based access structure
Customer APIs
Membership API
Consent API
Audit logging base
CORS for frontend
Supabase is good here because it gives PostgreSQL database + APIs + Auth/Storage options, and it supports Row Level Security for secure access control when needed. [forbes.com], [marketingw...thdave.com]

0. Backend Folder Name
Create one folder:
omnilink-backend
Open this folder in VS Code.

1. Final Folder Structure
Create this structure:

omnilink-backend/
│
├── app/
│   ├── main.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   │
│   ├── db/
│   │   └── supabase_client.py
│   │
│   ├── schemas/
│   │   └── schemas.py
│   │
│   ├── api/
│   │   └── routes/
│   │       ├── health.py
│   │       ├── auth.py
│   │       ├── customers.py
│   │       ├── memberships.py
│   │       ├── consents.py
│   │       ├── campaigns.py
│   │       ├── audit.py
│   │       └── kpi.py
│   │
│   └── services/
│       ├── audit_service.py
│       ├── consent_service.py
│       └── segmentation_service.py
│
├── .env
├── requirements.txt
└── README.md

2. Create Virtual Environment
In terminal inside omnilink-backend:
python -m venv venv
Activate it:
Windows PowerShell
venv\Scripts\activate
Mac/Linux
source venv/bin/activate

3. Create requirements.txt
File:
requirements.txt
Code:

fastapi
uvicorn[standard]
python-dotenv
pydantic
pydantic-settings
supabase
PyJWT
Install:
pip install -r requirements.txt

4. Create Supabase Project
Go to Supabase and create a project.
You need these two values:

SUPABASE_URL
SUPABASE_SERVICE_ROLE_KEY
For backend only, we can use the service role key inside .env. Do not expose this key in frontend.

5. Create .env
File:
.env
Code:

APP_NAME=OmniLink CRM Backend
APP_ENV=development
SUPABASE_URL=PASTE_YOUR_SUPABASE_URL_HERE
SUPABASE_SERVICE_ROLE_KEY=PASTE_YOUR_SERVICE_ROLE_KEY_HERE
JWT_SECRET=change-this-secret-key
JWT_ALGORITHM=HS256
FRONTEND_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
Later when Ankit connects from same Wi-Fi, add Ankit’s IP:
FRONTEND_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://ANKIT_IP:3000

6. Supabase SQL Tables
In Supabase:
SQL Editor → New Query
Paste and run this:

create table if not exists customers (
  customer_id text primary key,
  name text not null,
  phone text,
  email text,
  city text,
  birthday_month text,
  status text,
  preferred_category text,
  total_spend numeric default 0,
  average_order_value numeric default 0,
  purchase_frequency integer default 0,
  last_purchase_date date,
  created_at timestamp default now()
);
create table if not exists memberships (
  membership_id text primary key,
  customer_id text references customers(customer_id),
  membership_status text,
  tier text,
  points_balance integer default 0,
  points_earned integer default 0,
  points_redeemed integer default 0,
  expiry_date date,
  upgrade_eligibility boolean default false,
  created_at timestamp default now()
);
create table if not exists consents (
  consent_id text primary key,
  customer_id text references customers(customer_id),
  whatsapp_consent boolean default false,
  sms_consent boolean default false,
  email_consent boolean default false,
  app_notification_consent boolean default false,
  personalization_consent boolean default false,
  do_not_contact boolean default false,
  consent_source text,
  consent_given_date timestamp default now(),
  consent_withdrawn_date timestamp
);
create table if not exists campaigns (
  campaign_id text primary key,
  campaign_name text not null,
  campaign_type text,
  channel text,
  target_segment text,
  status text default 'Draft',
  audience_count integer default 0,
  eligible_count integer default 0,
  created_by text,
  approved_by text,
  created_at timestamp default now()
);
create table if not exists audit_logs (
  audit_id bigserial primary key,
  user_email text,
  user_role text,
  action text,
  object_type text,
  object_id text,
  status text,
  details text,
  created_at timestamp default now()
);
create table if not exists campaign_responses (
  response_id bigserial primary key,
  campaign_id text references campaigns(campaign_id),
  customer_id text references customers(customer_id),
  sent_status text default 'simulated',
  opened boolean default false,
  clicked boolean default false,
  converted boolean default false,
  revenue numeric default 0,
  created_at timestamp default now()
);

7. Insert Sample Data
Run this in Supabase SQL Editor:

insert into customers
(customer_id, name, phone, email, city, birthday_month, status, preferred_category, total_spend, average_order_value, purchase_frequency, last_purchase_date)
values
('CUST-1001', 'Riya Sharma', '98xxxxxx45', 'r*****@mail.com', 'Mumbai', 'August', 'Member', 'Premium Dresses', 23800, 3400, 7, '2026-06-14'),
('CUST-1002', 'Aarav Mehta', '97xxxxxx22', 'a*****@mail.com', 'Pune', 'December', 'Non-member', 'Footwear', 14500, 2900, 5, '2026-06-02'),
('CUST-1003', 'Neha Iyer', '99xxxxxx78', 'n*****@mail.com', 'Mumbai', 'July', 'Member', 'Ethnic Wear', 52200, 4350, 12, '2026-06-18'),
('CUST-1004', 'Kabir Khan', '96xxxxxx54', 'k*****@mail.com', 'Navi Mumbai', 'March', 'Member', 'Casual Wear', 7200, 1800, 4, '2026-03-04')
on conflict (customer_id) do nothing;
insert into memberships
(membership_id, customer_id, membership_status, tier, points_balance, points_earned, points_redeemed, expiry_date, upgrade_eligibility)
values
('MEM-1001', 'CUST-1001', 'Active', 'Silver', 1320, 2000, 680, '2027-06-14', true),
('MEM-1002', 'CUST-1002', 'Non-member', 'Non-member', 0, 0, 0, null, true),
('MEM-1003', 'CUST-1003', 'Active', 'Gold', 4100, 6000, 1900, '2027-06-18', true),
('MEM-1004', 'CUST-1004', 'Active', 'Silver', 410, 600, 190, '2027-03-04', false)
on conflict (membership_id) do nothing;
insert into consents
(consent_id, customer_id, whatsapp_consent, sms_consent, email_consent, app_notification_consent, personalization_consent, do_not_contact, consent_source)
values
('CON-1001', 'CUST-1001', true, true, true, true, true, false, 'Membership Form'),
('CON-1002', 'CUST-1002', true, false, true, false, true, false, 'Website'),
('CON-1003', 'CUST-1003', false, false, true, true, true, false, 'App'),
('CON-1004', 'CUST-1004', false, false, false, false, false, true, 'Customer Service')
on conflict (consent_id) do nothing;

8. Create app/core/config.py
File:
app/core/config.py
Code:

from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "OmniLink CRM Backend"
    APP_ENV: str = "development"
    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    FRONTEND_ORIGINS: str = "http://localhost:3000"
    @property
    def allowed_origins(self) -> Listreturn [origin.strip() for origin in self.FRONTEND_ORIGINS.split(",")]
    class Config:
        env_file = ".env"

settings = Settings()

9. Create app/db/supabase_client.py
File:
app/db/supabase_client.py
Code:

from supabase import create_client, Client
from app.core.config import settings

supabase: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_ROLE_KEY
)

10. Create app/core/security.py
File:
app/core/security.py
Code:

import jwt
from datetime import datetime, timedelta
from fastapi import Header, HTTPException
from app.core.config import settings

ROLE_PERMISSIONS = {
    "Admin": ["dashboard", "customers", "loyalty", "consent", "campaigns", "kpi", "audit", "admin"],
    "CRM Team": ["dashboard", "customers", "loyalty", "consent", "campaigns", "kpi"],
    "Store Team": ["dashboard", "customers", "loyalty"],
    "Management": ["dashboard", "kpi"],
    "Customer Service": ["dashboard", "customers", "consent", "audit"],
    "Security / IT": ["dashboard", "audit", "admin"],
}

def create_access_token(user_email: str, role: str):
    payload = {
        "sub": user_email,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=8)
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token

def decode_token(token: str):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    token = authorization.replace("Bearer ", "")
    return decode_token(token)

def require_permission(user: dict, module: str):
    role = user.get("role")
    allowed_modules = ROLE_PERMISSIONS.get(role, [])
    if module not in allowed_modules:
        raise HTTPException(status_code=403, detail=f"Role '{role}' cannot access {module}")
    return True

11. Create app/schemas/schemas.py
File:
app/schemas/schemas.py
Code:

from pydantic import BaseModel
from typing import Optional

class LoginRequest(BaseModel):
    email: str
    role: str

class CampaignCreateRequest(BaseModel):
    campaign_name: str
    campaign_type: str
    channel: str
    target_segment: str
    created_by: Optional[str] = "CRM User"

class ConsentUpdateRequest(BaseModel):
    customer_id: str
    whatsapp_consent: Optional[bool] = None
    sms_consent: Optional[bool] = None
    email_consent: Optional[bool] = None
    app_notification_consent: Optional[bool] = None
    personalization_consent: Optional[bool] = None
    do_not_contact: Optional[bool] = None

12. Create app/services/audit_service.py
File:
app/services/audit_service.py
Code:

from app.db.supabase_client import supabase

def create_audit_log(
    user_email: str,
    user_role: str,
    action: str,
    object_type: str,
    object_id: str,
    status: str = "Allowed",
    details: str = ""
):
    data = {
        "user_email": user_email,
        "user_role": user_role,
        "action": action,
        "object_type": object_type,
        "object_id": object_id,
        "status": status,
        "details": details
    }
    supabase.table("audit_logs").insert(data).execute()

13. Create app/services/segmentation_service.py
File:
app/services/segmentation_service.py
Code:

def get_customer_segment(customer: dict, membership: dict, consent: dict):
    total_spend = float(customer.get("total_spend") or 0)
    purchase_frequency = int(customer.get("purchase_frequency") or 0)
    tier = membership.get("tier") if membership else "Non-member"
    do_not_contact = consent.get("do_not_contact") if consent else False
    if do_not_contact:
        return "Do Not Contact"
    if tier == "Non-member" and total_spend >= 10000 and purchase_frequency >= 3:
        return "Potential Member"
    if tier == "Silver" and total_spend >= 22000:
        return "Silver-to-Gold Eligible"
    if tier == "Gold" and total_spend >= 50000:
        return "Gold-to-Platinum Eligible"
    if purchase_frequency <= 2:
        return "Low Spender"
    if total_spend >= 50000:
        return "High Spender"
    if total_spend >= 20000:
        return "Medium Spender"
    return "General Customer"

14. Create app/services/consent_service.py
File:
app/services/consent_service.py
Code:

def is_customer_eligible_for_channel(consent: dict, channel: str):
    if not consent:
        return False
    if consent.get("do_not_contact"):
        return False
    channel = channel.lower()
    if channel == "whatsapp":
        return consent.get("whatsapp_consent", False)
    if channel == "sms":
        return consent.get("sms_consent", False)
    if channel == "email":
        return consent.get("email_consent", False)
    if channel == "app":
        return consent.get("app_notification_consent", False)
    return False

15. Create Route: app/api/routes/health.py

from fastapi import APIRouter
router = APIRouter(prefix="/health", tags=["Health"])

@router.get("")
def health_check():
    return {
        "status": "ok",
        "message": "OmniLink CRM backend is running"
    }

16. Create Route: app/api/routes/auth.py

from fastapi import APIRouter
from app.schemas.schemas import LoginRequest
from app.core.security import create_access_token, ROLE_PERMISSIONS
from app.services.audit_service import create_audit_log
router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login")
def login(payload: LoginRequest):
    if payload.role not in ROLE_PERMISSIONS:
        return {
            "success": False,
            "message": "Invalid role"
        }
    token = create_access_token(payload.email, payload.role)
    create_audit_log(
        user_email=payload.email,
        user_role=payload.role,
        action="Login",
        object_type="User",
        object_id=payload.email,
        status="Allowed",
        details="User logged in successfully"
    )
    return {
        "success": True,
        "access_token": token,
        "token_type": "Bearer",
        "user": {
            "email": payload.email,
            "role": payload.role,
            "allowed_modules": ROLE_PERMISSIONS[payload.role]
        }
    }

17. Create Route: app/api/routes/customers.py

from fastapi import APIRouter, Depends
from app.db.supabase_client import supabase
from app.core.security import get_current_user, require_permission
from app.services.audit_service import create_audit_log
router = APIRouter(prefix="/customers", tags=["Customers"])

@router.get("")
def get_customers(user=Depends(get_current_user)):
    require_permission(user, "customers")
    response = supabase.table("customers").select("").execute()
    create_audit_log(
        user_email=user["sub"],
        user_role=user["role"],
        action="View customer list",
        object_type="Customer",
        object_id="ALL",
        status="Allowed"
    )
    return {
        "success": True,
        "data": response.data
    }

@router.get("/{customer_id}")
def get_customer_detail(customer_id: str, user=Depends(get_current_user)):
    require_permission(user, "customers")
    customer = supabase.table("customers").select("").eq("customer_id", customer_id).single().execute()
    membership = supabase.table("memberships").select("").eq("customer_id", customer_id).execute()
    consent = supabase.table("consents").select("").eq("customer_id", customer_id).execute()
    create_audit_log(
        user_email=user["sub"],
        user_role=user["role"],
        action="View customer profile",
        object_type="Customer",
        object_id=customer_id,
        status="Allowed"
    )
    customer_data = customer.data
    if user["role"] == "Store Team":
        customer_data["email"] = "Restricted"
    return {
        "success": True,
        "customer": customer_data,
        "membership": membership.data[0] if membership.data else None,
        "consent": consent.data[0] if consent.data else None
    }

18. Create Route: app/api/routes/memberships.py

from fastapi import APIRouter, Depends
from app.db.supabase_client import supabase
from app.core.security import get_current_user, require_permission
router = APIRouter(prefix="/memberships", tags=["Memberships"])

@router.get("/{customer_id}")
def get_membership(customer_id: str, user=Depends(get_current_user)):
    require_permission(user, "loyalty")
    response = supabase.table("memberships").select("").eq("customer_id", customer_id).execute()
    return {
        "success": True,
        "data": response.data[0] if response.data else None
    }

@router.get("")
def get_all_memberships(user=Depends(get_current_user)):
    require_permission(user, "loyalty")
    response = supabase.table("memberships").select("").execute()
    return {
        "success": True,
        "data": response.data
    }

19. Create Route: app/api/routes/consents.py

from fastapi import APIRouter, Depends
from app.db.supabase_client import supabase
from app.schemas.schemas import ConsentUpdateRequest
from app.core.security import get_current_user, require_permission
from app.services.audit_service import create_audit_log
router = APIRouter(prefix="/consents", tags=["Consents"])

@router.get("/{customer_id}")
def get_consent(customer_id: str, user=Depends(get_current_user)):
    require_permission(user, "consent")
    response = supabase.table("consents").select("*").eq("customer_id", customer_id).execute()
    return {
        "success": True,
        "data": response.data[0] if response.data else None
    }

@router.post("/update")
def update_consent(payload: ConsentUpdateRequest, user=Depends(get_current_user)):
    require_permission(user, "consent")
    update_data = payload.dict(exclude_unset=True)
    customer_id = update_data.pop("customer_id")
    response = supabase.table("consents").update(update_data).eq("customer_id", customer_id).execute()
    create_audit_log(
        user_email=user["sub"],
        user_role=user["role"],
        action="Update consent",
        object_type="Consent",
        object_id=customer_id,
        status="Allowed",
        details=str(update_data)
    )
    return {
        "success": True,
        "data": response.data
    }

20. Create Route: app/api/routes/campaigns.py

import uuid
from fastapi import APIRouter, Depends
from app.db.supabase_client import supabase
from app.schemas.schemas import CampaignCreateRequest
from app.core.security import get_current_user, require_permission
from app.services.consent_service import is_customer_eligible_for_channel
from app.services.audit_service import create_audit_log
router = APIRouter(prefix="/campaigns", tags=["Campaigns"])

@router.get("")
def get_campaigns(user=Depends(get_current_user)):
    require_permission(user, "campaigns")
    response = supabase.table("campaigns").select("").execute()
    return {
        "success": True,
        "data": response.data
    }

@router.post("")
def create_campaign(payload: CampaignCreateRequest, user=Depends(get_current_user)):
    require_permission(user, "campaigns")
    campaign_id = "CMP-" + str(uuid.uuid4())[:8]
    data = {
        "campaign_id": campaign_id,
        "campaign_name": payload.campaign_name,
        "campaign_type": payload.campaign_type,
        "channel": payload.channel,
        "target_segment": payload.target_segment,
        "status": "Draft",
        "created_by": user["sub"]
    }
    response = supabase.table("campaigns").insert(data).execute()
    create_audit_log(
        user_email=user["sub"],
        user_role=user["role"],
        action="Create campaign",
        object_type="Campaign",
        object_id=campaign_id,
        status="Allowed",
        details=payload.campaign_name
    )
    return {
        "success": True,
        "data": response.data
    }

@router.post("/{campaign_id}/audience-preview")
def audience_preview(campaign_id: str, user=Depends(get_current_user)):
    require_permission(user, "campaigns")
    campaign_response = supabase.table("campaigns").select("").eq("campaign_id", campaign_id).single().execute()
    campaign = campaign_response.data
    customers_response = supabase.table("customers").select("").execute()
    customers = customers_response.data
    eligible_customers = []
    for customer in customers:
        consent_response = supabase.table("consents").select("").eq("customer_id", customer["customer_id"]).execute()
        consent = consent_response.data[0] if consent_response.data else None
        if is_customer_eligible_for_channel(consent, campaign["channel"]):
            eligible_customers.append(customer)
    supabase.table("campaigns").update({
        "audience_count": len(customers),
        "eligible_count": len(eligible_customers)
    }).eq("campaign_id", campaign_id).execute()
    return {
        "success": True,
        "campaign_id": campaign_id,
        "total_audience": len(customers),
        "eligible_after_consent": len(eligible_customers),
        "removed_due_to_consent": len(customers) - len(eligible_customers),
        "eligible_customers": eligible_customers
    }

@router.post("/{campaign_id}/simulate-send")
def simulate_send(campaign_id: str, user=Depends(get_current_user)):
    require_permission(user, "campaigns")
    preview = audience_preview(campaign_id, user)
    for customer in preview["eligible_customers"]:
        supabase.table("campaign_responses").insert({
            "campaign_id": campaign_id,
            "customer_id": customer["customer_id"],
            "sent_status": "simulated"
        }).execute()
    supabase.table("campaigns").update({
        "status": "Simulated Sent"
    }).eq("campaign_id", campaign_id).execute()
    create_audit_log(
        user_email=user["sub"],
        user_role=user["role"],
        action="Simulate campaign send",
        object_type="Campaign",
        object_id=campaign_id,
        status="Allowed",
        details="Campaign simulated after consent filtering"
    )
    return {
        "success": True,
        "message": "Campaign simulated successfully",
        "campaign_id": campaign_id,
        "eligible_sent_count": preview["eligible_after_consent"]
    }

21. Create Route: app/api/routes/audit.py

from fastapi import APIRouter, Depends
from app.db.supabase_client import supabase
from app.core.security import get_current_user, require_permission
router = APIRouter(prefix="/audit", tags=["Audit Logs"])

@router.get("/logs")
def get_audit_logs(user=Depends(get_current_user)):
    require_permission(user, "audit")
    response = supabase.table("audit_logs").select("*").order("created_at", desc=True).execute()
    return {
        "success": True,
        "data": response.data
    }

22. Create Route: app/api/routes/kpi.py

from fastapi import APIRouter, Depends
from app.db.supabase_client import supabase
from app.core.security import get_current_user, require_permission
router = APIRouter(prefix="/kpi", tags=["KPIs"])

@router.get("/summary")
def get_kpi_summary(user=Depends(get_current_user)):
    require_permission(user, "kpi")
    customers = supabase.table("customers").select("").execute().data
    memberships = supabase.table("memberships").select("").execute().data
    campaigns = supabase.table("campaigns").select("*").execute().data
    total_customers = len(customers)
    total_members = len([m for m in memberships if m.get("tier") != "Non-member"])
    membership_conversion_rate = round((total_members / total_customers) * 100, 2) if total_customers else 0
    total_revenue = sum([float(c.get("total_spend") or 0) for c in customers])
    avg_order_value = round(sum([float(c.get("average_order_value") or 0) for c in customers]) / total_customers, 2) if total_customers else 0
    return {
        "success": True,
        "data": {
            "total_customers": total_customers,
            "total_members": total_members,
            "membership_conversion_rate": membership_conversion_rate,
            "total_revenue": total_revenue,
            "average_order_value": avg_order_value,
            "campaign_count": len(campaigns),
            "repeat_purchase_rate": 58,
            "campaign_roi": 336,
            "privacy_complaints": 3,
            "consent_withdrawals": 42
        }
    }

23. Create app/main.py
File:
app/main.py
Code:

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import health, auth, customers, memberships, consents, campaigns, audit, kpi
app = FastAPI(
    title="OmniLink CRM Backend",
    description="Backend API for secure loyalty CRM prototype",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=[""],
    allow_headers=[""],
)
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(customers.router)
app.include_router(memberships.router)
app.include_router(consents.router)
app.include_router(campaigns.router)
app.include_router(audit.router)
app.include_router(kpi.router)

@app.get("/")
def root():
    return {
        "message": "Welcome to OmniLink CRM Backend",
        "docs": "/docs"
    }

24. Create Empty __init__.py Files
Create empty files:

app/init.py
app/core/init.py
app/db/init.py
app/api/init.py
app/api/routes/init.py
app/schemas/init.py
app/services/init.py
Important, because Python packages need it.

25. Run Backend
From main project folder:
uvicorn app.main:app --reload
Open:
http://127.0.0.1:8000
Swagger:
http://127.0.0.1:8000/docs

26. Test Login in Swagger
Go to:
POST /auth/login
Request body:

{
  "email": "harshit@omnilink.local",
  "role": "Admin"
}
Copy token from response.

27. Test Protected API
In Swagger, click:
Authorize
Paste:
Bearer YOUR_TOKEN_HERE
Then test:

GET /customers
GET /customers/CUST-1001
GET /kpi/summary

28. What You Should Complete Today
Your backend setup target today:

1. Project folder created
2. Virtual environment created
3. FastAPI installed
4. Supabase project created
5. Tables created in Supabase
6. Sample data inserted
7. Backend runs locally
8. Swagger UI opens
9. Login API works
10. Customer list API works

29. What You Can Show Tomorrow / Thursday
You can show:

FastAPI backend running
Swagger UI
Login API
Customer API
Supabase tables
Sample customer data
Basic RBAC token flow
Architecture explanation
This is a very solid first backend milestone.

30. Your Next Step
Start with this exact order:

Step 1: Create folder
Step 2: Create venv
Step 3: Install requirements
Step 4: Create Supabase tables
Step 5: Add .env
Step 6: Add config.py
Step 7: Add supabase_client.py
Step 8: Add main.py
Step 9: Add health route
Step 10: Run backend
Once backend runs, tell me:
backend running
Then I’ll guide you to test login, customer API, and connect with Supabase step by step.

From <https://www.microsoft365.com/hwav2/chat/conversation/20af5c7a-eb91-4670-87f2-0293544b1af0?version=19.2606.38031.0&capabilities=interopPromise%2CsuspendOnClose%2CautoStart&client-request-id=f2ad3f48-bf53-b449-af9c-4bfaa56a8b6b&fromCode=cmm6j3rjue2&SSRDesktopTest=2> 
