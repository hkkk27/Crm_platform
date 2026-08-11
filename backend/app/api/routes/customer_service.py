# from fastapi import APIRouter, Depends, HTTPException
# from app.db.sqlite_client import fetch_all, fetch_one, execute_query
# from app.core.security import get_current_user, require_permission
# from app.services.audit_service import create_audit_log

# router = APIRouter(prefix="/customer-service", tags=["Customer Service"])


# @router.get("/tickets")
# def get_customer_service_tickets(user=Depends(get_current_user)):
#     require_permission(user, "customer_service")

#     rows = fetch_all("""
#     SELECT *
#     FROM customer_service_tickets
#     ORDER BY created_on DESC
#     LIMIT 1000
#     """)

#     create_audit_log(
#         user_email=user["sub"],
#         user_role=user["role"],
#         action="View customer service tickets",
#         object_type="CustomerService",
#         object_id="ALL",
#         status="Allowed",
#         details="Customer service ticket list viewed"
#     )

#     return {
#         "success": True,
#         "count": len(rows),
#         "data": rows
#     }


# @router.get("/tickets/{ticket_id}")
# def get_customer_service_ticket_detail(
#     ticket_id: str,
#     user=Depends(get_current_user)
# ):
#     require_permission(user, "customer_service")

#     ticket = fetch_one("""
#     SELECT *
#     FROM customer_service_tickets
#     WHERE ticket_id = ?
#     """, (ticket_id,))

#     if not ticket:
#         raise HTTPException(
#             status_code=404,
#             detail="Ticket not found"
#         )

#     timeline = fetch_all("""
#     SELECT *
#     FROM customer_service_timeline
#     WHERE ticket_id = ?
#     ORDER BY created_at ASC, timeline_id ASC
#     """, (ticket_id,))

#     action_history = [
#         event
#         for event in timeline
#         if event.get("event_type") in [
#             "Agent Update",
#             "Call Review",
#             "Status Changed",
#             "Follow-up Scheduled",
#             "Ticket Resolved",
#             "Ticket Closed"
#         ]
#     ]

#     create_audit_log(
#         user_email=user["sub"],
#         user_role=user["role"],
#         action="View customer service ticket",
#         object_type="CustomerServiceTicket",
#         object_id=ticket_id,
#         status="Allowed",
#         details="Ticket detail viewed"
#     )

#     return {
#         "success": True,
#         "ticket": ticket,
#         "timeline": timeline,
#         "action_history": action_history
#     }


# @router.put("/tickets/{ticket_id}/update")
# def update_customer_service_ticket(
#     ticket_id: str,
#     payload: dict,
#     user=Depends(get_current_user)
# ):
#     require_permission(user, "customer_service")

#     existing = fetch_one("""
#     SELECT *
#     FROM customer_service_tickets
#     WHERE ticket_id = ?
#     """, (ticket_id,))

#     if not existing:
#         raise HTTPException(
#             status_code=404,
#             detail="Ticket not found"
#         )

#     allowed_fields = [
#         "status",
#         "priority",
#         "call_review",
#         "contact_result",
#         "follow_up_required",
#         "follow_up_date",
#         "follow_up_note",
#         "internal_notes",
#         "resolution_summary"
#     ]

#     update_data = {
#         key: value
#         for key, value in payload.items()
#         if key in allowed_fields
#     }

#     if not update_data:
#         raise HTTPException(
#             status_code=400,
#             detail="No valid update fields provided"
#         )

#     # Normalize follow-up value
#     follow_up_value = update_data.get(
#         "follow_up_required",
#         existing.get("follow_up_required") or "No"
#     )

#     if follow_up_value in [1, "1", True, "true", "Yes", "yes"]:
#         update_data["follow_up_required"] = "Yes"
#     else:
#         update_data["follow_up_required"] = "No"

#     new_status = update_data.get(
#         "status",
#         existing.get("status")
#     )

#     new_priority = update_data.get(
#         "priority",
#         existing.get("priority")
#     )

#     resolution_summary = update_data.get(
#         "resolution_summary",
#         existing.get("resolution_summary")
#     )

#     if new_status in ["Resolved", "Closed"] and not resolution_summary:
#         raise HTTPException(
#             status_code=400,
#             detail="Resolution summary is required before resolving or closing ticket"
#         )

#     if (
#         update_data.get("follow_up_required") == "Yes"
#         and not update_data.get("follow_up_date")
#     ):
#         raise HTTPException(
#             status_code=400,
#             detail="Follow-up date is required when follow-up is Yes"
#         )

#     # Clear follow-up fields if follow-up is not required
#     if update_data.get("follow_up_required") == "No":
#         update_data["follow_up_date"] = ""
#         update_data["follow_up_note"] = ""

#     update_data["last_action_by"] = user["sub"]

#     set_parts = []
#     values = []

#     for field, value in update_data.items():
#         set_parts.append(f"{field} = ?")
#         values.append(value)

#     set_parts.append("last_updated = CURRENT_TIMESTAMP")

#     if new_status in ["Resolved", "Closed"]:
#         set_parts.append("completed_on = CURRENT_TIMESTAMP")
#         set_parts.append("follow_up_required = 'No'")
#         set_parts.append("follow_up_date = ''")
#         set_parts.append("follow_up_note = ''")
#     else:
#         set_parts.append("completed_on = ''")

#     values.append(ticket_id)

