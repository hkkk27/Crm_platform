const ADMIN_API_BASE_URL = window.API_BASE_URL || localStorage.getItem("omnilink_api_base") || "http://127.0.0.1:8000";

let adminSelectedDate = "";

const adminState = {
  users: { page: 1, size: 10, total: 0, items: [] },
  agents: { page: 1, size: 10, total: 0, items: [] },
  campaigns: { page: 1, size: 10, total: 0, items: [] },
  passwordResets: { page: 1, size: 10, total: 0, items: [] },
  dataHealth: []
};

function adminHeaders() {
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${localStorage.getItem("omnilink_token") || ""}`
  };
}

function escapeHtml(value) {
  return String(value === undefined || value === null ? "" : value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function normalValue(value) {
  return value === undefined || value === null || value === "" ? "-" : value;
}

function titleFromKey(key) {
  return String(key || "")
    .replaceAll("_", " ")
    .replaceAll("-", " ")
    .replace(/\b\w/g, char => char.toUpperCase());
}

function pick(row, keys) {
  for (const key of keys) {
    if (row && row[key] !== undefined && row[key] !== null) return row[key];
  }
  return "";
}

function formatAdminApiError(result, fallback) {
  const value = result?.detail || result?.message || fallback;

  if (Array.isArray(value)) {
    return value.map(item => {
      if (typeof item === "string") return item;
      if (item?.msg) return item.msg;
      return JSON.stringify(item);
    }).join("\n");
  }

  if (value && typeof value === "object") {
    if (value.msg) return value.msg;
    return JSON.stringify(value);
  }

  return String(value || fallback);
}

async function adminGet(path) {
  const response = await fetch(`${ADMIN_API_BASE_URL}${path}`, {
    method: "GET",
    headers: adminHeaders()
  });

  const result = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(formatAdminApiError(result, `Admin request failed: ${path}`));
  }

  return result;
}

async function adminGetCached(cacheKey, endpoint, ttlMilliseconds) {
  if (typeof cachedApiGet === "function") {
    return cachedApiGet(cacheKey, endpoint, ttlMilliseconds);
  }

  return adminGet(endpoint);
}


function showAdminError(message) {
  if (window.showAppPopup) {
    window.showAppPopup(message, { type: "error" });
    return;
  }
  console.error(message);
}

function startAdminLoading(message) {
  if (window.showLoadingPopup) {
    window.showLoadingPopup(message);
  }
}

function stopAdminLoading() {
  if (window.hideLoadingPopup) {
    window.hideLoadingPopup();
  }
}

function buildAdminQuery(state) {
  const params = new URLSearchParams({
    page: String(state.page),
    page_size: String(state.size)
  });
  return params.toString();
}

function normalizeAdminDateValue(value) {
  if (value === undefined || value === null || value === "") return "";
  const text = String(value).trim();

  const isoDate = text.match(/\d{4}-\d{2}-\d{2}/);
  if (isoDate) return isoDate[0];

  const ddMmYyyy = text.match(/\b(\d{1,2})[-/](\d{1,2})[-/](\d{4})\b/);
  if (ddMmYyyy) {
    const day = ddMmYyyy[1].padStart(2, "0");
    const month = ddMmYyyy[2].padStart(2, "0");
    const year = ddMmYyyy[3];
    return `${year}-${month}-${day}`;
  }

  return "";
}

function rowMatchesUserDate(row) {
  if (!adminSelectedDate) return true;

  const preferredKeys = [
    "last_activity", "lastActivity", "last_activity_at", "lastActivityAt",
    "last_login", "lastLogin", "last_login_at", "lastLoginAt",
    "last_seen", "lastSeen", "updated_at", "created_at", "date"
  ];

  return preferredKeys.some(key => normalizeAdminDateValue(row?.[key]) === adminSelectedDate);
}

function isLongStatValue(value) {
  const text = String(value === undefined || value === null ? "" : value);
  return text.includes("@") || text.length > 10;
}

function extractItems(result) {
  if (Array.isArray(result)) return result;
  if (Array.isArray(result.items)) return result.items;
  if (Array.isArray(result.data)) return result.data;
  if (Array.isArray(result.results)) return result.results;
  if (Array.isArray(result.users)) return result.users;
  if (Array.isArray(result.agents)) return result.agents;
  if (Array.isArray(result.campaigns)) return result.campaigns;
  if (Array.isArray(result.password_resets)) return result.password_resets;
  return [];
}

function extractTotal(result, items) {
  if (result && result.total !== undefined) return Number(result.total || 0);
  if (result && result.count !== undefined) return Number(result.count || 0);
  return items.length;
}

function extractPlainObject(result) {
  if (!result || typeof result !== "object" || Array.isArray(result)) return {};
  if (result.summary && typeof result.summary === "object") return result.summary;
  if (result.data && typeof result.data === "object" && !Array.isArray(result.data)) return result.data;
  return result;
}

function renderAdminStats(result) {
  const summary = extractPlainObject(result);
  const entries = Object.entries(summary).filter(([, value]) => typeof value !== "object");
  const root = document.getElementById("adminStatGrid");

  if (!entries.length) {
    root.innerHTML = `<article class="admin-stat-card"><p>Admin Summary</p><h2 class="admin-stat-value">-</h2></article>`;
    return;
  }

  root.innerHTML = entries.map(([key, value]) => `
    <article class="admin-stat-card">
      <p>${escapeHtml(titleFromKey(key))}</p>
      <h2 class="admin-stat-value ${isLongStatValue(value) ? "stat-value-long" : ""}" title="${escapeHtml(normalValue(value))}">${escapeHtml(normalValue(value))}</h2>
    </article>
  `).join("");
}

function ensurePager(tbodyId) {
  const wrap = document.getElementById(tbodyId)?.closest(".admin-table-scroll");
  if (!wrap) return null;

  let pager = wrap.nextElementSibling;
  if (!pager || !pager.classList.contains("table-pagination")) {
    pager = document.createElement("div");
    pager.className = "table-pagination";
    wrap.insertAdjacentElement("afterend", pager);
  }
  return pager;
}

function renderPager({ tbodyId, state, loadFn }) {
  const pager = ensurePager(tbodyId);
  if (!pager || adminSelectedDate) {
    if (pager) pager.innerHTML = "";
    return;
  }

  const pages = Math.max(1, Math.ceil(state.total / state.size));
  if (state.total <= state.size) {
    pager.innerHTML = "";
    return;
  }

  pager.innerHTML = `
    <span>Page ${state.page} of ${pages}</span>
    <div class="table-page-actions">
      <select class="table-page-size">
        <option ${state.size === 5 ? "selected" : ""}>5</option>
        <option ${state.size === 10 ? "selected" : ""}>10</option>
        <option ${state.size === 25 ? "selected" : ""}>25</option>
        <option ${state.size === 50 ? "selected" : ""}>50</option>
      </select>
      <button class="table-page-btn" data-page="prev" ${state.page === 1 ? "disabled" : ""}>Prev</button>
      <button class="table-page-btn" data-page="next" ${state.page === pages ? "disabled" : ""}>Next</button>
    </div>
  `;

  pager.querySelector("[data-page='prev']")?.addEventListener("click", async () => {
    if (state.page <= 1) return;
    state.page -= 1;
    await loadFn();
  });

  pager.querySelector("[data-page='next']")?.addEventListener("click", async () => {
    if (state.page >= pages) return;
    state.page += 1;
    await loadFn();
  });

  pager.querySelector(".table-page-size")?.addEventListener("change", async event => {
    state.size = Number(event.target.value);
    state.page = 1;
    await loadFn();
  });
}

function userRow(user) {
  const email = pick(user, ["email", "user_email", "username"]);
  const role = pick(user, ["role", "user_role"]);
  const status = pick(user, ["status", "is_active"]);
  const lastActivity = pick(user, ["last_activity", "lastActivity", "last_activity_at", "lastActivityAt", "last_login", "lastLogin", "updated_at", "created_at"]);
  return `
    <tr>
      <td>${escapeHtml(normalValue(email))}</td>
      <td>${escapeHtml(normalValue(role))}</td>
      <td>${escapeHtml(normalValue(status))}</td>
      <td>${escapeHtml(normalValue(lastActivity))}</td>
    </tr>
  `;
}

function agentRow(agent) {
  return `
    <tr>
      <td>${escapeHtml(normalValue(pick(agent, ["agent_name", "name"])))}</td>
      <td>${escapeHtml(normalValue(pick(agent, ["agent_email", "email"])))}</td>
      <td>${escapeHtml(normalValue(pick(agent, ["role", "agent_role"])))}</td>
      <td>${escapeHtml(normalValue(pick(agent, ["status"])))}</td>
      <td>${escapeHtml(normalValue(pick(agent, ["assigned_tickets", "assigned", "open_tickets"])))}</td>
      <td>${escapeHtml(normalValue(pick(agent, ["sla", "sla_status", "sla_percentage"])))}</td>
    </tr>
  `;
}

function campaignRow(campaign) {
  return `
    <tr>
      <td>${escapeHtml(normalValue(pick(campaign, ["campaign_name", "name", "title"])))}</td>
      <td>${escapeHtml(normalValue(pick(campaign, ["business_channel", "channel"])))}</td>
      <td>${escapeHtml(normalValue(pick(campaign, ["status"])))}</td>
      <td>${escapeHtml(normalValue(pick(campaign, ["total_audience", "audience"])))}</td>
      <td>${escapeHtml(normalValue(pick(campaign, ["sent_count", "sent"])))}</td>
      <td>${escapeHtml(normalValue(pick(campaign, ["failed_count", "failed"])))}</td>
      <td>${escapeHtml(normalValue(pick(campaign, ["created_by", "owner"])))}</td>
    </tr>
  `;
}

function dataHealthRow(row) {
  return `
    <tr>
      <td>${escapeHtml(normalValue(pick(row, ["area", "module", "name"])))}</td>
      <td>${escapeHtml(normalValue(pick(row, ["records", "record_count", "total_records"])))}</td>
      <td>${escapeHtml(normalValue(pick(row, ["issue", "primary_issue", "problem"])))}</td>
      <td>${escapeHtml(normalValue(pick(row, ["count", "issue_count"])))}</td>
      <td>${escapeHtml(normalValue(pick(row, ["quality", "quality_score", "data_quality_score"])))}</td>
    </tr>
  `;
}

function passwordResetCard(row) {
  const email = pick(row, ["email", "user_email"]);
  const requestedAt = pick(row, ["requested_at", "created_at", "requestedAt"]);
  const expiresAt = pick(row, ["expires_at", "expiresAt"]);
  const used = pick(row, ["used", "is_used", "status"]);
  return `
    <div class="admin-reset-item">
      <strong>${escapeHtml(normalValue(email))}</strong>
      <span>Requested: ${escapeHtml(normalValue(requestedAt))}</span>
      <span>Expires: ${escapeHtml(normalValue(expiresAt))}</span>
      <span>Used: ${escapeHtml(normalValue(used))}</span>
    </div>
  `;
}

async function loadAdminSummary() {
  const result = await adminGetCached(
    "admin-summary",
    "/admin/summary",
    30000
  );

  renderAdminStats(result);
}

async function getUsersForSelectedDate() {
  const pageSize = 50;
  const first = await adminGet(`/admin/users?page=1&page_size=${pageSize}`);
  let items = extractItems(first);
  const total = extractTotal(first, items);
  const pages = Math.max(1, Math.ceil(total / pageSize));

  for (let page = 2; page <= pages; page += 1) {
    const result = await adminGet(`/admin/users?page=${page}&page_size=${pageSize}`);
    items = items.concat(extractItems(result));
  }

  return items.filter(rowMatchesUserDate);
}

async function loadUsers() {
  const state = adminState.users;
  const resultItems = adminSelectedDate ? await getUsersForSelectedDate() : null;
  const result = adminSelectedDate ? null : await adminGet(`/admin/users?${buildAdminQuery(state)}`);
  const items = adminSelectedDate ? resultItems : extractItems(result);

  state.items = items;
  state.total = adminSelectedDate ? items.length : extractTotal(result, items);

  document.getElementById("adminUsersCount").textContent = `${state.total} record${state.total === 1 ? "" : "s"}`;
  document.getElementById("adminUsersTable").innerHTML = items.map(userRow).join("") || `<tr><td colspan="4">No users returned for selected date.</td></tr>`;
  renderPager({ tbodyId: "adminUsersTable", state, loadFn: loadUsers });
}

async function loadAgents() {
  const state = adminState.agents;
  const result = await adminGet(`/admin/agents?${buildAdminQuery(state)}`);
  state.items = extractItems(result);
  state.total = extractTotal(result, state.items);
  document.getElementById("adminAgentsCount").textContent = `${state.total} record${state.total === 1 ? "" : "s"}`;
  document.getElementById("adminAgentsTable").innerHTML = state.items.map(agentRow).join("") || `<tr><td colspan="6">No agents returned by backend.</td></tr>`;
  renderPager({ tbodyId: "adminAgentsTable", state, loadFn: loadAgents });
}

async function loadCampaigns() {
  const state = adminState.campaigns;
  const result = await adminGet(`/admin/campaigns?${buildAdminQuery(state)}`);
  state.items = extractItems(result);
  state.total = extractTotal(result, state.items);
  document.getElementById("adminCampaignsCount").textContent = `${state.total} record${state.total === 1 ? "" : "s"}`;
  document.getElementById("adminCampaignsTable").innerHTML = state.items.map(campaignRow).join("") || `<tr><td colspan="7">No campaigns returned by backend.</td></tr>`;
  renderPager({ tbodyId: "adminCampaignsTable", state, loadFn: loadCampaigns });
}

async function loadDataHealth() {
  const result = await adminGetCached(
    "admin-data-health",
    "/admin/data-health",
    60000
  );

  adminState.dataHealth = extractItems(result);

  document.getElementById("adminDataHealthTable").innerHTML =
    adminState.dataHealth.map(dataHealthRow).join("") ||
    `<tr><td colspan="5">No data health records returned by backend.</td></tr>`;
}

async function loadPasswordResets() {
  const state = adminState.passwordResets;
  const result = await adminGet(`/admin/password-resets?${buildAdminQuery(state)}`);
  state.items = extractItems(result);
  state.total = extractTotal(result, state.items);
  document.getElementById("adminPasswordResetCount").textContent = `${state.total} record${state.total === 1 ? "" : "s"}`;
  document.getElementById("adminPasswordResetList").innerHTML = state.items.map(passwordResetCard).join("") || `<div class="admin-reset-item"><strong>No password reset records returned by backend.</strong></div>`;
}

function clearAdminFrontendCache() {
  if (typeof clearCachedApiData === "function") {
    clearCachedApiData("admin-summary");
    clearCachedApiData("admin-data-health");
    clearCachedApiData("dashboard-summary");
  }
}

async function downloadDataHealthReport() {
  const response = await fetch(`${ADMIN_API_BASE_URL}/admin/data-health/export`, {
    method: "GET",
    headers: adminHeaders()
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(formatAdminApiError(error, "Download failed"));
  }

  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "data-health-report.csv";
  link.click();
  URL.revokeObjectURL(url);
}

async function reloadAdminPageData() {
  adminState.users.page = 1;
  adminState.agents.page = 1;
  adminState.campaigns.page = 1;
  adminState.passwordResets.page = 1;
  await Promise.all([
    loadAdminSummary(),
    loadUsers(),
    loadAgents(),
    loadCampaigns(),
    loadDataHealth(),
    loadPasswordResets()
  ]);
}

async function reloadUserManagementOnly() {
  adminState.users.page = 1;
  await loadUsers();
}

function setupAdminDateFilter() {
  const dateInput = document.getElementById("adminDateFilter");
  const clearButton = document.getElementById("adminClearDateFilter");

  async function applyDateFilter(value) {
    adminSelectedDate = value || "";
    startAdminLoading("Loading user management data from backend...");
    try {
      await reloadUserManagementOnly();
    } catch (error) {
      console.error("Admin user date filter error:", error);
      showAdminError(error.message || "Unable to filter user management data.");
    } finally {
      stopAdminLoading();
    }
  }

  dateInput?.addEventListener("change", () => applyDateFilter(dateInput.value));
  clearButton?.addEventListener("click", () => {
    if (dateInput) dateInput.value = "";
    applyDateFilter("");
  });
}

function setupAdminActions() {
  document.getElementById("downloadReportBtn")?.addEventListener("click", async () => {
    try {
      await downloadDataHealthReport();
    } catch (error) {
      showAdminError(error.message || "Unable to download data health report.");
    }
  });
}

async function initAdminPage() {
  if (typeof guardPage === "function") guardPage("admin");
  if (typeof loadNavigation === "function") loadNavigation("admin");

  setupAdminActions();
  setupAdminDateFilter();

  startAdminLoading("Loading admin data from backend...");
  try {
    await reloadAdminPageData();
  } catch (error) {
    console.error("Admin backend error:", error);
    showAdminError(error.message || "Unable to load admin data from backend.");
  } finally {
    stopAdminLoading();
  }
}

document.addEventListener("DOMContentLoaded", initAdminPage);
