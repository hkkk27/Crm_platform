const AppState = {
    user: null,
    currentTab: "workspace"
};

const BACKEND_BASE_URL = "http://127.0.0.1:8000";

document.addEventListener("DOMContentLoaded", function () {
    console.log("script.js loaded. Backend URL:", BACKEND_BASE_URL);

    const loginForm = document.getElementById("login-form");
    if (loginForm) {
        loginForm.addEventListener("submit", handleLiveBackendLogin);
    }

    const cachedSession = localStorage.getItem("crm_session");
    if (cachedSession) {
        try {
            AppState.user = JSON.parse(cachedSession);
        } catch (error) {
            localStorage.removeItem("crm_session");
            AppState.user = null;
        }
    }

    syncInterfaceDOM();
});

function normalizeLoginRole(value) {
    const role = String(value || "").trim().toLowerCase();

    const roleMap = {
        "admin": "System Administrator",
        "administrator": "System Administrator",
        "system administrator": "System Administrator",

        "crm team": "Marketing Team",
        "crm & marketing team": "Marketing Team",
        "crm and marketing team": "Marketing Team",
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

    return roleMap[role] || value;
}

function getDefaultPageByRole(role) {
    const normalizedRole = normalizeLoginRole(role);

    const landingPages = {
        "System Administrator": "./pages/dashboard.html",
        "Marketing Team": "./pages/campaign.html",
        "Store Team": "./pages/customer.html",
        "Management Team": "./pages/dashboard.html",
        "Customer Service Team": "./pages/customer.html",
        "IT Team": "./pages/admin.html"
    };

    return landingPages[normalizedRole] || "./pages/settings.html";
}

async function handleLiveBackendLogin(event) {
    event.preventDefault();

    const emailInput = document.getElementById("login-email");
    const passwordInput = document.getElementById("login-password");
    const roleInput = document.getElementById("login-role");

    if (!emailInput || !passwordInput || !roleInput) {
        dispatchToast("Login form fields are missing.");
        return;
    }

    const emailValue = emailInput.value.trim();
    const passwordValue = passwordInput.value.trim();
    const roleValue = roleInput.value;

    if (emailValue === "" || passwordValue === "") {
        dispatchToast("Please enter email and password.");
        return;
    }

    const BACKEND_AUTH_ENDPOINT = `${BACKEND_BASE_URL}/auth/login`;

    try {
        const response = await fetch(BACKEND_AUTH_ENDPOINT, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                email: emailValue,
                password: passwordValue
            })
        });

        let result = {};
        try {
            result = await response.json();
        } catch (jsonError) {
            dispatchToast("Backend response is invalid. Please check API response format.");
            return;
        }

        if (!response.ok) {
            dispatchToast(
                `Access Denied: ${
                    result.detail || result.message || "Invalid email or password."
                }`
            );
            return;
        }

        if (!result.access_token) {
            dispatchToast("Login failed. Backend did not return access token.");
            return;
        }

        const normalizedRole = normalizeLoginRole(result.user?.role || roleValue);
        const redirectTarget = getDefaultPageByRole(normalizedRole);

        AppState.user = {
            email: result.user?.email || emailValue,
            name: result.user?.name || result.user?.full_name || result.user?.user_name || emailValue.split("@")[0],
            role: normalizedRole,
            token: result.access_token,
            allowedModules: result.user?.allowed_modules || []
        };

        localStorage.setItem("crm_session", JSON.stringify(AppState.user));
        localStorage.setItem("omnilink_token", result.access_token);
        localStorage.setItem("omnilink_role", AppState.user.role);
        localStorage.setItem("omnilink_email", AppState.user.email);
        localStorage.setItem("userRole", AppState.user.role);
        localStorage.setItem("userName", AppState.user.name);

        dispatchToast("Login successful. Redirecting...");
        setTimeout(function () {
            window.location.href = redirectTarget;
        }, 800);
    } catch (error) {
        console.error("Backend connection failed:", error);
        dispatchToast(
            `Backend Server Issue: Please make sure FastAPI backend is running on ${BACKEND_BASE_URL}`
        );
    }
}

function handleLogout() {
    AppState.user = null;
    AppState.currentTab = "workspace";

    localStorage.removeItem("crm_session");
    localStorage.removeItem("omnilink_token");
    localStorage.removeItem("omnilink_role");
    localStorage.removeItem("omnilink_email");
    localStorage.removeItem("userRole");
    localStorage.removeItem("userName");
    localStorage.removeItem("token");

    dispatchToast("Session ended successfully.");
    setTimeout(function () {
        window.location.href = "../login.html";
    }, 600);
}