#     execute_query(
#         f"""
#         UPDATE customer_service_tickets
#         SET {", ".join(set_parts)}
#         WHERE ticket_id = ?
#         """,
#         tuple(values)
#     )

#     # Build meaningful timeline description
#     description_parts = []

#     if existing.get("status") != new_status:
#         description_parts.append(
#             f"Status changed from {existing.get('status')} to {new_status}"
#         )

#     if existing.get("priority") != new_priority:
#         description_parts.append(
#             f"Priority changed from {existing.get('priority')} to {new_priority}"
#         )

#     if update_data.get("call_review"):
#         description_parts.append(
#             f"Call review: {update_data.get('call_review')}"
#         )

#     if update_data.get("contact_result"):
#         description_parts.append(
#             f"Customer response: {update_data.get('contact_result')}"
#         )

#     if update_data.get("follow_up_required") == "Yes":
#         description_parts.append(
#             f"Follow-up scheduled for {update_data.get('follow_up_date')}"
#         )

#     if update_data.get("follow_up_note"):
#         description_parts.append(
#             f"Follow-up note: {update_data.get('follow_up_note')}"
#         )

#     if update_data.get("internal_notes"):
#         description_parts.append(
#             f"Internal note updated: {update_data.get('internal_notes')}"
#         )

#     if update_data.get("resolution_summary"):
#         description_parts.append(
#             f"Resolution: {update_data.get('resolution_summary')}"
#         )

#     event_description = " | ".join(description_parts)

#     if not event_description:
#         event_description = "Ticket updated by customer service employee"

#     # Determine timeline event type
#     event_type = "Agent Update"
#     event_title = "Ticket Updated"

#     if new_status == "Resolved":
#         event_type = "Ticket Resolved"
#         event_title = "Ticket Resolved"

#     elif new_status == "Closed":
#         event_type = "Ticket Closed"
#         event_title = "Ticket Closed"

#     elif existing.get("status") != new_status:
#         event_type = "Status Changed"
#         event_title = f"Status Changed to {new_status}"

#     elif update_data.get("follow_up_required") == "Yes":
#         event_type = "Follow-up Scheduled"
#         event_title = "Customer Follow-up Scheduled"

#     elif update_data.get("call_review"):
#         event_type = "Call Review"
#         event_title = "Customer Conversation Updated"

#     execute_query("""
#     INSERT INTO customer_service_timeline (
#         ticket_id,
#         event_type,
#         event_title,
#         event_description,
#         old_status,
#         new_status,
#         old_priority,
#         new_priority,
#         assigned_from,
#         assigned_to,
#         escalation_level,
#         escalated_to,
#         sla_status,
#         created_by,
#         created_at
#     )
#     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
#     """, (
#         ticket_id,
#         event_type,
#         event_title,
#         event_description,
#         existing.get("status"),
#         new_status,
#         existing.get("priority"),
#         new_priority,
#         existing.get("assigned_to"),
#         existing.get("assigned_to"),
#         existing.get("escalation_level"),
#         existing.get("escalated_to"),
#         existing.get("sla_status"),
#         user["sub"]
#     ))

#     create_audit_log(
#         user_email=user["sub"],
#         user_role=user["role"],
#         action="Update customer service ticket",
#         object_type="CustomerServiceTicket",
#         object_id=ticket_id,
#         status="Allowed",
#         details=event_description
#     )

#     # Return refreshed data
#     updated_ticket = fetch_one("""
#     SELECT *
#     FROM customer_service_tickets
#     WHERE ticket_id = ?
#     """, (ticket_id,))

#     updated_timeline = fetch_all("""
#     SELECT *
#     FROM customer_service_timeline
#     WHERE ticket_id = ?
#     ORDER BY created_at ASC, timeline_id ASC
#     """, (ticket_id,))

#     return {
#         "success": True,
#         "message": "Ticket updated successfully",
#         "ticket_id": ticket_id,
#         "updated_fields": update_data,
#         "ticket": updated_ticket,
#         "timeline": updated_timeline
#     }

# @router.get("/metrics/summary")
# def get_customer_service_metrics(user=Depends(get_current_user)):
#     require_permission(user, "customer_service")

#     summary = fetch_one("""
#     SELECT
#         COUNT(*) as total_tickets,
#         SUM(CASE WHEN status IN ('Resolved', 'Closed') THEN 1 ELSE 0 END) as resolved_tickets,
#         SUM(CASE WHEN status IN ('Open', 'Waiting for Customer', 'Escalated') THEN 1 ELSE 0 END) as open_pipeline,
#         SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END) as active_resolutions,
#         SUM(CASE WHEN priority IN ('High', 'Critical') OR status = 'Escalated' THEN 1 ELSE 0 END) as priority_escalations,
#         SUM(CASE WHEN sla_status = 'At Risk' THEN 1 ELSE 0 END) as at_risk_sla
#     FROM customer_service_tickets
#     """)

#     return {
#         "success": True,
#         "summary": summary
#     }


# @router.get("/agents/workload")
# def get_customer_service_agent_workload(user=Depends(get_current_user)):
#     require_permission(user, "customer_service")

#     rows = fetch_all("""
#     SELECT
#         assigned_agent_id,
#         assigned_to,
#         COUNT(*) as total,
#         SUM(CASE WHEN status = 'Open' THEN 1 ELSE 0 END) as open,
#         SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END) as progress,
#         SUM(CASE WHEN status = 'Escalated' THEN 1 ELSE 0 END) as escalated,
#         SUM(CASE WHEN status IN ('Resolved', 'Closed') THEN 1 ELSE 0 END) as resolved
#     FROM customer_service_tickets
#     GROUP BY assigned_agent_id, assigned_to
#     """)

