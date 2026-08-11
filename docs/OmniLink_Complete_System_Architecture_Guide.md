# OmniLink CRM - Complete System Architecture, Database, Workflow & Logic Guide

## Purpose
This document explains the complete OmniLink CRM system from login to dashboard, customer management, loyalty, campaigns, consent management, customer service, audit logs, database structure, APIs, calculations, and business logic.

---
# 1. High-Level Architecture

Frontend (HTML/CSS/JavaScript)
    ↓
FastAPI REST APIs
    ↓
Business Services Layer
    ↓
SQLite Database
    ↓
Audit Logs & Analytics

Main Modules:
- Authentication
- Dashboard
- Customer 360
- Loyalty
- Consent Management
- Campaign Management
- Customer Service
- Audit Logs
- Administration

---
# 2. Login Flow

Step 1
User enters:
- Email
- Password

Step 2
Frontend calls:
POST /auth/login

Step 3
Backend checks users table:

users
- email
- password
- role
- status

Step 4
If credentials match:
- JWT token created
- Role identified
- Permissions identified

Step 5
JWT returned

Step 6
Frontend stores JWT token.

Step 7
Every API call sends:
Authorization: Bearer <token>

---
# 3. Role Based Access Control

Roles:
- Admin
- CRM Team
- Store Team
- Management
- Customer Service
- Security / IT

Backend checks:
require_permission()

Example:
GET /memberships

Backend validates:
1. JWT valid?
2. User active?
3. User has loyalty permission?

If yes:
API executed.

---
# 4. Dashboard Flow

Dashboard page loads.

Frontend calls:
GET /dashboard/summary

Backend reads from:
- customers_360
- crm_campaigns
- crm_campaign_message_logs
- customer_service_tickets
- loyalty tables

Returns:
- KPI cards
- chart data
- table data

---
# 5. Dashboard KPIs Meaning

## Total Customers
Count of all rows in customers_360.

Formula:
COUNT(customer_id)

## Active Members
Customers whose membership tier is not Non-member.

## Member Percentage
(active_members / total_customers) * 100

## Average CLV
Average estimated customer lifetime value.

Column:
estimated_clv

## Repeat Purchase Rate
Customers with repeat_purchase_flag.

## Churn Risk
Customers with:
churn_risk_level = High

## Campaign Eligible
Customers allowed for marketing communication.

Uses:
- consent fields
- do_not_contact

---
# 6. Customer 360 Page

Customer page loads.

Frontend calls:
GET /customers

Data source:
customers_360

Purpose:
Show complete customer profile.

---
# 7. Customers_360 Table Explained

Main master table.

Contains:

Identity:
- customer_id
- customer_name
- crm_customer_key

Contact:
- phone_number
- email
- masked_phone_number
- masked_email

Location:
- customer_city
- customer_state

Behavior:
- total_sales
- total_transactions
- purchase_frequency
- avg_transaction_value

Engagement:
- app_sessions_30d
- website_visits
- wishlist_count

Loyalty:
- membership_tier
- points_earned
- points_redeemed
- points_balance

Marketing:
- customer_segment
- potential_member_score
- churn_risk_level

Consent:
- whatsapp_consent
- sms_consent
- email_consent
- app_notification_consent
- do_not_contact

This is the most important table in the CRM.

---
# 8. Consent Management

Purpose:
Ensure marketing follows customer permissions.

Fields:
- whatsapp_consent
- sms_consent
- email_consent
- app_notification_consent
- do_not_contact

Logic:

If do_not_contact = true

Customer cannot receive:
- email
- sms
- whatsapp
- app notifications

---
# 9. Loyalty System Architecture

Loyalty uses:

customers_360
+
loyalty_tier_rules
+
loyalty_benefits
+
loyalty_point_transactions
+
loyalty_redemptions
+
loyalty_tier_history

---
# 10. Loyalty Tier Rules Table

Stores configuration.

Columns:
- tier_name
- next_tier
- spend_unit
- points_multiplier
- minimum_recommendation_score

Rules:

Non-member
- 1 point
- next tier Silver

Silver
- 2 points
- next tier Gold

Gold
- 3 points
- next tier Platinum

Platinum
- 4 points
- highest tier

