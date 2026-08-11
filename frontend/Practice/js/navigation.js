const NAV_ITEMS = [
  {
    label: "Dashboard",
    href: "dashboard.html",
    key: "dashboard",
    active: "dashboard",
    icon: "../nav-dashboard.png"
  },
  {
    label: "Customers",
    href: "customer.html",
    key: "customers",
    active: "customers",
    icon: "../nav-customers.png"
  },
  {
    label: "Loyalty",
    href: "loyalty.html",
    key: "loyalty",
    active: "loyalty",
    icon: "../nav-loyalty.png"
  },
  {
    label: "Customer Service",
    href: "Customer Service.html",
    key: "customer-service",
    active: "customer-service",
    icon: "../nav-service.png"
  },
  {
    label: "Campaigns",
    href: "campaign.html",
    key: "campaigns",
    active: "campaigns",
    icon: "../nav-campaign.png"
  },
  {
    label: "Reports",
    href: "Reports.html",
    key: "reports",
    active: "reports",
    icon: "../nav-reports.png"
  },
  {
    label: "Audit Logs",
    href: "audit.html",
    key: "audit",
    active: "audit",
    icon: "../nav-audit.png"
  },
  {
    label: "Admin",
    href: "admin.html",
    key: "admin",
    active: "admin",
    icon: "../nav-admin.png"
  },
  {
    label: "Settings",
    href: "settings.html",
    key: "settings",
    active: "settings",
    icon: "../nav-settings.png"
  }
];

const ROLE_ACCESS = {
  "System Administrator": [
    "dashboard",
    "customers",
    "loyalty",
    "customer-service",
    "campaigns",
    "reports",
    "audit",
    "admin",
    "settings"
  ],
  "Marketing Team": ["campaigns", "loyalty", "settings"],
  "Store Team": ["customers", "loyalty", "settings"],
  "Management Team": ["dashboard", "customers", "reports", "settings"],
  "Customer Service Team": ["customers", "customer-service", "settings"],
  "IT Team": ["admin", "audit", "settings"]
};

function loadNavigation(activePage) {
  const sidebar = document.getElementById("sidebar");
  const profile = getSidebarProfile();
  const allowedKeys = getAllowedPageKeys(profile.role);
  const navLinks = NAV_ITEMS
    .filter(item => allowedKeys.includes(item.key))
    .map(item => `
      <a href="${item.href}" class="${activePage === item.active ? "active" : ""}">
        <img src="${item.icon}" class="nav-img-icon" alt="">
        <span>${item.label}</span>
      </a>
    `)
    .join("");

  sidebar.innerHTML = `
    <div class="logo">
      <img src="../logo.png" alt="OmniLink Logo" class="sidebar-logo" onerror="this.style.display='none'; this.parentElement.insertAdjacentHTML('beforeend', '<strong class=&quot;sidebar-logo-text&quot;>Omnilink</strong>')">
    </div>

    <nav class="nav">
      ${navLinks}
    </nav>

    <div class="sidebar-user-area">
      <div class="sidebar-user-card">
        <div class="sidebar-user-avatar">${profile.initials}</div>
        <div class="sidebar-user-text">
          <strong>${profile.name}</strong>
          <small>${profile.role}</small>
        </div>
      </div>
      <button class="logout-btn" onclick="logout()">Logout</button>
    </div>
  `;

  initSidebarToggle();
  hideRestrictedPageActions();
}

function getAllowedPageKeys(role) {
  return ROLE_ACCESS[role] || ["settings"];
}

function userCanAccess(pageKey) {
  const profile = getSidebarProfile();
  return getAllowedPageKeys(profile.role).includes(pageKey);
}

function guardPage(pageKey) {
  if (!userCanAccess(pageKey)) {
    window.location.href = "settings.html";
  }
}

function hideRestrictedPageActions() {
  const allowedKeys = getAllowedPageKeys(getSidebarProfile().role);

  document.querySelectorAll("[data-page-key]").forEach(element => {
    const key = element.getAttribute("data-page-key");
    element.style.display = allowedKeys.includes(key) ? "" : "none";
  });

  if (!allowedKeys.includes("dashboard")) {
    document.querySelectorAll("a, button").forEach(element => {
      const text = element.textContent.trim().toLowerCase();
      const href = (element.getAttribute("href") || "").toLowerCase();
      if (text === "dashboard" || href.includes("dashboard.html")) {
        element.style.display = "none";
      }
    });
  }
}

