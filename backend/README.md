# OmniLink CRM - Backend

The backend for OmniLink CRM is built using **FastAPI** and uses a **SQLite** database to manage customer data, loyalty tiers, marketing campaigns, customer service tickets, and more.

## Features

- **Authentication & RBAC**: JWT-based login with role-based access control.
- **RESTful APIs**: Clean and performant endpoints for all CRM functionalities.
- **Modular Architecture**: Separate routers for campaigns, loyalty, customer service, dashboard, etc.
- **Database Integrated**: Uses SQLite for rapid development and deployment, with comprehensive data modeling.

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

3. Configure Environment Variables:
   Create a `.env` file in the root of the `backend` directory.

4. Start the Application:
   Run the FastAPI server using Uvicorn:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

5. Access the API Documentation:
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
