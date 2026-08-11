# OmniLink CRM

OmniLink CRM is a comprehensive Customer Relationship Management platform designed for modern retail. It seamlessly integrates customer analytics, loyalty programs, marketing campaigns, consent management, and customer service into a single cohesive system.

## Project Structure

- **frontend/**: The user interface built with HTML/CSS/JS. Contains the CRM dashboards, Customer 360 views, loyalty management, and administrative panels.
- **backend/**: The FastAPI REST APIs that power the frontend, handling authentication, role-based access control, business logic, and database interactions using SQLite.
- **docs/**: Comprehensive project documentation, including the System Architecture Guide and Technical Bible.

## Key Modules

- **Dashboard**: Real-time KPIs and business insights.
- **Customer 360**: Complete customer profiles including demographics, purchase behavior, and digital engagement.
- **Loyalty System**: Tier-based loyalty management, recommendation engine, and point tracking.
- **Campaign Management**: Targeted marketing communications integrated with Discord.
- **Consent Management**: Strict adherence to customer communication preferences.
- **Customer Service**: Complete ticketing system with SLA tracking and history.
- **Audit Logs**: Comprehensive tracking of all system operations.

## Architecture

The system uses a modern 3-tier architecture:
1. **Frontend**: HTML/CSS/JavaScript
2. **Backend**: FastAPI (Python) REST API
3. **Database**: SQLite (via SQLAlchemy or raw queries)

## Setup

For detailed instructions on running the backend and viewing the frontend, please refer to the respective `README.md` files in the `frontend` and `backend` directories.

## Documentation

Detailed architectural and technical documentation can be found in the `docs/` directory.