#     return {
#         "success": True,
#         "count": len(rows),
#         "data": rows
#     }
# from fastapi import APIRouter, Depends, HTTPException
# from app.db.sqlite_client import fetch_all, fetch_one, execute_query
# from app.core.security import get_current_user, require_permission
# from app.services.audit_service import create_audit_log
 
# router = APIRouter(prefix="/customer-service", tags=["Customer Service"])
 
 
# # ---------------------------------------------------------
# # MINIMAL ROLE / AGENT-SCOPE HELPERS
# # ---------------------------------------------------------
# # Existing Admin/System Administrator logic is preserved.
# # Only Customer Service users are scoped to their own assigned tickets.
 
# def is_customer_service_agent(user: dict):
#     role = str(user.get("role", "")).strip().lower()
#     return role in ["customer service", "customer service team"]
 
 
# def ticket_belongs_to_user(ticket: dict, user: dict):
#     if not is_customer_service_agent(user):
#         return True
 
#     assigned_email = str(ticket.get("assigned_agent_email", "")).strip().lower()
#     current_email = str(user.get("sub", "")).strip().lower()
#     return assigned_email == current_email
 
 
# # ---------------------------------------------------------
# # TICKET LIST
# # ---------------------------------------------------------
 
# @router.get("/tickets")
# def get_customer_service_tickets(user=Depends(get_current_user)):
#     require_permission(user, "customer_service")
 
#     if is_customer_service_agent(user):
#         rows = fetch_all("""
#         SELECT
#             t.*,
#             a.agent_email AS assigned_agent_email
#         FROM customer_service_tickets t
#         LEFT JOIN customer_service_agents a
#             ON lower(t.assigned_agent_id) = lower(a.agent_id)
#             OR lower(t.assigned_to) = lower(a.agent_name)
#         WHERE lower(a.agent_email) = lower(?)
#         ORDER BY t.created_on DESC
#         LIMIT 1000
#         """, (user["sub"],))
 
#         object_id = "OWN"
#         details = "Customer service ticket list viewed for logged-in agent"
#     else:
#         rows = fetch_all("""
#         SELECT
#             t.*,
#             a.agent_email AS assigned_agent_email
#         FROM customer_service_tickets t
#         LEFT JOIN customer_service_agents a
#             ON lower(t.assigned_agent_id) = lower(a.agent_id)
#             OR lower(t.assigned_to) = lower(a.agent_name)
#         ORDER BY t.created_on DESC
#         LIMIT 1000
#         """)
 
#         object_id = "ALL"
#         details = "Customer service ticket list viewed"
 
#     create_audit_log(
#         user_email=user["sub"],
#         user_role=user["role"],
#         action="View customer service tickets",
#         object_type="CustomerService",
#         object_id=object_id,
#         status="Allowed",
#         details=details
#     )
 
#     return {
#         "success": True,
#         "count": len(rows),
#         "data": rows
#     }
 
 
# # ---------------------------------------------------------
# # TICKET DETAIL
# # ---------------------------------------------------------
 
# @router.get("/tickets/{ticket_id}")
# def get_customer_service_ticket_detail(
#     ticket_id: str,
#     user=Depends(get_current_user)
# ):
#     require_permission(user, "customer_service")
 
#     ticket = fetch_one("""
#     SELECT
#         t.*,
#         a.agent_email AS assigned_agent_email
#     FROM customer_service_tickets t
#     LEFT JOIN customer_service_agents a
#         ON lower(t.assigned_agent_id) = lower(a.agent_id)
#         OR lower(t.assigned_to) = lower(a.agent_name)
#     WHERE t.ticket_id = ?
#     """, (ticket_id,))
 
#     if not ticket:
#         raise HTTPException(
#             status_code=404,
#             detail="Ticket not found"
#         )
 
#     if not ticket_belongs_to_user(ticket, user):
#         raise HTTPException(
#             status_code=403,
#             detail="You can only view tickets assigned to you"
#         )
 
#     timeline = fetch_all("""
#     SELECT *
#     FROM customer_service_timeline
#     WHERE ticket_id = ?
#     ORDER BY created_at ASC, timeline_id ASC
#     """, (ticket_id,))
 
#     action_history = [
#         event
#         for event in timeline
#         if event.get("event_type") in [
#             "Agent Update",
#             "Call Review",
#             "Status Changed",
#             "Follow-up Scheduled",
#             "Ticket Resolved",
#             "Ticket Closed"
#         ]
#     ]
 
#     create_audit_log(
#         user_email=user["sub"],
#         user_role=user["role"],
#         action="View customer service ticket",
#         object_type="CustomerServiceTicket",
#         object_id=ticket_id,
#         status="Allowed",
#         details="Ticket detail viewed"
#     )
 
#     return {
#         "success": True,
#         "ticket": ticket,
#         "timeline": timeline,
#         "action_history": action_history
#     }
 
 
# # ---------------------------------------------------------
# # TICKET UPDATE
# # ---------------------------------------------------------
 
# @router.put("/tickets/{ticket_id}/update")
# def update_customer_service_ticket(
#     ticket_id: str,
#     payload: dict,
#     user=Depends(get_current_user)
# ):
#     require_permission(user, "customer_service")
 
