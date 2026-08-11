let selectedCustomerId = "1";
let customers = [];

let currentCustomerPage = 1;
const customersPerPage = 10;

const API_BASE_URL = "http://127.0.0.1:8000";

function showCustomerPopup(message, type = "info") {
  if (window.showAppPopup) {
    return window.showAppPopup(message, { type });
  }
  console[type === "error" ? "error" : "log"](message);
  return Promise.resolve();
}

function showCustomerPopupLoading(message) {
  if (window.showLoadingPopup) {
    window.showLoadingPopup(message || "Loading customers...");
  }
}

function hideCustomerPopupLoading() {
  if (window.hideLoadingPopup) {
    window.hideLoadingPopup();
  }
}

/* ---------------------------------------------
   Auth helper
--------------------------------------------- */

function getAuthToken() {
  const directToken =
    localStorage.getItem("omnilink_token") ||
    localStorage.getItem("token");

  if (directToken) {
    return directToken;
  }

  const crmSession = localStorage.getItem("crm_session");

  if (crmSession) {
    try {
      const session = JSON.parse(crmSession);
      return session.token || session.access_token || null;
    } catch (error) {
      console.warn("Invalid CRM session found in localStorage.");
      return null;
    }
  }

  return null;
}

function getAuthHeaders() {
  const token = getAuthToken();

  const headers = {
    "Content-Type": "application/json"
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  return headers;
}

/* ---------------------------------------------
   Load customers from backend
--------------------------------------------- */

async function loadCustomersFromBackend() {
  showCustomerPopupLoading("Loading customers...");

  try {
    const token = getAuthToken();

    if (!token) {
      throw new Error("Login token missing. Please login again.");
    }

    const response = await fetch(`${API_BASE_URL}/customers`, {
      method: "GET",
      headers: getAuthHeaders()
    });

    const result = await response.json().catch(() => ({}));

    if (!response.ok) {
      throw new Error(
        result.detail ||
        result.message ||
        "Failed to load customers."
      );
    }

    const customerData = Array.isArray(result)
      ? result
      : result.data || result.customers || [];

    customers = customerData.map(normalizeCustomerData);
    filterCustomers();
  } catch (error) {
    console.error("Customer API error:", error);

    const customerRows = document.getElementById("customerRows");
    if (customerRows) {
      customerRows.innerHTML = "";
    }

    showCustomerPopup(error.message || "Unable to load customer data.", "error");
  } finally {
    hideCustomerPopupLoading();
  }
}

/* ---------------------------------------------
   Loading state
--------------------------------------------- */

function showCustomerLoading() {
  showCustomerPopupLoading("Loading customers...");
}

/* ---------------------------------------------
   Boolean helper
--------------------------------------------- */

function toBoolean(value) {
  if (value === true || value === 1 || value === "1") return true;
  if (value === "true" || value === "yes" || value === "Yes") return true;
  return false;
}

/* ---------------------------------------------
   Normalize backend customer list data
--------------------------------------------- */

function normalizeCustomerData(c) {
  return {
    id: String(c.customer_id || c.id || "-"),

    name:
      c.customer_name ||
      c.name ||
      "-",

    phone:
      c.phone_number ||
      c.masked_phone_number ||
      c.phone ||
      "-",

    email:
      c.email ||
      c.masked_email ||
      "-",

    city:
      c.customer_city ||
      c.city ||
      "-",

    state:
      c.customer_state ||
      c.state ||
      "-",

    birthdayMonth:
      c.birthday_month ||
      c.birthdayMonth ||
      "-",

    tier:
      c.membership_tier ||
      c.tier ||
      "Non-member",

    status:
      c.membership_status ||
      c.status ||
      "Non-member",

    membershipExpiry:
      c.membership_expiry_date ||
      c.membershipExpiry ||
      "-",

    upgradeEligibility:
      c.upgrade_eligibility ||
      c.upgradeEligibility ||
      "-",

    birthdayVoucher:
      c.birthday_voucher ||
      c.birthdayVoucher ||
      "-",

    tierBenefits:
      c.tier_benefits ||
      c.tierBenefits ||
      [],

    totalSpend: Number(
      c.total_sales ||
      c.total_spend ||
      c.totalSpend ||
      0
    ),

    aov: Number(
      c.average_order_value ||
      c.avg_transaction_value ||
      c.aov ||
      0
    ),

    frequency:
      c.purchase_frequency ||
      c.frequency ||
      "-",

    lastPurchase:
      c.last_purchase_date ||
      c.lastPurchase ||
      "-",

    preferredCategory:
      c.preferred_category ||
      c.product_category ||
      c.preferredCategory ||
      "-",

    points: Number(
      c.points_balance ||
      c.reward_points ||
      c.points ||
      0
    ),

    pointsEarned: Number(
      c.points_earned ||
      c.pointsEarned ||
      0
    ),

    pointsRedeemed: Number(
      c.points_redeemed ||
      c.pointsRedeemed ||
      0
    ),

    segment:
      c.customer_segment ||
      c.segment ||
      c.primary_segment ||
      "General Customer",

    segments:
      c.segments ||
      [],

    churnRisk:
      c.churn_risk_level ||
      c.churnRisk ||
      "Unknown",

    potentialScore: Number(
      c.potential_member_score ||
      c.potentialScore ||
      0
    ),

    estimatedClv: Number(
      c.estimated_clv ||
      c.estimatedClv ||
      0
    ),

    doNotContact:
      toBoolean(
        c.do_not_contact_status ||
        c.do_not_contact ||
        c.doNotContact
      ),

    consent: {
      whatsapp: toBoolean(c.whatsapp_consent || c.consent?.whatsapp),
      sms: toBoolean(c.sms_consent || c.consent?.sms),
      email: toBoolean(c.email_consent || c.consent?.email),
      app: toBoolean(c.app_notification_consent || c.consent?.app),
      personalization: toBoolean(
        c.personalization_consent ||
        c.consent?.personalization
      ),
      consentGivenDate:
        c.consent_given_date ||
        c.consent?.consentGivenDate ||
        "-",
      consentSource:
        c.consent_source ||
        c.consent?.consentSource ||
        "-",
      consentWithdrawnDate:
        c.consent_withdrawn_date ||
        c.consent?.consentWithdrawnDate ||
        "-"
    },

    campaignHistory:
      c.campaign_history ||
      c.campaignHistory ||
      [],

    complaintHistory:
      c.complaint_history ||
      c.complaintHistory ||
      []
  };
}

/* ---------------------------------------------
   Consent helpers
--------------------------------------------- */

function getAllowedChannels(customer) {
  if (!customer.consent) return [];

  const channels = [];

  if (customer.consent.whatsapp) channels.push("WhatsApp");
  if (customer.consent.sms) channels.push("SMS");
  if (customer.consent.email) channels.push("Email");
  if (customer.consent.app) channels.push("App");

  return channels;
}

function getConsentStatus(customer) {
  if (customer.doNotContact) {
    return badge("Do Not Contact", "danger");
  }

  const allowedChannels = getAllowedChannels(customer);

  if (allowedChannels.length === 0) {
    return badge("No Consent", "danger");
  }

  return badge(`Allowed: ${allowedChannels.join(", ")}`, "success");
}

/* ---------------------------------------------
   Tier badge
--------------------------------------------- */

function getTierBadge(tier) {
  if (tier === "Gold" || tier === "Platinum") {
    return badge(tier, "success");
  }

  if (tier === "Non-member") {
    return badge(tier, "warning");
  }

  return badge(tier || "Unknown", "info");
}

/* ---------------------------------------------
   Search filter
--------------------------------------------- */

function getFilteredCustomers() {
  const searchInput = document.getElementById("customerSearch");
  const query = searchInput ? searchInput.value.toLowerCase().trim() : "";

  return customers.filter((c) => {
    const searchableText = `
      ${c.name}
      ${c.id}
      ${c.phone}
      ${c.email}
      ${c.city}
      ${c.state}
      ${c.tier}
      ${c.status}
      ${c.segment}
      ${c.preferredCategory}
      ${c.churnRisk}
      ${c.segments ? c.segments.join(" ") : ""}
    `.toLowerCase();

    return searchableText.includes(query);
  });
}

/* ---------------------------------------------
   Pagination - Customer List
   Shows only: Prev 1 2 3 Next
--------------------------------------------- */

function renderCustomerPagination(totalCustomers) {
  let pagination = document.getElementById("customerPagination");

  if (!pagination) {
    pagination = document.createElement("div");
    pagination.id = "customerPagination";
    pagination.className = "customer-pagination";

    const tableCard = document.querySelector("#customers .table-card");

    if (tableCard) {
      tableCard.insertAdjacentElement("afterend", pagination);
    }
  }

  const totalPages = Math.ceil(totalCustomers / customersPerPage);

  pagination.innerHTML = "";

  if (totalPages <= 1) {
    return;
  }

  if (currentCustomerPage > totalPages) {
    currentCustomerPage = totalPages;
  }

  const startRecord = (currentCustomerPage - 1) * customersPerPage + 1;
  const endRecord = Math.min(
    currentCustomerPage * customersPerPage,
    totalCustomers
  );

  const paginationInfo = document.createElement("div");
  paginationInfo.className = "pagination-info";
  paginationInfo.textContent = `Showing ${startRecord}-${endRecord} of ${totalCustomers} customers`;

  const paginationButtons = document.createElement("div");
  paginationButtons.className = "pagination-buttons";

  const prevButton = document.createElement("button");
  prevButton.className = "page-btn page-nav-btn";
  prevButton.textContent = "Prev";
  prevButton.disabled = currentCustomerPage === 1;
  prevButton.onclick = function () {
    goToCustomerPage(currentCustomerPage - 1);
  };

  paginationButtons.appendChild(prevButton);

  const visiblePages = getVisibleCustomerPages(currentCustomerPage, totalPages);

  visiblePages.forEach(function (page) {
    const pageButton = document.createElement("button");
    pageButton.className =
      "page-btn" + (page === currentCustomerPage ? " active" : "");
    pageButton.textContent = page;
    pageButton.onclick = function () {
      goToCustomerPage(page);
    };

    paginationButtons.appendChild(pageButton);
  });

  const nextButton = document.createElement("button");
  nextButton.className = "page-btn page-nav-btn";
  nextButton.textContent = "Next";
  nextButton.disabled = currentCustomerPage === totalPages;
  nextButton.onclick = function () {
    goToCustomerPage(currentCustomerPage + 1);
  };

  paginationButtons.appendChild(nextButton);

  pagination.appendChild(paginationInfo);
  pagination.appendChild(paginationButtons);
}

function getVisibleCustomerPages(currentPage, totalPages) {
  if (totalPages <= 3) {
    return Array.from({ length: totalPages }, function (_, index) {
      return index + 1;
    });
  }

  if (currentPage === 1) {
    return [1, 2, 3];
  }

  if (currentPage === totalPages) {
    return [totalPages - 2, totalPages - 1, totalPages];
  }

  return [currentPage - 1, currentPage, currentPage + 1];
}

function goToCustomerPage(pageNumber) {
  const filteredCustomers = getFilteredCustomers();
  const totalPages = Math.ceil(filteredCustomers.length / customersPerPage);

  if (pageNumber < 1 || pageNumber > totalPages) {
    return;
  }

  currentCustomerPage = pageNumber;
  filterCustomers(false);
}

/* ---------------------------------------------
   Render customer table
--------------------------------------------- */

function filterCustomers(resetPage = true) {
  if (resetPage) {
    currentCustomerPage = 1;
  }

  const filteredCustomers = getFilteredCustomers();

  const startIndex = (currentCustomerPage - 1) * customersPerPage;
  const endIndex = startIndex + customersPerPage;
  const paginatedCustomers = filteredCustomers.slice(startIndex, endIndex);

  const rows = paginatedCustomers
    .map((c) => {
      return `
        <tr>
          <td>
            <strong>${c.name}</strong>
            <div class="muted-text">${c.id} · ${c.phone}</div>
          </td>

          <td>${getTierBadge(c.tier)}</td>

          <td>
            <strong>${money(c.totalSpend)}</strong>
            <div class="muted-text">CLV: ${money(c.estimatedClv)}</div>
          </td>

          <td>
            <span class="badge info">${c.segment}</span>
            <div class="muted-text">Risk: ${c.churnRisk}</div>
          </td>

          <td>${getConsentStatus(c)}</td>

          <td>
            <button class="secondary-btn" onclick="openCustomer('${c.id}')">
              View
            </button>
          </td>
        </tr>
      `;
    })
    .join("");

  const customerRows = document.getElementById("customerRows");

  if (customerRows) {
    customerRows.innerHTML =
      rows || `
        <tr>
          <td colspan="6" class="empty-state">
            No customers found.
          </td>
        </tr>
      `;
  }

  renderCustomerPagination(filteredCustomers.length);
}