const CUSTOMER_SERVICE_API_BASE_URL = window.API_BASE_URL || "http://127.0.0.1:8000";
 
const CUSTOMER_SERVICE_ENDPOINTS = {
  tickets: "/customer-service/tickets",
  ticketDetail: function (ticketId) {
    return "/customer-service/tickets/" + encodeURIComponent(ticketId);
  },
  ticketUpdate: function (ticketId) {
    return "/customer-service/tickets/" + encodeURIComponent(ticketId) + "/update";
  },
  metricsSummary: "/customer-service/metrics/summary",
  agentsWorkload: "/customer-service/agents/workload"
};
 
let customerServiceCurrentPage = 1;
const customerServiceRowsPerPage = 4;
let customerServiceTickets = [];
let customerServiceFilteredTickets = [];
let customerServiceMetrics = null;
let customerServiceAgentsWorkload = [];

function showCustomerServicePopupLoading(message) {
  if (window.showLoadingPopup) {
    window.showLoadingPopup(message || "Loading customer service data...");
  }
}

function hideCustomerServicePopupLoading() {
  if (window.hideLoadingPopup) {
    window.hideLoadingPopup();
  }
}

function showCustomerServicePopupMessage(message, type = "info") {
  if (window.showAppPopup) {
    return window.showAppPopup(message, { type: type });
  }
  if (message) console[type === "error" ? "error" : "log"](message);
  return Promise.resolve();
}

 
/* ---------------------------------------------
   AUTH + API
--------------------------------------------- */
function getCustomerServiceToken() {
  const token = localStorage.getItem("omnilink_token");
  if (token) return token;
 
  const crmSession = localStorage.getItem("crm_session");
  if (!crmSession) return null;
 
  try {
    const session = JSON.parse(crmSession);
    return session.token || session.access_token || null;
  } catch (error) {
    console.warn("Invalid crm_session in localStorage.");
    return null;
  }
}
 
function getCustomerServiceHeaders() {
  return {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + getCustomerServiceToken()
  };
}
 
async function customerServiceGet(endpoint) {
  const response = await fetch(CUSTOMER_SERVICE_API_BASE_URL + endpoint, {
    method: "GET",
    headers: getCustomerServiceHeaders()
  });
 
  const result = await parseCustomerServiceResponse(response);
  if (!response.ok) {
    throw new Error(result.detail || result.message || "API request failed");
  }
 
  return result;
}
 
async function customerServiceGetCached(cacheKey, endpoint, ttlMilliseconds) {
  if (typeof cachedApiGet === "function") {
    return cachedApiGet(cacheKey, endpoint, ttlMilliseconds);
  }

  return customerServiceGet(endpoint);
}

function clearCustomerServiceFrontendCache() {
  if (typeof clearCachedApiPrefix === "function") {
    clearCachedApiPrefix("customer-service-");
  }

  if (typeof clearCachedApiData === "function") {
    clearCachedApiData("dashboard-summary");
    clearCachedApiData("admin-summary");
    clearCachedApiData("admin-data-health");
  }
}

async function customerServiceSend(endpoint, method, body) {
  const response = await fetch(CUSTOMER_SERVICE_API_BASE_URL + endpoint, {
    method: method,
    headers: getCustomerServiceHeaders(),
    body: JSON.stringify(body)
  });
 
  const result = await parseCustomerServiceResponse(response);
  if (!response.ok) {
    throw new Error(result.detail || result.message || "API request failed");
  }
 
  return result;
}
 
async function parseCustomerServiceResponse(response) {
  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    return response.json();
  }
 
  const text = await response.text();
  return { detail: text || response.statusText };
}
 
function getCurrentCustomerServiceUser() {
  const crmSession = localStorage.getItem("crm_session");
  if (crmSession) {
    try {
      return JSON.parse(crmSession);
    } catch (error) {
      localStorage.removeItem("crm_session");
    }
  }
 
  return {
    email: localStorage.getItem("omnilink_email") || "",
    role: localStorage.getItem("omnilink_role") || ""
  };
}
 
function isCustomerServiceAdmin() {
  const role = String(getCurrentCustomerServiceUser().role || "").toLowerCase();
  return role.includes("admin") || role.includes("manager");
}
 
