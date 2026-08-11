# OmniLink CRM

An Integrated Customer Relationship Management Platform for Retail Customer Intelligence, Loyalty, Campaigns, Consent, and Customer Service.

**Prepared by:** Harshit Singh and Ankit Kumar (Team Syndicate)  
**Project Mentor:** Mrs. Varsha Domb  
**Date:** 24/07/2026  

> [!IMPORTANT]
> **For detailed instructions, comprehensive architecture breakdowns, and full project details, please read the [Final Software Project Documentation PDF](docs/Final%20Software%20Project%20Documentation.pdf).**

## Executive Summary

OmniLink CRM was developed to address a common retail-business problem: customer information is often distributed across separate systems for purchases, loyalty membership, marketing communication, consent, and support operations. This fragmentation makes it difficult for employees to understand the customer completely, identify business opportunities, communicate through permitted channels, and provide consistent service.

The platform provides a unified **Customer 360** data foundation and connects that foundation with multiple operational modules:
- **Dashboard**: Converts customer and operational data into live KPIs and charts.
- **Customer 360**: Provides searchable, enriched customer profiles.
- **Consent Management**: Records communication permissions and Do-Not-Contact status.
- **Loyalty Management**: Supports membership tiers, benefits, points, redemptions, and recommendation logic.
- **Campaign Management**: Creates segmented audiences, validates consent, personalizes templates, demonstrates delivery through Discord, and records outcomes.
- **Customer Service**: Manages tickets, follow-ups, resolutions, timelines, SLA information, and workload.
- **Admin and Audit**: Provide operational control and traceability.

## Technology Stack

The system uses a modern 3-tier architecture:
1. **Frontend**: HTML, CSS, JavaScript (Vanilla), and Chart.js for visualization.
2. **Backend**: Python and FastAPI, served via Uvicorn.
3. **Database**: SQLite.
4. **Security**: JWT Bearer authentication, Role-Based Access Control (RBAC), and PBKDF2-HMAC-SHA256 password hashing.
5. **External Integrations**: Discord webhooks used for simulated campaign delivery.

## Project Structure

- `frontend/`: The user interface built with HTML/CSS/JS. Contains the CRM dashboards, Customer 360 views, loyalty management, and administrative panels.
- `backend/`: The FastAPI REST APIs that power the frontend, handling authentication, business logic, and database interactions.
- `docs/`: Comprehensive project documentation.

## Getting Started

For detailed instructions on running the backend and viewing the frontend, please refer to the respective `README.md` files in the `frontend` and `backend` directories.

> **Reminder:** Don't forget to check the [Final Software Project Documentation](docs/Final%20Software%20Project%20Documentation.pdf) for an in-depth walkthrough of the system.
