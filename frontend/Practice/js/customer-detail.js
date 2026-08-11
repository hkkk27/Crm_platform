function showCustomerDetailPopup(message, type = "info") {
  if (window.showAppPopup) {
    return window.showAppPopup(message, { type });
  }
  console[type === "error" ? "error" : "log"](message);
  return Promise.resolve();
}

function showCustomerDetailLoading(message) {
  if (window.showLoadingPopup) {
    window.showLoadingPopup(message || "Loading customer profile...");
  }
}

function hideCustomerDetailLoading() {
  if (window.hideLoadingPopup) {
    window.hideLoadingPopup();
  }
}

const detailTablePageSize = 3;
let orderPageMap = {};
let complaintPageMap = {};
let activeDetailTab = "overview";
let customerDetailLoadingMap = {};

function openCustomer(id) {
  showCustomerDetailLoading("Loading customer profile...");

  try {
    selectedCustomerId = id;
    orderPageMap[id] = 1;
    complaintPageMap[id] = 1;
    activeDetailTab = "overview";

    renderCustomerDetail();
    document.getElementById("customers").style.display = "none";
    document.getElementById("customerDetail").style.display = "block";

    loadCustomerDetailBackendData(id);
  } catch (error) {
    hideCustomerDetailLoading();
    console.error("Customer profile open error:", error);
    showCustomerDetailPopup(error.message || "Unable to open customer profile.", "error");
  }
}

function showCustomers() {
  document.getElementById("customerDetail").style.display = "none";
  document.getElementById("customers").style.display = "block";
}

function switchDetailTab(tab) {
  activeDetailTab = tab;
  renderCustomerDetail();
}

function yesNoBadge(value) {
  return value ? badge("Allowed", "success") : badge("Not Allowed", "danger");
}

function normalValue(value) {
  return value === undefined || value === null || value === "" ? "-" : value;
}

function getCustomerInitials(name) {
  return String(name || "Customer").trim().split(/\s+/).slice(0, 2).map(part => part.charAt(0)).join("").toUpperCase() || "C";
}

function renderDetailGrid(rows) {
  return `<div class="detail-grid">${rows.map(row => `<div class="detail-item"><span>${row.label}</span><strong>${row.value}</strong></div>`).join("")}</div>`;
}

function renderSegments(segments) {
  if (!segments || segments.length === 0) return `<p class="muted-text">No segments available.</p>`;
  return `<div class="segment-list">${segments.map(segment => `<span class="badge info">${segment}</span>`).join("")}</div>`;
}

function renderTierBenefits(benefits) {
  if (!benefits || benefits.length === 0) return `<p class="muted-text">No tier benefits available.</p>`;
  return benefits.map(benefit => `<span class="benefit-pill">${benefit}</span>`).join("");
}

function renderConsentChannels(consent = {}) {
  const channels = [
    { label: "WhatsApp", value: consent.whatsapp },
    { label: "SMS", value: consent.sms },
    { label: "Email", value: consent.email },
    { label: "App Notifications", value: consent.app },
    { label: "Personalization", value: consent.personalization }
  ];

  return `<div class="consent-grid">${channels.map(ch => `<div class="consent-item ${ch.value ? "consent-yes" : "consent-no"}"><span>${ch.label}</span>${yesNoBadge(ch.value)}</div>`).join("")}</div>`;
}