#     existing = fetch_one("""
#     SELECT
#         t.*,
#         a.agent_email AS assigned_agent_email
#     FROM customer_service_tickets t
#     LEFT JOIN customer_service_agents a
#         ON lower(t.assigned_agent_id) = lower(a.agent_id)
#         OR lower(t.assigned_to) = lower(a.agent_name)
#     WHERE t.ticket_id = ?
#     """, (ticket_id,))
 
#     if not existing:
#         raise HTTPException(
#             status_code=404,
#             detail="Ticket not found"
#         )
 
#     if not ticket_belongs_to_user(existing, user):
#         raise HTTPException(
#             status_code=403,
#             detail="You can only update tickets assigned to you"
#         )
 
#     allowed_fields = [
#         "status",
#         "priority",
#         "call_review",
#         "contact_result",
#         "follow_up_required",
#         "follow_up_date",
#         "follow_up_note",
#         "internal_notes",
#         "resolution_summary"
#     ]
 
#     update_data = {
#         key: value
#         for key, value in payload.items()
#         if key in allowed_fields
#     }
 
#     if not update_data:
#         raise HTTPException(
#             status_code=400,
#             detail="No valid update fields provided"
#         )
 
#     # Normalize follow-up value
#     follow_up_value = update_data.get(
#         "follow_up_required",
#         existing.get("follow_up_required") or "No"
#     )
 
#     if follow_up_value in [1, "1", True, "true", "Yes", "yes"]:
#         update_data["follow_up_required"] = "Yes"
#     else:
#         update_data["follow_up_required"] = "No"
 
#     new_status = update_data.get(
#         "status",
#         existing.get("status")
#     )
 
#     new_priority = update_data.get(
#         "priority",
#         existing.get("priority")
#     )
 
#     resolution_summary = update_data.get(
#         "resolution_summary",
#         existing.get("resolution_summary")
#     )
 
#     if new_status in ["Resolved", "Closed"] and not resolution_summary:
#         raise HTTPException(
#             status_code=400,
#             detail="Resolution summary is required before resolving or closing ticket"
#         )
 
#     if (
#         update_data.get("follow_up_required") == "Yes"
#         and not update_data.get("follow_up_date")
#     ):
#         raise HTTPException(
#             status_code=400,
#             detail="Follow-up date is required when follow-up is Yes"
#         )
 
#     # Clear follow-up fields if follow-up is not required
#     if update_data.get("follow_up_required") == "No":
#         update_data["follow_up_date"] = ""
#         update_data["follow_up_note"] = ""
 
#     update_data["last_action_by"] = user["sub"]
 
#     set_parts = []
#     values = []
 
#     for field, value in update_data.items():
#         set_parts.append(f"{field} = ?")
#         values.append(value)
 
#     set_parts.append("last_updated = CURRENT_TIMESTAMP")
 
#     if new_status in ["Resolved", "Closed"]:
#         set_parts.append("completed_on = CURRENT_TIMESTAMP")
#         set_parts.append("follow_up_required = 'No'")
#         set_parts.append("follow_up_date = ''")
#         set_parts.append("follow_up_note = ''")
#     else:
#         set_parts.append("completed_on = ''")
 
#     values.append(ticket_id)
 
#     execute_query(
#         f"""
#         UPDATE customer_service_tickets
#         SET {", ".join(set_parts)}
#         WHERE ticket_id = ?
#         """,
#         tuple(values)
#     )
 
#     # Build meaningful timeline description
#     description_parts = []
 
#     if existing.get("status") != new_status:
#         description_parts.append(
#             f"Status changed from {existing.get('status')} to {new_status}"
#         )
 
#     if existing.get("priority") != new_priority:
#         description_parts.append(
#             f"Priority changed from {existing.get('priority')} to {new_priority}"
#         )
 
#     if update_data.get("call_review"):
#         description_parts.append(
#             f"Call review: {update_data.get('call_review')}"
#         )
 
#     if update_data.get("contact_result"):
#         description_parts.append(
#             f"Customer response: {update_data.get('contact_result')}"
#         )
 
#     if update_data.get("follow_up_required") == "Yes":
#         description_parts.append(
#             f"Follow-up scheduled for {update_data.get('follow_up_date')}"
#         )
 
#     if update_data.get("follow_up_note"):
#         description_parts.append(
#             f"Follow-up note: {update_data.get('follow_up_note')}"
#         )
 
#     if update_data.get("internal_notes"):
#         description_parts.append(
#             f"Internal note updated: {update_data.get('internal_notes')}"
#         )
 
#     if update_data.get("resolution_summary"):
#         description_parts.append(
#             f"Resolution: {update_data.get('resolution_summary')}"
#         )
 
#     event_description = " | ".join(description_parts)
 
#     if not event_description:
#         event_description = "Ticket updated by customer service employee"
 
#     # Determine timeline event type
#     event_type = "Agent Update"
#     event_title = "Ticket Updated"
 
#     if new_status == "Resolved":
#         event_type = "Ticket Resolved"
#         event_title = "Ticket Resolved"
#     elif new_status == "Closed":
#         event_type = "Ticket Closed"
#         event_title = "Ticket Closed"
#     elif existing.get("status") != new_status:
#         event_type = "Status Changed"
#         event_title = f"Status Changed to {new_status}"
#     elif update_data.get("follow_up_required") == "Yes":
#         event_type = "Follow-up Scheduled"
#         event_title = "Customer Follow-up Scheduled"
#     elif update_data.get("call_review"):
#         event_type = "Call Review"
#         event_title = "Customer Conversation Updated"
 
