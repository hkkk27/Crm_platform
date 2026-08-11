const LOYALTY_API_BASE_URL = window.API_BASE_URL || localStorage.getItem("omnilink_api_base") || "http://127.0.0.1:8000";

/* Integrated frontend session cache for Loyalty page only */
const loyaltyApiMemoryCache = new Map();

function getLoyaltyCachedData(key, ttlMilliseconds) {
  const memoryItem = loyaltyApiMemoryCache.get(key);

  if (memoryItem && Date.now() - memoryItem.savedAt < ttlMilliseconds) {
    return memoryItem.value;
  }

  const stored = sessionStorage.getItem("omnilink_api_cache_" + key);

  if (!stored) {
    return null;
  }

  try {
    const parsed = JSON.parse(stored);

    if (Date.now() - parsed.savedAt >= ttlMilliseconds) {
      sessionStorage.removeItem("omnilink_api_cache_" + key);
      loyaltyApiMemoryCache.delete(key);
      return null;
    }

    loyaltyApiMemoryCache.set(key, parsed);
    return parsed.value;
  } catch (error) {
    sessionStorage.removeItem("omnilink_api_cache_" + key);
    loyaltyApiMemoryCache.delete(key);
    return null;
  }
}

function setLoyaltyCachedData(key, value) {
  const item = {
    value: value,
    savedAt: Date.now()
  };

  loyaltyApiMemoryCache.set(key, item);
  sessionStorage.setItem("omnilink_api_cache_" + key, JSON.stringify(item));
}

function clearLoyaltyCachedData(key) {
  loyaltyApiMemoryCache.delete(key);
  sessionStorage.removeItem("omnilink_api_cache_" + key);
}

function clearLoyaltyCachedPrefix(prefix) {
  for (const key of loyaltyApiMemoryCache.keys()) {
    if (key.startsWith(prefix)) {
      loyaltyApiMemoryCache.delete(key);
    }
  }

  const keysToRemove = [];

  for (let index = 0; index < sessionStorage.length; index += 1) {
    const storageKey = sessionStorage.key(index);

    if (storageKey && storageKey.startsWith("omnilink_api_cache_" + prefix)) {
      keysToRemove.push(storageKey);
    }
  }

  keysToRemove.forEach(function (key) {
    sessionStorage.removeItem(key);
  });
}

let loyaltyState = {
  summary: {},
  customers: [],
  rules: [],
  benefits: [],
  segments: [],
  potentialMembers: [],
  upgradeRecommendations: [],
  selectedCustomer: null,
  pointTransactions: [],
  redemptions: [],
  tierHistory: []
};

let loyaltyFilters = { search: "", tier: "All", status: "All", recommendation: "All" };
let loyaltyPage = 1;
const loyaltyPageSize = 8;
let loyaltyPageLoading = false;
let loyaltyPageLoaded = false;