/* ---------------------------------------------
   PAGE LOAD
--------------------------------------------- */
async function renderCustomerService() {
  const root = document.getElementById("customer-service-root");
  if (!root) return;
 
  if (!getCustomerServiceToken()) {
    showCustomerServicePopupMessage("Please login again. Customer Service APIs require login token.", "error");
    root.innerHTML = "";
    return;
  }
 
  showCustomerServicePopupLoading("Loading customer service data...");
  root.innerHTML = "";
 
  try {
    const results = await Promise.allSettled([
      customerServiceGet(CUSTOMER_SERVICE_ENDPOINTS.tickets),
      customerServiceGetCached(
        "customer-service-metrics",
        CUSTOMER_SERVICE_ENDPOINTS.metricsSummary,
        30000
      ),
      customerServiceGetCached(
        "customer-service-workload",
        CUSTOMER_SERVICE_ENDPOINTS.agentsWorkload,
        30000
      )
    ]);
 
    if (results[0].status === "rejected") {
      throw results[0].reason;
    }
 
    customerServiceTickets = normalizeTicketsResponse(results[0].value);
    customerServiceFilteredTickets = customerServiceTickets;
    customerServiceMetrics = results[1].status === "fulfilled"
      ? normalizeMetricsResponse(results[1].value)
      : calculateMetricsFromTickets(customerServiceTickets);
    customerServiceAgentsWorkload = results[2].status === "fulfilled"
      ? normalizeAgentsWorkloadResponse(results[2].value)
      : buildWorkloadFromTickets(customerServiceTickets);
 
    customerServiceCurrentPage = 1;
    renderCustomerServiceWorkspace();
    hideCustomerServicePopupLoading();
  } catch (error) {
    hideCustomerServicePopupLoading();
    root.innerHTML = renderStateCard(
      "Unable to Load Customer Service",
      error.message || "Request failed."
    );
    showCustomerServicePopupMessage("Unable to load Customer Service: " + (error.message || "Request failed."), "error");
  }
}
 
function renderCustomerServiceWorkspace() {
  const root = document.getElementById("customer-service-root");
  const user = getCurrentCustomerServiceUser();
  const metrics = customerServiceMetrics || calculateMetricsFromTickets(customerServiceTickets);
 
  root.innerHTML = `
    <div class="grid customer-service-kpis">
      ${renderKpiCard("Total Tickets", metrics.totalTickets, "Total records")}
      ${renderKpiCard("Resolved Tickets", metrics.resolvedTickets, "Resolved or closed")}
      ${renderKpiCard("Open Pipeline", metrics.openTickets, "Open, waiting, escalated")}
      ${renderKpiCard("Active Resolutions", metrics.inProgressTickets, "Currently in progress")}
      ${renderKpiCard("Priority Escalations", metrics.priorityEscalations, "High, critical, escalated")}
      ${renderKpiCard("Avg Resolution", metrics.avgResolutionTime, "Resolution performance")}
    </div>
 
    ${isCustomerServiceAdmin() ? renderAgentWorkload(customerServiceAgentsWorkload) : ""}
 
    <div class="card service-toolbar">
      <div>
        <h2>${isCustomerServiceAdmin() ? "All Service Desk Tickets" : "My Assigned Tickets"}</h2>
      </div>
      <div class="service-filters">
        <input id="ticketSearchInput" placeholder="Search ticket, customer, order, issue..." />
        <select id="ticketStatusFilter">
          <option value="All">All Status</option>
          <option value="Open">Open</option>
          <option value="In Progress">In Progress</option>
          <option value="Waiting for Customer">Waiting for Customer</option>
          <option value="Escalated">Escalated</option>
          <option value="Resolved">Resolved</option>
          <option value="Closed">Closed</option>
        </select>
        <select id="ticketPriorityFilter">
          <option value="All">All Priority</option>
          <option value="Low">Low</option>
          <option value="Medium">Medium</option>
          <option value="High">High</option>
          <option value="Critical">Critical</option>
        </select>
        ${isCustomerServiceAdmin() ? `<select id="ticketAgentFilter"><option value="All">All Agents</option>${getAgentOptions(customerServiceTickets)}</select>` : ""}
      </div>
    </div>
 
    <div class="table-card customer-service-table-wrap">
      <table>
        <thead>
          <tr>
            <th>Ticket ID</th>
            <th>Customer</th>
            <th>Linked Order</th>
            <th>Issue Category</th>
            <th>Priority</th>
            <th>Status</th>
            <th>Assigned To</th>
            <th>Customer Response</th>
            <th>Follow-up</th>
            <th>SLA Due</th>
            <th>Channel</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody id="customerServiceTableBody"></tbody>
      </table>
    </div>
 
    <div class="service-pagination">
      <div id="customerServicePaginationInfo" class="pagination-info"></div>
      <div id="customerServicePaginationControls" class="pagination-controls"></div>
    </div>
 
    <div id="ticketDrawerOverlay" class="ticket-drawer-overlay hidden" onclick="closeTicketDrawer(event)">
      <div class="ticket-drawer" onclick="event.stopPropagation()">
        <div id="ticketDrawerContent"></div>
      </div>
    </div>
  `;
 
  renderTicketPage();
  bindTicketFilters();
}
 