#     execute_query("""
#     INSERT INTO customer_service_timeline (
#         ticket_id,
#         event_type,
#         event_title,
#         event_description,
#         old_status,
#         new_status,
#         old_priority,
#         new_priority,
#         assigned_from,
#         assigned_to,
#         escalation_level,
#         escalated_to,
#         sla_status,
#         created_by,
#         created_at
#     )
#     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
#     """, (
#         ticket_id,
#         event_type,
#         event_title,
#         event_description,
#         existing.get("status"),
#         new_status,
#         existing.get("priority"),
#         new_priority,
#         existing.get("assigned_to"),
#         existing.get("assigned_to"),
#         existing.get("escalation_level"),
#         existing.get("escalated_to"),
#         existing.get("sla_status"),
#         user["sub"]
#     ))
 
#     create_audit_log(
#         user_email=user["sub"],
#         user_role=user["role"],
#         action="Update customer service ticket",
#         object_type="CustomerServiceTicket",
#         object_id=ticket_id,
#         status="Allowed",
#         details=event_description
#     )
 
#     # Return refreshed data
#     updated_ticket = fetch_one("""
#     SELECT
#         t.*,
#         a.agent_email AS assigned_agent_email
#     FROM customer_service_tickets t
#     LEFT JOIN customer_service_agents a
#         ON lower(t.assigned_agent_id) = lower(a.agent_id)
#         OR lower(t.assigned_to) = lower(a.agent_name)
#     WHERE t.ticket_id = ?
#     """, (ticket_id,))
 
#     updated_timeline = fetch_all("""
#     SELECT *
#     FROM customer_service_timeline
#     WHERE ticket_id = ?
#     ORDER BY created_at ASC, timeline_id ASC
#     """, (ticket_id,))
 
#     return {
#         "success": True,
#         "message": "Ticket updated successfully",
#         "ticket_id": ticket_id,
#         "updated_fields": update_data,
#         "ticket": updated_ticket,
#         "timeline": updated_timeline
#     }
 
 
# # ---------------------------------------------------------
# # METRICS SUMMARY
# # ---------------------------------------------------------
 
# @router.get("/metrics/summary")
# def get_customer_service_metrics(user=Depends(get_current_user)):
#     require_permission(user, "customer_service")
 
#     if is_customer_service_agent(user):
#         summary = fetch_one("""
#         SELECT
#             COUNT(*) as total_tickets,
#             SUM(CASE WHEN t.status IN ('Resolved', 'Closed') THEN 1 ELSE 0 END) as resolved_tickets,
#             SUM(CASE WHEN t.status IN ('Open', 'Waiting for Customer', 'Escalated') THEN 1 ELSE 0 END) as open_pipeline,
#             SUM(CASE WHEN t.status = 'In Progress' THEN 1 ELSE 0 END) as active_resolutions,
#             SUM(CASE WHEN t.priority IN ('High', 'Critical') OR t.status = 'Escalated' THEN 1 ELSE 0 END) as priority_escalations,
#             SUM(CASE WHEN t.sla_status = 'At Risk' THEN 1 ELSE 0 END) as at_risk_sla
#         FROM customer_service_tickets t
#         LEFT JOIN customer_service_agents a
#             ON lower(t.assigned_agent_id) = lower(a.agent_id)
#             OR lower(t.assigned_to) = lower(a.agent_name)
#         WHERE lower(a.agent_email) = lower(?)
#         """, (user["sub"],))
#     else:
#         summary = fetch_one("""
#         SELECT
#             COUNT(*) as total_tickets,
#             SUM(CASE WHEN status IN ('Resolved', 'Closed') THEN 1 ELSE 0 END) as resolved_tickets,
#             SUM(CASE WHEN status IN ('Open', 'Waiting for Customer', 'Escalated') THEN 1 ELSE 0 END) as open_pipeline,
#             SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END) as active_resolutions,
#             SUM(CASE WHEN priority IN ('High', 'Critical') OR status = 'Escalated' THEN 1 ELSE 0 END) as priority_escalations,
#             SUM(CASE WHEN sla_status = 'At Risk' THEN 1 ELSE 0 END) as at_risk_sla
#         FROM customer_service_tickets
#         """)
 
#     return {
#         "success": True,
#         "summary": summary
#     }
 
 
# # ---------------------------------------------------------
# # AGENT WORKLOAD
# # ---------------------------------------------------------
 
# @router.get("/agents/workload")
# def get_customer_service_agent_workload(user=Depends(get_current_user)):
#     require_permission(user, "customer_service")
 
#     if is_customer_service_agent(user):
#         return {
#             "success": True,
#             "count": 0,
#             "data": []
#         }
 
#     rows = fetch_all("""
#     SELECT
#         assigned_agent_id,
#         assigned_to,
#         COUNT(*) as total,
#         SUM(CASE WHEN status = 'Open' THEN 1 ELSE 0 END) as open,
#         SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END) as progress,
#         SUM(CASE WHEN status = 'Escalated' THEN 1 ELSE 0 END) as escalated,
#         SUM(CASE WHEN status IN ('Resolved', 'Closed') THEN 1 ELSE 0 END) as resolved
#     FROM customer_service_tickets
#     GROUP BY assigned_agent_id, assigned_to
#     """)
 
#     return {
#         "success": True,
#         "count": len(rows),
#         "data": rows
#     }