function getLoyaltyHeaders() {
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${localStorage.getItem("omnilink_token") || ""}`
  };
}

function formatLoyaltyApiError(result, fallback) {
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
    throw new Error(formatLoyaltyApiError(result, `Failed: ${path}`));
  }

  return result;
}

async function loyaltyCachedGet(cacheKey, path, ttlMilliseconds) {
  const cached = getLoyaltyCachedData(cacheKey, ttlMilliseconds);

  if (cached !== null) {
    return cached;
  }

  const result = await loyaltyGet(path);
  setLoyaltyCachedData(cacheKey, result);
  return result;
}

function showLoyaltyPopup(message, type = "info") {
  if (window.showAppPopup) return window.showAppPopup(message, { type });
  console[type === "error" ? "error" : "log"](message);
}

function showLoyaltyLoading(message) {
  if (window.showLoadingPopup) window.showLoadingPopup(message || "Loading loyalty data...");
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

function normalizeList(result) {
  if (Array.isArray(result)) return result;
  if (Array.isArray(result.data)) return result.data;
  if (Array.isArray(result.customers)) return result.customers;
  if (Array.isArray(result.results)) return result.results;
  if (Array.isArray(result.items)) return result.items;
  if (Array.isArray(result.memberships)) return result.memberships;
  if (Array.isArray(result.members)) return result.members;
  if (Array.isArray(result.rows)) return result.rows;
  return [];
}

function getLoyaltyCacheConfig(key, path) {
  if (key === "summary") {
    return { cacheKey: "loyalty-summary", ttl: 60000 };
  }

  if (key === "customers") {
    return { cacheKey: "loyalty-customers-preview", ttl: 60000 };
  }

  if (key === "rules") {
    return { cacheKey: "loyalty-rules", ttl: 600000 };
  }

  if (key === "benefits") {
    return { cacheKey: "loyalty-benefits", ttl: 600000 };
  }

  if (key === "potentialMembers") {
    return { cacheKey: "loyalty-potential-members-preview", ttl: 60000 };
  }

  return {
    cacheKey: "loyalty-" + key + "-" + path,
    ttl: 60000
  };
}

async function loadLoyaltyPart(key, path) {
  try {
    const cacheConfig = getLoyaltyCacheConfig(key, path);
    const result = await loyaltyCachedGet(cacheConfig.cacheKey, path, cacheConfig.ttl);

    if (key === "summary") {
      loyaltyState.summary = result.summary || result.data || result || {};

      if (Array.isArray(result.tier_distribution)) {
        loyaltyState.summary.tier_distribution = result.tier_distribution;
      }
    }

    if (key === "customers") loyaltyState.customers = normalizeList(result);
    if (key === "rules") loyaltyState.rules = normalizeList(result);
    if (key === "benefits") loyaltyState.benefits = normalizeList(result);
    if (key === "potentialMembers") loyaltyState.potentialMembers = normalizeList(result);

    return null;
  } catch (error) {
    console.error(`Loyalty ${key} error:`, error);
    return key;
  }
}

async function initLoyaltyPage() {
  if (typeof guardPage === "function") guardPage("loyalty");

  if (loyaltyPageLoading) return;

  if (loyaltyPageLoaded) {
    renderLoyalty();
    return;
  }

  loyaltyPageLoading = true;
  renderLoyalty();
  showLoyaltyLoading("Loading loyalty data...");

  try {
    const failed = await Promise.all([
      loadLoyaltyPart("summary", "/memberships/summary"),
      loadLoyaltyPart("customers", "/memberships?page=1&page_size=50"),
      loadLoyaltyPart("rules", "/memberships/rules"),
      loadLoyaltyPart("benefits", "/memberships/benefits"),
      loadLoyaltyPart("potentialMembers", "/memberships/segments/potential-members?page=1&page_size=8")
    ]);

    loyaltyState.segments = buildPreviewLoyaltySegments(loyaltyState.customers);
    loyaltyState.upgradeRecommendations = buildUpgradePreview(loyaltyState.customers);
    renderLoyalty();

    const failedParts = failed.filter(Boolean);

    if (failedParts.length) {
      showLoyaltyPopup(`Some loyalty data could not be loaded: ${failedParts.join(", ")}`, "error");
    }
  } catch (error) {
    console.error("Loyalty page error:", error);
    showLoyaltyPopup(error.message || "Unable to load loyalty data", "error");
  } finally {
    loyaltyPageLoading = false;
    loyaltyPageLoaded = true;
    hideLoyaltyLoading();
  }
}

function getTierClass(tier) {
  const value = String(tier || "").toLowerCase();
  if (value === "silver") return "silver";
  if (value === "gold") return "warning";
  if (value === "platinum") return "platinum";
  return "info";
}

function badge(text, className) {
  return `<span class="badge ${className || "info"}">${escapeHtml(text || "-")}</span>`;
}

function statCard(title, value) {
  return `<div class="card loyalty-stat"><div class="stat-title">${escapeHtml(title)}</div><div class="stat-value">${escapeHtml(value)}</div></div>`;
}

function getCustomerId(customer) {
  return customer.customer_id || customer.crm_customer_key || customer.id || "";
}

function getCustomerName(customer) {
  return customer.customer_name || customer.name || customer.full_name || getCustomerId(customer) || "Customer";
}

function getActualTier(customer) {
  return customer.actual_membership_tier || customer.membership_tier || customer.tier || customer.tier_name || "Non-member";
}

function getMembershipStatus(customer) {
  return customer.membership_status || customer.status || "-";
}

function getChannels(customer) {
  const channels = customer.available_channels || customer.approved_channels || [];
  return Array.isArray(channels) ? channels.join(", ") : channels || "-";
}

function toBoolean(value) {
  if (value === true || value === 1) return true;
  if (typeof value === "string") return ["true", "1", "yes", "y"].includes(value.trim().toLowerCase());
  return false;
}

function isContactAllowed(customer) {
  if (toBoolean(customer.do_not_contact)) return false;
  if (customer.contact_allowed !== undefined) return toBoolean(customer.contact_allowed);
  const channels = customer.available_channels || customer.approved_channels || [];
  return Array.isArray(channels) && channels.length > 0;
}

function renderLoyaltySummary() {
  const s = loyaltyState.summary || {};
  const totalPointsBalance = s.total_points_balance ?? s.current_points_balance ?? s.points_balance ?? 0;
  const activeMembers = s.active_members ?? s.members ?? 0;

  return `<div class="grid grid-4 loyalty-stats-grid">
    ${statCard("Total Customers", formatNumber(s.total_customers))}
    ${statCard("Active Members", formatNumber(activeMembers))}
    ${statCard("Non-members", formatNumber(s.non_members))}
    ${statCard("Potential Members", formatNumber(s.potential_members))}
    ${statCard("Upgrade Recommended", formatNumber(s.upgrade_recommended))}
    ${statCard("Contactable", formatNumber(s.contactable_recommendations))}
    ${statCard("Points Balance", formatNumber(totalPointsBalance))}
    ${statCard("Outstanding Value", formatMoney(s.outstanding_points_value))}
  </div>`;
}

function getTierDistribution() {
  const dist = loyaltyState.summary.tier_distribution || loyaltyState.summary.tierDistribution || [];
  if (Array.isArray(dist) && dist.length) return dist;
  return [];
}

function renderTierDistribution() {
  const distribution = getTierDistribution();
  if (!distribution.length) return "";

  return `<div class="grid grid-4 tier-grid">${distribution.map(function (item) {
    const tier = item.tier || item.label || item.membership_tier || item.tier_name || "Non-member";
    const count = item.count || item.value || item.customers || 0;
    return `<div class="card tier-card ${getTierClass(tier)}-outline"><div class="tier-title-row"><h3>${escapeHtml(tier)}</h3>${badge(count, getTierClass(tier))}</div><div class="tier-metric">${formatNumber(count)}</div></div>`;
  }).join("")}</div>`;
}

function memberLine(customer) {
  return `<div class="upgrade-member"><div><strong>${escapeHtml(getCustomerName(customer))}</strong><span>${escapeHtml(getCustomerId(customer))}</span></div><small>${escapeHtml(customer.recommended_tier || getActualTier(customer))}</small></div>`;
}

function buildPreviewLoyaltySegments(customers) {
  const segmentMap = {};

  (customers || []).forEach(function (customer) {
    const name = customer.loyalty_segment || "Unclassified";

    if (!segmentMap[name]) {
      segmentMap[name] = {
        segment_name: name,
        customer_count: 0,
        contactable_count: 0,
        recommended_action: customer.recommended_action || ""
      };
    }

    segmentMap[name].customer_count += 1;

    if (isContactAllowed(customer)) {
      segmentMap[name].contactable_count += 1;
    }
  });

  return Object.values(segmentMap);
}

function buildUpgradePreview(customers) {
  return (customers || [])
    .filter(function (customer) {
      return Boolean(customer.recommendation_flag) && ["Silver", "Gold"].includes(getActualTier(customer));
    })
    .sort(function (first, second) {
      return Number(second.tier_upgrade_score || 0) - Number(first.tier_upgrade_score || 0);
    })
    .slice(0, 8);
}

function renderRecommendations() {
  const potential = loyaltyState.potentialMembers.slice(0, 4);
  const upgrades = loyaltyState.upgradeRecommendations.slice(0, 4);
  const allRecommended = [...loyaltyState.potentialMembers, ...loyaltyState.upgradeRecommendations];
  const seenIds = new Set();

  const contactable = allRecommended.filter(function (customer) {
    const customerId = String(getCustomerId(customer));

    if (!customerId || seenIds.has(customerId) || !isContactAllowed(customer)) {
      return false;
    }

    seenIds.add(customerId);
    return true;
  }).slice(0, 4);

  const cards = [
    ["Potential Members", potential],
    ["Upgrade Recommendations", upgrades],
    ["Contactable Recommendations", contactable]
  ];

  return `<div class="grid grid-3 loyalty-upgrade-grid">${cards.map(function ([title, rows]) {
    return `<div class="card upgrade-card"><div class="upgrade-head"><div><h3>${escapeHtml(title)}</h3></div>${badge(rows.length, rows.length ? "success" : "info")}</div><div class="upgrade-members">${rows.length ? rows.map(memberLine).join("") : ""}</div></div>`;
  }).join("")}</div>`;
}

function renderSegments() {
  if (!loyaltyState.segments.length) return "";

  return `<div class="grid grid-4 tier-grid">${loyaltyState.segments.map(function (segment) {
    const name = segment.segment_name || segment.name || segment.loyalty_segment || segment.label || "Segment";
    const count = segment.customer_count || segment.count || segment.value || 0;
    return `<div class="card tier-card"><div class="tier-title-row"><h3>${escapeHtml(name)}</h3>${badge(count, "info")}</div><div class="tier-metric">${formatNumber(count)}</div></div>`;
  }).join("")}</div>`;
}

function renderBenefits() {
  const groups = loyaltyState.benefits.reduce(function (accumulator, benefit) {
    const tier = benefit.tier_name || benefit.tier || benefit.membership_tier || "Non-member";
    accumulator[tier] = accumulator[tier] || [];
    accumulator[tier].push(benefit);
    return accumulator;
  }, {});

  const tiers = ["Non-member", "Silver", "Gold", "Platinum"];

  return `<div class="grid grid-4 tier-grid">${tiers.map(function (tier) {
    const benefits = groups[tier] || [];
    return `<div class="card tier-card ${getTierClass(tier)}-outline"><div class="tier-title-row"><h3>${escapeHtml(tier)}</h3>${badge(benefits.length, getTierClass(tier))}</div><div class="upgrade-members">${benefits.length ? benefits.slice(0, 5).map(function (benefit) {
      return `<div class="upgrade-member"><strong>${escapeHtml(benefit.benefit_name || benefit.name || "Benefit")}</strong></div>`;
    }).join("") : ""}</div></div>`;
  }).join("")}</div>`;
}

function renderFilters() {
  return `<div class="loyalty-tools card"><input id="loyaltySearch" type="search" placeholder="Search customer, ID, segment, tier..." value="${escapeHtml(loyaltyFilters.search)}"><select id="tierFilter"><option>All</option><option>Non-member</option><option>Silver</option><option>Gold</option><option>Platinum</option></select><select id="statusFilter"><option>All</option><option>Active</option><option>Inactive</option><option>Potential</option></select><select id="recommendationFilter"><option>All</option><option>Recommended</option><option>Contact Allowed</option><option>Contact Blocked</option></select></div>`;
}

function filteredCustomers() {
  const query = loyaltyFilters.search.trim().toLowerCase();

  return loyaltyState.customers.filter(function (customer) {
    const text = [
      getCustomerId(customer),
      getCustomerName(customer),
      getActualTier(customer),
      getMembershipStatus(customer),
      customer.loyalty_segment,
      customer.recommended_tier,
      customer.recommended_action
    ].join(" ").toLowerCase();

    return (!query || text.includes(query))
      && (loyaltyFilters.tier === "All" || String(getActualTier(customer)).toLowerCase() === loyaltyFilters.tier.toLowerCase())
      && (loyaltyFilters.status === "All" || String(getMembershipStatus(customer)).toLowerCase() === loyaltyFilters.status.toLowerCase())
      && (loyaltyFilters.recommendation === "All"
        || (loyaltyFilters.recommendation === "Recommended" && customer.recommendation_flag)
        || (loyaltyFilters.recommendation === "Contact Allowed" && isContactAllowed(customer))
        || (loyaltyFilters.recommendation === "Contact Blocked" && !isContactAllowed(customer)));
  });
}

function renderPagination(totalRows) {
  const totalPages = Math.max(1, Math.ceil(totalRows / loyaltyPageSize));

  if (loyaltyPage > totalPages) loyaltyPage = totalPages;

  const start = totalRows ? (loyaltyPage - 1) * loyaltyPageSize + 1 : 0;
  const end = Math.min(loyaltyPage * loyaltyPageSize, totalRows);

  return `<div class="loyalty-pagination"><span>${start}-${end} of ${totalRows}</span><div class="pagination-actions"><button type="button" id="prevPage" class="secondary-btn" ${loyaltyPage === 1 ? "disabled" : ""}>Prev</button><span class="page-pill">${loyaltyPage} / ${totalPages}</span><button type="button" id="nextPage" class="secondary-btn" ${loyaltyPage === totalPages ? "disabled" : ""}>Next</button></div></div>`;
}

function renderCustomersTable() {
  const rows = filteredCustomers();
  const totalPages = Math.max(1, Math.ceil(rows.length / loyaltyPageSize));

  if (loyaltyPage > totalPages) loyaltyPage = totalPages;

  const pageRows = rows.slice((loyaltyPage - 1) * loyaltyPageSize, loyaltyPage * loyaltyPageSize);

  return `${renderFilters()}<div class="table-card loyalty-table-card">${pageRows.length ? `<table><thead><tr><th>Customer</th><th>Actual Tier</th><th>Membership Status</th><th>Points Balance</th><th>Redeemable Value</th><th>Potential Member Score</th><th>Internal Upgrade Score</th><th>Loyalty Segment</th><th>Recommended Tier</th><th>Recommended Action</th><th>Contact Allowed</th><th>Available Channels</th><th>Action</th></tr></thead><tbody>${pageRows.map(function (customer) {
    return `<tr><td><strong>${escapeHtml(getCustomerName(customer))}</strong><span class="customer-id">${escapeHtml(getCustomerId(customer))}</span></td><td>${badge(getActualTier(customer), getTierClass(getActualTier(customer)))}</td><td>${badge(getMembershipStatus(customer), String(getMembershipStatus(customer)).toLowerCase() === "active" ? "success" : "warning")}</td><td>${formatNumber(customer.points_balance)}</td><td>${formatMoney(customer.redeemable_value)}</td><td>${formatNumber(customer.potential_member_score)}</td><td>${formatNumber(customer.tier_upgrade_score)}</td><td>${escapeHtml(customer.loyalty_segment || "-")}</td><td>${badge(customer.recommended_tier || "-", getTierClass(customer.recommended_tier))}</td><td>${escapeHtml(customer.recommended_action || "-")}</td><td>${isContactAllowed(customer) ? badge("Allowed", "success") : badge("Blocked", "danger")}</td><td>${escapeHtml(getChannels(customer))}</td><td><button class="secondary-btn" type="button" onclick="openLoyaltyCustomer('${escapeHtml(getCustomerId(customer))}')">View</button></td></tr>`;
  }).join("")}</tbody></table>${renderPagination(rows.length)}` : ""}</div>`;
}

function attachLoyaltyEvents() {
  [["loyaltySearch", "search", "input"], ["tierFilter", "tier", "change"], ["statusFilter", "status", "change"], ["recommendationFilter", "recommendation", "change"]].forEach(function ([id, key, event]) {
    const element = document.getElementById(id);
    if (!element) return;

    element.value = loyaltyFilters[key];
    element.addEventListener(event, function (eventObject) {
      loyaltyFilters[key] = eventObject.target.value;
      loyaltyPage = 1;
      renderLoyalty();
    });
  });

  const prev = document.getElementById("prevPage");
  const next = document.getElementById("nextPage");

  if (prev) {
    prev.addEventListener("click", function () {
      if (loyaltyPage > 1) {
        loyaltyPage -= 1;
        renderLoyalty();
      }
    });
  }

  if (next) {
    next.addEventListener("click", function () {
      loyaltyPage += 1;
      renderLoyalty();
    });
  }
}

function openLoyaltyCustomer(customerId) {
  if (!customerId) return;
  window.location.href = `loyalty-profile.html?customer_id=${encodeURIComponent(customerId)}`;
}

function closeLoyaltyDetail() {
  loyaltyState.selectedCustomer = null;
  loyaltyState.pointTransactions = [];
  loyaltyState.redemptions = [];
  loyaltyState.tierHistory = [];
  renderLoyalty();
}

function detailRows(title, rows) {
  if (!rows.length) return "";

  return `<div class="card loyalty-table-card"><div class="section-title-row"><h2>${escapeHtml(title)}</h2></div><table><tbody>${rows.map(function (row) {
    return `<tr>${Object.values(row).slice(0, 6).map(function (value) { return `<td>${escapeHtml(value)}</td>`; }).join("")}</tr>`;
  }).join("")}</tbody></table></div>`;
}

function renderCustomerDetail() {
  const customer = loyaltyState.selectedCustomer;
  if (!customer) return "";

  return `<section class="loyalty-section"><div class="section-title-row"><h2>Customer Loyalty Detail</h2><button class="secondary-btn" type="button" onclick="closeLoyaltyDetail()">Close</button></div><div class="grid grid-4 loyalty-stats-grid">${statCard("Current Tier", getActualTier(customer))}${statCard("Points Balance", formatNumber(customer.points_balance))}${statCard("Redeemable Value", formatMoney(customer.redeemable_value))}${statCard("Recommended Tier", customer.recommended_tier || "-")}</div>${detailRows("Point Transactions", loyaltyState.pointTransactions)}${detailRows("Redemptions", loyaltyState.redemptions)}${detailRows("Tier History", loyaltyState.tierHistory)}</section>`;
}

function renderLoyalty() {
  const root = document.getElementById("loyalty");
  if (!root) return;

  root.innerHTML = `<div class="loyalty-page">${renderLoyaltySummary()}<section class="loyalty-section"><div class="section-title-row"><h2>Tier Distribution</h2></div>${renderTierDistribution()}</section><section class="loyalty-section"><div class="section-title-row"><h2>Recommendations</h2></div>${renderRecommendations()}</section><section class="loyalty-section"><div class="section-title-row"><h2>Loyalty Segment Preview</h2></div>${renderSegments()}</section><section class="loyalty-section"><div class="section-title-row"><h2>Tier Benefits</h2></div>${renderBenefits()}</section><section class="loyalty-section"><div class="section-title-row"><h2>Customer and Member Preview</h2></div>${renderCustomersTable()}</section>${renderCustomerDetail()}</div>`;
  attachLoyaltyEvents();
}

document.addEventListener("DOMContentLoaded", initLoyaltyPage);
