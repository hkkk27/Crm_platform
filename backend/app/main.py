# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware

# from app.core.config import settings
# from app.db.init_db import init_database
# from app.api.routes import health, auth, customers

# init_database()

# app = FastAPI(
#     title="OmniLink CRM Backend",
#     description="Backend API for secure loyalty CRM prototype",
#     version="1.0.0"
# )

# print(settings.allowed_origins)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=settings.allowed_origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# app.include_router(health.router)
# app.include_router(auth.router)
# app.include_router(customers.router)


# @app.get("/")
# def root():
#     return {
#         "message": "Welcome to OmniLink CRM Backend",
#         "docs": "/docs"
#     }
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import health, auth, customers, dashboard, consents, memberships, campaigns
from app.api.routes import customer_service
from app.api.routes import admin, audit
app = FastAPI(
    title="OmniLink CRM Backend",
    description="Backend API for secure loyalty CRM prototype",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(customers.router)
app.include_router(dashboard.router)
app.include_router(consents.router)
app.include_router(memberships.router)
app.include_router(campaigns.router)
app.include_router(customer_service.router)
app.include_router(admin.router)
app.include_router(audit.router)


@app.get("/")
def root():
    return {
        "message": "Welcome to OmniLink CRM Backend",
        "docs": "/docs"
    }