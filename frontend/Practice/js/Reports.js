let activeReportTemplate = "executive";
let reportPreviewMode = false;
let reportState = getDefaultReportState();

function initReportsPage() {
  loadDraftFromDashboardIfAvailable();
  renderReportTemplate("executive");
}

function getDefaultReportState() {
  const profile = getReportsProfile();
  return {
    title: "Executive Summary of Dashboard Report",
    subtitle: "This report summarizes dashboard performance, customer analytics, campaigns, service, loyalty, consent, data quality, risks and notes.",
    reportName: "Dashboard Business Review",
    preparedBy: profile.name,
    period: "Current Period",
    date: getReportDate(),
    overview: "Write the project overview here. Add the objective, current state, accomplishments and business context.",
    details: "Client / Business Unit: Add client\nReport Owner: Add owner\nPrepared For: Add recipient\nReview Date: Add date",
    metric1Label: "Total Customers",
    metric1Value: "Add value",
    metric2Label: "Active Members",
    metric2Value: "Add value",
    metric3Label: "Average CLV",
    metric3Value: "Add value",
    metric4Label: "Repeat Purchase Rate",
    metric4Value: "Add value",
    executiveSummary: "Add executive summary notes based on dashboard KPI cards.",
    customerAnalytics: "Add customer segmentation, churn risk and age-group insights here.",
    campaignAnalytics: "Add campaign status, campaign performance and recent campaign notes here.",
    serviceAnalytics: "Add ticket workload, ticket trend and SLA observations here.",
    loyaltyConsentGeo: "Add loyalty points, consent reachability and geography insights here.",
    dataQualityOperations: "Add data quality health, campaign/ticket snapshots and operational table notes here.",
    risks: "Risk | Response | Owner | Status\nAdd risk | Add response | Add owner | Add status",
    notes: "Write manager notes, recommendations, or final comments here."
  };
}

function loadDraftFromDashboardIfAvailable() {
  try {
    const draft = JSON.parse(localStorage.getItem("dashboard_report_draft") || "null");
    if (draft && typeof draft === "object") reportState = { ...reportState, ...draft };
  } catch (error) {
    console.warn("No valid dashboard report draft found.");
  }
}

function getReportDate() {
  return new Date().toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" });
}

function getReportsProfile() {
  let session = null;
  try { session = JSON.parse(localStorage.getItem("crm_session") || "null"); } catch (error) { session = null; }
  const email = session?.email || localStorage.getItem("omnilink_email") || localStorage.getItem("userName") || "admin@omnilink.com";
  const storedName = localStorage.getItem("userName");
  const sessionName = session?.name || session?.full_name || session?.user_name;
  const emailName = email.includes("@") ? email.split("@")[0].replace(/[._-]/g, " ") : "Admin User";
  return { name: titleCaseReport(storedName || sessionName || emailName) };
}

function titleCaseReport(value) {
  return String(value || "").split(" ").filter(Boolean).map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()).join(" ");
}

function collectReportState() {
  document.querySelectorAll("[data-report-field]").forEach(field => {
    const key = field.dataset.reportField;
    reportState[key] = field.value !== undefined ? field.value : field.textContent;
  });
}

function switchReportTemplate(templateName) {
  collectReportState();
  activeReportTemplate = templateName;
  renderReportTemplate(templateName);
  document.querySelectorAll(".template-card").forEach(card => card.classList.toggle("active", card.dataset.template === templateName));
}

function renderReportTemplate(templateName) {
  const reportCanvas = document.getElementById("reportCanvas");
  if (!reportCanvas) return;
  reportCanvas.className = `report-canvas ${templateName}-report`;
  if (templateName === "executive") reportCanvas.innerHTML = executiveTemplate();
  if (templateName === "performance") reportCanvas.innerHTML = performanceTemplate();
  if (templateName === "leadership") reportCanvas.innerHTML = leadershipTemplate();
  if (templateName === "brief") reportCanvas.innerHTML = briefTemplate();
  if (reportPreviewMode) reportCanvas.classList.add("report-preview");
}

function logoHtml() {
  return `<div class="report-logo"><img src="../logo.png" alt="Company Logo" onerror="this.style.display='none'; this.parentElement.textContent='Logo';"></div>`;
}

function watermarkHtml() {
  return `<img class="report-watermark-img" src="../logo.png" alt="" aria-hidden="true">`;
}

function inputField(key) {
  return `<input data-report-field="${key}" value="${escapeAttr(reportState[key])}">`;
}

function textField(key) {
  return `<textarea data-report-field="${key}">${escapeHtml(reportState[key])}</textarea>`;
}

function editableTitle(key, tag = "h2") {
  return `<${tag} contenteditable="true" data-report-field="${key}">${escapeHtml(reportState[key])}</${tag}>`;
}