/* ---------------------------------------------
   NORMALIZERS
--------------------------------------------- */
function normalizeTicketsResponse(result) {
  const rows = Array.isArray(result)
    ? result
    : Array.isArray(result.data)
      ? result.data
      : Array.isArray(result.tickets)
        ? result.tickets
        : [];
 
  return rows.map(normalizeTicket);
}
 
function normalizeTicketDetailResponse(result) {
  const rawTicket = result.ticket || result.data || result || {};
  const ticket = normalizeTicket(rawTicket);
 
  ticket.timeline = normalizeTimeline(result.timeline || []);
 
  ticket.actionHistory = normalizeActionHistory(
    result.action_history || result.timeline || []
  );
 
  return ticket;
}
 
function normalizeTicket(ticket) {
  return {
    ticketId: asText(ticket.ticket_id || ticket.ticketId || ticket.id),
    customerId: asText(ticket.customer_id || ticket.customerId),
    customerName: ticket.customer_name || ticket.customerName || ticket.name || "-",
    linkedOrder:ticket.linked_order_id || ticket.linked_order || ticket.linkedOrder || ticket.order_id || ticket.orderId || "-",
    issueCategory: ticket.issue_category || ticket.issueCategory || ticket.category || "-",
    queryType: ticket.query_type || ticket.queryType || "-",
    priority: ticket.priority || "Medium",
    status: ticket.status || "Open",
    assignedAgentId: ticket.assigned_agent_id || ticket.assignedAgentId || ticket.agent_id || "-",
    assignedTo: ticket.assigned_to || ticket.assignedTo || ticket.agent_name || "Unassigned",
    contactResult: ticket.contact_result || ticket.contactResult || "Not Contacted",
    followUpRequired: normalizeYesNo(ticket.follow_up_required ?? ticket.followUpRequired),
    followUpDate: normalizeDate(ticket.follow_up_date || ticket.followUpDate || ""),
    followUpNote: ticket.follow_up_note || ticket.followUpNote || "",
    slaDue: ticket.sla_due || ticket.slaDue || "-",
    channel: ticket.channel || "-",
    membershipTier: ticket.membership_tier || ticket.membershipTier || "-",
    maskedPhone: ticket.masked_phone_number || ticket.masked_phone || ticket.maskedPhone || ticket.phone_number || ticket.phone || "-",
    maskedEmail: ticket.masked_email || ticket.maskedEmail || ticket.email || "-",
    city: ticket.customer_city || ticket.city || "-",
    customerSegment: ticket.customer_segment || ticket.customerSegment || "-",
    churnRisk: ticket.churn_risk_level || ticket.churnRisk || ticket.churn_risk || "-",
    productName: ticket.product_name || ticket.productName || "-",
    productCategory: ticket.product_category || ticket.productCategory || "-",
    orderDate: normalizeDate( ticket.transaction_date || ticket.order_date || ticket.orderDate ||""),
    orderValue: Number(ticket.order_value || ticket.orderValue || 0),
    paymentStatus: ticket.payment_method ||ticket.payment_status || ticket.paymentStatus ||"-",
    deliveryStatus: ticket.delivery_status || ticket.deliveryStatus || "-",
    returnRefundStatus: ticket.return_refund_status || ticket.returnRefundStatus || "-",
    description: ticket.description || ticket.customer_concern || ticket.concern || "-",
    callReview: ticket.call_review || ticket.callReview || "",
    internalNotes: ticket.internal_notes || ticket.internalNotes || "",
    resolutionSummary: ticket.resolution_summary || ticket.resolutionSummary || "",
    actionHistory: normalizeActionHistory(ticket.action_history || ticket.actionHistory || []),
    timeline: normalizeTimeline(ticket.timeline || [])
  };
}
 
function normalizeMetricsResponse(result) {
  const source = result.data || result.summary || result.metrics || result || {};
  return {
    totalTickets: Number(source.total_tickets ?? source.totalTickets ?? source.total_interactions ?? 0),
    resolvedTickets: Number(source.resolved_tickets ?? source.resolvedTickets ?? source.resolved_touchpoints ?? 0),
    openTickets: Number(source.open_tickets ?? source.openTickets ?? source.open_pipeline ?? 0),
    inProgressTickets: Number(source.in_progress_tickets ?? source.inProgressTickets ?? source.active_resolutions ?? 0),
    priorityEscalations: Number(source.priority_escalations ?? source.priorityEscalations ?? source.escalations ?? 0),
    avgResolutionTime: source.avg_resolution_time || source.avgResolutionTime || source.avg_resolution_hours || source.avgResolutionHours || "-"
  };
}
 