from fastapi import APIRouter, Depends, HTTPException

from app.db.sqlite_client import fetch_all, fetch_one, execute_query
from app.core.security import get_current_user, require_permission
from app.services.audit_service import create_audit_log
from app.services.cache_service import cache


router = APIRouter(
    prefix="/customer-service",
    tags=["Customer Service"],
)


# ---------------------------------------------------------
# MINIMAL ROLE / AGENT-SCOPE HELPERS
# ---------------------------------------------------------
# Existing Admin/System Administrator logic is preserved.
# Only Customer Service users are scoped to their own assigned tickets.


def is_customer_service_agent(user: dict):
    role = str(user.get("role", "")).strip().lower()
    return role in ["customer service", "customer service team"]


def ticket_belongs_to_user(ticket: dict, user: dict):
    if not is_customer_service_agent(user):
        return True

    assigned_email = str(
        ticket.get("assigned_agent_email", "")
    ).strip().lower()

    current_email = str(
        user.get("sub", "")
    ).strip().lower()

    return assigned_email == current_email


def get_metrics_cache_key(user: dict):
    if is_customer_service_agent(user):
        return (
            "customer-service:metrics:"
            + str(user.get("sub", "")).strip().lower()
        )

    return "customer-service:metrics"


# ---------------------------------------------------------
# TICKET LIST
# ---------------------------------------------------------


@router.get("/tickets")
def get_customer_service_tickets(user=Depends(get_current_user)):
    require_permission(user, "customer_service")

    if is_customer_service_agent(user):
        rows = fetch_all(
            """
            SELECT
                t.*,
                a.agent_email AS assigned_agent_email
            FROM customer_service_tickets t
            LEFT JOIN customer_service_agents a
                ON lower(t.assigned_agent_id) = lower(a.agent_id)
                OR lower(t.assigned_to) = lower(a.agent_name)
            WHERE lower(a.agent_email) = lower(?)
            ORDER BY t.created_on DESC
            LIMIT 1000
            """,
            (user["sub"],),
        )

        object_id = "OWN"
        details = "Customer service ticket list viewed for logged-in agent"

    else:
        rows = fetch_all(
            """
            SELECT
                t.*,
                a.agent_email AS assigned_agent_email
            FROM customer_service_tickets t
            LEFT JOIN customer_service_agents a
                ON lower(t.assigned_agent_id) = lower(a.agent_id)
                OR lower(t.assigned_to) = lower(a.agent_name)
            ORDER BY t.created_on DESC
            LIMIT 1000
            """
        )

        object_id = "ALL"
        details = "Customer service ticket list viewed"

    create_audit_log(
        user_email=user["sub"],
        user_role=user["role"],
        action="View customer service tickets",
        object_type="CustomerService",
        object_id=object_id,
        status="Allowed",
        details=details,
    )

    return {
        "success": True,
        "count": len(rows),
        "data": rows,
    }


# ---------------------------------------------------------
# TICKET DETAIL
# ---------------------------------------------------------


@router.get("/tickets/{ticket_id}")
def get_customer_service_ticket_detail(
    ticket_id: str,
    user=Depends(get_current_user),
):
    require_permission(user, "customer_service")

    ticket = fetch_one(
        """
        SELECT
            t.*,
            a.agent_email AS assigned_agent_email
        FROM customer_service_tickets t
        LEFT JOIN customer_service_agents a
            ON lower(t.assigned_agent_id) = lower(a.agent_id)
            OR lower(t.assigned_to) = lower(a.agent_name)
        WHERE t.ticket_id = ?
        """,
        (ticket_id,),
    )

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    if not ticket_belongs_to_user(ticket, user):
        raise HTTPException(
            status_code=403,
            detail="You can only view tickets assigned to you",
        )

    timeline = fetch_all(
        """
        SELECT *
        FROM customer_service_timeline
        WHERE ticket_id = ?
        ORDER BY created_at ASC, timeline_id ASC
        """,
        (ticket_id,),
    )

    action_history = [
        event
        for event in timeline
        if event.get("event_type")
        in [
            "Agent Update",
            "Call Review",
            "Status Changed",
            "Follow-up Scheduled",
            "Ticket Resolved",
            "Ticket Closed",
        ]
    ]

    create_audit_log(
        user_email=user["sub"],
        user_role=user["role"],
        action="View customer service ticket",
        object_type="CustomerServiceTicket",
        object_id=ticket_id,
        status="Allowed",
        details="Ticket detail viewed",
    )

    return {
        "success": True,
        "ticket": ticket,
        "timeline": timeline,
        "action_history": action_history,
    }


# ---------------------------------------------------------
# TICKET UPDATE
# ---------------------------------------------------------


