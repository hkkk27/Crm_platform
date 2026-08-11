# OmniLink CRM — Complete Technical Knowledge Guide

**Purpose:** A detailed, presentation-ready explanation of how the complete OmniLink CRM works—from opening the frontend and logging in, through JWT authentication, role-based access, dashboard analytics, Customer 360, consent, loyalty, campaigns, customer service, audit logging, database updates, and reporting.

**Audience:** Project team, evaluator, viva panel, frontend developer, backend developer, and future maintainers.

**Important note:** This document explains the schema and logic confirmed during development. If the live SQLite database has been altered after this document was created, run `PRAGMA table_info(<table_name>)` to verify the exact physical columns.

---

# 1. The Simplest Way to Understand OmniLink CRM

OmniLink CRM is a connected retail CRM system.

The system begins with customer and transaction data. It turns that data into customer profiles, dashboard metrics, loyalty recommendations, campaign audiences, and customer-service workflows.

The complete business flow is:

```text
Retail and customer data
        ↓
Customer 360 profile
        ↓
Dashboard analytics and customer insights
        ↓
Membership, loyalty, churn, and segmentation logic
        ↓
Consent and Do-Not-Contact validation
        ↓
Campaign audience and personalized message
        ↓
Campaign response and business metrics
        ↓
Customer-service ticket handling
        ↓
Timeline and audit history
```

The technical flow is:

```text
Browser frontend
        ↓ HTTP/JSON
FastAPI route
        ↓
Authentication and permission check
        ↓
Business logic/service functions
        ↓
SQLite queries
        ↓
JSON response
        ↓
Frontend rendering
```

---

# 2. Main Technology Stack

## Frontend

```text
HTML
CSS
JavaScript
Chart.js
localStorage for the signed-in session/token
```

The frontend is responsible for:

- Showing forms, pages, cards, charts, tables, drawers, and filters.
- Sending API requests.
- Adding the JWT Bearer token to protected requests.
- Converting backend snake_case fields into frontend-friendly values when required.
- Rendering API responses.
- Showing validation and backend errors.

The frontend is not supposed to be the permanent database.

## Backend

```text
Python
FastAPI
JWT authentication
Role-based access control
SQLite
```

The backend is responsible for:

- Verifying login credentials.
- Creating and validating JWT tokens.
- Enforcing role permissions.
- Reading and updating SQLite.
- Applying business rules.
- Building dashboard metrics.
- Calculating loyalty recommendations.
- Filtering campaign audiences by consent.
- Sending campaign demonstrations through Discord.
- Updating customer-service tickets and timeline events.
- Recording audit logs.

## Database

The main database file is:

```text
omnilink_crm.db
```

SQLite stores structured records in tables. A table contains:

```text
Columns = attributes or fields
Rows = individual records or events
```

Example:

```text
customers_360 table
One row = one enriched customer record
One column = one customer attribute, such as customer_name or total_sales
```

---

# 3. Application Startup

The FastAPI application starts through a command such as:

```powershell
uvicorn app.main:app --reload
```

At startup:

1. Python imports `app.main`.
2. FastAPI creates the application object.
3. CORS configuration allows the frontend origin to call the backend.
4. Route files are registered.
5. Uvicorn listens on `http://127.0.0.1:8000`.
6. Swagger is available at `http://127.0.0.1:8000/docs`.

Typical registered route groups include:

```text
/auth
/dashboard
/customers
/consents
/memberships
/campaigns
/customer-service
/audit or administrative routes
```

---

# 4. Complete Login and JWT Flow

## 4.1 User opens the frontend

The login page displays email and password inputs.

Example:

```text
Email: admin@omnilink.com
Password: **********
```

## 4.2 Frontend sends login request

The frontend calls:

```http
POST /auth/login
```

Example body:

```json
{
  "email": "admin@omnilink.com",
  "password": "1234567890"
}
```

## 4.3 Backend reads the `users` table

The backend searches for the email in:

```text
users
```

Important columns:

```text
user_id   — internal unique row ID
email     — login name and unique identity
password  — current project password value
role      — Admin, CRM Team, Customer Service, etc.
status    — Active or Inactive
```