---
# 11. Loyalty Benefits Table

Stores benefits.

Examples:

Silver:
- birthday voucher
- offers
- delivery benefit

Gold:
- early access
- priority service

Platinum:
- VIP invitations
- previews
- premium support

---
# 12. Loyalty Recommendation Engine

Purpose:
Recommend who should become a member.

Inputs:
- total_sales
- CLV
- transactions
- recency
- digital engagement

Produces:
- potential_member_score
- tier_upgrade_score
- loyalty_segment
- recommendation_flag

This DOES NOT change membership.

It is only a recommendation.

---
# 13. Membership Purchase Flow

Customer buys Gold.

Frontend:
POST /memberships/{id}/purchase

Backend:
1. Validate tier.
2. Update customers_360.
3. Set membership_status = Active.
4. Set expiry date.
5. Write loyalty_tier_history.
6. Write audit log.

---
# 14. Points Earning Logic

Purchase Amount:
3400

Gold Multiplier:
3

Spend Unit:
1000

Formula:
base_units = floor(3400/1000)
= 3

points = 3 * 3
= 9

Stored:
customers_360
loyalty_point_transactions

---
# 15. Points Redemption Logic

Rule:
100 points = Rs 10

Minimum redemption:
100 points

Cannot exceed:
20% order value

Stores:
- loyalty_redemptions
- loyalty_point_transactions

Updates:
- points_balance

---
# 16. Campaign Management

Campaign Creation:
POST /campaigns

Campaign includes:
- segment
- channel
- template

Audience Preview:
POST /campaigns/{id}/audience-preview

Uses:
- customer_segment
- loyalty_segment
- consent data

---
# 17. Campaign Delivery Flow

Campaign
↓
Audience Selection
↓
Consent Filter
↓
Eligible Customers
↓
Message Rendering
↓
Discord Send
↓
Message Logs

Tables:
- crm_campaigns
- crm_campaign_message_logs

---
# 18. Customer Service Module

Main table:
customer_service_tickets

Contains:
- ticket_id
- customer_id
- status
- priority
- issue_category
- assigned_to
- sla_due

---
# 19. Ticket Update Flow

Agent opens ticket
↓
Adds notes
↓
Changes status
↓
Adds follow-up
↓
Backend updates ticket
↓
Creates timeline entry
↓
Creates audit log

---
# 20. Customer Service Timeline Table

Stores:
- event_type
- event_title
- event_description
- old_status
- new_status
- created_by
- created_at

Purpose:
Track ticket history.

---
# 21. Audit Logging

Every action writes to audit table.

Examples:
- Login
- Loyalty purchase
- Redeem points
- Ticket update
- Campaign execution

Fields:
- user
- action
- object
- timestamp

---
# 22. End-to-End System Flow

User Login
↓
JWT Generated
↓
Permissions Loaded
↓
Dashboard Loaded
↓
Customer Analytics Read
↓
Loyalty Recommendations Calculated
↓
Campaign Segments Built
↓
Consent Applied
↓
Campaign Sent
↓
Customer Interacts
↓
Customer Service Handles Request
↓
Audit Logs Generated

---
# 23. Database Dependency Map

customers_360
    ├── Dashboard
    ├── Customer 360
    ├── Loyalty
    ├── Campaigns
    └── Customer Service

loyalty_tier_rules
    └── Loyalty Engine

loyalty_benefits
    └── Loyalty Engine

loyalty_point_transactions
    └── Reward Ledger

loyalty_redemptions
    └── Redemptions

loyalty_tier_history
    └── Membership History

crm_campaigns
    └── Campaign Management

crm_campaign_message_logs
    └── Campaign Analytics

customer_service_tickets
    └── Customer Service

customer_service_timeline
    └── Ticket History

users
    └── Authentication & RBAC

password_reset_codes
    └── Forgot Password

---
# 24. Final Business Story

OmniLink CRM starts with customer data.

Customer behavior is stored inside customers_360.

Dashboard converts data into KPIs.

Customer 360 converts data into insights.

Loyalty converts data into membership actions.

Campaigns convert segments into communications.

Consent ensures compliance.

Customer Service resolves customer issues.

Audit Logs track every operation.

Together these modules form a complete CRM platform.