function escapeHtml(value) {
  return String(value || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function escapeAttr(value) {
  return escapeHtml(value).replace(/"/g, "&quot;");
}

function metaGrid() {
  return `
    <label><span class="report-label">Report / Project</span>${inputField("reportName")}</label>
    <label><span class="report-label">Prepared By</span>${inputField("preparedBy")}</label>
    <label><span class="report-label">Period</span>${inputField("period")}</label>
    <label><span class="report-label">Date</span>${inputField("date")}</label>
  `;
}

function metricsHtml() {
  return `
    <div class="metric-card"><label><span class="report-label">Metric</span>${inputField("metric1Label")}</label><label><span class="report-label">Value</span>${inputField("metric1Value")}</label></div>
    <div class="metric-card"><label><span class="report-label">Metric</span>${inputField("metric2Label")}</label><label><span class="report-label">Value</span>${inputField("metric2Value")}</label></div>
    <div class="metric-card"><label><span class="report-label">Metric</span>${inputField("metric3Label")}</label><label><span class="report-label">Value</span>${inputField("metric3Value")}</label></div>
    <div class="metric-card"><label><span class="report-label">Metric</span>${inputField("metric4Label")}</label><label><span class="report-label">Value</span>${inputField("metric4Value")}</label></div>
  `;
}

function executiveTemplate() {
  return `
    ${watermarkHtml()}
    <div class="ex-head"><div>${editableTitle("title")}<p contenteditable="true" data-report-field="subtitle">${escapeHtml(reportState.subtitle)}</p></div>${logoHtml()}</div>
    <div class="ex-meta">${metaGrid()}</div>
    <div class="ex-body">
      <div class="project-overview"><div class="building-icon">▦</div><div><h3 class="report-title">Project Overview</h3>${textField("overview")}</div></div>
      <div class="report-section-label">Report Details</div><div class="report-panel">${textField("details")}</div>
      <div class="report-section-label">Executive Summary</div><div class="metric-grid">${metricsHtml()}</div><div class="report-panel" style="margin-top:12px;">${textField("executiveSummary")}</div>
      <div class="report-section-label">Customer Analytics</div><div class="report-panel">${textField("customerAnalytics")}</div>
      <div class="two-col"><div><div class="report-section-label">Campaign Analytics</div><div class="report-panel">${textField("campaignAnalytics")}</div></div><div><div class="report-section-label">Customer Service Analytics</div><div class="report-panel">${textField("serviceAnalytics")}</div></div></div>
      <div class="two-col"><div><div class="report-section-label">Loyalty, Consent & Geography</div><div class="report-panel">${textField("loyaltyConsentGeo")}</div></div><div><div class="report-section-label">Data Quality & Operational Tables</div><div class="report-panel">${textField("dataQualityOperations")}</div></div></div>
      <div class="report-section-label">Risks</div><div class="report-panel">${textField("risks")}</div>
      <div class="report-section-label">Notes</div><div class="report-panel">${textField("notes")}</div>
    </div>
  `;
}

function performanceTemplate() {
  return `
    ${watermarkHtml()}
    <div class="perf-head"><div>${editableTitle("title")}<p contenteditable="true" data-report-field="subtitle">${escapeHtml(reportState.subtitle)}</p></div>${logoHtml()}</div>
    <div class="perf-meta">${metaGrid()}</div>
    <div class="perf-kpis">${metricsHtml()}</div>
    <div class="perf-grid">
      <div class="perf-section"><h3 class="report-title">Project Overview</h3>${textField("overview")}</div>
      <div class="perf-section"><h3 class="report-title">Report Details</h3>${textField("details")}</div>
      <div class="perf-section"><h3 class="report-title">Executive Summary</h3>${textField("executiveSummary")}</div>
      <div class="perf-section"><h3 class="report-title">Customer Analytics</h3><div class="perf-chart">${textField("customerAnalytics")}</div></div>
      <div class="perf-section"><h3 class="report-title">Campaign Analytics</h3><div class="perf-chart">${textField("campaignAnalytics")}</div></div>
      <div class="perf-section"><h3 class="report-title">Customer Service Analytics</h3><div class="perf-chart">${textField("serviceAnalytics")}</div></div>
      <div class="perf-section"><h3 class="report-title">Loyalty, Consent & Geography</h3>${textField("loyaltyConsentGeo")}</div>
      <div class="perf-section"><h3 class="report-title">Data Quality & Operational Tables</h3>${textField("dataQualityOperations")}</div>
      <div class="perf-section"><h3 class="report-title">Risks</h3>${textField("risks")}</div>
      <div class="perf-section"><h3 class="report-title">Notes</h3>${textField("notes")}</div>
    </div>
  `;
}

function leadershipTemplate() {
  return `
    ${watermarkHtml()}
    <div class="lead-head"><div>${editableTitle("title")}<p contenteditable="true" data-report-field="subtitle">${escapeHtml(reportState.subtitle)}</p></div>${logoHtml()}</div>
    <div class="lead-cards">
      <div class="lead-card wide"><h3 class="report-title">Project Overview</h3>${textField("overview")}</div>
      <div class="lead-card"><h3 class="report-title">Report Details</h3>${textField("details")}</div>
      <div class="lead-card wide"><h3 class="report-title">Executive Summary</h3><div class="metric-grid">${metricsHtml()}</div>${textField("executiveSummary")}</div>
      <div class="lead-card"><h3 class="report-title">Customer Analytics</h3>${textField("customerAnalytics")}</div>
      <div class="lead-card"><h3 class="report-title">Campaign Analytics</h3>${textField("campaignAnalytics")}</div>
      <div class="lead-card"><h3 class="report-title">Customer Service Analytics</h3>${textField("serviceAnalytics")}</div>
      <div class="lead-card"><h3 class="report-title">Loyalty, Consent & Geography</h3>${textField("loyaltyConsentGeo")}</div>
      <div class="lead-card"><h3 class="report-title">Data Quality & Operations</h3>${textField("dataQualityOperations")}</div>
      <div class="lead-card"><h3 class="report-title">Risks</h3>${textField("risks")}</div>
      <div class="lead-card wide"><h3 class="report-title">Notes</h3>${textField("notes")}</div>
    </div>
  `;
}

function briefTemplate() {
  return `
    ${watermarkHtml()}
    <div class="brief-head"><div>${editableTitle("title")}<p contenteditable="true" data-report-field="subtitle">${escapeHtml(reportState.subtitle)}</p></div>${logoHtml()}</div>
    <div class="brief-body">
      <div class="brief-box"><h3 class="report-title">Report Details</h3><div class="metric-grid">${metaGrid()}</div></div>
      <div class="metric-grid" style="margin:12px 0;">${metricsHtml()}</div>
      <div class="brief-grid">
        <div class="brief-box"><h3 class="report-title">Project Overview</h3>${textField("overview")}</div>
        <div class="brief-box"><h3 class="report-title">Executive Summary</h3>${textField("executiveSummary")}</div>
        <div class="brief-box"><h3 class="report-title">Customer Analytics</h3>${textField("customerAnalytics")}</div>
        <div class="brief-box"><h3 class="report-title">Campaign Analytics</h3>${textField("campaignAnalytics")}</div>
        <div class="brief-box"><h3 class="report-title">Customer Service Analytics</h3>${textField("serviceAnalytics")}</div>
        <div class="brief-box"><h3 class="report-title">Loyalty, Consent & Geography</h3>${textField("loyaltyConsentGeo")}</div>
        <div class="brief-box"><h3 class="report-title">Data Quality & Operations</h3>${textField("dataQualityOperations")}</div>
        <div class="brief-box"><h3 class="report-title">Risks & Notes</h3>${textField("risks")}${textField("notes")}</div>
      </div>
    </div>
  `;
}

function toggleReportPreview() {
  collectReportState();
  reportPreviewMode = !reportPreviewMode;
  const reportCanvas = document.getElementById("reportCanvas");
  const previewBtn = document.getElementById("previewBtn");
  if (!reportCanvas || !previewBtn) return;
  reportCanvas.classList.toggle("report-preview", reportPreviewMode);
  previewBtn.textContent = reportPreviewMode ? "Edit" : "Preview";
}

function downloadReportPdf() {
  collectReportState();
  const reportCanvas = document.getElementById("reportCanvas");
  const wasPreview = reportPreviewMode;
  if (reportCanvas) reportCanvas.classList.add("report-preview");
  window.print();
  if (reportCanvas && !wasPreview) reportCanvas.classList.remove("report-preview");
}

function downloadReportWord() {
  collectReportState();
  const reportCanvas = document.getElementById("reportCanvas");
  if (!reportCanvas) return;
  const title = `${activeReportTemplate}-report-${Date.now()}`;
  const html = `<html><head><meta charset="UTF-8"><title>${title}</title><style>body{font-family:Arial,Helvetica,sans-serif;color:#1f2937;}img{max-width:520px;}textarea,input{border:none;font:inherit;width:100%;}table{width:100%;border-collapse:collapse;}th,td{border:1px solid #e5e7eb;padding:8px;}</style></head><body>${reportCanvas.innerHTML}</body></html>`;
  const blob = new Blob([html], { type: "application/msword" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = `${title}.doc`;
  link.click();
  URL.revokeObjectURL(link.href);
}
/* =====================================================
   REPORTS PREVIEW LOCK FIX
   Add this at the END of js/Reports.js
   Keeps existing function names and overrides only behavior.
===================================================== */

function setReportEditability(isEditable) {
  const reportCanvas = document.getElementById("reportCanvas");
  if (!reportCanvas) return;

  reportCanvas.querySelectorAll("input, textarea").forEach(field => {
    field.readOnly = !isEditable;
    field.tabIndex = isEditable ? 0 : -1;
  });

  reportCanvas.querySelectorAll("[contenteditable]").forEach(field => {
    field.setAttribute("contenteditable", isEditable ? "true" : "false");
    field.tabIndex = isEditable ? 0 : -1;
  });
}

function toggleReportPreview() {
  collectReportState();
  reportPreviewMode = !reportPreviewMode;

  const reportCanvas = document.getElementById("reportCanvas");
  const previewBtn = document.getElementById("previewBtn");
  if (!reportCanvas || !previewBtn) return;

  reportCanvas.classList.toggle("report-preview", reportPreviewMode);
  previewBtn.textContent = reportPreviewMode ? "Edit" : "Preview";

  setReportEditability(!reportPreviewMode);
}

function renderReportTemplate(templateName) {
  const reportCanvas = document.getElementById("reportCanvas");
  if (!reportCanvas) return;

  reportCanvas.className = `report-canvas ${templateName}-report`;

  if (templateName === "executive") reportCanvas.innerHTML = executiveTemplate();
  if (templateName === "performance") reportCanvas.innerHTML = performanceTemplate();
  if (templateName === "leadership") reportCanvas.innerHTML = leadershipTemplate();
  if (templateName === "brief") reportCanvas.innerHTML = briefTemplate();

  if (reportPreviewMode) reportCanvas.classList.add("report-preview");
  setReportEditability(!reportPreviewMode);
}

function downloadReportPdf() {
  collectReportState();

  const reportCanvas = document.getElementById("reportCanvas");
  const wasPreview = reportPreviewMode;

  if (reportCanvas) reportCanvas.classList.add("report-preview");
  setReportEditability(false);

  window.print();

  if (reportCanvas && !wasPreview) reportCanvas.classList.remove("report-preview");
  setReportEditability(!wasPreview);
}
/* =====================================================
   REPORTS DASHBOARD EXPORT IMPORT + CHART RENDERING
   Add this at the END of js/Reports.js
   Keeps current HTML file names and existing function names.
===================================================== */

function getChartsForSection(sectionName) {
  const charts = reportState.dashboardCharts || [];
  const section = String(sectionName || "").toLowerCase();

  return charts.filter(chart => {
    const title = String(chart.title || "").toLowerCase();
    if (section === "customer") return title.includes("customer") || title.includes("segmentation") || title.includes("churn") || title.includes("age");
    if (section === "campaign") return title.includes("campaign");
    if (section === "service") return title.includes("ticket") || title.includes("sla");
    if (section === "loyalty") return title.includes("loyalty") || title.includes("consent") || title.includes("cities") || title.includes("city") || title.includes("membership");
    if (section === "data") return title.includes("data quality");
    return false;
  });
}

function chartGalleryHtml(sectionName) {
  const charts = getChartsForSection(sectionName);
  if (!charts.length) return "";

  return `
    <div class="report-chart-gallery">
      ${charts.map(chart => `
        <figure class="report-chart-figure">
          <figcaption>${escapeHtml(chart.title)}</figcaption>
          <img src="${chart.image}" alt="${escapeAttr(chart.title)}">
        </figure>
      `).join("")}
    </div>
  `;
}

function dashboardTablesHtml() {
  const tables = reportState.dashboardTables || [];
  if (!tables.length) return "";

  return `
    <div class="report-table-gallery">
      ${tables.map(table => `
        <div class="report-table-block">
          <h4>${escapeHtml(table.title || "Dashboard Table")}</h4>
          ${table.html || ""}
        </div>
      `).join("")}
    </div>
  `;
}

function executiveTemplate() {
  return `
    ${watermarkHtml()}
    <div class="ex-head"><div>${editableTitle("title")}<p contenteditable="true" data-report-field="subtitle">${escapeHtml(reportState.subtitle)}</p></div>${logoHtml()}</div>
    <div class="ex-meta">${metaGrid()}</div>
    <div class="ex-body">
      <div class="project-overview"><div class="building-icon">▦</div><div><h3 class="report-title">Project Overview</h3>${textField("overview")}</div></div>
      <div class="report-section-label">Report Details</div><div class="report-panel">${textField("details")}</div>
      <div class="report-section-label">Executive Summary</div><div class="metric-grid">${metricsHtml()}</div><div class="report-panel" style="margin-top:12px;">${textField("executiveSummary")}</div>
      <div class="report-section-label">Customer Analytics</div><div class="report-panel">${textField("customerAnalytics")}${chartGalleryHtml("customer")}</div>
      <div class="two-col"><div><div class="report-section-label">Campaign Analytics</div><div class="report-panel">${textField("campaignAnalytics")}${chartGalleryHtml("campaign")}</div></div><div><div class="report-section-label">Customer Service Analytics</div><div class="report-panel">${textField("serviceAnalytics")}${chartGalleryHtml("service")}</div></div></div>
      <div class="two-col"><div><div class="report-section-label">Loyalty, Consent & Geography</div><div class="report-panel">${textField("loyaltyConsentGeo")}${chartGalleryHtml("loyalty")}</div></div><div><div class="report-section-label">Data Quality & Operational Tables</div><div class="report-panel">${textField("dataQualityOperations")}${chartGalleryHtml("data")}${dashboardTablesHtml()}</div></div></div>
      <div class="report-section-label">Risks</div><div class="report-panel">${textField("risks")}</div>
      <div class="report-section-label">Notes</div><div class="report-panel">${textField("notes")}</div>
    </div>
  `;
}

function performanceTemplate() {
  return `
    ${watermarkHtml()}
    <div class="perf-head"><div>${editableTitle("title")}<p contenteditable="true" data-report-field="subtitle">${escapeHtml(reportState.subtitle)}</p></div>${logoHtml()}</div>
    <div class="perf-meta">${metaGrid()}</div>
    <div class="perf-kpis">${metricsHtml()}</div>
    <div class="perf-grid">
      <div class="perf-section"><h3 class="report-title">Project Overview</h3>${textField("overview")}</div>
      <div class="perf-section"><h3 class="report-title">Report Details</h3>${textField("details")}</div>
      <div class="perf-section"><h3 class="report-title">Executive Summary</h3>${textField("executiveSummary")}</div>
      <div class="perf-section"><h3 class="report-title">Customer Analytics</h3><div class="perf-chart">${textField("customerAnalytics")}${chartGalleryHtml("customer")}</div></div>
      <div class="perf-section"><h3 class="report-title">Campaign Analytics</h3><div class="perf-chart">${textField("campaignAnalytics")}${chartGalleryHtml("campaign")}</div></div>
      <div class="perf-section"><h3 class="report-title">Customer Service Analytics</h3><div class="perf-chart">${textField("serviceAnalytics")}${chartGalleryHtml("service")}</div></div>
      <div class="perf-section"><h3 class="report-title">Loyalty, Consent & Geography</h3>${textField("loyaltyConsentGeo")}${chartGalleryHtml("loyalty")}</div>
      <div class="perf-section"><h3 class="report-title">Data Quality & Operational Tables</h3>${textField("dataQualityOperations")}${chartGalleryHtml("data")}${dashboardTablesHtml()}</div>
      <div class="perf-section"><h3 class="report-title">Risks</h3>${textField("risks")}</div>
      <div class="perf-section"><h3 class="report-title">Notes</h3>${textField("notes")}</div>
    </div>
  `;
}

function leadershipTemplate() {
  return `
    ${watermarkHtml()}
    <div class="lead-head"><div>${editableTitle("title")}<p contenteditable="true" data-report-field="subtitle">${escapeHtml(reportState.subtitle)}</p></div>${logoHtml()}</div>
    <div class="lead-cards">
      <div class="lead-card wide"><h3 class="report-title">Project Overview</h3>${textField("overview")}</div>
      <div class="lead-card"><h3 class="report-title">Report Details</h3>${textField("details")}</div>
      <div class="lead-card wide"><h3 class="report-title">Executive Summary</h3><div class="metric-grid">${metricsHtml()}</div>${textField("executiveSummary")}</div>
      <div class="lead-card"><h3 class="report-title">Customer Analytics</h3>${textField("customerAnalytics")}${chartGalleryHtml("customer")}</div>
      <div class="lead-card"><h3 class="report-title">Campaign Analytics</h3>${textField("campaignAnalytics")}${chartGalleryHtml("campaign")}</div>
      <div class="lead-card"><h3 class="report-title">Customer Service Analytics</h3>${textField("serviceAnalytics")}${chartGalleryHtml("service")}</div>
      <div class="lead-card"><h3 class="report-title">Loyalty, Consent & Geography</h3>${textField("loyaltyConsentGeo")}${chartGalleryHtml("loyalty")}</div>
      <div class="lead-card"><h3 class="report-title">Data Quality & Operations</h3>${textField("dataQualityOperations")}${chartGalleryHtml("data")}${dashboardTablesHtml()}</div>
      <div class="lead-card"><h3 class="report-title">Risks</h3>${textField("risks")}</div>
      <div class="lead-card wide"><h3 class="report-title">Notes</h3>${textField("notes")}</div>
    </div>
  `;
}

function briefTemplate() {
  return `
    ${watermarkHtml()}
    <div class="brief-head"><div>${editableTitle("title")}<p contenteditable="true" data-report-field="subtitle">${escapeHtml(reportState.subtitle)}</p></div>${logoHtml()}</div>
    <div class="brief-body">
      <div class="brief-box"><h3 class="report-title">Report Details</h3><div class="metric-grid">${metaGrid()}</div></div>
      <div class="metric-grid" style="margin:12px 0;">${metricsHtml()}</div>
      <div class="brief-grid">
        <div class="brief-box"><h3 class="report-title">Project Overview</h3>${textField("overview")}</div>
        <div class="brief-box"><h3 class="report-title">Executive Summary</h3>${textField("executiveSummary")}</div>
        <div class="brief-box"><h3 class="report-title">Customer Analytics</h3>${textField("customerAnalytics")}${chartGalleryHtml("customer")}</div>
        <div class="brief-box"><h3 class="report-title">Campaign Analytics</h3>${textField("campaignAnalytics")}${chartGalleryHtml("campaign")}</div>
        <div class="brief-box"><h3 class="report-title">Customer Service Analytics</h3>${textField("serviceAnalytics")}${chartGalleryHtml("service")}</div>
        <div class="brief-box"><h3 class="report-title">Loyalty, Consent & Geography</h3>${textField("loyaltyConsentGeo")}${chartGalleryHtml("loyalty")}</div>
        <div class="brief-box"><h3 class="report-title">Data Quality & Operations</h3>${textField("dataQualityOperations")}${chartGalleryHtml("data")}${dashboardTablesHtml()}</div>
        <div class="brief-box"><h3 class="report-title">Risks & Notes</h3>${textField("risks")}${textField("notes")}</div>
      </div>
    </div>
  `;
}

function renderReportTemplate(templateName) {
  const reportCanvas = document.getElementById("reportCanvas");
  if (!reportCanvas) return;

  reportCanvas.className = `report-canvas ${templateName}-report`;

  if (templateName === "executive") reportCanvas.innerHTML = executiveTemplate();
  if (templateName === "performance") reportCanvas.innerHTML = performanceTemplate();
  if (templateName === "leadership") reportCanvas.innerHTML = leadershipTemplate();
  if (templateName === "brief") reportCanvas.innerHTML = briefTemplate();

  if (reportPreviewMode) reportCanvas.classList.add("report-preview");
  if (typeof setReportEditability === "function") setReportEditability(!reportPreviewMode);
}
/* =====================================================
   REPORTS: SHOW ALL DASHBOARD KPI CARDS + CHARTS
   Add this at the VERY END of js/Reports.js
   This keeps current names and overrides only template rendering helpers.
===================================================== */

function allDashboardKpiCardsHtml() {
  const kpis = reportState.dashboardKpis || [];

  if (!kpis.length) {
    return `<div class="metric-grid">${metricsHtml()}</div>`;
  }

  return `
    <div class="report-kpi-card-grid">
      ${kpis.map(kpi => `
        <article class="report-kpi-card">
          <span>${escapeHtml(kpi.source || "Dashboard")}</span>
          <h4>${escapeHtml(kpi.title || "KPI")}</h4>
          <strong>${escapeHtml(kpi.value || "-")}</strong>
          <small>${escapeHtml(kpi.note || "")}</small>
        </article>
      `).join("")}
    </div>
  `;
}

function getChartsForSection(sectionName) {
  const charts = reportState.dashboardCharts || [];
  const section = String(sectionName || "").toLowerCase();

  return charts.filter(chart => {
    const title = String(chart.title || "").toLowerCase();
    const id = String(chart.id || "").toLowerCase();
    const combined = `${title} ${id}`;

    if (section === "customer") return /customer|segment|churn|age/.test(combined);
    if (section === "campaign") return /campaign/.test(combined);
    if (section === "service") return /ticket|sla|service/.test(combined);
    if (section === "loyalty") return /loyalty|consent|city|cities|membership/.test(combined);
    if (section === "data") return /data|quality/.test(combined);
    return false;
  });
}

function chartGalleryHtml(sectionName) {
  const charts = getChartsForSection(sectionName);
  if (!charts.length) {
    return `<p class="report-chart-empty">No chart image exported for this section yet. Go back to Dashboard, wait for charts to finish loading, then click Export.</p>`;
  }

  return `
    <div class="report-chart-gallery">
      ${charts.map(chart => `
        <figure class="report-chart-figure">
          <figcaption>${escapeHtml(chart.title)}</figcaption>
          <img src="${chart.image}" alt="${escapeAttr(chart.title)}">
        </figure>
      `).join("")}
    </div>
  `;
}

function dashboardTablesHtml() {
  const tables = reportState.dashboardTables || [];
  if (!tables.length) return "";

  return `
    <div class="report-table-gallery">
      ${tables.map(table => `
        <div class="report-table-block">
          <h4>${escapeHtml(table.title || "Dashboard Table")}</h4>
          ${table.html || ""}
        </div>
      `).join("")}
    </div>
  `;
}

function executiveTemplate() {
  return `
    ${watermarkHtml()}
    <div class="ex-head"><div>${editableTitle("title")}<p contenteditable="true" data-report-field="subtitle">${escapeHtml(reportState.subtitle)}</p></div>${logoHtml()}</div>
    <div class="ex-meta">${metaGrid()}</div>
    <div class="ex-body">
      <div class="project-overview"><div class="building-icon">▦</div><div><h3 class="report-title">Project Overview</h3>${textField("overview")}</div></div>
      <div class="report-section-label">Report Details</div><div class="report-panel">${textField("details")}</div>
      <div class="report-section-label">Executive Summary</div><div class="report-panel">${allDashboardKpiCardsHtml()}${textField("executiveSummary")}</div>
      <div class="report-section-label">Customer Analytics</div><div class="report-panel">${textField("customerAnalytics")}${chartGalleryHtml("customer")}</div>
      <div class="two-col"><div><div class="report-section-label">Campaign Analytics</div><div class="report-panel">${textField("campaignAnalytics")}${chartGalleryHtml("campaign")}</div></div><div><div class="report-section-label">Customer Service Analytics</div><div class="report-panel">${textField("serviceAnalytics")}${chartGalleryHtml("service")}</div></div></div>
      <div class="two-col"><div><div class="report-section-label">Loyalty, Consent & Geography</div><div class="report-panel">${textField("loyaltyConsentGeo")}${chartGalleryHtml("loyalty")}</div></div><div><div class="report-section-label">Data Quality & Operational Tables</div><div class="report-panel">${textField("dataQualityOperations")}${chartGalleryHtml("data")}${dashboardTablesHtml()}</div></div></div>
      <div class="report-section-label">Risks</div><div class="report-panel">${textField("risks")}</div>
      <div class="report-section-label">Notes</div><div class="report-panel">${textField("notes")}</div>
    </div>
  `;
}

function performanceTemplate() {
  return `
    ${watermarkHtml()}
    <div class="perf-head"><div>${editableTitle("title")}<p contenteditable="true" data-report-field="subtitle">${escapeHtml(reportState.subtitle)}</p></div>${logoHtml()}</div>
    <div class="perf-meta">${metaGrid()}</div>
    <div class="perf-kpis">${allDashboardKpiCardsHtml()}</div>
    <div class="perf-grid">
      <div class="perf-section"><h3 class="report-title">Project Overview</h3>${textField("overview")}</div>
      <div class="perf-section"><h3 class="report-title">Report Details</h3>${textField("details")}</div>
      <div class="perf-section"><h3 class="report-title">Executive Summary</h3>${textField("executiveSummary")}</div>
      <div class="perf-section"><h3 class="report-title">Customer Analytics</h3><div class="perf-chart">${textField("customerAnalytics")}${chartGalleryHtml("customer")}</div></div>
      <div class="perf-section"><h3 class="report-title">Campaign Analytics</h3><div class="perf-chart">${textField("campaignAnalytics")}${chartGalleryHtml("campaign")}</div></div>
      <div class="perf-section"><h3 class="report-title">Customer Service Analytics</h3><div class="perf-chart">${textField("serviceAnalytics")}${chartGalleryHtml("service")}</div></div>
      <div class="perf-section"><h3 class="report-title">Loyalty, Consent & Geography</h3>${textField("loyaltyConsentGeo")}${chartGalleryHtml("loyalty")}</div>
      <div class="perf-section"><h3 class="report-title">Data Quality & Operational Tables</h3>${textField("dataQualityOperations")}${chartGalleryHtml("data")}${dashboardTablesHtml()}</div>
      <div class="perf-section"><h3 class="report-title">Risks</h3>${textField("risks")}</div>
      <div class="perf-section"><h3 class="report-title">Notes</h3>${textField("notes")}</div>
    </div>
  `;
}

function leadershipTemplate() {
  return `
    ${watermarkHtml()}
    <div class="lead-head"><div>${editableTitle("title")}<p contenteditable="true" data-report-field="subtitle">${escapeHtml(reportState.subtitle)}</p></div>${logoHtml()}</div>
    <div class="lead-cards">
      <div class="lead-card wide"><h3 class="report-title">Project Overview</h3>${textField("overview")}</div>
      <div class="lead-card"><h3 class="report-title">Report Details</h3>${textField("details")}</div>
      <div class="lead-card wide"><h3 class="report-title">Executive Summary</h3>${allDashboardKpiCardsHtml()}${textField("executiveSummary")}</div>
      <div class="lead-card"><h3 class="report-title">Customer Analytics</h3>${textField("customerAnalytics")}${chartGalleryHtml("customer")}</div>
      <div class="lead-card"><h3 class="report-title">Campaign Analytics</h3>${textField("campaignAnalytics")}${chartGalleryHtml("campaign")}</div>
      <div class="lead-card"><h3 class="report-title">Customer Service Analytics</h3>${textField("serviceAnalytics")}${chartGalleryHtml("service")}</div>
      <div class="lead-card"><h3 class="report-title">Loyalty, Consent & Geography</h3>${textField("loyaltyConsentGeo")}${chartGalleryHtml("loyalty")}</div>
      <div class="lead-card"><h3 class="report-title">Data Quality & Operations</h3>${textField("dataQualityOperations")}${chartGalleryHtml("data")}${dashboardTablesHtml()}</div>
      <div class="lead-card"><h3 class="report-title">Risks</h3>${textField("risks")}</div>
      <div class="lead-card wide"><h3 class="report-title">Notes</h3>${textField("notes")}</div>
    </div>
  `;
}

function briefTemplate() {
  return `
    ${watermarkHtml()}
    <div class="brief-head"><div>${editableTitle("title")}<p contenteditable="true" data-report-field="subtitle">${escapeHtml(reportState.subtitle)}</p></div>${logoHtml()}</div>
    <div class="brief-body">
      <div class="brief-box"><h3 class="report-title">Report Details</h3><div class="metric-grid">${metaGrid()}</div></div>
      <div style="margin:12px 0;">${allDashboardKpiCardsHtml()}</div>
      <div class="brief-grid">
        <div class="brief-box"><h3 class="report-title">Project Overview</h3>${textField("overview")}</div>
        <div class="brief-box"><h3 class="report-title">Executive Summary</h3>${textField("executiveSummary")}</div>
        <div class="brief-box"><h3 class="report-title">Customer Analytics</h3>${textField("customerAnalytics")}${chartGalleryHtml("customer")}</div>
        <div class="brief-box"><h3 class="report-title">Campaign Analytics</h3>${textField("campaignAnalytics")}${chartGalleryHtml("campaign")}</div>
        <div class="brief-box"><h3 class="report-title">Customer Service Analytics</h3>${textField("serviceAnalytics")}${chartGalleryHtml("service")}</div>
        <div class="brief-box"><h3 class="report-title">Loyalty, Consent & Geography</h3>${textField("loyaltyConsentGeo")}${chartGalleryHtml("loyalty")}</div>
        <div class="brief-box"><h3 class="report-title">Data Quality & Operations</h3>${textField("dataQualityOperations")}${chartGalleryHtml("data")}${dashboardTablesHtml()}</div>
        <div class="brief-box"><h3 class="report-title">Risks & Notes</h3>${textField("risks")}${textField("notes")}</div>
      </div>
    </div>
  `;
}

function renderReportTemplate(templateName) {
  const reportCanvas = document.getElementById("reportCanvas");
  if (!reportCanvas) return;

  reportCanvas.className = `report-canvas ${templateName}-report`;

  if (templateName === "executive") reportCanvas.innerHTML = executiveTemplate();
  if (templateName === "performance") reportCanvas.innerHTML = performanceTemplate();
  if (templateName === "leadership") reportCanvas.innerHTML = leadershipTemplate();
  if (templateName === "brief") reportCanvas.innerHTML = briefTemplate();

  if (reportPreviewMode) reportCanvas.classList.add("report-preview");
  if (typeof setReportEditability === "function") setReportEditability(!reportPreviewMode);
}
/* =====================================================
   REPORT PRINT TEXTAREA HEIGHT FIX
   Add this at the VERY END of js/Reports.js
   Helps printed PDF avoid text clipping/missing words.
===================================================== */

function resizeReportTextareasForPrint() {
  document.querySelectorAll("#reportCanvas textarea").forEach(textarea => {
    textarea.dataset.oldHeight = textarea.style.height || "";
    textarea.style.height = "auto";
    textarea.style.height = `${textarea.scrollHeight}px`;
  });
}

function restoreReportTextareasAfterPrint() {
  document.querySelectorAll("#reportCanvas textarea").forEach(textarea => {
    textarea.style.height = textarea.dataset.oldHeight || "";
    delete textarea.dataset.oldHeight;
  });
}

window.addEventListener("beforeprint", resizeReportTextareasForPrint);
window.addEventListener("afterprint", restoreReportTextareasAfterPrint);

const originalDownloadReportPdfForLayout = downloadReportPdf;
downloadReportPdf = function () {
  resizeReportTextareasForPrint();
  originalDownloadReportPdfForLayout();
  setTimeout(restoreReportTextareasAfterPrint, 800);
};