One row represents one application user.

## 4.4 Credential checks

The backend verifies:

```text
Does the user exist?
Is the status Active?
Does the submitted password match?
```

If any check fails, login is rejected.

## 4.5 JWT creation

If the checks pass, the backend creates a JWT token.

The token normally contains claims such as:

```text
sub  — user email
role — user role
exp  — token expiration time
```

The JWT is digitally signed with the backend secret.

The token is not a database row. It is a signed login credential carried by the frontend.

## 4.6 Frontend stores session values

The frontend stores values such as:

```text
omnilink_token
omnilink_email
omnilink_role
crm_session
```

The exact set depends on the page integration.

## 4.7 Protected API request

When the frontend calls a protected endpoint, it sends:

```http
Authorization: Bearer <jwt-token>
```

## 4.8 Backend validates token

`get_current_user()`:

1. Reads the Bearer token.
2. Verifies the signature.
3. Checks the expiration.
4. Reads `sub` and `role`.
5. Returns the current user context.

## 4.9 Permission check

A route then calls:

```python
require_permission(user, "dashboard")
```

or:

```python
require_permission(user, "loyalty")
```

The role-permission mapping determines whether the route may continue.

Example:

```text
Admin → all modules
CRM Team → customers, consent, loyalty, campaigns, dashboard
Customer Service → customer service and selected supporting modules
Store Team → customers and loyalty
Management → dashboard/KPI/campaign visibility
Security / IT → audit and administration
```

## 4.10 Why both frontend and backend access checks are needed

Frontend navigation hiding improves user experience, but it is not security.

Backend `require_permission()` is the real security boundary. A user cannot gain access merely by typing an API URL if the role lacks permission.

---

# 5. Forgot-Password Flow

## Database table: `password_reset_codes`

Columns:

```text
reset_id   — unique reset request ID
email      — account requesting reset
code_hash  — hash of the reset code
expires_at — expiration timestamp
used       — 0 before use, 1 after successful reset
created_at — request creation timestamp
```

## Request flow

```text
Frontend submits email
→ POST /auth/forgot-password/request
→ Backend checks users table
→ Creates a six-digit reset code
→ Hashes the code
→ Stores hash and expiry
→ Prints development code in backend terminal
```

The plain reset code is not stored in SQLite.

## Reset flow

```text
Frontend submits email + code + new password
→ POST /auth/forgot-password/reset
→ Backend hashes submitted code
→ Finds matching unused record
→ Checks expiration
→ Updates users.password
→ Marks reset code used
→ Creates audit record
```

The current demo prints the code in the terminal because Outlook SMTP authentication was unavailable. A production version should use password hashing and Microsoft Graph or another transactional email service.

---

# 6. Core Database Tables and Their Roles

## 6.1 `users`

Purpose:

```text
Application authentication and role identity
```

One row means:

```text
One employee/application user
```

Used by:

```text
Login
Forgot password
Role checks
Audit attribution
```

## 6.2 `customers_360`

Purpose:

```text
Main enriched customer snapshot
```

One row normally represents one customer/customer snapshot containing identity, retail behavior, product behavior, store behavior, digital engagement, consent, loyalty, segmentation, churn, and data-quality fields.

This is the most important analytical table and feeds:

```text
Dashboard
Customer 360
Consent
Loyalty
Campaign segmentation
Customer Service context
```

## 6.3 Campaign tables

```text
crm_campaigns
crm_campaign_templates
crm_campaign_runs
crm_campaign_message_logs
```

Each table has a separate job:

```text
crm_campaigns             — campaign definition and aggregate counters
crm_campaign_templates    — reusable message structure
crm_campaign_runs         — individual execution/simulation runs
crm_campaign_message_logs — one message attempt/customer response record
```

## 6.4 Customer Service tables

```text
customer_service_agents
customer_service_tickets
customer_service_timeline
```

```text
agents   — employee/agent identity and status
tickets  — current ticket snapshot
timeline — append-only history of ticket events
```

## 6.5 Loyalty tables