function normalizeAgentsWorkloadResponse(result) {
  const rows = Array.isArray(result)
    ? result
    : Array.isArray(result.data)
      ? result.data
      : Array.isArray(result.workload)
        ? result.workload
        : Array.isArray(result.agents)
          ? result.agents
          : [];
 
  return rows.map(function (agent) {
    return {
      agentId: agent.agent_id || agent.agentId || agent.assigned_agent_id || "-",
      agentName: agent.agent_name || agent.agentName || agent.assigned_to || "Unassigned",
      total: Number(agent.total || agent.total_tickets || 0),
      open: Number(agent.open || agent.open_tickets || 0),
      progress: Number(agent.progress || agent.in_progress || agent.in_progress_tickets || 0),
      escalated: Number(agent.escalated || agent.escalated_tickets || 0),
      resolved: Number(agent.resolved || agent.resolved_tickets || 0)
    };
  });
}
 
function normalizeActionHistory(actions) {
  if (!Array.isArray(actions)) return [];
 
  const allowedEventTypes = [
    "Agent Update",
    "Call Review",
    "Status Changed",
    "Follow-up Scheduled",
    "Ticket Resolved",
    "Ticket Closed"
  ];
 
  return actions
    .filter(function (action) {
      if (!action.event_type) return true;
 
      return allowedEventTypes.includes(action.event_type);
    })
    .map(function (action) {
      return {
        actionBy:
          action.created_by ||
          action.action_by ||
          action.actionBy ||
          "-",
 
        role:
          action.role ||
          "Customer Service",
 
        date:
          action.created_at ||
          action.date ||
          action.createdAt ||
          "-",
 
        newStatus:
          action.new_status ||
          action.newStatus ||
          action.status ||
          action.event_title ||
          "-",
 
        note:
          action.event_description ||
          action.note ||
          action.details ||
          "-"
      };
    });
}
 
function normalizeTimeline(items) {
  if (!Array.isArray(items)) return [];
 
  return items.map(function (item) {
    return {
      title:
        item.event_title ||
        item.title ||
        item.event_type ||
        item.event ||
        item.activity_type ||
        "Update",
 
      date:
        item.created_at ||
        item.date ||
        item.createdAt ||
        "-",
 
      note:
        item.event_description ||
        item.note ||
        item.description ||
        item.details ||
        "-"
    };
  });
}
 
function normalizeYesNo(value) {
  if (value === true || value === 1 || value === "1" || String(value).toLowerCase() === "yes") {
    return "Yes";
  }
  return "No";
}
 
function normalizeDate(value) {
  if (!value) return "";
 
  const text = String(value).trim();
 
  // YYYY-MM-DD or YYYY-MM-DD HH:mm:ss
  if (/^\d{4}-\d{2}-\d{2}/.test(text)) {
    return text.slice(0, 10);
  }
 
  // DD-MM-YYYY or DD-MM-YYYY HH:mm
  const match = text.match(/^(\d{2})-(\d{2})-(\d{4})/);
 
  if (match) {
    return `${match[3]}-${match[2]}-${match[1]}`;
  }
 
  return "";
}
 
/* ---------------------------------------------
   METRICS + WORKLOAD FALLBACKS
--------------------------------------------- */
function calculateMetricsFromTickets(tickets) {
  return {
    totalTickets: tickets.length,
    resolvedTickets: tickets.filter(function (ticket) {
      return ["Resolved", "Closed"].includes(ticket.status);
    }).length,
    openTickets: tickets.filter(function (ticket) {
      return ["Open", "Waiting for Customer", "Escalated"].includes(ticket.status);
    }).length,
    inProgressTickets: tickets.filter(function (ticket) {
      return ticket.status === "In Progress";
    }).length,
    priorityEscalations: tickets.filter(function (ticket) {
      return ["High", "Critical"].includes(ticket.priority) || ticket.status === "Escalated";
    }).length,
    avgResolutionTime: "-"
  };
}
 
function buildWorkloadFromTickets(tickets) {
  const map = {};
 
  tickets.forEach(function (ticket) {
    const key = ticket.assignedAgentId || "UNASSIGNED";
    if (!map[key]) {
      map[key] = {
        agentId: ticket.assignedAgentId || "-",
        agentName: ticket.assignedTo || "Unassigned",
        total: 0,
        open: 0,
        progress: 0,
        escalated: 0,
        resolved: 0
      };
    }
 
    map[key].total += 1;
    if (ticket.status === "Open") map[key].open += 1;
    if (ticket.status === "In Progress") map[key].progress += 1;
    if (ticket.status === "Escalated") map[key].escalated += 1;
    if (["Resolved", "Closed"].includes(ticket.status)) map[key].resolved += 1;
  });
 
  return Object.values(map);
}
 
/* ---------------------------------------------
   RENDER HELPERS
--------------------------------------------- */
function renderKpiCard(title, value, subText) {
  return `
    <div class="card">
      <div class="stat-title">${title}</div>
      <div class="stat-value">${value ?? 0}</div>
      <div class="stat-sub">${subText}</div>
    </div>
  `;
}
 