function renderOrderTable(customer) {
  const orders = customer.orderHistory || [];
  const currentPage = orderPageMap[customer.id] || 1;

  if (customerDetailLoadingMap[customer.id]) return `<p class="empty-state"></p>`;
  if (orders.length === 0) return `<p class="empty-state">No order details available.</p>`;

  const start = (currentPage - 1) * detailTablePageSize;
  const paginatedOrders = orders.slice(start, start + detailTablePageSize);
  const totalPages = Math.ceil(orders.length / detailTablePageSize);

  return `
    <div class="table-card">
      <table>
        <thead><tr><th>Order</th><th>Date</th><th>Channel / Store</th><th>Items</th><th>Amount</th><th>Status</th><th>Payment</th></tr></thead>
        <tbody>
          ${paginatedOrders.map(item => `
            <tr>
              <td><strong>${normalValue(item.orderId || item.order_id || item.id || item.order_number || item.invoice_number)}</strong><br><small>${normalValue(item.invoiceNumber || item.invoice_number || item.bill_number || item.receipt_number)}</small></td>
              <td>${normalValue(item.orderDate || item.order_date || item.purchaseDate || item.purchase_date || item.transaction_date || item.created_at)}</td>
              <td>${normalValue(item.channel || item.order_channel || item.storeName || item.store_name || item.business_channel || item.store_id)}</td>
              <td>${normalValue(item.itemCount || item.item_count || item.quantity || item.items_count || item.product_count)}</td>
              <td>${money(Number(item.totalAmount || item.total_amount || item.orderAmount || item.order_amount || item.net_amount || item.gross_amount || item.amount || 0))}</td>
              <td>${badge(normalValue(item.status || item.order_status || item.fulfillment_status), String(item.status || item.order_status || "").toLowerCase().includes("cancel") ? "danger" : "success")}</td>
              <td>${normalValue(item.paymentStatus || item.payment_status || item.paymentMethod || item.payment_method)}</td>
            </tr>`).join("")}
        </tbody>
      </table>
    </div>
    ${renderDetailPagination("order", customer.id, currentPage, totalPages)}
  `;
}

function renderComplaintTable(customer) {
  const complaints = customer.complaintHistory || [];
  const currentPage = complaintPageMap[customer.id] || 1;

  if (customerDetailLoadingMap[customer.id]) return `<p class="empty-state"></p>`;
  if (complaints.length === 0) return `<p class="empty-state">No complaint or privacy request history available.</p>`;

  const start = (currentPage - 1) * detailTablePageSize;
  const paginatedComplaints = complaints.slice(start, start + detailTablePageSize);
  const totalPages = Math.ceil(complaints.length / detailTablePageSize);

  return `
    <div class="table-card">
      <table>
        <thead><tr><th>Ticket</th><th>Request Type</th><th>Description</th><th>Status</th><th>Created Date</th><th>Resolved Date</th></tr></thead>
        <tbody>
          ${paginatedComplaints.map(item => `
            <tr>
              <td><strong>${normalValue(item.ticketId || item.ticket_id || item.id)}</strong></td>
              <td>${normalValue(item.requestType || item.request_type || item.issue_category || item.type)}</td>
              <td>${normalValue(item.description || item.issue_description || item.notes || item.summary)}</td>
              <td>${badge(normalValue(item.status), String(item.status || "").toLowerCase().includes("resolved") || String(item.status || "").toLowerCase().includes("closed") ? "success" : "warning")}</td>
              <td>${normalValue(item.createdDate || item.created_date || item.created_on || item.created_at)}</td>
              <td>${normalValue(item.resolvedDate || item.resolved_date || item.resolved_on || item.closed_at)}</td>
            </tr>`).join("")}
        </tbody>
      </table>
    </div>
    ${renderDetailPagination("complaint", customer.id, currentPage, totalPages)}
  `;
}

function renderDetailPagination(type, customerId, currentPage, totalPages) {
  if (totalPages <= 1) return "";
  const visiblePages = getVisibleDetailPages(currentPage, totalPages);
  let buttons = `<div class="detail-pagination"><span>Page ${currentPage} of ${totalPages}</span><button onclick="changeDetailPage('${type}', '${customerId}', ${currentPage - 1})" ${currentPage === 1 ? "disabled" : ""}>Prev</button>`;
  visiblePages.forEach(page => {
    buttons += `<button class="${page === currentPage ? "active" : ""}" onclick="changeDetailPage('${type}', '${customerId}', ${page})">${page}</button>`;
  });
  buttons += `<button onclick="changeDetailPage('${type}', '${customerId}', ${currentPage + 1})" ${currentPage === totalPages ? "disabled" : ""}>Next</button></div>`;
  return buttons;
}