```text
loyalty_tier_rules
loyalty_benefits
loyalty_point_transactions
loyalty_redemptions
loyalty_tier_history
```

```text
rules        — configurable multipliers and recommendation thresholds
benefits     — tier-specific benefits
transactions — point ledger
redemptions  — business record of redemption
tier history — membership purchase or tier movement history
```

## 6.6 `audit_logs`

Purpose:

```text
Who performed which operation, on what object, and when
```

This is different from a business timeline.

```text
Customer Service timeline = history of the ticket
Audit log = history of user/system access and operations
```

---

# 7. Understanding `customers_360` in Detail

The enriched dataset groups can be understood as follows.

## 7.1 Customer identity

```text
customer_id      — source customer identifier
crm_customer_key — standardized CRM key, e.g. CRM-000001
customer_name    — display name
age              — numeric age if available
age_group        — grouped age range
gender           — source demographic value
marital_status   — source demographic value
number_of_children
education_level
occupation
income_bracket
```

Usage:

```text
Customer profile
Demographic analysis
Segmentation
Personalization where consent permits
```

## 7.2 Contact information

```text
phone_number
masked_phone_number
email
masked_email
```

Usage:

```text
Full values for authorized operations
Masked values for safer display
Consent-aware campaign reachability
Customer Service contact context
```

## 7.3 Geography

```text
customer_zip_code
customer_city
customer_state
customer_city_tier
store_zip_code
store_city
store_state
distance_to_store
```

Usage:

```text
Top-city charts
Regional campaigns
Nearest-store/service context
Geographic customer analysis
```

## 7.4 Transaction-level attributes

```text
transaction_id
transaction_date
transaction_date_parsed
quantity
unit_price
discount_applied
payment_method
transaction_hour
day_of_week
week_of_year
month_of_year
```

Usage:

```text
Transaction context
Seasonality
Time-of-day behavior
Discount sensitivity
Payment preferences
```

Important design note:

The enriched dataset appears to combine detailed transaction attributes and aggregate customer attributes. In a normalized production database, transactions would normally be in a separate transaction table with multiple rows per customer.

## 7.5 Purchase behavior and aggregates

```text
avg_purchase_value
purchase_frequency
last_purchase_date
last_purchase_date_parsed
days_since_last_purchase
avg_discount_used
online_purchases
in_store_purchases
avg_items_per_transaction
avg_transaction_value
total_returned_items
total_returned_value
total_sales
total_transactions
total_items_purchased
total_discounts_received
avg_spent_per_category
max_single_purchase_value
min_single_purchase_value
```

Usage:

```text
Dashboard KPIs
Loyalty recommendation score
Churn analysis
Value segmentation
Campaign targeting
```

Meaning examples:

```text
total_sales = cumulative monetary sales associated with customer record
total_transactions = number of purchases
avg_transaction_value = average money per transaction
days_since_last_purchase = recency indicator
purchase_frequency = categorical or numeric frequency indicator
```

## 7.6 Product attributes

```text
product_id
product_name
product_category
product_brand
product_rating
product_review_count
product_stock
product_return_rate
product_size
product_weight
product_color
product_material
product_manufacture_date
product_expiry_date
product_shelf_life
```

Usage:

```text
Preferred-category messaging
Product/segment analysis
Campaign template personalization
Customer Service order context
```

## 7.7 Promotion attributes

```text
promotion_id
promotion_type
promotion_start_date
promotion_end_date
promotion_effectiveness
promotion_channel
promotion_target_audience
```

Usage:

```text
Promotion history and effectiveness context
Campaign analysis
Discount and response behavior
```

## 7.8 Store and channel attributes

```text
store_id
store_name
store_format
store_location
preferred_store
primary_shopping_channel
online_purchases
in_store_purchases
```

Usage:

```text
Omnichannel profile
Store targeting
Channel preference
Operational reporting
```

## 7.9 Digital engagement attributes

```text
app_installed
app_sessions_30d
product_views_30d
wishlist_count
cart_abandoned
push_token_available
last_app_open_date
email_subscriptions
app_usage
website_visits
social_media_engagement
```

