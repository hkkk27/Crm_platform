const AUDIT_API_BASE_URL = window.API_BASE_URL || localStorage.getItem("omnilink_api_base") || "http://127.0.0.1:8000";

let auditSelectedDate = "";
let auditPage = 1;
let auditSize = 10;
let auditTotal = 0;
let auditLogs = [];

function auditHeaders() {
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

function formatAuditApiError(result, fallback) {
  const value = result?.detail || result?.message || fallback;
  if (Array.isArray(value)) {
    return value.map(item => typeof item === "string" ? item : (item?.msg || JSON.stringify(item))).join("\n");
  }
  if (value && typeof value === "object") return value.msg || JSON.stringify(value);
  return String(value || fallback);
}

async function auditGet(path) {
  const response = await fetch(`${AUDIT_API_BASE_URL}${path}`, {
    method: "GET",
    headers: auditHeaders()
  });
  const result = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(formatAuditApiError(result, `Audit request failed: ${path}`));
  return result;
}

async function auditGetCached(cacheKey, endpoint, ttlMilliseconds) {
  if (typeof cachedApiGet === "function") {
    return cachedApiGet(cacheKey, endpoint, ttlMilliseconds);
  }

  return auditGet(endpoint);
}


function showAuditError(message) {
  if (window.showAppPopup) {
    window.showAppPopup(message, { type: "error" });
    return;
  }
  console.error(message);
}

function startAuditLoading(message) {
  if (window.showLoadingPopup) window.showLoadingPopup(message);
}

function stopAuditLoading() {
  if (window.hideLoadingPopup) window.hideLoadingPopup();
}

function normalizeLog(row) {
  const source = row || {};
  return {
    raw: source,
    auditId: pick(source, ["audit_id", "auditId", "id", "audit_log_id"]),
    time: pick(source, ["created_at", "timestamp", "time", "event_time"]),
    user: pick(source, ["user_email", "user", "email", "performed_by"]),
    role: pick(source, ["user_role", "role"]),
    action: pick(source, ["action", "event_action"]),
    module: pick(source, ["object_type", "module", "table_name", "entity_type"]),
    status: pick(source, ["status", "result"]),
    risk: pick(source, ["risk", "risk_level", "riskLevel"])
  };
}

function normalizeAuditDateValue(value) {
  if (value === undefined || value === null || value === "") return "";
  const text = String(value).trim();
  const isoDate = text.match(/\d{4}-\d{2}-\d{2}/);
  if (isoDate) return isoDate[0];
  const ddMmYyyy = text.match(/\b(\d{1,2})[-/](\d{1,2})[-/](\d{4})\b/);
  if (ddMmYyyy) {
    return `${ddMmYyyy[3]}-${ddMmYyyy[2].padStart(2, "0")}-${ddMmYyyy[1].padStart(2, "0")}`;
  }
  return "";
}

function rowMatchesAuditDate(row) {
  if (!auditSelectedDate) return true;
  return ["created_at", "timestamp", "time", "event_time"].some(key => normalizeAuditDateValue(row?.[key]) === auditSelectedDate);
}

function buildAuditLogsQuery() {
  const params = new URLSearchParams({ page: String(auditPage), page_size: String(auditSize) });
  if (auditSelectedDate) params.set("date", auditSelectedDate);
  return params.toString();
}

function buildAuditDateQuery() {
  const params = new URLSearchParams();
  if (auditSelectedDate) params.set("date", auditSelectedDate);
  return params.toString();
}

function extractSummary(result) {
  if (!result || typeof result !== "object") return {};
  if (result.summary && typeof result.summary === "object") return result.summary;
  if (result.data && typeof result.data === "object" && !Array.isArray(result.data)) return result.data;
  return result;
}

function extractItems(result) {
  if (Array.isArray(result)) return result;
  if (Array.isArray(result.items)) return result.items;
  if (Array.isArray(result.data)) return result.data;
  if (Array.isArray(result.logs)) return result.logs;
  if (Array.isArray(result.results)) return result.results;
  return [];
}

function extractTotal(result, items) {
  if (result && result.total !== undefined) return Number(result.total || 0);
  if (result && result.count !== undefined) return Number(result.count || 0);
  return items.length;
}

function isMostActiveUserKey(key) {
  const normalized = String(key || "").toLowerCase().replaceAll("_", " ").replaceAll("-", " ").trim();
  return normalized.includes("most active user");
}

function isLongStatValue(value) {
  const text = String(value === undefined || value === null ? "" : value);
  return text.includes("@") || text.length > 10;
}

function renderAuditStats(summary) {
  const summaryObject = extractSummary(summary);
  const entries = Object.entries(summaryObject).filter(([key, value]) => typeof value !== "object" && !isMostActiveUserKey(key));
  const root = document.getElementById("auditStatGrid");
  if (!entries.length) {
    root.innerHTML = `<article class="audit-stat-card"><p>Audit Summary</p><h2 class="audit-stat-value">-</h2></article>`;
    return;
  }
  root.innerHTML = entries.map(([key, value]) => `
    <article class="audit-stat-card">
      <p>${escapeHtml(titleFromKey(key))}</p>
      <h2 class="audit-stat-value ${isLongStatValue(value) ? "stat-value-long" : ""}" title="${escapeHtml(normalValue(value))}">${escapeHtml(normalValue(value))}</h2>
    </article>
  `).join("");
}

async function loadAuditSummary() {
  const dateQuery = buildAuditDateQuery();
  const endpoint = `/audit/summary${dateQuery ? `?${dateQuery}` : ""}`;
  const cacheKey = auditSelectedDate
    ? `audit-summary-${auditSelectedDate}`
    : "audit-summary";

  const result = await auditGetCached(
    cacheKey,
    endpoint,
    15000
  );

  renderAuditStats(result);
}

async function loadAuditLogs() {
  const result = await auditGet(`/audit/logs?${buildAuditLogsQuery()}`);
  let items = extractItems(result);
  if (auditSelectedDate) items = items.filter(rowMatchesAuditDate);
  auditLogs = items.map(normalizeLog);
  auditTotal = auditSelectedDate ? auditLogs.length : extractTotal(result, auditLogs);
  renderAuditTable();
}

function ensurePager() {
  const wrap = document.getElementById("auditLogsTable")?.closest(".audit-table-scroll");
  if (!wrap) return null;
  let pager = wrap.nextElementSibling;
  if (!pager || !pager.classList.contains("table-pagination")) {
    pager = document.createElement("div");
    pager.className = "table-pagination";
    pager.id = "auditPagination";
    wrap.insertAdjacentElement("afterend", pager);
  }
  return pager;
}

function renderAuditTable() {
  const body = document.getElementById("auditLogsTable");
  const count = document.getElementById("auditResultCount");
  const pager = ensurePager();
  const pages = Math.max(1, Math.ceil(auditTotal / auditSize));
  count.textContent = `${auditTotal} record${auditTotal === 1 ? "" : "s"}`;
  body.innerHTML = auditLogs.map(log => `
    <tr data-audit-id="${escapeHtml(log.auditId)}">
      <td>${escapeHtml(normalValue(log.time))}</td>
      <td>${escapeHtml(normalValue(log.user))}</td>
      <td>${escapeHtml(normalValue(log.role))}</td>
      <td>${escapeHtml(normalValue(log.action))}</td>
      <td>${escapeHtml(normalValue(log.module))}</td>
      <td>${escapeHtml(normalValue(log.status))}</td>
      <td>${escapeHtml(normalValue(log.risk))}</td>
    </tr>
  `).join("") || `<tr><td colspan="7">No audit records returned for selected date.</td></tr>`;
  if (!pager) return;
  if (auditSelectedDate || auditTotal <= auditSize) {
    pager.innerHTML = "";
    return;
  }
  pager.innerHTML = `
    <span>Page ${auditPage} of ${pages}</span>
    <div class="table-page-actions">
      <select class="table-page-size">
        <option ${auditSize === 5 ? "selected" : ""}>5</option>
        <option ${auditSize === 10 ? "selected" : ""}>10</option>
        <option ${auditSize === 25 ? "selected" : ""}>25</option>
        <option ${auditSize === 50 ? "selected" : ""}>50</option>
      </select>
      <button class="table-page-btn" data-go="prev" ${auditPage === 1 ? "disabled" : ""}>Prev</button>
      <button class="table-page-btn" data-go="next" ${auditPage === pages ? "disabled" : ""}>Next</button>
    </div>
  `;
  pager.querySelector("[data-go='prev']")?.addEventListener("click", async () => {
    if (auditPage <= 1) return;
    auditPage -= 1;
    await loadAuditLogs();
  });
  pager.querySelector("[data-go='next']")?.addEventListener("click", async () => {
    if (auditPage >= pages) return;
    auditPage += 1;
    await loadAuditLogs();
  });
  pager.querySelector(".table-page-size")?.addEventListener("change", async event => {
    auditSize = Number(event.target.value);
    auditPage = 1;
    await loadAuditLogs();
  });
}

async function reloadAuditPageData() {
  auditPage = 1;
  await Promise.all([loadAuditSummary(), loadAuditLogs()]);
}

function setupAuditDateFilter() {
  const dateInput = document.getElementById("auditDateFilter");
  const clearButton = document.getElementById("auditClearDateFilter");
  async function applyDateFilter(value) {
    auditSelectedDate = value || "";
    startAuditLoading("Loading audit data from backend...");
    try {
      await reloadAuditPageData();
    } catch (error) {
      console.error("Audit backend error:", error);
      showAuditError(error.message || "Unable to load audit data from backend.");
      document.getElementById("auditStatGrid").innerHTML = "";
      document.getElementById("auditLogsTable").innerHTML = "";
      document.getElementById("auditResultCount").textContent = "";
    } finally {
      stopAuditLoading();
    }
  }
  dateInput?.addEventListener("change", () => applyDateFilter(dateInput.value));
  clearButton?.addEventListener("click", () => {
    if (dateInput) dateInput.value = "";
    applyDateFilter("");
  });
}

async function initAuditPage() {
  if (typeof guardPage === "function") guardPage("audit");
  if (typeof loadNavigation === "function") loadNavigation("audit");
  setupAuditDateFilter();
  startAuditLoading("Loading audit data from backend...");
  try {
    await reloadAuditPageData();
  } catch (error) {
    console.error("Audit backend error:", error);
    showAuditError(error.message || "Unable to load audit data from backend.");
    document.getElementById("auditStatGrid").innerHTML = "";
    document.getElementById("auditLogsTable").innerHTML = "";
    document.getElementById("auditResultCount").textContent = "";
  } finally {
    stopAuditLoading();
  }
}

document.addEventListener("DOMContentLoaded", initAuditPage);