function renderAgentWorkload(agents) {
  const workload = agents.length ? agents : buildWorkloadFromTickets(customerServiceTickets);
 
  return `
    <div class="card agent-workload-section">
      <div class="section-title-row">
        <h2>Agent Workload & Completion</h2>

      </div>
      <div class="agent-workload-grid">
        ${workload.map(function (agent) {
    return `
            <div class="agent-workload-card">
              <div class="agent-name">${escapeHtml(agent.agentName)}</div>
              <div class="muted-text">${escapeHtml(agent.agentId)}</div>
              <div class="agent-metrics">
                <span>Total <strong>${agent.total}</strong></span>
                <span>Open <strong>${agent.open}</strong></span>
                <span>Progress <strong>${agent.progress}</strong></span>
                <span>Escalated <strong>${agent.escalated}</strong></span>
                <span>Resolved <strong>${agent.resolved}</strong></span>
              </div>
            </div>
          `;
  }).join("")}
      </div>
    </div>
  `;
}
 
function renderTicketPage() {
  const start = (customerServiceCurrentPage - 1) * customerServiceRowsPerPage;
  const end = start + customerServiceRowsPerPage;
  renderTicketRows(customerServiceFilteredTickets.slice(start, end));
  renderPagination();
}
 
function renderTicketRows(tickets) {
  const tbody = document.getElementById("customerServiceTableBody");
  if (!tbody) return;
 
  if (!tickets.length) {
    tbody.innerHTML = `<tr><td colspan="12" class="empty-state">No customer service tickets found.</td></tr>`;
    return;
  }
 
  tbody.innerHTML = tickets.map(function (ticket) {
    return `
      <tr>
        <td><strong>${escapeHtml(ticket.ticketId)}</strong></td>
        <td><strong>${escapeHtml(ticket.customerName)}</strong><div class="muted-text">${escapeHtml(ticket.customerId)}</div></td>
        <td>${escapeHtml(ticket.linkedOrder)}</td>
        <td>${escapeHtml(ticket.issueCategory)}</td>
        <td>${serviceBadge(ticket.priority, getPriorityClass(ticket.priority))}</td>
        <td>${serviceBadge(ticket.status, getStatusClass(ticket.status))}</td>
        <td><strong>${escapeHtml(ticket.assignedTo)}</strong><div class="muted-text">${escapeHtml(ticket.assignedAgentId)}</div></td>
        <td>${serviceBadge(ticket.contactResult, "badge-neutral")}</td>
        <td>${ticket.followUpRequired === "Yes" ? serviceBadge("Yes", "badge-progress") : serviceBadge("No", "badge-neutral")}</td>
        <td>${escapeHtml(ticket.slaDue)}</td>
        <td>${escapeHtml(ticket.channel)}</td>
        <td><button class="secondary-btn compact-btn" onclick="openTicketDrawer('${escapeForAttribute(ticket.ticketId)}')">View / Action</button></td>
      </tr>
    `;
  }).join("");
}
 
function renderPagination() {
  const info = document.getElementById("customerServicePaginationInfo");
  const controls = document.getElementById("customerServicePaginationControls");
  if (!info || !controls) return;
 
  const total = customerServiceFilteredTickets.length;
  const totalPages = Math.ceil(total / customerServiceRowsPerPage) || 1;
 
  if (customerServiceCurrentPage > totalPages) {
    customerServiceCurrentPage = totalPages;
  }
 
  const startItem = total === 0 ? 0 : (customerServiceCurrentPage - 1) * customerServiceRowsPerPage + 1;
  const endItem = Math.min(customerServiceCurrentPage * customerServiceRowsPerPage, total);
  info.innerHTML = `Showing ${startItem}-${endItem} of ${total} tickets`;
 
  controls.innerHTML = `
    <button class="page-btn" onclick="goToCustomerServicePage(${customerServiceCurrentPage - 1})" ${customerServiceCurrentPage === 1 ? "disabled" : ""}>Prev</button>
    ${getVisiblePages(customerServiceCurrentPage, totalPages).map(function (page) {
    return `<button class="page-btn ${page === customerServiceCurrentPage ? "active" : ""}" onclick="goToCustomerServicePage(${page})">${page}</button>`;
  }).join("")}
    <button class="page-btn" onclick="goToCustomerServicePage(${customerServiceCurrentPage + 1})" ${customerServiceCurrentPage === totalPages ? "disabled" : ""}>Next</button>
  `;
}
 
function getVisiblePages(current, total) {
  if (total <= 3) return Array.from({ length: total }, function (_, index) { return index + 1; });
  if (current === 1) return [1, 2, 3];
  if (current === total) return [total - 2, total - 1, total];
  return [current - 1, current, current + 1];
}
 
