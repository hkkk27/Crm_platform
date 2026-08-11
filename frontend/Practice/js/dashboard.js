const DASHBOARD_API_BASE_URL = localStorage.getItem("omnilink_api_base") || "http://127.0.0.1:8000";
let dashboardBackendData = { summary: {}, charts: {}, loyalty: {}, tables: {}, metadata: {} };
let dashboardCharts = {};

function formatNumber(value) {
  const number = Number(value || 0);
  return Number.isNaN(number) ? "0" : number.toLocaleString("en-IN");
}
function formatCurrency(value) {
  const number = Number(value || 0);
  return Number.isNaN(number) ? "₹0" : "₹" + number.toLocaleString("en-IN");
}
function formatPercent(value) {
  const number = Number(value || 0);
  return Number.isNaN(number) ? "0%" : number.toFixed(2) + "%";
}
function escapeHtml(value) {
  return String(value === undefined || value === null ? "" : value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
function cleanText(value) {
  return String(value || "").replace(/\s+/g, " ").trim();
}
function getDashboardAuthToken() {
  const direct = localStorage.getItem("omnilink_token");
  if (direct) return direct;
  try {
    const session = JSON.parse(localStorage.getItem("crm_session") || "null");
    return session && (session.token || session.access_token) || "";
  } catch (error) {
    return "";
  }
}
function getDashboardAuthHeaders() {
  return { "Content-Type": "application/json", Authorization: "Bearer " + getDashboardAuthToken() };
}
function showDashboardLoading() {
  if (window.showLoadingPopup) window.showLoadingPopup("Loading dashboard data...");
}
function hideDashboardLoading() {
  if (window.hideLoadingPopup) window.hideLoadingPopup();
}
function showDashboardError(message) {
  if (window.showAppPopup) return window.showAppPopup(message, { type: "error" });
  alert(message);
}
let dashboardLoadingPromise = null;

async function fetchDashboardSummary() {
  if (dashboardLoadingPromise) {
    return dashboardLoadingPromise;
  }

  dashboardLoadingPromise = cachedApiGet(
    "dashboard-summary",
    "/dashboard/summary",
    60000
  );

  try {
    const result = await dashboardLoadingPromise;

    if (!result.success) {
      throw new Error("Invalid dashboard response");
    }

    return result;
  } finally {
    dashboardLoadingPromise = null;
  }
}
async function renderDashboard() {
  const dashboardEl = document.getElementById("dashboard");
  dashboardEl.innerHTML = loadingLayout();
  showDashboardLoading();
  try {
    const result = await fetchDashboardSummary();
    dashboardBackendData = {
      summary: result.summary || {},
      charts: result.charts || {},
      loyalty: result.loyalty || {},
      tables: result.tables || {},
      metadata: result.metadata || {}
    };
    dashboardEl.innerHTML = dashboardLayout(dashboardBackendData.summary);
    renderDashboardCharts();
  } catch (error) {
    console.error("Dashboard summary error:", error);
    dashboardEl.innerHTML = errorLayout(error.message);
    showDashboardError("Dashboard backend unavailable: " + error.message);
  } finally {
    hideDashboardLoading();
  }
}
function loadingLayout() {
  return '<div class="dash-hero"><div><h1>Summary Dashboard</h1></div><div class="dash-hero-actions"><button class="primary-btn" type="button" onclick="exportDashboardToReports()">Export</button></div></div><div class="dash-grid dash-kpis"><article class="card dash-kpi"><strong>Loading</strong></article><article class="card dash-kpi"><strong>Loading</strong></article><article class="card dash-kpi"><strong>Loading</strong></article></div>';
}
function errorLayout(message) {
  return '<div class="dash-hero"><div><h1>Summary Dashboard</h1></div><div class="dash-hero-actions"><button class="primary-btn" type="button" onclick="exportDashboardToReports()">Export</button></div></div><section class="dash-card"><h2>Dashboard data unavailable</h2><p>' + escapeHtml(message || "Please check backend connection.") + '</p></section>';
}
function dashboardLayout(summary) {
  return '<div class="dash-hero"><div><h1>Summary Dashboard</h1></div><div class="dash-hero-actions"><button class="primary-btn" type="button" onclick="exportDashboardToReports()">Export</button></div></div>' +
    renderKpis(summary) +
    sectionTitle("Customer Analytics") + renderCustomerAnalytics() +
    sectionTitle("Campaign Analytics") + renderCampaignAnalytics() +
    sectionTitle("Customer Service Analytics") + renderServiceAnalytics(summary) +
    sectionTitle("Loyalty, Consent & Geography") + renderLoyaltyConsentGeo() +
    sectionTitle("Data Quality & Operational Tables") + renderDataQualityAndTables();
}
function sectionTitle(title) {
  return '<div class="dash-section-title"><h2>' + escapeHtml(title) + '</h2></div>';
}
function renderKpis(summary) {
  const cards = [
    ["Total Customers", formatNumber(summary.total_customers), "👥"],
    ["Active Members", formatNumber(summary.members), "🏆"],
    ["Average CLV", formatCurrency(summary.avg_clv), "💰"],
    ["Repeat Purchase Rate", formatPercent(summary.repeat_purchase_rate), "🔁"],
    ["High Churn Customers", formatNumber(summary.high_churn_customers), "⚠️"],
    ["Campaign Eligible", formatNumber(summary.campaign_eligible_customers), "📣"],
    ["Total Sales", formatCurrency(summary.total_sales), "📈"],
    ["Open Service Tickets", formatNumber(summary.open_service_tickets), "🎧"],
    ["Total Campaigns", formatNumber(summary.total_campaigns), "🗓️"],
    ["WhatsApp Reachable", formatNumber(summary.whatsapp_reachable), "💬"],
    ["Avg Data Quality", formatPercent(summary.average_data_quality), "✅"],
    ["Missing Emails", formatNumber(summary.missing_emails), "✉️"]
  ];
  return '<div class="dash-grid dash-kpis">' + cards.map(function (card) {
    return '<article class="card dash-kpi"><div class="dash-kpi-top"><span class="dash-kpi-icon">' + card[2] + '</span></div><h3>' + escapeHtml(card[0]) + '</h3><strong>' + escapeHtml(card[1]) + '</strong></article>';
  }).join("") + '</div>';
}
function chartCard(title, id, full) {
  return '<section class="dash-card"><div class="dash-card-head"><h2>' + escapeHtml(title) + '</h2></div><div class="dash-chart ' + (full ? 'full' : '') + '"><canvas id="' + id + '"></canvas></div></section>';
}
function tableCard(title, html) {
  return '<section class="dash-card"><div class="dash-card-head"><h2>' + escapeHtml(title) + '</h2></div><div class="dash-table-wrap">' + html + '</div></section>';
}
function renderCustomerAnalytics() {
  return '<div class="dash-grid dash-two">' + chartCard("Customer Segmentation", "segmentChart") + chartCard("Churn Risk", "churnChart") + '</div>';
}
function renderCampaignAnalytics() {
  return '<div class="dash-grid dash-two">' + chartCard("Campaign Status", "campaignStatusChart") + tableCard("Recent Campaigns", recentCampaignRows()) + '</div><div class="dash-grid dash-full">' + chartCard("Campaign Performance", "campaignPerformanceChart", true) + '</div>';
}
function renderServiceAnalytics(summary) {
  return '<div class="dash-grid dash-two">' + chartCard("Ticket Status", "ticketStatusChart") + '<section class="dash-card"><div class="dash-card-head"><h2>SLA Compliance</h2></div><div class="dash-ring"><div><strong>' + formatPercent(summary.sla_compliance_percentage) + '</strong><span>Within SLA</span></div></div><div class="dash-chart" style="height:170px;margin-top:10px"><canvas id="slaChart"></canvas></div></section></div><div class="dash-grid dash-full">' + chartCard("Ticket Trend", "ticketTrendChart", true) + '</div><div class="dash-grid dash-full">' + tableCard("Recent Service Tickets", recentTicketRows()) + '</div>';
}
function renderLoyaltyConsentGeo() {
  const summary = dashboardBackendData.summary || {};
  const balance = dashboardBackendData.loyalty && dashboardBackendData.loyalty.points_balance || 0;
  return '<div class="dash-grid dash-two"><section class="dash-card"><div class="dash-card-head"><h2>Loyalty Points</h2></div><div class="dash-mini-kpis"><div class="dash-mini"><span>Balance</span><strong>' + formatNumber(balance) + '</strong></div><div class="dash-mini"><span>Members</span><strong>' + formatNumber(summary.members) + '</strong></div><div class="dash-mini"><span>Membership %</span><strong>' + formatPercent(summary.member_percentage) + '</strong></div></div><div class="dash-chart" style="height:170px;margin-top:10px"><canvas id="membershipChart"></canvas></div></section>' + chartCard("Consent Reachability", "consentChart") + '</div><div class="dash-grid dash-full">' + chartCard("Top Customer Cities", "cityChart", true) + '</div>';
}
function renderDataQualityAndTables() {
  return '<div class="dash-grid dash-two">' + chartCard("Data Quality", "dataQualityChart") + tableCard("High Churn Customers", highChurnRows()) + '</div>';
}
function renderTable(headers, rows, emptyMessage) {
  const body = rows.length ? rows.map(function (row) {
    return '<tr>' + row.map(function (cell) { return '<td>' + escapeHtml(cell) + '</td>'; }).join("") + '</tr>';
  }).join("") : '<tr><td colspan="' + headers.length + '">' + escapeHtml(emptyMessage || "No records found") + '</td></tr>';
  return '<table class="dash-table"><thead><tr>' + headers.map(function (h) { return '<th>' + escapeHtml(h) + '</th>'; }).join("") + '</tr></thead><tbody>' + body + '</tbody></table>';
}
function recentCampaignRows() {
  const rows = (dashboardBackendData.tables.recent_campaigns || []).map(function (item) {
    return [item.campaign_name || item.campaign_id || "-", item.campaign_type || "-", item.status || "-", formatNumber(item.total_audience), formatCurrency(item.revenue)];
  });
  return renderTable(["Campaign", "Type", "Status", "Audience", "Revenue"], rows, "No recent campaigns found");
}
function recentTicketRows() {
  const rows = (dashboardBackendData.tables.recent_tickets || []).map(function (item) {
    return [item.ticket_id || "-", item.priority || "-", item.status || "-", item.assigned_to || item.assigned_agent_id || "-", item.sla_status || "-"];
  });
  return renderTable(["Ticket", "Priority", "Status", "Agent", "SLA"], rows, "No recent tickets found");
}
function highChurnRows() {
  const rows = (dashboardBackendData.tables.high_churn_customers || []).map(function (item) {
    return [item.customer_id || item.crm_customer_key || "-", item.churn_risk_level || "-", formatCurrency(item.estimated_clv), item.membership_tier || "-"];
  });
  return renderTable(["Customer", "Risk", "CLV", "Tier"], rows, "No high-churn customers found");
}
function chartSeries(rows) {
  const safeRows = Array.isArray(rows) ? rows : [];
  return { labels: safeRows.map(function (item) { return item.label || "Unknown"; }), values: safeRows.map(function (item) { return Number(item.value || 0); }) };
}
function renderDashboardCharts() {
  if (typeof Chart === "undefined") return;
  const colors = ["#009688", "#2563eb", "#F58220", "#39B54A", "#D94A4A", "#7c3aed", "#64748b", "#ec4899", "#0ea5e9", "#84cc16"];
  const charts = dashboardBackendData.charts || {};
  const segments = chartSeries(charts.customer_segments);
  const churn = chartSeries(charts.churn_distribution);
  const campaignStatus = chartSeries(charts.campaign_status);
  const campaignPerformance = chartSeries(charts.campaign_performance);
  const ticketStatus = chartSeries(charts.ticket_status);
  const tiers = chartSeries(charts.membership_tiers);
  const consent = chartSeries(charts.consent_reachability);
  const cities = chartSeries(charts.top_cities);
  const quality = chartSeries(charts.data_quality);
  const sla = chartSeries(charts.sla_distribution);
  doughnut("segmentChart", segments.labels, segments.values, colors);
  bar("churnChart", churn.labels, churn.values, ["#39B54A", "#F58220", "#D94A4A"]);
  doughnut("campaignStatusChart", campaignStatus.labels, campaignStatus.values, colors);
  bar("campaignPerformanceChart", campaignPerformance.labels, campaignPerformance.values, colors);
  doughnut("ticketStatusChart", ticketStatus.labels, ticketStatus.values, colors);
  renderTicketTrendChart(charts.ticket_trend || []);
  bar("membershipChart", tiers.labels, tiers.values, colors);
  bar("consentChart", consent.labels, consent.values, colors);
  bar("cityChart", cities.labels, cities.values, "#009688", "#3c14aa", "#200096", "#009854", "#585a5e");
  doughnut("dataQualityChart", quality.labels, quality.values, ["#F58220", "#D94A4A", "#39B54A"]);
  doughnut("slaChart", sla.labels, sla.values, ["#ce1313", "#F58220", "#64748b"]);
}
function renderTicketTrendChart(rows) {
  const data = Array.isArray(rows) ? rows : [];
  makeChart("ticketTrendChart", { type: "line", data: { labels: data.map(function (item) { return item.label; }), datasets: [{ label: "Created", data: data.map(function (item) { return Number(item.created || 0); }), borderColor: "#2563eb", tension: 0.35 }, { label: "Resolved", data: data.map(function (item) { return Number(item.resolved || 0); }), borderColor: "#39B54A", tension: 0.35 }, { label: "Escalated", data: data.map(function (item) { return Number(item.escalated || 0); }), borderColor: "#D94A4A", tension: 0.35 }] }, options: opts(false) });
}
function doughnut(id, labels, values, colors) { makeChart(id, { type: "doughnut", data: { labels: labels, datasets: [{ data: values, backgroundColor: colors }] }, options: opts(true) }); }
function bar(id, labels, values, color) { makeChart(id, { type: "bar", data: { labels: labels, datasets: [{ label: "Value", data: values, backgroundColor: color }] }, options: opts(false) }); }
function makeChart(id, config) {
  const canvas = document.getElementById(id);
  if (!canvas) return null;
  if (dashboardCharts[id]) dashboardCharts[id].destroy();
  dashboardCharts[id] = new Chart(canvas, config);
  return dashboardCharts[id];
}
function opts(legend) {
  return { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: legend, position: "bottom", labels: { boxWidth: 10, usePointStyle: true } } }, scales: legend ? undefined : { y: { beginAtZero: true, grid: { color: "#eef2f7" } }, x: { grid: { display: false } } } };
}
function getSelectedDashboardPeriod() { return "Current Period"; }
async function exportDashboardToReports() {
  const button = Array.from(document.querySelectorAll("button")).find(function (btn) { return btn.textContent.trim().toLowerCase() === "export" && btn.classList.contains("primary-btn"); });
  if (button) { button.disabled = true; button.textContent = "Preparing..."; }
  await new Promise(function (resolve) { requestAnimationFrame(function () { requestAnimationFrame(function () { setTimeout(resolve, 450); }); }); });
  localStorage.setItem("dashboard_report_draft", JSON.stringify(buildDashboardReportDraft()));
  if (button) { button.disabled = false; button.textContent = "Export"; }
  window.location.href = "Reports.html";
}
function buildDashboardReportDraft() {
  const kpis = collectDashboardKpis();
  return { title: "Executive Summary of Dashboard Report", reportName: "Dashboard Business Review", period: getSelectedDashboardPeriod(), date: new Date().toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" }), dashboardKpis: kpis, dashboardCharts: collectDashboardCharts(), dashboardTables: collectDashboardTables(), backendPayload: dashboardBackendData, exportedAt: new Date().toISOString() };
}
function collectDashboardKpis() { return Array.from(document.querySelectorAll(".dash-kpi")).map(function (card) { return { title: cleanText(card.querySelector("h3")?.textContent), value: cleanText(card.querySelector("strong")?.textContent) }; }).filter(function (item) { return item.title || item.value; }); }
function collectDashboardCharts() { return Array.from(document.querySelectorAll(".dash-card canvas")).map(function (canvas) { const card = canvas.closest(".dash-card"); let image = ""; try { const chart = typeof Chart !== "undefined" && Chart.getChart ? Chart.getChart(canvas) : null; if (chart) chart.update("none"); image = canvas.toDataURL("image/png", 1.0); } catch (error) { console.warn("Unable to export chart", canvas.id, error); } return { id: canvas.id, title: cleanText(card?.querySelector("h2")?.textContent) || canvas.id, image: image }; }).filter(function (chart) { return chart.image && chart.image.length > 100; }); }
function collectDashboardTables() { return Array.from(document.querySelectorAll(".dash-card .dash-table")).map(function (table) { const card = table.closest(".dash-card"); return { title: cleanText(card?.querySelector("h2")?.textContent), html: table.outerHTML }; }); }
/* =====================================================
   CAMPAIGN PERFORMANCE SPLIT CHART - INTEGRATED PATCH
   Paste at VERY END of js/dashboard.js

   Result:
   - Removes old single Campaign Performance chart
   - Adds Campaign Engagement chart: Opened, Clicked, Converted
   - Adds Campaign Revenue chart: Revenue
   - Keeps both new charts in same horizontal row
===================================================== */

function renderCampaignAnalytics() {
  return `
    <div class="dash-grid dash-two">
      ${chartCard("Campaign Status", "campaignStatusChart")}
      ${tableCard("Recent Campaigns", recentCampaignRows())}
    </div>

    <div class="dash-grid dash-two">
      ${chartCard("Campaign Engagement", "campaignEngagementChart")}
      ${chartCard("Campaign Revenue", "campaignRevenueChart")}
    </div>
  `;
}

function splitCampaignPerformanceData(rows) {
  const safeRows = Array.isArray(rows) ? rows : [];

  const engagementRows = safeRows.filter(function (item) {
    const label = String(item.label || "").toLowerCase();

    return (
      label.includes("open") ||
      label.includes("click") ||
      label.includes("convert")
    );
  });

  const revenueRows = safeRows.filter(function (item) {
    const label = String(item.label || "").toLowerCase();
    return label.includes("revenue");
  });

  return {
    engagement: {
      labels: engagementRows.map(function (item) {
        return item.label || "Unknown";
      }),
      values: engagementRows.map(function (item) {
        return Number(item.value || 0);
      })
    },
    revenue: {
      labels: revenueRows.map(function (item) {
        return item.label || "Revenue";
      }),
      values: revenueRows.map(function (item) {
        return Number(item.value || 0);
      })
    }
  };
}

function renderDashboardCharts() {
  if (typeof Chart === "undefined") return;

  const colors = [
    "#009688",
    "#2563eb",
    "#F58220",
    "#39B54A",
    "#D94A4A",
    "#7c3aed",
    "#64748b",
    "#ec4899",
    "#0ea5e9",
    "#84cc16"
  ];

  const charts = dashboardBackendData.charts || {};

  const segments = chartSeries(charts.customer_segments);
  const churn = chartSeries(charts.churn_distribution);
  const campaignStatus = chartSeries(charts.campaign_status);
  const campaignPerformanceSplit = splitCampaignPerformanceData(charts.campaign_performance);
  const ticketStatus = chartSeries(charts.ticket_status);
  const tiers = chartSeries(charts.membership_tiers);
  const consent = chartSeries(charts.consent_reachability);
  const cities = chartSeries(charts.top_cities);
  const quality = chartSeries(charts.data_quality);
  const sla = chartSeries(charts.sla_distribution);

  doughnut("segmentChart", segments.labels, segments.values, colors);

  bar(
    "churnChart",
    churn.labels,
    churn.values,
    ["#39B54A", "#F58220", "#D94A4A"]
  );

  doughnut(
    "campaignStatusChart",
    campaignStatus.labels,
    campaignStatus.values,
    colors
  );

  bar(
    "campaignEngagementChart",
    campaignPerformanceSplit.engagement.labels,
    campaignPerformanceSplit.engagement.values,
    ["#2563eb", "#F58220", "#009688"]
  );

  bar(
    "campaignRevenueChart",
    campaignPerformanceSplit.revenue.labels,
    campaignPerformanceSplit.revenue.values,
    "#39B54A"
  );

  doughnut(
    "ticketStatusChart",
    ticketStatus.labels,
    ticketStatus.values,
    colors
  );

  renderTicketTrendChart(charts.ticket_trend || []);

  bar(
    "membershipChart",
    tiers.labels,
    tiers.values,
    colors
  );

  bar(
    "consentChart",
    consent.labels,
    consent.values,
    colors
  );

  bar(
    "cityChart",
    cities.labels,
    cities.values,
    ["#009688", "#2563eb", "#F58220", "#39B54A", "#7c3aed", "#D94A4A", "#0ea5e9", "#84cc16", "#ec4899", "#64748b"]
  );

  doughnut(
    "dataQualityChart",
    quality.labels,
    quality.values,
    ["#F58220", "#D94A4A", "#39B54A"]
  );

  doughnut(
    "slaChart",
    sla.labels,
    sla.values,
    ["#ce1313", "#F58220", "#64748b"]
  );
}