Usage:

```text
Loyalty recommendation score
App campaign eligibility
Digital propensity
Abandoned-cart opportunity
Engagement segmentation
```

## 7.10 Consent fields

```text
email_consent
whatsapp_consent
sms_consent
app_notification_consent
personalization_consent
do_not_contact
consent_source
consent_given_date
consent_withdrawn_date
preferred_campaign_channel
```

Meaning:

```text
email_consent — email promotional permission
whatsapp_consent — WhatsApp promotional permission
sms_consent — SMS promotional permission
app_notification_consent — push/app permission
personalization_consent — permission for personalized use where applicable
do_not_contact — master marketing block
consent_source — where consent was collected
```

## 7.11 Loyalty fields

```text
membership_status
membership_tier
points_earned
points_redeemed
points_balance
membership_expiry_date
upgrade_eligibility
```

Meaning:

```text
membership_status — Active or Non-member state
membership_tier — actual purchased/assigned tier
points_earned — accumulated reward earning counter
points_redeemed — accumulated redeemed counter
points_balance — currently redeemable points
membership_expiry_date — validity date
upgrade_eligibility — older/static source recommendation flag
```

The system now calculates a fresh `recommendation_flag` at API time instead of relying only on the static source flag.

## 7.12 Analytical fields

```text
customer_segment
potential_member_score
churn_risk_level
estimated_clv
repeat_purchase_flag
recommendation_reason_codes
```

Meaning:

```text
customer_segment — business classification
potential_member_score — non-member conversion propensity
churn_risk_level — Low, Medium, or High risk
estimated_clv — predicted/estimated customer lifetime value
repeat_purchase_flag — customer has repeat behavior
recommendation_reason_codes — explanation such as frequent purchase or app active
```

## 7.13 Campaign eligibility flags

```text
campaign_eligible_whatsapp
campaign_eligible_sms
campaign_eligible_email
campaign_eligible_app
```

These fields represent precomputed channel eligibility. Final campaign execution should still validate active consent and DNC.

## 7.14 Data-quality fields

```text
missing_email_flag
missing_phone_flag
duplicate_customer_flag
data_quality_score
```

Usage:

```text
Dashboard data-quality KPIs
Operational cleanup
Campaign exclusion or caution
```

---

# 8. Dashboard Page — Complete Operation

## 8.1 Frontend load

After login, the dashboard page calls:

```http
GET /dashboard/summary
```

The request includes the JWT token.

## 8.2 Backend checks

```text
JWT valid?
Role has dashboard permission?
```

## 8.3 Backend data sources

```text
customers_360
crm_campaigns
crm_campaign_message_logs
customer_service_tickets
loyalty tables where needed
```

## 8.4 KPI definitions

### Total Customers

```sql
COUNT(*) FROM customers_360
```

Meaning:

```text
Size of the customer master dataset
```

### Active Members

Counts customers whose membership is not Non-member.

Meaning:

```text
Customers currently enrolled in a membership tier
```

### Member Percentage

```text
(active members / total customers) × 100
```

Meaning:

```text
Loyalty penetration across the customer base
```

### Average CLV

```sql
AVG(estimated_clv)
```

Meaning:

```text
Average projected customer lifetime business value
```

### Repeat Purchase Rate

```text
customers with repeat_purchase_flag / total customers × 100
```

Meaning:

```text
Share of customers showing repeat purchase behavior
```

### High-Churn Customers

```sql
COUNT(*) WHERE churn_risk_level = 'High'
```

Meaning:

```text
Customers needing retention attention
```

### Campaign Eligible

Counts customers with at least one eligible marketing channel.

Meaning:

```text
Potential reach before final campaign filters
```

### Total Sales

```sql
SUM(total_sales)
```

Meaning:

```text
Aggregate sales represented in the customer master
```

### Open Service Tickets

Counts tickets not in Resolved or Closed.

Meaning:

```text
Current unresolved service workload
```

### Total Campaigns

```sql
COUNT(*) FROM crm_campaigns
```

### WhatsApp Reachable

Customers with WhatsApp consent and no DNC.