function goToCustomerServicePage(page) {
  const totalPages = Math.ceil(customerServiceFilteredTickets.length / customerServiceRowsPerPage) || 1;
  if (page < 1 || page > totalPages) return;
  customerServiceCurrentPage = page;
  renderTicketPage();
}
 
function bindTicketFilters() {
  const searchInput = document.getElementById("ticketSearchInput");
  const statusFilter = document.getElementById("ticketStatusFilter");
  const priorityFilter = document.getElementById("ticketPriorityFilter");
  const agentFilter = document.getElementById("ticketAgentFilter");
 
  if (!searchInput || !statusFilter || !priorityFilter) return;
 
  function applyFilters() {
    const searchValue = searchInput.value.toLowerCase().trim();
    const statusValue = statusFilter.value;
    const priorityValue = priorityFilter.value;
    const agentValue = agentFilter ? agentFilter.value : "All";
 
    customerServiceFilteredTickets = customerServiceTickets.filter(function (ticket) {
      const text = [
        ticket.ticketId,
        ticket.customerName,
        ticket.customerId,
        ticket.linkedOrder,
        ticket.issueCategory,
        ticket.queryType,
        ticket.assignedTo,
        ticket.assignedAgentId,
        ticket.channel,
        ticket.contactResult
      ].join(" ").toLowerCase();
 
      return text.includes(searchValue) &&
        (statusValue === "All" || ticket.status === statusValue) &&
        (priorityValue === "All" || ticket.priority === priorityValue) &&
        (agentValue === "All" || ticket.assignedAgentId === agentValue);
    });
 
    customerServiceCurrentPage = 1;
    renderTicketPage();
  }
 
  searchInput.addEventListener("input", applyFilters);
  statusFilter.addEventListener("change", applyFilters);
  priorityFilter.addEventListener("change", applyFilters);
  if (agentFilter) agentFilter.addEventListener("change", applyFilters);
}
 
function getAgentOptions(tickets) {
  const agents = new Map();
  tickets.forEach(function (ticket) {
    if (ticket.assignedAgentId && ticket.assignedAgentId !== "-") {
      agents.set(ticket.assignedAgentId, ticket.assignedTo || ticket.assignedAgentId);
    }
  });
 
  return Array.from(agents.entries()).map(function (entry) {
    return `<option value="${escapeForAttribute(entry[0])}">${escapeHtml(entry[1])}</option>`;
  }).join("");
}
 
/* ---------------------------------------------
   DRAWER + UPDATE
--------------------------------------------- */
async function openTicketDrawer(ticketId) {
  const overlay = document.getElementById("ticketDrawerOverlay");
  const content = document.getElementById("ticketDrawerContent");
  if (!overlay || !content) return;
 
  content.innerHTML = renderDrawerLoading("Loading ticket...");
  overlay.classList.remove("hidden");
 
  try {
    const result = await customerServiceGet(CUSTOMER_SERVICE_ENDPOINTS.ticketDetail(ticketId));
    renderTicketDrawer(normalizeTicketDetailResponse(result));
  } catch (error) {
    content.innerHTML = renderDrawerError(ticketId, error.message || "Unable to load ticket.");
  }
}
 
