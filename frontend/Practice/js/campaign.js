let campaignState = {
  campaigns: [],
  templates: [],
  selectedCampaignId: null,
  latestMetrics: null,
  latestResponses: [],
  dailySummary: null,
  historyPage: 1,
  responsesPage: 1,
  historyPageSize: 10,
  responsesPageSize: 10
};
 
const API_BASE_URL =
  localStorage.getItem("omnilink_api_base") || "http://127.0.0.1:8000";
 
function getAuthHeaders() {
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${localStorage.getItem("omnilink_token") || ""}`
  };
}
 
async function apiRequest(path, method = "GET", body = null) {
  const options = {
    method,
    headers: getAuthHeaders()
  };
 
  if (body !== null) {
    options.body = JSON.stringify(body);
  }
 
  const response = await fetch(`${API_BASE_URL}${path}`, options);
 
  let data = null;
 
  try {
    data = await response.json();
  } catch (error) {
    data = null;
  }
 
  if (!response.ok) {
    const message =
      data && data.detail
        ? data.detail
        : `API error ${response.status}: ${response.statusText}`;
 
    throw new Error(message);
  }
 
  return data;
}
 
function apiGet(path) {
  return apiRequest(path, "GET");
}

function apiGetCached(cacheKey, path, ttlMilliseconds) {
  if (typeof cachedApiGet === "function") {
    return cachedApiGet(cacheKey, path, ttlMilliseconds);
  }

  return apiGet(path);
}

function clearCampaignFrontendCache() {
  if (typeof clearCachedApiPrefix === "function") {
    clearCachedApiPrefix("campaign-");
  }

  if (typeof clearCachedApiData === "function") {
    clearCachedApiData("dashboard-summary");
    clearCachedApiData("admin-summary");
  }
}

 
function apiSend(path, method, body) {
  return apiRequest(path, method, body);
}
 
async function initCampaignModule() {
  try {
    await Promise.all([
      loadCampaigns(),
      loadCampaignTemplates(),
      loadCampaignDailySummary()
    ]);
 
    renderAllCampaignDropdowns();
    renderTemplateDropdowns();
    renderCampaignDashboard();
    renderCampaignHistory();
    renderResponses();
    renderDailyMetrics();
    loadSendPreview();
  } catch (error) {
    console.error(error);
    alert(`Campaign module failed to load: ${error.message}`);
  }
}
 
function switchCampaignTab(tabName, buttonEl) {
  document.querySelectorAll(".campaign-tab-panel").forEach((panel) => {
    panel.classList.remove("active");
  });
 
  document.querySelectorAll(".tab-btn").forEach((button) => {
    button.classList.remove("active");
  });
 
  const selectedPanel = document.getElementById(`tab-${tabName}`);
 
  if (selectedPanel) {
    selectedPanel.classList.add("active");
  }
 
  if (buttonEl) {
    buttonEl.classList.add("active");
  }
 
  if (tabName === "dashboard") {
    loadCampaignDailySummary();
  }
 
  if (tabName === "history") {
    loadCampaigns();
  }
 
  if (tabName === "templates") {
    loadCampaignTemplates();
  }
 
  if (tabName === "metrics") {
    loadCampaignDailySummary();
  }
 
  if (tabName === "send") {
    loadSendPreview();
  }
 
  if (tabName === "responses") {
    const campaignId =
      getValue("responsesCampaignSelect") || campaignState.selectedCampaignId;
 
    if (campaignId) {
      loadCampaignResponses(campaignId);
    }
  }
}
 
async function loadCampaigns() {
  const result = await apiGetCached("campaign-list", "/campaigns", 30000);
  campaignState.campaigns = toList(result);
  campaignState.historyPage = 1;
 
  if (!campaignState.selectedCampaignId && campaignState.campaigns.length > 0) {
    campaignState.selectedCampaignId = getCampaignId(campaignState.campaigns[0]);
  }
 
  renderAllCampaignDropdowns();
  renderCampaignHistory();
 
  return campaignState.campaigns;
}
 
async function loadCampaignTemplates() {
  const result = await apiGetCached("campaign-templates", "/campaigns/templates", 600000);
  campaignState.templates = toList(result);
 
  renderTemplateDropdowns();
  renderTemplateEditorFromSelected();
 
  return campaignState.templates;
}
 
async function loadCampaignDailySummary() {
  const result = await apiGetCached("campaign-daily-summary", "/campaigns/summary/daily", 30000);
  campaignState.dailySummary = result;
 
  renderCampaignDashboard();
  renderDailyMetrics();
 
  return result;
}
 
async function loadCampaignMetrics(campaignId) {
  if (!campaignId) return null;
 
  const result = await apiGetCached(`campaign-metrics-${campaignId}`, `/campaigns/${campaignId}/metrics`, 30000);
  campaignState.latestMetrics = result;
 
  renderSelectedCampaignMetrics(result);
 
  return result;
}
 
async function loadCampaignResponses(campaignId) {
  if (!campaignId) return [];
 
  const result = await apiGet(`/campaigns/${campaignId}/responses`);
  campaignState.latestResponses = toList(result);
  campaignState.responsesPage = 1;
 
  renderResponses();
 
  return campaignState.latestResponses;
}
 
async function createCampaignFromForm() {
  try {
    const payload = {
      campaign_name: getValue("campaignName"),
      campaign_type: getValue("campaignType"),
      business_channel: getValue("businessChannel"),
      demo_platform: getValue("deliveryPlatform"),
      target_segment: getValue("targetSegment"),
      template_id: getValue("createTemplateSelect"),
      campaign_objective: getValue("campaignObjective"),
      created_by: getValue("createdBy")
    };
 
    if (!payload.campaign_name) {
      alert("Please enter campaign name.");
      return;
    }
 
    if (!payload.template_id) {
      alert("Please select a template.");
      return;
    }
 
    if (!payload.created_by) {
      alert("Please enter creator name.");
      return;
    }
 
    const result = await apiSend("/campaigns", "POST", payload);
 
    setJson("createdCampaignPreview", result);
 
    campaignState.selectedCampaignId = getCampaignId(result);
 
    await loadCampaigns();
    await loadCampaignDailySummary();
 
    alert(`Campaign created successfully. ID: ${campaignState.selectedCampaignId}`);
  } catch (error) {
    console.error(error);
    alert(`Create campaign failed: ${error.message}`);
  }
}
 
function renderTemplateDropdowns() {
  const ids = ["templateSelect", "sendTemplateSelect", "createTemplateSelect"];
 
  const options = campaignState.templates
    .map((template) => {
      const id = getTemplateId(template);
      const name = template.template_name || template.name || id;
 
      return `<option value="${escapeAttr(id)}">${escapeHtml(name)}</option>`;
    })
    .join("");
 
  ids.forEach((id) => {
    const select = document.getElementById(id);
 
    if (select) {
      select.innerHTML = options || `<option value="">No templates found</option>`;
    }
  });
}
async function saveTemplate() {
  try {
    const rawValue = getValue("templateJsonEditor");
 
    if (!rawValue) {
      alert("Template JSON is empty.");
      return;
    }
 
    const parsed = JSON.parse(rawValue);
 
    let payload = {};
 
    // Case 1: User writes backend-style JSON
    if (parsed.template_json) {
      payload = {
        template_name: parsed.template_name || parsed.name || "Untitled Template",
        template_type: parsed.template_type || parsed.type || "General",
        template_json: parsed.template_json
      };
    }
 
    // Case 2: User writes simple JSON directly with title/body
    else {
      payload = {
        template_name: parsed.template_name || parsed.name || "Untitled Template",
        template_type: parsed.template_type || parsed.type || "General",
        template_json: {
          title: parsed.title || "",
          body: parsed.body || "",
          cta_text: parsed.cta_text || "",
          cta_url: parsed.cta_url || "",
          footer: parsed.footer || ""
        }
      };
    }
 
    if (!payload.template_name) {
      alert("template_name is required.");
      return;
    }
 
    if (!payload.template_json.title) {
      alert("template_json.title is required.");
      return;
    }
 
    if (!payload.template_json.body) {
      alert("template_json.body is required.");
      return;
    }
 
    if (!payload.template_json.cta_text) {
      alert("template_json.cta_text is required.");
      return;
    }
 
    if (!payload.template_json.footer) {
      payload.template_json.footer = "";
    }
 
    const saved = await apiSend("/campaigns/templates", "POST", payload);
 
    await loadCampaignTemplates();
 
    const savedId =
      saved.template_id ||
      saved.data?.template_id ||
      saved.id ||
      "";
 
    if (savedId) {
      setSelectValue("templateSelect", savedId);
      setSelectValue("sendTemplateSelect", savedId);
      setSelectValue("createTemplateSelect", savedId);
    }
 
    renderTemplatePreview(payload);
 
    alert("Template saved successfully.");
 
  } catch (error) {
    console.error(error);
    alert(`Save template failed: ${error.message}`);
  }
}
function loadSelectedTemplate() {
  renderTemplateEditorFromSelected();
}
 
function renderTemplateEditorFromSelected() {
  const selectedId = getValue("templateSelect");
  const rawTemplate = getTemplateById(selectedId) || campaignState.templates[0];
 
  if (!rawTemplate) {
    setValue("templateJsonEditor", "");
    setHtml("renderedTemplatePreview", "No template selected.");
    return;
  }
 
  const template = normalizeTemplateForFrontend(rawTemplate);
 
  const editableJson = {
    template_name: template.template_name,
    template_type: template.template_type,
    template_json: template.template_json
  };
 
  setValue("templateJsonEditor", JSON.stringify(editableJson, null, 2));
  renderTemplatePreview(template);
}
 
function resetTemplateEditor() {
  renderTemplateEditorFromSelected();
}
 
function normalizeTemplateForFrontend(template) {
  if (!template) return null;
 
  let templateJson = template.template_json || template;
 
  if (typeof templateJson === "string") {
    try {
      templateJson = JSON.parse(templateJson);
    } catch (error) {
      templateJson = {};
    }
  }
 
  return {
    template_id: template.template_id || template.id || "",
    template_name:
      template.template_name ||
      template.name ||
      templateJson.template_name ||
      "Untitled Template",
    template_type:
      template.template_type ||
      template.type ||
      templateJson.template_type ||
      "General",
    template_json: {
      title: templateJson.title || "",
      body: templateJson.body || "",
      cta_text: templateJson.cta_text || "",
      cta_url: templateJson.cta_url || "",
      footer: templateJson.footer || ""
    }
  };
}
 
function handleTemplateUpload(event) {
  const file = event.target.files[0];
 
  if (!file) return;
 
  if (!file.name.toLowerCase().endsWith(".json")) {
    alert("Please upload a JSON file.");
    return;
  }
 
  const reader = new FileReader();
 
  reader.onload = function (e) {
    try {
      const parsed = JSON.parse(e.target.result);
 
      setValue("templateJsonEditor", JSON.stringify(parsed, null, 2));
      renderTemplatePreview(parsed);
    } catch (error) {
      console.error(error);
      alert("Invalid JSON file.");
    }
  };
 
  reader.readAsText(file);
}
 
function renderTemplatePreview(template) {
  if (!template) {
    setHtml("renderedTemplatePreview", "No template selected.");
    return;
  }

  const normalized = normalizeTemplateForFrontend(template);
  const templateJson = normalized.template_json;

  const html = `
    <h4>${escapeHtml(templateJson.title || "No title")}</h4>
    <p>${escapeHtml(templateJson.body || "No body")}</p>
  `;

  setHtml("renderedTemplatePreview", html);
}
function loadSendPreview() {
  const campaignId =
    getValue("sendCampaignSelect") || campaignState.selectedCampaignId;
 
  const campaign = getCampaignById(campaignId);
 
  if (!campaign) {
    setJson("sendPayloadPreview", {
      message: "Select a campaign."
    });
 
    return;
  }
 
  const requestPayload = {
    endpoint: `/campaigns/${getCampaignId(campaign)}/simulate-send`,
    method: "POST",
    body: {
      max_send_count: 5
    }
  };
 
  setJson("sendPayloadPreview", requestPayload);
}
 
async function simulateCampaignSend() {
  try {
    const campaignId =
      getValue("sendCampaignSelect") || campaignState.selectedCampaignId;
 
    if (!campaignId) {
      alert("Please select a campaign.");
      return;
    }
 
    const result = await apiSend(`/campaigns/${campaignId}/simulate-send`, "POST", {
      max_send_count: 5
    });
 
    setJson("sendPayloadPreview", result);
 
    await loadCampaigns();
    await loadCampaignDailySummary();
    await loadCampaignMetrics(campaignId);
    await loadCampaignResponses(campaignId);
 
    alert(`Campaign processed. Sent: ${result.sent_count || result.sent || 0}`);
  } catch (error) {
    console.error(error);
    alert(`Send failed: ${error.message}`);
  }
}
 

function ensureTablePagination(tbodyId, paginationId) {
  const tbody = document.getElementById(tbodyId);
  if (!tbody) return null;
  const tableScroll = tbody.closest(".table-scroll");
  if (!tableScroll) return null;
  let pagination = document.getElementById(paginationId);
  if (!pagination) {
    pagination = document.createElement("div");
    pagination.id = paginationId;
    pagination.className = "table-pagination";
    tableScroll.insertAdjacentElement("afterend", pagination);
  }
  return pagination;
}

function renderTablePagination(paginationId, totalRows, page, pageSize, handlerName) {
  const pagination = document.getElementById(paginationId);
  if (!pagination) return;
  const totalPages = Math.max(1, Math.ceil(totalRows / pageSize));
  const start = totalRows ? (page - 1) * pageSize + 1 : 0;
  const end = Math.min(page * pageSize, totalRows);
  pagination.innerHTML = `
    <span>${start}-${end} of ${totalRows}</span>
    <div class="pagination-actions">
      <button type="button" class="secondary-btn compact-page-btn" onclick="${handlerName}(-1)" ${page <= 1 ? "disabled" : ""}>Prev</button>
      <span class="page-pill">${page} / ${totalPages}</span>
      <button type="button" class="secondary-btn compact-page-btn" onclick="${handlerName}(1)" ${page >= totalPages ? "disabled" : ""}>Next</button>
    </div>
  `;
}

function changeCampaignHistoryPage(direction) {
  const totalPages = Math.max(1, Math.ceil(campaignState.campaigns.length / campaignState.historyPageSize));
  campaignState.historyPage = Math.min(totalPages, Math.max(1, campaignState.historyPage + direction));
  renderCampaignHistory();
}

function changeCampaignResponsesPage(direction) {
  const totalPages = Math.max(1, Math.ceil(campaignState.latestResponses.length / campaignState.responsesPageSize));
  campaignState.responsesPage = Math.min(totalPages, Math.max(1, campaignState.responsesPage + direction));
  renderResponses();
}

function renderCampaignHistory() {
  ensureTablePagination("campaignHistoryBody", "campaignHistoryPagination");
  const totalRows = campaignState.campaigns.length;
  const pageSize = campaignState.historyPageSize;
  const totalPages = Math.max(1, Math.ceil(totalRows / pageSize));
  campaignState.historyPage = Math.min(totalPages, Math.max(1, campaignState.historyPage));
  const startIndex = (campaignState.historyPage - 1) * pageSize;
  const pageCampaigns = campaignState.campaigns.slice(startIndex, startIndex + pageSize);
  const rows = pageCampaigns.map((campaign) => {
    const id = getCampaignId(campaign);
    const removed = num(campaign, ["removed_count", "removed_due_to_consent_or_dnc"]) || num(campaign, ["no_consent_removed"]) + num(campaign, ["dnc_removed"]);
    return `
      <tr>
        <td>${escapeHtml(id)}</td>
        <td>${escapeHtml(campaign.campaign_name || campaign.name || "-")}</td>
        <td>${escapeHtml(campaign.campaign_type || "-")}</td>
        <td>${escapeHtml(campaign.business_channel || campaign.channel || "-")}</td>
        <td>${escapeHtml(campaign.demo_platform || "-")}</td>
        <td>${escapeHtml(campaign.target_segment || campaign.segment || "-")}</td>
        <td>${statusBadge(campaign.status || "-", statusType(campaign.status))}</td>
        <td>${num(campaign, ["total_audience", "audience"])}</td>
        <td>${num(campaign, ["eligible_count", "eligible_after_consent"])}</td>
        <td>${removed}</td>
        <td>${num(campaign, ["sent_count"])}</td>
        <td>${num(campaign, ["failed_count"])}</td>
        <td>${escapeHtml(campaign.created_by || "-")}</td>
        <td>${formatDateTime(campaign.created_at || campaign.created_date)}</td>
        <td>
          <button class="secondary-btn table-action-btn" onclick="historySimulateCampaign('${escapeAttr(id)}')">Send</button>
          <button class="secondary-btn table-action-btn" onclick="historyLoadResponses('${escapeAttr(id)}')">Responses</button>
          <button class="secondary-btn table-action-btn" onclick="historyLoadMetrics('${escapeAttr(id)}')">Metrics</button>
        </td>
      </tr>`;
  }).join("");
  setHtml("campaignHistoryBody", rows || emptyRow(15, "No campaigns found."));
  renderTablePagination("campaignHistoryPagination", totalRows, campaignState.historyPage, pageSize, "changeCampaignHistoryPage");
}

function historySimulateCampaign(campaignId) {
  campaignState.selectedCampaignId = campaignId;
 
  setSelectValue("sendCampaignSelect", campaignId);
  loadSendPreview();
  openTab("send");
}
 
async function historyLoadResponses(campaignId) {
  campaignState.selectedCampaignId = campaignId;
 
  setSelectValue("responsesCampaignSelect", campaignId);
  await loadCampaignResponses(campaignId);
 
  openTab("responses");
}
 
async function historyLoadMetrics(campaignId) {
  campaignState.selectedCampaignId = campaignId;
 
  setSelectValue("metricsCampaignSelect", campaignId);
  await loadCampaignMetrics(campaignId);
 
  openTab("metrics");
}
 
function onResponsesCampaignChange() {
  const campaignId = getValue("responsesCampaignSelect");
 
  campaignState.selectedCampaignId = campaignId;
 
  loadCampaignResponses(campaignId);
}
 

function normalizeResponseTableColumns() {
  const table = document.querySelector("#campaignResponsesBody")?.closest("table");
  if (!table) return;

  const headerCount = table.querySelectorAll("thead th").length;
  const rows = table.querySelectorAll("#campaignResponsesBody tr");

  rows.forEach((row) => {
    while (row.children.length > headerCount) {
      const extraIndex = Math.max(0, row.children.length - 2);
      row.children[extraIndex].remove();
    }
  });
}

function renderResponses() {
  ensureTablePagination("campaignResponsesBody", "campaignResponsesPagination");
  const totalRows = campaignState.latestResponses.length;
  const pageSize = campaignState.responsesPageSize;
  const totalPages = Math.max(1, Math.ceil(totalRows / pageSize));
  campaignState.responsesPage = Math.min(totalPages, Math.max(1, campaignState.responsesPage));
  const startIndex = (campaignState.responsesPage - 1) * pageSize;
  const pageResponses = campaignState.latestResponses.slice(startIndex, startIndex + pageSize);
  const rows = pageResponses.map((response) => `
      <tr>
        <td>${escapeHtml(response.customer_id || "-")}</td>
        <td>${escapeHtml(response.customer_name || "-")}</td>
        <td>${escapeHtml(response.business_channel || "-")}</td>
        <td>${escapeHtml(response.demo_platform || "-")}</td>
        <td>${statusBadge(response.sent_status || response.status || "-", statusType(response.sent_status || response.status))}</td>
        <td>${escapeHtml(response.rendered_title || response.title || "-")}</td>
        <td>${escapeHtml(response.rendered_message || response.message || response.body || "-")}</td>
        <td>${yesNo(response.opened)}</td>
        <td>${yesNo(response.clicked)}</td>
        <td>${yesNo(response.converted)}</td>
        <td>${formatDateTime(response.sent_at || response.response_time || response.created_at)}</td>
      </tr>`).join("");
  setHtml("campaignResponsesBody", rows || emptyRow(11, "No responses found."));
  normalizeResponseTableColumns();
  renderTablePagination("campaignResponsesPagination", totalRows, campaignState.responsesPage, pageSize, "changeCampaignResponsesPage");
}

function onMetricsCampaignChange() {
  const campaignId = getValue("metricsCampaignSelect");
 
  campaignState.selectedCampaignId = campaignId;
 
  loadCampaignMetrics(campaignId);
}
 
function renderSelectedCampaignMetrics(metrics = campaignState.latestMetrics) {
  const grid = document.getElementById("selectedCampaignMetricsGrid");
 
  if (!grid) return;
 
  if (!metrics) {
    grid.innerHTML = `<p class="muted">Select a campaign to load metrics.</p>`;
    return;
  }
 
  const removed =
    num(metrics, ["removed_count", "removed_due_to_consent_or_dnc"]) ||
    num(metrics, ["no_consent_removed"]) + num(metrics, ["dnc_removed"]);
 
  const cards = [
    ["Campaign ID", metrics.campaign_id || "-"],
    ["Total Audience", num(metrics, ["total_audience"])],
    ["Eligible", num(metrics, ["eligible_count", "eligible_after_consent"])],
    ["Removed", removed],
    ["Sent", num(metrics, ["sent_count"])],
    ["Failed", num(metrics, ["failed_count"])],
    ["Opened", num(metrics, ["opened_count", "opened_today"])],
    ["Clicked", num(metrics, ["clicked_count", "clicked_today"])],
    ["Converted", num(metrics, ["converted_count", "converted_today"])],
  ];
 
  grid.innerHTML = cards.map(([label, value]) => metricCard(label, value)).join("");
}
 
function renderCampaignDashboard() {
  const data = campaignState.dailySummary || {};
  const summary = data.summary || data;
 
  setText(
    "kpiTotalCampaigns",
    summary.total_campaigns ||
      summary.campaigns_created_today ||
      campaignState.campaigns.length ||
      0
  );
 
  setText("kpiSentToday", summary.sent_today || summary.campaigns_sent_today || 0);
  setText("kpiMessagesToday", summary.messages_sent_today || summary.sent_count || 0);
  setText("kpiEligibleToday", summary.eligible_audience_today || summary.eligible_count || 0);
  setText("kpiRemovedToday", summary.removed_due_to_consent_or_dnc || summary.removed_count || 0);
  setText("kpiOpenCount", summary.opened_today || summary.open_count || 0);
  setText("kpiClickCount", summary.clicked_today || summary.click_count || 0);
  setText("kpiConversionCount", summary.converted_today || summary.conversion_count || 0);
 
  renderBestCampaign(data.best_campaign);
  renderChannelSplit(data.channel_split || []);
}
 
function renderBestCampaign(best) {
  const box = document.getElementById("bestCampaignBox");
 
  if (!box) return;
 
  if (!best) {
    box.innerHTML = `
      <strong>No data available</strong>
      <span>Campaign performance will appear after records are available.</span>
    `;
 
    return;
  }
 
  box.innerHTML = `
    <strong>${escapeHtml(best.campaign_name || best.name || "-")}</strong>
    <span>Conversions: ${num(best, ["converted_count", "conversion_count"])}</span>
  `;
}
 
function renderChannelSplit(split) {
  const box = document.getElementById("channelSplitBox");
 
  if (!box) return;
 
  const html = toList(split)
    .map((item) => {
      return `
        <div class="channel-item">
          <span>${escapeHtml(item.business_channel || item.channel || "-")}</span>
          <strong>${escapeHtml(item.campaign_count || item.count || 0)}</strong>
        </div>
      `;
    })
    .join("");
 
  box.innerHTML = html || `<p class="muted">No channel data available.</p>`;
}
 
function renderDailyMetrics() {
  const grid = document.getElementById("dailyMetricsGrid");
 
  if (!grid) return;
 
  const data = campaignState.dailySummary || {};
  const summary = data.summary || data;
 
  const cards = [
    ["Messages Sent Today", summary.messages_sent_today || 0],
    ["Sent Today", summary.sent_today || summary.campaigns_sent_today || 0],
    ["Failed Today", summary.failed_today || summary.failed_count || 0],
    ["Opened Today", summary.opened_today || summary.open_count || 0],
    ["Clicked Today", summary.clicked_today || summary.click_count || 0],
    ["Converted Today", summary.converted_today || summary.conversion_count || 0],
    ["Campaigns Created Today", summary.campaigns_created_today || summary.total_campaigns || 0]
  ];
 
  grid.innerHTML = cards.map(([label, value]) => metricCard(label, value)).join("");
}
 
function renderAllCampaignDropdowns() {
  const ids = [
    "sendCampaignSelect",
    "responsesCampaignSelect",
    "metricsCampaignSelect"
  ];
 
  const options = campaignState.campaigns
    .map((campaign) => {
      const id = getCampaignId(campaign);
      const name = campaign.campaign_name || campaign.name || id;
 
      return `<option value="${escapeAttr(id)}">${escapeHtml(id)} - ${escapeHtml(name)}</option>`;
    })
    .join("");
 
  ids.forEach((id) => {
    const select = document.getElementById(id);
 
    if (!select) return;
 
    select.innerHTML = options || `<option value="">No campaigns found</option>`;
 
    if (campaignState.selectedCampaignId) {
      select.value = campaignState.selectedCampaignId;
    }
  });
}
 
function toList(result) {
  if (Array.isArray(result)) return result;
  if (result && Array.isArray(result.data)) return result.data;
  if (result && Array.isArray(result.items)) return result.items;
  if (result && Array.isArray(result.results)) return result.results;
  if (result && Array.isArray(result.templates)) return result.templates;
  if (result && Array.isArray(result.campaigns)) return result.campaigns;
  if (result && Array.isArray(result.responses)) return result.responses;
 
  return [];
}
 
function getCampaignId(campaign) {
  return String(
    campaign &&
      (campaign.campaign_id || campaign.id || campaign.campaignId || "")
  );
}
 
function getTemplateId(template) {
  return String(
    template &&
      (template.template_id || template.id || template.templateId || "")
  );
}
 
function getCampaignById(id) {
  return campaignState.campaigns.find((campaign) => {
    return String(getCampaignId(campaign)) === String(id);
  });
}
 
function getTemplateById(id) {
  return campaignState.templates.find((template) => {
    return String(getTemplateId(template)) === String(id);
  });
}
 
function num(obj, keys) {
  if (!obj) return 0;
 
  for (const key of keys) {
    if (obj[key] !== undefined && obj[key] !== null && obj[key] !== "") {
      const parsed = Number(obj[key]);
      return Number.isNaN(parsed) ? 0 : parsed;
    }
  }
 
  return 0;
}
 
function statusType(status) {
  const value = String(status || "").toLowerCase();
 
  if (
    value.includes("sent") ||
    value.includes("success") ||
    value.includes("completed") ||
    value.includes("live")
  ) {
    return "success";
  }
 
  if (value.includes("fail") || value.includes("error")) {
    return "danger";
  }
 
  return "warning";
}
 
function statusBadge(text, type) {
  return `<span class="status-pill ${escapeAttr(type || "warning")}">${escapeHtml(text)}</span>`;
}
 
function metricCard(label, value) {
  return `
    <div class="kpi-card">
      <span>${escapeHtml(label)}</span>
      <strong>${escapeHtml(value)}</strong>
    </div>
  `;
}
 
function emptyRow(colspan, message) {
  return `
    <tr>
      <td colspan="${colspan}" class="muted">${escapeHtml(message)}</td>
    </tr>
  `;
}
 
function yesNo(value) {
  return value === true || value === 1 || value === "1" ? "Yes" : "No";
}
 
function formatCurrency(value) {
  const number = Number(value || 0);
  return `₹${number.toLocaleString("en-IN")}`;
}
 
function formatDateTime(value) {
  if (!value) return "-";
 
  const date = new Date(value);
 
  return Number.isNaN(date.getTime()) ? String(value) : date.toLocaleString();
}
 
function getValue(id) {
  const el = document.getElementById(id);
  return el ? String(el.value || "").trim() : "";
}
 
function setValue(id, value) {
  const el = document.getElementById(id);
 
  if (el) {
    el.value = value;
  }
}
 
function setSelectValue(id, value) {
  const el = document.getElementById(id);
 
  if (el && value !== undefined && value !== null) {
    el.value = String(value);
  }
}
 
function setText(id, value) {
  const el = document.getElementById(id);
 
  if (el) {
    el.textContent = value;
  }
}
 
function setHtml(id, html) {
  const el = document.getElementById(id);
 
  if (el) {
    el.innerHTML = html;
  }
}
 
function setJson(id, data) {
  const el = document.getElementById(id);
 
  if (el) {
    el.textContent = JSON.stringify(data, null, 2);
  }
}
 
function openTab(tabName) {
  const btn = document.querySelector(
    `.tab-btn[onclick*="'${tabName}'"], .tab-btn[onclick*='"${tabName}"']`
  );
 
  switchCampaignTab(tabName, btn);
}
 
function escapeHtml(value) {
  return String(value === undefined || value === null ? "" : value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
 
function escapeAttr(value) {
  return escapeHtml(value);
}