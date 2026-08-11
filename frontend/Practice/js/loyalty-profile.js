const LOYALTY_API_BASE_URL = window.API_BASE_URL || localStorage.getItem("omnilink_api_base") || "http://127.0.0.1:8000";

let loyaltyProfileState = {
  customer: null,
  benefits: [],
  pointTransactions: [],
  redemptions: [],
  tierHistory: []
};

function getLoyaltyHeaders() {
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${localStorage.getItem("omnilink_token") || ""}`
  };
}

function formatLoyaltyProfileApiError(result, fallback) {
  const value = result?.detail || result?.message || fallback;

  if (Array.isArray(value)) {
    return value.map(function (item) {
      if (typeof item === "string") return item;
      if (item && item.msg) return item.msg;
      return JSON.stringify(item);
    }).join("\n");
  }

  if (value && typeof value === "object") {
    return value.msg || JSON.stringify(value);
  }

  return String(value || fallback);
}

async function loyaltyGet(path) {
  const response = await fetch(`${LOYALTY_API_BASE_URL}${path}`, {
    method: "GET",
    headers: getLoyaltyHeaders()
  });

  const result = await response.json().catch(function () {
    return {};
  });

  if (!response.ok) {
    throw new Error(formatLoyaltyProfileApiError(result, `Failed: ${path}`));
  }

  return result;
}

async function loyaltyProfileGetCached(cacheKey, endpoint, ttl) {
  if (typeof cachedApiGet === "function") {
    return cachedApiGet(cacheKey, endpoint, ttl);
  }

  return loyaltyGet(endpoint);
}

function showLoyaltyPopup(message, type = "info") {
  if (window.showAppPopup) return window.showAppPopup(message, { type });
  console[type === "error" ? "error" : "log"](message);
}

function showLoyaltyLoading(message) {
  if (window.showLoadingPopup) window.showLoadingPopup(message || "Loading customer profile...");
}

function hideLoyaltyLoading() {
  if (window.hideLoadingPopup) window.hideLoadingPopup();
}

function escapeHtml(value) {
  return String(value === undefined || value === null ? "" : value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function formatNumber(value) {
  return new Intl.NumberFormat("en-IN").format(Number(value || 0));
}

function formatMoney(value) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0
  }).format(Number(value || 0));
}

function hasValue(value) {
  return value !== undefined && value !== null && value !== "";
}

function titleFromKey(key) {
  return String(key || "")
    .replaceAll("_", " ")
    .replaceAll("-", " ")
    .replace(/\b\w/g, function (char) {
      return char.toUpperCase();
    });
}

function normalizeList(result, key) {
  if (Array.isArray(result)) return result;
  if (Array.isArray(result?.[key])) return result[key];
  if (Array.isArray(result?.data)) return result.data;
  if (Array.isArray(result?.items)) return result.items;
  if (Array.isArray(result?.results)) return result.results;
  if (Array.isArray(result?.rows)) return result.rows;
  if (Array.isArray(result?.benefits)) return result.benefits;
  return [];
}

function getCustomerId(customer) {
  return customer.customer_id || customer.crm_customer_key || customer.id || "";
}

function getCustomerName(customer) {
  return customer.customer_name || customer.name || customer.full_name || getCustomerId(customer) || "";
}

function getActualTier(customer) {
  return customer.actual_membership_tier || customer.membership_tier || customer.tier || customer.tier_name || "";
}

function getMembershipStatus(customer) {
  return customer.membership_status || customer.status || "";
}

function getChannels(customer) {
  const channels = customer.available_channels || customer.approved_channels || [];
  if (Array.isArray(channels)) return channels;
  return String(channels || "").split(",").map(function (item) {
    return item.trim();
  }).filter(Boolean);
}

function toBoolean(value) {
  if (value === true || value === 1) return true;
  if (typeof value === "string") {
    return ["true", "1", "yes", "y"].includes(value.trim().toLowerCase());
  }
  return false;
}

function isContactAllowed(customer) {
  if (toBoolean(customer.do_not_contact)) return false;
  if (customer.contact_allowed !== undefined) return toBoolean(customer.contact_allowed);
  const channels = getChannels(customer);
  return channels.length > 0;
}

function getTierClass(tier) {
  const value = String(tier || "").toLowerCase();
  if (value === "silver") return "silver";
  if (value === "gold") return "warning";
  if (value === "platinum") return "platinum";
  return "info";
}

function badge(text, className) {
  if (!hasValue(text)) return "";
  return `<span class="badge ${className || "info"}">${escapeHtml(text)}</span>`;
}

function metricCard(title, value) {
  if (!hasValue(value)) return "";
  return `<div class="card loyalty-profile-metric"><span>${escapeHtml(title)}</span><strong>${escapeHtml(value)}</strong></div>`;
}

function detailItem(key, value) {
  if (!hasValue(value)) return "";
  return `<div class="loyalty-profile-detail-item"><span>${escapeHtml(titleFromKey(key))}</span><strong>${escapeHtml(value)}</strong></div>`;
}

function getBenefitsForTier(tier) {
  return loyaltyProfileState.benefits.filter(function (benefit) {
    const benefitTier = benefit.tier_name || benefit.tier || benefit.membership_tier || "Non-member";
    return String(benefitTier).toLowerCase() === String(tier || "Non-member").toLowerCase();
  });
}

async function initLoyaltyProfilePage() {
  if (typeof guardPage === "function") guardPage("loyalty");

  const customerId = new URLSearchParams(window.location.search).get("customer_id");
  const root = document.getElementById("loyaltyProfileRoot");

  if (!customerId) {
    if (root) root.innerHTML = "";
    showLoyaltyPopup("Customer ID missing.", "error");
    return;
  }

  showLoyaltyLoading("Loading customer profile...");

  try {
    const [detailResult, benefitsResult] = await Promise.allSettled([
      loyaltyProfileGetCached(
        "loyalty-customer-" + customerId,
        `/memberships/${encodeURIComponent(customerId)}`,
        30000
      ),
      loyaltyProfileGetCached(
        "loyalty-benefits",
        "/memberships/benefits",
        600000
      )
    ]);

    if (detailResult.status !== "fulfilled") throw detailResult.reason;

    const detail = detailResult.value || {};
    loyaltyProfileState.customer = detail.data || detail.customer || detail.member || detail;
    loyaltyProfileState.pointTransactions = normalizeList(detail, "point_transactions");
    loyaltyProfileState.redemptions = normalizeList(detail, "redemptions");
    loyaltyProfileState.tierHistory = normalizeList(detail, "tier_history");
    loyaltyProfileState.benefits = benefitsResult.status === "fulfilled"
      ? normalizeList(benefitsResult.value, "benefits")
      : [];

    renderLoyaltyProfile();
  } catch (error) {
    if (root) root.innerHTML = "";
    showLoyaltyPopup(error.message || "Unable to load customer profile.", "error");
  } finally {
    hideLoyaltyLoading();
  }
}

function renderDataTable(title, rows) {
  if (!Array.isArray(rows) || !rows.length) return "";

  const columns = Object.keys(rows[0]).slice(0, 6);

  return `
    <section class="card loyalty-profile-section">
      <div class="section-title-row"><h2>${escapeHtml(title)}</h2></div>
      <div class="loyalty-profile-table-wrap">
        <table>
          <thead><tr>${columns.map(function (column) {
            return `<th>${escapeHtml(titleFromKey(column))}</th>`;
          }).join("")}</tr></thead>
          <tbody>${rows.map(function (row) {
            return `<tr>${columns.map(function (column) {
              return `<td>${escapeHtml(row[column])}</td>`;
            }).join("")}</tr>`;
          }).join("")}</tbody>
        </table>
      </div>
    </section>`;
}

function renderProfileMetrics(customer) {
  return `<div class="grid grid-4 loyalty-profile-metrics-grid">
    ${metricCard("Points Balance", formatNumber(customer.points_balance ?? customer.total_points_balance))}
    ${metricCard("Redeemable Value", hasValue(customer.redeemable_value) ? formatMoney(customer.redeemable_value) : "")}
    ${metricCard("Potential Score", hasValue(customer.potential_member_score) ? formatNumber(customer.potential_member_score) : "")}
    ${metricCard("Upgrade Score", hasValue(customer.tier_upgrade_score) ? formatNumber(customer.tier_upgrade_score) : "")}
  </div>`;
}

function renderProfileDetails(customer, tier, channels) {
  const details = [
    ["actual_membership_tier", tier],
    ["membership_status", getMembershipStatus(customer)],
    ["loyalty_segment", customer.loyalty_segment],
    ["recommended_tier", customer.recommended_tier],
    ["recommended_action", customer.recommended_action],
    ["available_channels", channels.join(", ")],
    ["points_earned", hasValue(customer.points_earned) ? formatNumber(customer.points_earned) : ""],
    ["points_redeemed", hasValue(customer.points_redeemed) ? formatNumber(customer.points_redeemed) : ""]
  ];

  const html = details.map(function ([key, value]) {
    return detailItem(key, value);
  }).join("");

  if (!html) return "";

  return `<section class="card loyalty-profile-section"><div class="section-title-row"><h2>Customer Profile</h2></div><div class="loyalty-profile-detail-grid">${html}</div></section>`;
}

function renderRecommendationReasons(customer) {
  const reasons = Array.isArray(customer.score_reasons)
    ? customer.score_reasons.filter(Boolean).join(", ")
    : customer.score_reasons;

  if (!hasValue(reasons)) return "";

  return `<section class="card loyalty-profile-section"><div class="section-title-row"><h2>Recommendation Reasons</h2></div><div class="loyalty-reason-box">${escapeHtml(reasons)}</div></section>`;
}

function renderBenefits(benefits) {
  if (!benefits.length) return "";

  return `<section class="card loyalty-profile-section"><div class="section-title-row"><h2>Current Tier Benefits</h2></div><div class="loyalty-benefit-grid">${benefits.map(function (benefit) {
    return `<div class="loyalty-benefit-card"><strong>${escapeHtml(benefit.benefit_name || benefit.name || "Benefit")}</strong></div>`;
  }).join("")}</div></section>`;
}

function renderLoyaltyProfile() {
  const customer = loyaltyProfileState.customer || {};
  const tier = getActualTier(customer);
  const channels = getChannels(customer);
  const benefits = getBenefitsForTier(tier);
  const root = document.getElementById("loyaltyProfileRoot");

  if (!root) return;

  root.innerHTML = `
    <div class="loyalty-profile-page">
      <section class="card loyalty-profile-hero">
        <button type="button" class="secondary-btn loyalty-back-btn" onclick="window.location.href='loyalty.html'">Back</button>
        <div class="loyalty-avatar">${escapeHtml(String(getCustomerName(customer)).slice(0, 1).toUpperCase())}</div>
        <div class="loyalty-profile-title">
          <h1>${escapeHtml(getCustomerName(customer))}</h1>
          <p>${escapeHtml(getCustomerId(customer))}</p>
          <div class="loyalty-profile-badges">
            ${badge(tier, getTierClass(tier))}
            ${badge(getMembershipStatus(customer), String(getMembershipStatus(customer)).toLowerCase() === "active" ? "success" : "warning")}
            ${badge(isContactAllowed(customer) ? "Contact Allowed" : "Contact Blocked", isContactAllowed(customer) ? "success" : "danger")}
          </div>
        </div>
      </section>
      ${renderProfileMetrics(customer)}
      ${renderProfileDetails(customer, tier, channels)}
      ${renderRecommendationReasons(customer)}
      ${renderBenefits(benefits)}
      ${renderDataTable("Point Transactions", loyaltyProfileState.pointTransactions)}
      ${renderDataTable("Redemptions", loyaltyProfileState.redemptions)}
      ${renderDataTable("Tier History", loyaltyProfileState.tierHistory)}
    </div>`;
}

document.addEventListener("DOMContentLoaded", initLoyaltyProfilePage);