function renderTicketDrawer(ticket) {
  const content = document.getElementById("ticketDrawerContent");
  if (!content) return;
 
  content.innerHTML = `
    <div class="drawer-header">
      <div><h2>${escapeHtml(ticket.ticketId)}</h2><p>${escapeHtml(ticket.issueCategory)} · ${escapeHtml(ticket.queryType)}</p></div>
      <button class="drawer-close" onclick="closeTicketDrawer()">×</button>
    </div>
 
    <div class="drawer-status-row">
      ${serviceBadge(ticket.priority, getPriorityClass(ticket.priority))}
      ${serviceBadge(ticket.status, getStatusClass(ticket.status))}
      ${serviceBadge(ticket.channel, "badge-neutral")}
      ${serviceBadge(ticket.contactResult, "badge-progress")}
    </div>
 
    <div class="drawer-section">
      <h3>Customer Profile</h3>
      <div class="detail-grid">
        ${detailItem("Customer Name", ticket.customerName)}
        ${detailItem("Customer ID", ticket.customerId)}
        ${detailItem("Membership Tier", ticket.membershipTier)}
        ${detailItem("Phone", ticket.maskedPhone)}
        ${detailItem("Email", ticket.maskedEmail)}
        ${detailItem("City", ticket.city)}
        ${detailItem("Segment", ticket.customerSegment)}
        ${detailItem("Churn Risk", ticket.churnRisk)}
      </div>
    </div>
 
    <div class="drawer-section">
      <h3>Order Concern</h3>
      <div class="detail-grid">
        ${detailItem("Order ID", ticket.linkedOrder)}
        ${detailItem("Product", ticket.productName)}
        ${detailItem("Category", ticket.productCategory)}
        ${detailItem("Order Date", ticket.orderDate)}
        ${detailItem("Order Value", formatCurrency(ticket.orderValue))}
        ${detailItem("Payment Method", ticket.paymentStatus)}
        ${detailItem("Delivery Status", ticket.deliveryStatus)}
        ${detailItem("Return / Refund", ticket.returnRefundStatus)}
      </div>
      <div class="note-block"><strong>Customer Concern</strong><p>${escapeHtml(ticket.description)}</p></div>
    </div>
 
    <div class="drawer-section">
      <h3>Agent Action / Call Review</h3>
 
      <label class="form-label">Ticket Status</label>
      <select id="ticketStatusUpdate" class="service-input">${renderStatusOptions(ticket.status)}</select>
 
      <label class="form-label">Call / Conversation Review</label>
      <textarea id="ticketCallReview" class="service-textarea" placeholder="Write what happened on call or interaction...">${escapeHtml(ticket.callReview)}</textarea>
 
      <label class="form-label">Customer Response</label>
      <select id="ticketContactResult" class="service-input">${renderContactResultOptions(ticket.contactResult)}</select>
 
      <label class="form-label">Need Follow-up?</label>
      <select id="ticketFollowUpRequired" class="service-input">
        <option value="No" ${ticket.followUpRequired === "No" ? "selected" : ""}>No</option>
        <option value="Yes" ${ticket.followUpRequired === "Yes" ? "selected" : ""}>Yes</option>
      </select>
 
      <label class="form-label">Follow-up Date</label>
      <input id="ticketFollowUpDate" class="service-input" type="date" value="${escapeForAttribute(ticket.followUpDate)}" />
 
      <label class="form-label">Follow-up Note</label>
      <textarea id="ticketFollowUpNote" class="service-textarea" placeholder="Write follow-up note...">${escapeHtml(ticket.followUpNote)}</textarea>
 
      <label class="form-label">Internal Notes</label>
      <textarea id="ticketInternalNotes" class="service-textarea">${escapeHtml(ticket.internalNotes)}</textarea>
 
      <label class="form-label">Resolution Summary</label>
      <textarea id="ticketResolutionSummary" class="service-textarea" placeholder="Required when resolving or closing ticket...">${escapeHtml(ticket.resolutionSummary)}</textarea>
 
      <button id="ticketSubmitButton" class="primary-btn service-submit-btn" onclick="submitTicketUpdate('${escapeForAttribute(ticket.ticketId)}')">Submit Update</button>
      <div id="ticketUpdateMessage" class="muted-text"></div>
    </div>
 
    <div class="drawer-section"><h3>Action History</h3>${renderActionHistory(ticket.actionHistory)}</div>
    <div class="drawer-section"><h3>Timeline</h3>${renderTimeline(ticket.timeline)}</div>
  `;
}
 
async function submitTicketUpdate(ticketId) {
  const status =
    document.getElementById("ticketStatusUpdate").value;
 
  const followUpRequired =
    document.getElementById("ticketFollowUpRequired").value;
 
  const followUpDate =
    document.getElementById("ticketFollowUpDate").value;
 
  const resolutionSummary =
    document.getElementById("ticketResolutionSummary").value.trim();
 
  const submitButton =
    document.getElementById("ticketSubmitButton");
 
  const message =
    document.getElementById("ticketUpdateMessage");
 
  if (
    ["Resolved", "Closed"].includes(status) &&
    !resolutionSummary
  ) {
    showCustomerServicePopupMessage("Resolution Summary is required before resolving or closing the ticket.", "error");
    return;
  }
 
  if (
    followUpRequired === "Yes" &&
    !followUpDate
  ) {
    showCustomerServicePopupMessage("Follow-up Date is required when follow-up is marked Yes.", "error");
    return;
  }
 
  const payload = {
    status: status,
 
    call_review:
      document.getElementById("ticketCallReview").value.trim(),
 
    contact_result:
      document.getElementById("ticketContactResult").value,
 
    follow_up_required:
      followUpRequired,
 
    follow_up_date:
      followUpRequired === "Yes"
        ? followUpDate
        : "",
 
    follow_up_note:
      followUpRequired === "Yes"
        ? document.getElementById("ticketFollowUpNote").value.trim()
        : "",
 
    internal_notes:
      document.getElementById("ticketInternalNotes").value.trim(),
 
    resolution_summary:
      resolutionSummary
  };
 
  try {
    if (submitButton) {
      submitButton.disabled = true;
    }
 
    if (message) {
      message.textContent = "Saving...";
    }
    showCustomerServicePopupLoading("Saving ticket update...");
 
    const result = await customerServiceSend(
      CUSTOMER_SERVICE_ENDPOINTS.ticketUpdate(ticketId),
      "PUT",
      payload
    );
 
    console.log("Ticket update result:", result);
 
    await renderCustomerService();
    await openTicketDrawer(ticketId);
    hideCustomerServicePopupLoading();
    showCustomerServicePopupMessage("Ticket updated successfully.", "success");
 
  } catch (error) {
    hideCustomerServicePopupLoading();
    console.error("Ticket update failed:", error);
 
    if (message) {
      message.textContent =
        "Update failed: " +
        (error.message || "Request failed.");
    }
    showCustomerServicePopupMessage("Ticket update failed: " + (error.message || "Request failed."), "error");
  } finally {
    if (submitButton) {
      submitButton.disabled = false;
    }
  }
}
 