function getVisibleDetailPages(currentPage, totalPages) {
  if (totalPages <= 3) return Array.from({ length: totalPages }, (_, index) => index + 1);
  if (currentPage === 1) return [1, 2, 3];
  if (currentPage === totalPages) return [totalPages - 2, totalPages - 1, totalPages];
  return [currentPage - 1, currentPage, currentPage + 1];
}

function changeDetailPage(type, customerId, pageNumber) {
  const customer = customers.find(x => x.id === customerId);
  if (!customer) return;
  let totalPages = 1;
  if (type === "order") totalPages = Math.ceil((customer.orderHistory || []).length / detailTablePageSize);
  if (type === "complaint") totalPages = Math.ceil((customer.complaintHistory || []).length / detailTablePageSize);
  if (pageNumber < 1 || pageNumber > totalPages) return;
  if (type === "order") orderPageMap[customerId] = pageNumber;
  if (type === "complaint") complaintPageMap[customerId] = pageNumber;
  renderCustomerDetail();
}

function renderOverviewTab(c) {
  return `
    <div class="summary-grid">
      <div class="summary-card"><span>Total Spend</span><strong>${money(c.totalSpend)}</strong><small>Customer lifetime value indicator</small></div>
      <div class="summary-card"><span>Average Order Value</span><strong>${money(c.aov)}</strong><small>Average purchase amount</small></div>
      <div class="summary-card"><span>Purchase Frequency</span><strong>${c.frequency}</strong><small>Total purchases</small></div>
      <div class="summary-card"><span>Reward Points</span><strong>${c.points}</strong><small>Available loyalty points</small></div>
    </div>
    <section class="detail-section"><h3>Customer Profile</h3>${renderDetailGrid([{label:"Phone",value:c.phone},{label:"Email",value:c.email},{label:"City",value:c.city},{label:"Birthday Month",value:c.birthdayMonth},{label:"Preferred Category",value:c.preferredCategory},{label:"Last Purchase",value:c.lastPurchase}])}</section>
    <section class="detail-section"><h3>Customer Segments</h3>${renderSegments(c.segments)}</section>
  `;
}

function renderMembershipTab(c) {
  return `
    <section class="detail-section"><h3>Membership & Loyalty</h3>${renderDetailGrid([{label:"Membership Status",value:c.status},{label:"Tier",value:c.tier},{label:"Points Earned",value:c.pointsEarned},{label:"Points Redeemed",value:c.pointsRedeemed},{label:"Membership Expiry",value:normalValue(c.membershipExpiry)},{label:"Upgrade Eligibility",value:normalValue(c.upgradeEligibility)},{label:"Birthday Voucher",value:normalValue(c.birthdayVoucher)}])}</section>
    <section class="detail-section"><h3>Tier Benefits</h3>${renderTierBenefits(c.tierBenefits)}</section>
  `;
}

function renderConsentTab(c) {
  return `<section class="detail-section"><h3>Consent Channels</h3>${renderConsentChannels(c.consent)}</section>`;
}

function renderHistoryTab(c) {
  return `
    <section class="detail-section"><div class="section-head"><h3>Order Details</h3><span>${(c.orderHistory || []).length} records</span></div>${renderOrderTable(c)}</section>
    <section class="detail-section"><div class="section-head"><h3>Complaint / Privacy Request History</h3><span>${(c.complaintHistory || []).length} records</span></div>${renderComplaintTable(c)}</section>
  `;
}

const detailTabs = [
  { id: "overview", label: "Overview" },
  { id: "membership", label: "Membership" },
  { id: "consent", label: "Consent" },
  { id: "history", label: "History" }
];

function renderTabContent(tabId, c) {
  if (tabId === "overview") return renderOverviewTab(c);
  if (tabId === "membership") return renderMembershipTab(c);
  if (tabId === "consent") return renderConsentTab(c);
  if (tabId === "history") return renderHistoryTab(c);
  return "";
}