@router.put("/tickets/{ticket_id}/update")
def update_customer_service_ticket(
    ticket_id: str,
    payload: dict,
    user=Depends(get_current_user),
):
    require_permission(user, "customer_service")

    existing = fetch_one(
        """
        SELECT
            t.*,
            a.agent_email AS assigned_agent_email
        FROM customer_service_tickets t
        LEFT JOIN customer_service_agents a
            ON lower(t.assigned_agent_id) = lower(a.agent_id)
            OR lower(t.assigned_to) = lower(a.agent_name)
        WHERE t.ticket_id = ?
        """,
        (ticket_id,),
    )

    if not existing:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    if not ticket_belongs_to_user(existing, user):
        raise HTTPException(
            status_code=403,
            detail="You can only update tickets assigned to you",
        )

    allowed_fields = [
        "status",
        "priority",
        "call_review",
        "contact_result",
        "follow_up_required",
        "follow_up_date",
        "follow_up_note",
        "internal_notes",
        "resolution_summary",
    ]

    update_data = {
        key: value
        for key, value in payload.items()
        if key in allowed_fields
    }

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No valid update fields provided",
        )

    # Normalize follow-up value
    follow_up_value = update_data.get(
        "follow_up_required",
        existing.get("follow_up_required") or "No",
    )

    if follow_up_value in [1, "1", True, "true", "Yes", "yes"]:
        update_data["follow_up_required"] = "Yes"
    else:
        update_data["follow_up_required"] = "No"

    new_status = update_data.get(
        "status",
        existing.get("status"),
    )

    new_priority = update_data.get(
        "priority",
        existing.get("priority"),
    )

    resolution_summary = update_data.get(
        "resolution_summary",
        existing.get("resolution_summary"),
    )

    if new_status in ["Resolved", "Closed"] and not resolution_summary:
        raise HTTPException(
            status_code=400,
            detail=(
                "Resolution summary is required before resolving "
                "or closing ticket"
            ),
        )

    if (
        update_data.get("follow_up_required") == "Yes"
        and not update_data.get("follow_up_date")
    ):
        raise HTTPException(
            status_code=400,
            detail="Follow-up date is required when follow-up is Yes",
        )

    # Clear follow-up fields if follow-up is not required
    if update_data.get("follow_up_required") == "No":
        update_data["follow_up_date"] = ""
        update_data["follow_up_note"] = ""

    update_data["last_action_by"] = user["sub"]

    set_parts = []
    values = []

    for field, value in update_data.items():
        set_parts.append(f"{field} = ?")
        values.append(value)

    set_parts.append("last_updated = CURRENT_TIMESTAMP")

    if new_status in ["Resolved", "Closed"]:
        set_parts.append("completed_on = CURRENT_TIMESTAMP")
        set_parts.append("follow_up_required = 'No'")
        set_parts.append("follow_up_date = ''")
        set_parts.append("follow_up_note = ''")
    else:
        set_parts.append("completed_on = ''")

    values.append(ticket_id)

    execute_query(
        f"""
        UPDATE customer_service_tickets
        SET {", ".join(set_parts)}
        WHERE ticket_id = ?
        """,
        tuple(values),
    )

    # Build meaningful timeline description
    description_parts = []

    if existing.get("status") != new_status:
        description_parts.append(
            f"Status changed from {existing.get('status')} to {new_status}"
        )

    if existing.get("priority") != new_priority:
        description_parts.append(
            f"Priority changed from {existing.get('priority')} to {new_priority}"
        )

    if update_data.get("call_review"):
        description_parts.append(
            f"Call review: {update_data.get('call_review')}"
        )

    if update_data.get("contact_result"):
        description_parts.append(
            f"Customer response: {update_data.get('contact_result')}"
        )

    if update_data.get("follow_up_required") == "Yes":
        description_parts.append(
            f"Follow-up scheduled for {update_data.get('follow_up_date')}"
        )

    if update_data.get("follow_up_note"):
        description_parts.append(
            f"Follow-up note: {update_data.get('follow_up_note')}"
        )

    if update_data.get("internal_notes"):
        description_parts.append(
            f"Internal note updated: {update_data.get('internal_notes')}"
        )

    if update_data.get("resolution_summary"):
        description_parts.append(
            f"Resolution: {update_data.get('resolution_summary')}"
        )

    event_description = " | ".join(description_parts)

    if not event_description:
        event_description = "Ticket updated by customer service employee"

    # Determine timeline event type
    event_type = "Agent Update"
    event_title = "Ticket Updated"

    if new_status == "Resolved":
        event_type = "Ticket Resolved"
        event_title = "Ticket Resolved"

    elif new_status == "Closed":
        event_type = "Ticket Closed"
        event_title = "Ticket Closed"

    elif existing.get("status") != new_status:
        event_type = "Status Changed"
        event_title = f"Status Changed to {new_status}"

    elif update_data.get("follow_up_required") == "Yes":
        event_type = "Follow-up Scheduled"
        event_title = "Customer Follow-up Scheduled"

    elif update_data.get("call_review"):
        event_type = "Call Review"
        event_title = "Customer Conversation Updated"

    execute_query(
        """
        INSERT INTO customer_service_timeline (
            ticket_id,
            event_type,
            event_title,
            event_description,
            old_status,
            new_status,
            old_priority,
            new_priority,
            assigned_from,
            assigned_to,
            escalation_level,
            escalated_to,
            sla_status,
            created_by,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """,
        (
            ticket_id,
            event_type,
            event_title,
            event_description,
            existing.get("status"),
            new_status,
            existing.get("priority"),
            new_priority,
            existing.get("assigned_to"),
            existing.get("assigned_to"),
            existing.get("escalation_level"),
            existing.get("escalated_to"),
            existing.get("sla_status"),
            user["sub"],
        ),
    )

    create_audit_log(
        user_email=user["sub"],
        user_role=user["role"],
        action="Update customer service ticket",
        object_type="CustomerServiceTicket",
        object_id=ticket_id,
        status="Allowed",
        details=event_description,
    )

    cache.delete_prefix(
        "customer-service:metrics"
    )

    cache.delete(
        "customer-service:workload"
    )

    cache.delete(
        "dashboard:summary"
    )

    cache.delete(
        "admin:summary"
    )

    cache.delete(
        "admin:data-health"
    )

    # Return refreshed data
    updated_ticket = fetch_one(
        """
        SELECT
            t.*,
            a.agent_email AS assigned_agent_email
        FROM customer_service_tickets t
        LEFT JOIN customer_service_agents a
            ON lower(t.assigned_agent_id) = lower(a.agent_id)
            OR lower(t.assigned_to) = lower(a.agent_name)
        WHERE t.ticket_id = ?
        """,
        (ticket_id,),
    )

    updated_timeline = fetch_all(
        """
        SELECT *
        FROM customer_service_timeline
        WHERE ticket_id = ?
        ORDER BY created_at ASC, timeline_id ASC
        """,
        (ticket_id,),
    )

    return {
        "success": True,
        "message": "Ticket updated successfully",
        "ticket_id": ticket_id,
        "updated_fields": update_data,
        "ticket": updated_ticket,
        "timeline": updated_timeline,
    }