function switchTab(targetTabId) {
    AppState.currentTab = targetTabId;

    const workspaceButton = document.getElementById("tab-btn-workspace");
    const customerButton = document.getElementById("tab-btn-customer360");

    if (workspaceButton && customerButton) {
        if (targetTabId === "workspace") {
            workspaceButton.classList.add("active-tab");
            customerButton.classList.remove("active-tab");
        } else {
            customerButton.classList.add("active-tab");
            workspaceButton.classList.remove("active-tab");
            triggerSecureDataQuery();
        }
    }

    syncInterfaceDOM();
}

function syncInterfaceDOM() {
    const loginPage = document.getElementById("login-page");
    const mainLayout = document.getElementById("main-layout");

    if (!loginPage || !mainLayout) {
        return;
    }

    if (!AppState.user) {
        loginPage.classList.remove("hidden");
        mainLayout.classList.add("hidden");
        return;
    }

    loginPage.classList.add("hidden");
    mainLayout.classList.remove("hidden");

    const userBadge = document.getElementById("user-badge");
    const headerUserEmail = document.getElementById("header-user-email");

    if (userBadge) {
        userBadge.innerText = `Role Context: ${AppState.user.role}`;
    }

    if (headerUserEmail) {
        headerUserEmail.innerText = AppState.user.email;
    }

    const workspaceView = document.getElementById("view-workspace");
    const customerView = document.getElementById("view-customer360");

    if (!workspaceView || !customerView) {
        return;
    }

    if (AppState.currentTab === "workspace") {
        workspaceView.classList.remove("hidden");
        customerView.classList.add("hidden");

        const roleBanner = document.getElementById("role-alert-box");
        const customPolicy = typeof POLICY_MATRIX !== "undefined" ? POLICY_MATRIX[AppState.user.role] : null;

        if (roleBanner && customPolicy) {
            roleBanner.className = `role-banner ${customPolicy.cssClass}`;
            roleBanner.innerText = customPolicy.text;
            roleBanner.classList.remove("hidden");
        }
    } else {
        workspaceView.classList.add("hidden");
        customerView.classList.remove("hidden");

        const phoneSelector = document.getElementById("masked-phone-field");
        if (phoneSelector) {
            if (
                AppState.user.role === "Store Team" ||
                AppState.user.role === "Management Team"
            ) {
                phoneSelector.innerText = "98xxxxxx45 (Field Masked via Profile Scope Rules)";
            } else {
                phoneSelector.innerText = "9876543210 (Full Administrative Clear Read Authorized)";
            }
        }
    }
}

function dispatchToast(messageText) {
    if (typeof window.showAppPopup === "function") {
        window.showAppPopup(messageText);
        return;
    }

    const layerTarget = document.getElementById("toast-container");
    if (!layerTarget) {
        alert(messageText);
        return;
    }

    const toastNode = document.createElement("div");
    toastNode.className = "toast-message-box";
    toastNode.innerHTML = `
        <span class="toast-tag">System Broadcast</span>
        <span class="toast-text">${messageText}</span>
    `;

    layerTarget.appendChild(toastNode);

    setTimeout(function () {
        toastNode.style.opacity = "0";
        toastNode.style.transform = "translateY(-15px)";
        setTimeout(function () {
            toastNode.remove();
        }, 300);
    }, 4000);
}

async function triggerSecureDataQuery() {
    if (!AppState.user || !AppState.user.token) {
        console.warn("No active token found.");
        return;
    }

    const SECURE_API_TARGET = `${BACKEND_BASE_URL}/customers/CUST-1001`;

    try {
        const queryResponse = await fetch(SECURE_API_TARGET, {
            method: "GET",
            headers: {
                Authorization: `Bearer ${AppState.user.token}`
            }
        });

        if (queryResponse.ok) {
            const serverPayload = await queryResponse.json();
            console.log("Secure transmission verified:", serverPayload);

            const phoneSelector = document.getElementById("masked-phone-field");
            if (phoneSelector && serverPayload.phone) {
                phoneSelector.innerText = serverPayload.phone;
            }
        }
    } catch (error) {
        console.warn("Backend customer API currently unavailable.");
    }
}