function renderCustomerDetail() {
  const c = customers.find(x => x.id === selectedCustomerId);
  if (!c) {
    document.getElementById("customerDetailContent").innerHTML = `<p>Customer not found.</p>`;
    return;
  }
  const initials = getCustomerInitials(c.name);
  document.getElementById("customerDetailContent").innerHTML = `
    <div class="customer-hero card">
      <div class="customer-avatar">${initials}</div>
      <div><h2>${c.name}</h2><p>${c.id} · ${c.city} · Preferred Category: ${c.preferredCategory}</p><div class="badge-row">${badge(c.status, c.status === "Member" ? "success" : "warning")} ${badge(c.tier, c.tier === "Non-member" ? "warning" : "info")} ${c.doNotContact ? badge("Do Not Contact", "danger") : badge("Contact Allowed", "success")}</div></div>
      <div class="hero-meta"><span>Last Purchase</span><strong>${c.lastPurchase}</strong></div>
    </div>
    <div class="detail-tabs">${detailTabs.map(tab => `<button class="${activeDetailTab === tab.id ? "active" : ""}" onclick="switchDetailTab('${tab.id}')">${tab.label}</button>`).join("")}</div>
    ${renderTabContent(activeDetailTab, c)}
  `;
}

function detailListFromResponse(result) {
  if (Array.isArray(result)) return result;
  if (!result || typeof result !== "object") return [];
  return result.data || result.items || result.results || result.orders || result.order_details || result.orderHistory || result.history || result.tickets || result.complaints || [];
}

async function fetchFirstAvailable(paths) {
  for (const path of paths) {
    try {
      const response = await fetch(`${API_BASE_URL}${path}`, { method: "GET", headers: getAuthHeaders() });
      if (!response.ok) continue;
      const result = await response.json();
      return detailListFromResponse(result);
    } catch (error) {
      console.warn("Customer detail endpoint skipped:", path, error);
    }
  }
  return [];
}


function detailText(value) {
  return String(value === undefined || value === null ? "" : value).trim().toLowerCase();
}

function detailDigits(value) {
  const digits = String(value === undefined || value === null ? "" : value).replace(/\D/g, "");
  return digits ? String(Number(digits)) : "";
}

function detailIdMatches(left, right) {
  const leftText = detailText(left);
  const rightText = detailText(right);
  if (leftText && rightText && leftText === rightText) return true;

  const leftDigits = detailDigits(left);
  const rightDigits = detailDigits(right);
  return Boolean(leftDigits && rightDigits && leftDigits === rightDigits);
}

function detailListFromCustomerServiceResponse(result) {
  if (Array.isArray(result)) return result;
  if (!result || typeof result !== "object") return [];

  if (Array.isArray(result.data)) return result.data;
  if (Array.isArray(result.tickets)) return result.tickets;
  if (Array.isArray(result.items)) return result.items;
  if (Array.isArray(result.results)) return result.results;

  if (result.data && typeof result.data === "object") {
    if (Array.isArray(result.data.tickets)) return result.data.tickets;
    if (Array.isArray(result.data.items)) return result.data.items;
    if (Array.isArray(result.data.results)) return result.data.results;
  }

  return [];
}

function ticketBelongsToSelectedCustomer(ticket, customer) {
  const ticketCustomerId = ticket.customer_id || ticket.customerId || ticket.crm_customer_key || ticket.customer_key;
  const ticketCustomerName = ticket.customer_name || ticket.customerName || ticket.name;
  const ticketPhone = ticket.masked_phone_number || ticket.masked_phone || ticket.phone_number || ticket.phone || ticket.maskedPhone;
  const ticketEmail = ticket.masked_email || ticket.maskedEmail || ticket.email;

  return (
    detailIdMatches(ticketCustomerId, customer.id) ||
    (detailText(ticketCustomerName) && detailText(ticketCustomerName) === detailText(customer.name)) ||
    (detailText(ticketPhone) && detailText(ticketPhone) === detailText(customer.phone)) ||
    (detailText(ticketEmail) && detailText(ticketEmail) === detailText(customer.email))
  );
}