function getSidebarProfile() {
  let session = null;
  try { session = JSON.parse(localStorage.getItem("crm_session") || "null"); } catch (error) { session = null; }

  const email = session?.email || localStorage.getItem("omnilink_email") || localStorage.getItem("userName") || "admin@omnilink.com";
  const role = session?.role || localStorage.getItem("omnilink_role") || localStorage.getItem("userRole") || "System Administrator";
  const storedName = localStorage.getItem("userName");
  const sessionName = session?.name || session?.full_name || session?.user_name;
  const emailName = email.includes("@") ? email.split("@")[0].replace(/[._-]/g, " ") : "Admin";
  const name = titleCaseForSidebar(storedName || sessionName || emailName || "Admin");

  return { name, role: normalizeRole(role), initials: getSidebarInitials(name) };
}

function normalizeRole(value) {
  const role = String(value || "").trim().toLowerCase();
  const roleMap = {
    "admin": "System Administrator",
    "administrator": "System Administrator",
    "system administrator": "System Administrator",
    "crm team": "Marketing Team",
    "crm & marketing team": "Marketing Team",
    "marketing": "Marketing Team",
    "marketing team": "Marketing Team",
    "store": "Store Team",
    "store team": "Store Team",
    "management": "Management Team",
    "management team": "Management Team",
    "customer service": "Customer Service Team",
    "customer service team": "Customer Service Team",
    "security / it": "IT Team",
    "security/it": "IT Team",
    "it": "IT Team",
    "it team": "IT Team"
  };
  return roleMap[role] || titleCaseForSidebar(value);
}

function titleCaseForSidebar(value) {
  return String(value || "").split(" ").filter(Boolean).map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()).join(" ");
}

function getSidebarInitials(name) {
  return String(name || "Admin").trim().split(/\s+/).slice(0, 2).map(part => part.charAt(0)).join("").toUpperCase() || "A";
}

function logout() {
  localStorage.removeItem("crm_session");
  localStorage.removeItem("omnilink_email");
  localStorage.removeItem("omnilink_role");
  localStorage.removeItem("userRole");
  localStorage.removeItem("userName");
  localStorage.removeItem("token");
  window.location.href = "../login.html";
}

function initSidebarToggle() {
  const sidebar = document.getElementById("sidebar");
  const main = document.querySelector(".main");
  if (!sidebar || !main) return;

  let toggleBtn = document.getElementById("sidebarToggle");
  let overlay = document.getElementById("sidebarOverlay");

  if (!toggleBtn) {
    toggleBtn = document.createElement("button");
    toggleBtn.id = "sidebarToggle";
    toggleBtn.className = "sidebar-toggle";
    toggleBtn.type = "button";
    toggleBtn.setAttribute("aria-label", "Toggle sidebar");
    toggleBtn.innerHTML = '❮';
    document.body.appendChild(toggleBtn);
  }

  if (!overlay) {
    overlay = document.createElement("div");
    overlay.id = "sidebarOverlay";
    overlay.className = "sidebar-overlay";
    document.body.appendChild(overlay);
  }

  const isMobile = () => window.matchMedia("(max-width: 900px)").matches;

  function applyState() {
    if (isMobile()) {
      sidebar.classList.remove("collapsed");
      main.classList.remove("full-width");
      const open = sidebar.classList.contains("mobile-open");
      overlay.classList.toggle("active", open);
      toggleBtn.classList.toggle("sidebar-hidden", !open);
    } else {
      sidebar.classList.remove("mobile-open");
      overlay.classList.remove("active");
      const collapsed = localStorage.getItem("sidebarCollapsed") === "true";
      sidebar.classList.toggle("collapsed", collapsed);
      main.classList.toggle("full-width", collapsed);
      toggleBtn.classList.toggle("sidebar-hidden", collapsed);
    }
  }

  toggleBtn.onclick = () => {
    if (isMobile()) { sidebar.classList.toggle("mobile-open"); }
    else { const collapsed = !sidebar.classList.contains("collapsed"); localStorage.setItem("sidebarCollapsed", collapsed ? "true" : "false"); }
    applyState();
  };

  overlay.onclick = () => { sidebar.classList.remove("mobile-open"); applyState(); };
  window.addEventListener("resize", applyState);
  applyState();
}

document.addEventListener("DOMContentLoaded", () => {
  hideRestrictedPageActions();
  setTimeout(hideRestrictedPageActions, 0);
});