### Missing Emails

Customers with null/blank email.

### Average Data Quality

Can use average `data_quality_score` or percentage of records with essential fields, depending on the implemented query.

### SLA Compliance

```text
SLA-compliant tickets / total tickets × 100
```

## 8.5 Chart meanings

### Customer Segmentation

Groups by:

```text
customer_segment
```

Shows how customers are distributed across business groups.

### Churn Risk

Groups by:

```text
churn_risk_level
```

Shows Low/Medium/High risk distribution.

### Membership Tiers

Groups by:

```text
membership_tier
```

Shows Non-member, Silver, Gold, and Platinum counts.

### Top Cities

Groups by `customer_city`, sorts count descending, and limits the result.

### Consent Reachability

Counts approved and non-DNC customers for Email, SMS, WhatsApp, and App.

### Campaign Status

Groups campaigns by:

```text
Draft
Running
Paused
Completed
```

### Campaign Performance

Uses message logs:

```text
opened
clicked
converted
revenue
```

### Ticket Status

Groups service tickets by status.

### Ticket Trend

Groups tickets by normalized creation date and compares created, resolved, and escalated counts.

### Data Quality

Shows missing emails, missing phones, duplicates if available, and good records.

---

# 9. Customer 360 Page — Complete Operation

## 9.1 Customer list

Frontend calls a customer-list endpoint.

Backend selects customer fields from `customers_360` and returns JSON.

The list can show:

```text
Customer ID
Name
City
Segment
Membership
CLV
Churn risk
Preferred category/channel
```

## 9.2 Customer detail

When View is clicked:

```text
Frontend reads customer ID
→ GET customer detail endpoint
→ Backend queries WHERE customer_id = ?
→ Returns complete customer snapshot
→ Frontend opens profile drawer/page
```

## 9.3 Customer timeline

Customer timeline can combine business events such as:

```text
Purchase
Consent change
Membership purchase
Campaign response
Customer Service interaction
```

In the current project, some timeline views use dedicated module tables and some use enriched source attributes.

## 9.4 Why Customer 360 is central

Customer 360 allows every team to see one unified customer context instead of separate disconnected systems.

---

# 10. Consent Management — Detailed Logic

Consent is separate from recommendation.

Example:

```text
Customer is a strong Gold-upgrade candidate
Email consent = false
WhatsApp consent = true
DNC = false
```

Result:

```text
Recommendation remains valid
Email campaign not allowed
WhatsApp campaign allowed
```

If:

```text
DNC = true
```

all promotional channels are blocked regardless of individual channel flags.

Consent endpoints support viewing and updating preferences. Every consent update should create an audit record.

---

# 11. Loyalty Page — Complete Operation

## 11.1 Tables used

```text
customers_360
loyalty_tier_rules
loyalty_benefits
loyalty_point_transactions
loyalty_redemptions
loyalty_tier_history
```

## 11.2 Summary endpoint

```http
GET /memberships/summary
```

The optimized endpoint uses direct SQL aggregates instead of building a full loyalty object for every customer.

This avoids the earlier N+1 query problem.

### Loyalty summary fields

```text
total_customers
active_members
non_members
potential_members
total_points_earned
total_points_redeemed
total_points_balance
outstanding_points_value
member_sales
tier_distribution
```

## 11.3 Tier rules

`loyalty_tier_rules` columns:

```text
rule_id
 tier_name
next_tier
membership_price
spend_unit
points_multiplier
minimum_recommendation_score
is_active
created_at
updated_at
```

Current business setup:

```text
Non-member → 1 point per Rs. 1,000
Silver → 2 points per Rs. 1,000
Gold → 3 points per Rs. 1,000
Platinum → 4 points per Rs. 1,000
```

## 11.4 Benefits

Tier benefits come from `loyalty_benefits`, not hardcoded frontend arrays.

Examples:

```text
Silver — birthday voucher, member offers, standard delivery benefit
Gold — free delivery, early sale access, priority support
Platinum — priority delivery, pre-launch access, pre-booking, exclusive events
```

## 11.5 Potential member logic

For non-members:

```text
potential_member_score >= 70 → High Potential Member
50–69 → Medium Potential Member
below 50 → Low Potential Member
```

This is an internal recommendation only. Any customer may directly purchase membership.

## 11.6 Upgrade score

The internal upgrade score uses:

```text
Total sales: max 30
Total transactions: max 20
Estimated CLV: max 20
Recent activity: max 10
Repeat purchase: max 15
Digital engagement: max 5
Total: 100
```

### Sales score

```text
>= 50,000 → 30
>= 20,000 → 20
>= 10,000 → 10
```

### Transaction score

```text
>= 20 → 20
>= 10 → 12
>= 5 → 6
```

### CLV score

```text
>= 50,000 → 20
>= 20,000 → 12
>= 10,000 → 6
```

### Recency

```text
<= 30 days → 10
<= 90 days → 5
```

### Repeat and digital

```text
repeat_purchase_flag → 15
strong app/web/wishlist engagement → 5
```

## 11.7 Recommended segments

```text
High Potential Member
Medium Potential Member
Low Potential Member
Silver-to-Gold Recommended
Gold-to-Platinum Recommended
Silver Member
Gold Member
Top-Tier Platinum
Loyal but High Churn Risk
```

## 11.8 Membership purchase

```http
POST /memberships/{customer_id}/purchase
```

Operation:

```text
Validate customer
Validate tier
Update customers_360 membership fields
Set expiry
Insert loyalty_tier_history
Create audit log
Return updated customer
```

## 11.9 Earn points

```http
POST /memberships/{customer_id}/earn
```

Formula:

```text
base_units = floor(order_amount / spend_unit)
points = base_units × multiplier
```

Updates:

```text
customers_360.points_earned
customers_360.points_balance
loyalty_point_transactions
```

## 11.10 Redeem points

```http
POST /memberships/{customer_id}/redeem
```

Rules:

```text
100 points = Rs. 10
minimum redemption = 100 points
cannot exceed balance
cannot exceed 20% of order amount
```

Updates:

```text
customers_360.points_redeemed
customers_360.points_balance
loyalty_redemptions
loyalty_point_transactions
```

## 11.11 Performance optimization

The initial implementation loaded rule and benefits with additional SQL calls for every customer.

That produced an N+1 query pattern:

```text
1 customer list query
+ one rule query per customer
+ one benefits query per customer
```

The optimized approach:

```text
Summary → direct SQL aggregation
List → limited/paginated lightweight customer objects
Rules → separate endpoint
Benefits → separate endpoint
Customer detail → load detailed benefits only when needed
```

---

# 12. Campaign Module — Complete Operation

## 12.1 Campaign creation

Frontend sends:

```http
POST /campaigns
```

Campaign definition includes:

```text
campaign_name
campaign_type
business_channel
demo_platform
target_segment
template_id
status
created_by
created_at
```

## 12.2 Templates

Templates contain:

```text
template_name
template_type
template_json.title
template_json.body
template_json.cta_text
template_json.cta_url
template_json.footer
```

Placeholders are rendered with customer fields.

Example:

```text
{{customer_name}}
{{membership_tier}}
{{points_balance}}
{{preferred_category}}
```

The backend aliases `product_category AS preferred_category` where needed.

## 12.3 Audience preview

The backend:

```text
Loads campaign
Builds segment query
Gets potential audience
Checks channel consent
Checks DNC
Returns total, eligible, and removed counts
```

## 12.4 Send simulation

```http
POST /campaigns/{campaign_id}/simulate-send
```

Flow:

```text
Create run ID
Load eligible audience
Limit demo send count
Render one personalized message per customer
Choose Discord webhook
Send message
Record status
Update counters
```

## 12.5 Message logs

One row in `crm_campaign_message_logs` means one customer-message attempt.

Columns include:

```text
message_id
run_id
campaign_id
customer_id
customer_name
business_channel
demo_platform
sent_status
rendered_title
rendered_message
opened
clicked
converted
revenue
error_message
sent_at
```

Meaning of status:

```text
sent — Discord accepted message
simulated — no live webhook used/demo record
failed — delivery failed
```