function closeTicketDrawer() {
  const overlay = document.getElementById("ticketDrawerOverlay");
  if (overlay) overlay.classList.add("hidden");
}
 
/* ---------------------------------------------
   SMALL UTILITIES
--------------------------------------------- */
function renderStatusOptions(currentStatus) {
  const statuses = ["Open", "In Progress", "Waiting for Customer", "Escalated", "Resolved", "Closed"];
  return statuses.map(function (status) {
    return `<option value="${status}" ${status === currentStatus ? "selected" : ""}>${status}</option>`;
  }).join("");
}
 
function renderContactResultOptions(currentValue) {
  const results = ["Not Contacted", "Connected", "Need Follow-up", "Interested", "Not Interested", "No Response", "Wrong Number"];
  return results.map(function (result) {
    return `<option value="${result}" ${result === currentValue ? "selected" : ""}>${result}</option>`;
  }).join("");
}
 
function renderActionHistory(actions) {
  if (!actions.length) return `<div class="empty-state">No agent action submitted yet.</div>`;
 
  return `<div class="timeline-list">${actions.map(function (action) {
    return `<div class="timeline-item"><div class="timeline-dot"></div><div><strong>${escapeHtml(action.actionBy)} · ${escapeHtml(action.newStatus)}</strong><span>${escapeHtml(action.date)} · ${escapeHtml(action.role)}</span><p>${escapeHtml(action.note)}</p></div></div>`;
  }).join("")}</div>`;
}
 
function renderTimeline(timeline) {
  if (!timeline.length) return `<div class="empty-state">No timeline available.</div>`;
 
  return `<div class="timeline-list">${timeline.map(function (item) {
    return `<div class="timeline-item"><div class="timeline-dot"></div><div><strong>${escapeHtml(item.title)}</strong><span>${escapeHtml(item.date)}</span><p>${escapeHtml(item.note)}</p></div></div>`;
  }).join("")}</div>`;
}
 
function renderStateCard(title, message) {
  return `<div class="card empty-state"><h2>${escapeHtml(title)}</h2><p>${escapeHtml(message)}</p></div>`;
}
 
function renderDrawerLoading(message) {
  return `<div class="drawer-header"><div><h2>Please wait</h2><p>${escapeHtml(message)}</p></div><button class="drawer-close" onclick="closeTicketDrawer()">×</button></div>`;
}
 
function renderDrawerError(ticketId, message) {
  return `<div class="drawer-header"><div><h2>${escapeHtml(ticketId)}</h2><p>Request failed</p></div><button class="drawer-close" onclick="closeTicketDrawer()">×</button></div><div class="drawer-section"><div class="empty-state">${escapeHtml(message)}</div></div>`;
}
 
function detailItem(label, value) {
  return `<div class="detail-item"><span>${escapeHtml(label)}</span><strong>${escapeHtml(value || "-")}</strong></div>`;
}
 
function serviceBadge(label, className) {
  return `<span class="service-badge ${className}">${escapeHtml(label || "-")}</span>`;
}
 
function getPriorityClass(priority) {
  switch (priority) {
    case "Critical": return "badge-critical";
    case "High": return "badge-high";
    case "Medium": return "badge-medium";
    case "Low": return "badge-low";
    default: return "badge-neutral";
  }
}
 
function getStatusClass(status) {
  switch (status) {
    case "Open": return "badge-open";
    case "In Progress": return "badge-progress";
    case "Waiting for Customer": return "badge-waiting";
    case "Escalated": return "badge-critical";
    case "Resolved": return "badge-resolved";
    case "Closed": return "badge-closed";
    default: return "badge-neutral";
  }
}
 
function formatCurrency(amount) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0
  }).format(Number(amount || 0));
}
 
function asText(value) {
  if (value === undefined || value === null || value === "") return "-";
  return String(value);
}
 
function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
 
 
function escapeForAttribute(value) {
  return escapeHtml(value);
}