function normalizeComplaintFromServiceTicket(ticket) {
  return {
    ticketId: ticket.ticket_id || ticket.ticketId || ticket.id,
    requestType: ticket.issue_category || ticket.issueCategory || ticket.category || ticket.query_type || ticket.queryType,
    description: ticket.description || ticket.customer_concern || ticket.concern || ticket.issue_description || ticket.notes || ticket.summary,
    status: ticket.status || "Open",
    createdDate: ticket.created_on || ticket.created_at || ticket.createdDate || ticket.created_date,
    resolvedDate: ticket.resolved_on || ticket.resolved_at || ticket.closed_at || ticket.resolvedDate || ticket.resolved_date
  };
}

function normalizeOrderFromServiceTicket(ticket) {
  return {
    orderId: ticket.linked_order_id || ticket.linked_order || ticket.linkedOrder || ticket.order_id || ticket.orderId,
    invoiceNumber: ticket.invoice_number || ticket.bill_number || ticket.receipt_number,
    orderDate: ticket.transaction_date || ticket.order_date || ticket.orderDate,
    channel: ticket.channel || ticket.order_channel || ticket.business_channel,
    itemCount: ticket.product_name || ticket.productName || ticket.product_category || ticket.productCategory,
    totalAmount: ticket.order_value || ticket.orderValue || ticket.order_amount || ticket.amount,
    status: ticket.delivery_status || ticket.deliveryStatus || ticket.return_refund_status || ticket.returnRefundStatus || ticket.status,
    paymentStatus: ticket.payment_method || ticket.payment_status || ticket.paymentStatus
  };
}

async function fetchServiceTicketsForCustomer(customer) {
  try {
    const response = await fetch(`${API_BASE_URL}/customer-service/tickets`, {
      method: "GET",
      headers: getAuthHeaders()
    });

    if (!response.ok) {
      console.warn("Customer detail ticket fetch failed", response.status);
      return [];
    }

    const result = await response.json();
    const allTickets = detailListFromCustomerServiceResponse(result);
    const matchedTickets = allTickets.filter(ticket => ticketBelongsToSelectedCustomer(ticket, customer));

    console.log("Customer detail ticket match", {
      customerId: customer.id,
      customerName: customer.name,
      totalTickets: allTickets.length,
      matchedTickets: matchedTickets.length,
      sampleTicketCustomerId: allTickets[0]?.customer_id || allTickets[0]?.customerId || ""
    });

    return matchedTickets;
  } catch (error) {
    console.warn("Customer detail ticket fetch error", error);
    return [];
  }
}

async function loadCustomerDetailBackendData(customerId) {
  const customer = customers.find(x => x.id === customerId);

  if (!customer) {
    hideCustomerDetailLoading();
    showCustomerDetailPopup("Customer not found.", "error");
    return;
  }

  if (customer.detailDataLoaded) {
    hideCustomerDetailLoading();
    return;
  }

  customerDetailLoadingMap[customerId] = true;

  try {
    if (activeDetailTab === "history") renderCustomerDetail();

    const serviceTickets = await fetchServiceTicketsForCustomer(customer);
    const complaintRows = serviceTickets.map(normalizeComplaintFromServiceTicket);
    const orderRows = serviceTickets
      .map(normalizeOrderFromServiceTicket)
      .filter(order => normalValue(order.orderId) !== "-");

    customer.complaintHistory = complaintRows;
    customer.orderHistory = orderRows;
    customer.detailDataLoaded = true;
  } catch (error) {
    console.error("Customer profile detail error:", error);
    showCustomerDetailPopup(error.message || "Unable to load customer profile details.", "error");
  } finally {
    customerDetailLoadingMap[customerId] = false;
    hideCustomerDetailLoading();
    renderCustomerDetail();
  }
}