## 12.6 Campaign analytics

Uses message-log aggregations:

```text
sent count
failed count
opened count
clicked count
converted count
revenue
```

---

# 13. Customer Service — Complete Operation

## 13.1 Ticket table

`customer_service_tickets` stores the current ticket snapshot.

Major columns:

```text
ticket_id
customer_id
crm_customer_key
customer_name
linked_order_id
issue_category
query_type
priority
status
assigned_agent_id
assigned_to
created_on
sla_due
last_updated
channel
sla_status
escalation_level
escalated_to
membership_tier
masked_phone_number
masked_email
customer_city
customer_segment
churn_risk_level
product_id
product_name
product_category
transaction_date
order_value
payment_method
delivery_status
return_refund_status
description
call_review
contact_result
follow_up_required
follow_up_date
follow_up_note
internal_notes
resolution_summary
completed_on
last_action_by
```

One row means:

```text
Current state of one customer-service ticket
```

## 13.2 Ticket list

```http
GET /customer-service/tickets
```

Returns ticket rows for table rendering.

## 13.3 Ticket detail

```http
GET /customer-service/tickets/{ticket_id}
```

Returns:

```text
ticket
full timeline
action history
```

## 13.4 Update

```http
PUT /customer-service/tickets/{ticket_id}/update
```

Valid fields:

```text
status
priority
call_review
contact_result
follow_up_required
follow_up_date
follow_up_note
internal_notes
resolution_summary
```

Validation:

```text
Resolved/Closed requires resolution summary
Follow-up Yes requires date
```

## 13.5 Timeline table

`customer_service_timeline` is append-only history.

One row means:

```text
One event in a ticket's lifecycle
```

Examples:

```text
Ticket Created
Assigned
Status Changed
Call Review
Follow-up Scheduled
Escalated
Resolved
Closed
```

## 13.6 Why snapshot plus timeline

```text
Ticket table → current truth
Timeline table → history of how current truth was reached
```

This pattern is common in operational systems.

---

# 14. Audit Logging

`create_audit_log()` is called after important operations.

Examples:

```text
View customer
Update consent
Purchase membership
Earn points
Redeem points
Create campaign
Send campaign
View ticket
Update ticket
Password reset
```

Main audit fields:

```text
audit_id
user_email
user_role
action
object_type
object_id
status
details
created_at
```

One row means:

```text
One application action performed or attempted
```

Audit logging supports:

```text
Traceability
Security review
Operational accountability
Demo evidence
```

---

# 15. Frontend-to-Backend Request Pattern

All protected page modules generally follow this pattern:

```javascript
const response = await fetch(API_BASE_URL + endpoint, {
  method: "GET",
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`
  }
});
```

For POST/PUT:

```javascript
body: JSON.stringify(payload)
```

Backend responds with JSON:

```json
{
  "success": true,
  "data": []
}
```

Frontend normalizes and renders the response.

---

# 16. Important Distinctions for Viva Questions

## Authentication vs authorization

```text
Authentication = Who is the user?
Authorization = What is the user allowed to access?
```

## Customer segment vs loyalty segment

```text
customer_segment = existing source/business segment
loyalty_segment = calculated loyalty recommendation segment
```

## Membership tier vs upgrade score

```text
membership_tier = actual purchased tier
upgrade score = internal CRM recommendation
```

## Points balance vs tier

```text
points_balance = redeemable points
membership_tier = purchased membership
```

Redeeming points does not automatically downgrade the membership.

## Consent vs recommendation

```text
Recommendation says what opportunity exists.
Consent says whether/how the company may communicate.
```

## Ticket snapshot vs timeline

```text
Ticket row = current state
Timeline rows = historical events
```

## Campaign business channel vs Discord

```text
Business channel = Email, SMS, WhatsApp, App
Discord = demonstration delivery platform
```

---

# 17. End-to-End Example

Consider Customer 1.

## Step 1 — Customer data

`customers_360` contains:

```text
Customer identity
Purchases
CLV
Membership
Consent
Engagement
Churn risk
```

## Step 2 — Dashboard

Customer 1 contributes to:

```text
Total customer count
Sales
CLV average
Segment distribution
Churn distribution
Consent reachability
Tier distribution
```

## Step 3 — Loyalty

Backend calculates:

```text
Potential score if non-member
Upgrade score if member
Recommended tier
Loyalty segment
Contactable channels
```

## Step 4 — Campaign

Campaign chooses the segment.

Backend checks:

```text
Is Customer 1 in target segment?
Is selected channel allowed?
Is DNC false?
```

If yes, the customer is eligible.

## Step 5 — Message

Template placeholders are replaced with Customer 1 values and sent to Discord for demonstration.

## Step 6 — Service interaction

If Customer 1 contacts support, a ticket is opened with customer/order context.

The employee updates the ticket, and the backend stores:

```text
Current ticket state
Timeline event
Audit record
```

This demonstrates how one customer record can support multiple departments.

---

# 18. Current Project Limitations

Be honest during presentation:

```text
SQLite is suitable for prototype/demo, not high-concurrency enterprise scale.
Current passwords are plain text for compatibility and must be hashed in production.
Reset email uses terminal fallback in development.
Discord simulates external campaign delivery.
Some data is synthetic/demo retail data.
customers_360 is denormalized and combines many business domains.
Some metrics are rule-based rather than machine-learning predictions.
List APIs require pagination/optimization for very large datasets.
```

These are not failures. They are prototype scope decisions.

---

# 19. Recommended Production Improvements

```text
PostgreSQL instead of SQLite
Password hashing with bcrypt/Argon2
Microsoft Graph or transactional email
Refresh tokens and token revocation
Server-side pagination
Background campaign workers
Real Email/SMS/WhatsApp integrations
Normalized transaction/order/product schemas
Database foreign keys and indexes
Automated tests
Docker deployment
Machine-learning propensity and churn models
Monitoring and structured logs
```

---

# 20. Useful Database Inspection Commands

## List tables

```sql
SELECT name
FROM sqlite_master
WHERE type = 'table'
ORDER BY name;
```

## Show columns

```sql
PRAGMA table_info(customers_360);
```

## Count rows

```sql
SELECT COUNT(*) FROM customers_360;
```

## Inspect sample rows

```sql
SELECT *
FROM customers_360
LIMIT 5;
```

## Inspect loyalty rules

```sql
SELECT *
FROM loyalty_tier_rules;
```

## Inspect point ledger

```sql
SELECT *
FROM loyalty_point_transactions
ORDER BY created_at DESC;
```

## Inspect service timeline

```sql
SELECT *
FROM customer_service_timeline
WHERE ticket_id = 'SR-2026-001248'
ORDER BY created_at;
```

## Inspect campaign logs

```sql
SELECT *
FROM crm_campaign_message_logs
ORDER BY sent_at DESC;
```

## Inspect audit logs

```sql
SELECT *
FROM audit_logs
ORDER BY created_at DESC;
```

---

# 21. Presentation Summary

A concise technical explanation is:

> OmniLink CRM uses a JavaScript frontend, FastAPI REST backend, JWT authentication, role-based permissions, and SQLite. The enriched `customers_360` table acts as the central customer snapshot. Dashboard APIs aggregate this data into KPIs and charts. Customer 360 exposes individual profiles. Consent controls contact permissions. The Loyalty service calculates reward activity and internal membership recommendations using configurable rules, while transaction tables maintain history. The Campaign module creates audiences, applies consent filters, renders templates, and demonstrates delivery through Discord. The Customer Service module maintains ticket snapshots and event timelines. Audit logs provide traceability across modules.

---

# 22. Final Mental Model

Remember the system in seven layers:

```text
1. Identity
   users + JWT + roles

2. Customer truth
   customers_360

3. Intelligence
   dashboard + CLV + churn + segments + loyalty scoring

4. Permission
   consent + DNC

5. Engagement
   campaigns + templates + message logs

6. Service
   tickets + timeline + workload

7. Governance
   audit logs + role-based access
```

If these seven layers are understood, the complete OmniLink CRM architecture is understood.
