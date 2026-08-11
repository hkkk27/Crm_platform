# OmniLink CRM - Backend

The backend for OmniLink CRM is built using **FastAPI** and uses a **SQLite** database to manage customer data, loyalty tiers, marketing campaigns, customer service tickets, and more.

> [!IMPORTANT]
> **For detailed backend instructions, API design, and database schema diagrams, please read the [Final Software Project Documentation PDF](../docs/Final%20Software%20Project%20Documentation.pdf).**

## Features & Architecture

- **Authentication & RBAC**: JWT-based login with role-based access control. Passwords are secured using PBKDF2-HMAC-SHA256 with a random salt.
- **RESTful APIs**: Clean and performant endpoints for all CRM functionalities (Auth, Customers, Consents, Memberships, Campaigns, Customer Service, Admin, Audit).
- **Performance Controls**: Direct SQL aggregation for summaries, Backend TTL caching for short-lived summary data, and server-side pagination.
- **Modular Architecture**: Layered design separating presentation (API routers), business logic (services), and data access (SQLite queries).
- **Database Integrated**: Uses SQLite for rapid development and deployment. Includes a central `customers_360` snapshot table, operational tables, and append-only ledgers/timelines for historical tracking.

## Prerequisites

- Python 3.9+
- pip (Python package installer)

## Setup & Installation

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the Application:
   Run the FastAPI server using Uvicorn (make sure you are in the `backend` folder):
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

4. Access the API Documentation:
   Once the server is running, navigate to:
   - **Swagger UI**: `http://localhost:8000/docs`
   - **ReDoc**: `http://localhost:8000/redoc`

## Project Structure

- `app/api/`: API routers and endpoints.
- `app/core/`: Security, authentication, and core configurations.
- `app/db/`: Database configuration and SQLite client setup.
- `app/schemas/`: Pydantic models for data validation.
- `app/services/`: Core business logic (loyalty calculations, campaign dispatch, etc.).
- `app/main.py`: The FastAPI application instance and entry point.

> **Reminder:** For full documentation on the backend data model and workflows, please refer to the [Final Software Project Documentation](../docs/Final%20Software%20Project%20Documentation.pdf).