# ---------------------------------------------------------
# METRICS SUMMARY
# ---------------------------------------------------------


@router.get("/metrics/summary")
def get_customer_service_metrics(user=Depends(get_current_user)):
    require_permission(user, "customer_service")

    cache_key = get_metrics_cache_key(user)

    cached_response = cache.get(
        cache_key
    )

    if cached_response is not None:
        return cached_response

    if is_customer_service_agent(user):
        summary = fetch_one(
            """
            SELECT
                COUNT(*) AS total_tickets,
                SUM(
                    CASE
                        WHEN t.status IN ('Resolved', 'Closed')
                        THEN 1 ELSE 0
                    END
                ) AS resolved_tickets,
                SUM(
                    CASE
                        WHEN t.status IN (
                            'Open',
                            'Waiting for Customer',
                            'Escalated'
                        )
                        THEN 1 ELSE 0
                    END
                ) AS open_pipeline,
                SUM(
                    CASE
                        WHEN t.status = 'In Progress'
                        THEN 1 ELSE 0
                    END
                ) AS active_resolutions,
                SUM(
                    CASE
                        WHEN t.priority IN ('High', 'Critical')
                          OR t.status = 'Escalated'
                        THEN 1 ELSE 0
                    END
                ) AS priority_escalations,
                SUM(
                    CASE
                        WHEN t.sla_status = 'At Risk'
                        THEN 1 ELSE 0
                    END
                ) AS at_risk_sla
            FROM customer_service_tickets t
            LEFT JOIN customer_service_agents a
                ON lower(t.assigned_agent_id) = lower(a.agent_id)
                OR lower(t.assigned_to) = lower(a.agent_name)
            WHERE lower(a.agent_email) = lower(?)
            """,
            (user["sub"],),
        )

    else:
        summary = fetch_one(
            """
            SELECT
                COUNT(*) AS total_tickets,
                SUM(
                    CASE
                        WHEN status IN ('Resolved', 'Closed')
                        THEN 1 ELSE 0
                    END
                ) AS resolved_tickets,
                SUM(
                    CASE
                        WHEN status IN (
                            'Open',
                            'Waiting for Customer',
                            'Escalated'
                        )
                        THEN 1 ELSE 0
                    END
                ) AS open_pipeline,
                SUM(
                    CASE
                        WHEN status = 'In Progress'
                        THEN 1 ELSE 0
                    END
                ) AS active_resolutions,
                SUM(
                    CASE
                        WHEN priority IN ('High', 'Critical')
                          OR status = 'Escalated'
                        THEN 1 ELSE 0
                    END
                ) AS priority_escalations,
                SUM(
                    CASE
                        WHEN sla_status = 'At Risk'
                        THEN 1 ELSE 0
                    END
                ) AS at_risk_sla
            FROM customer_service_tickets
            """
        )

    response = {
        "success": True,
        "summary": summary,
    }

    cache.set(
        cache_key,
        response,
        ttl_seconds=30,
    )

    return response


# ---------------------------------------------------------
# AGENT WORKLOAD
# ---------------------------------------------------------


@router.get("/agents/workload")
def get_customer_service_agent_workload(user=Depends(get_current_user)):
    require_permission(user, "customer_service")

    if is_customer_service_agent(user):
        return {
            "success": True,
            "count": 0,
            "data": [],
        }

    cached_response = cache.get(
        "customer-service:workload"
    )

    if cached_response is not None:
        return cached_response

    rows = fetch_all(
        """
        SELECT
            assigned_agent_id,
            assigned_to,
            COUNT(*) AS total,
            SUM(
                CASE
                    WHEN status = 'Open'
                    THEN 1 ELSE 0
                END
            ) AS open,
            SUM(
                CASE
                    WHEN status = 'In Progress'
                    THEN 1 ELSE 0
                END
            ) AS progress,
            SUM(
                CASE
                    WHEN status = 'Escalated'
                    THEN 1 ELSE 0
                END
            ) AS escalated,
            SUM(
                CASE
                    WHEN status IN ('Resolved', 'Closed')
                    THEN 1 ELSE 0
                END
            ) AS resolved
        FROM customer_service_tickets
        GROUP BY assigned_agent_id, assigned_to
        """
    )

    response = {
        "success": True,
        "count": len(rows),
        "data": rows,
    }

    cache.set(
        "customer-service:workload",
        response,
        ttl_seconds=30,
    )

    return response